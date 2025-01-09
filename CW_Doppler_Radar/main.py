from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
import pyqtgraph as pg
import numpy as np
import data_processing as dp
import adi
import sys
import csv

spectrogram_width = 75
file_name = 'data.npy'
fopen = ('data.npy', 'ab')

#Initialize SDR and Phaser
try:
    #initialize hardware
    sdr_ip = "ip:192.168.2.1"
    phaser_ip = "ip:phaser.local"
    sdr = adi.ad9361(uri=sdr_ip)
    phaser = adi.CN0566(uri=phaser_ip, sdr=sdr)
    print('Phaser and Pluto Connected')
except:
    print('Error connecting phaser and sdr')
    exit()

phaser.configure(device_mode="rx")

#initialize ADAR1000
for i in range(0, 8):
    phaser.set_chan_phase(i, 0)

gain_list = [8, 34, 84, 127, 127, 84, 34, 8]

for i in range(0, len(gain_list)):
    phaser.set_chan_gain(i, gain_list[i], apply_cal=True)

# Setup Raspberry Pi GPIO states
try:
    phaser._gpios.gpio_tx_sw = 0 
    phaser._gpios.gpio_vctrl_1 = 1 # 1=Use onboard PLL/LO source
    phaser._gpios.gpio_vctrl_2 = 1 # 1=Send LO to transmit circuitry
except:
    phaser.gpios.gpio_tx_sw = 0  # 0 = TX_OUT_2, 1 = TX_OUT_1
    phaser.gpios.gpio_vctrl_1 = 1 # 1=Use onboard PLL/LO source  (0=disable PLL and VCO, and set switch to use external LO input)
    phaser.gpios.gpio_vctrl_2 = 1 # 1=Send LO to transmit circuitry  (0=disable Tx path, and send LO to LO_OUT)

#sdr settings
sample_rate = 0.6e6
center_freq = 4.2e9 #center_freq = 2.1e9
signal_freq = 100e3
fft_size = 1024 * 64

sdr.sample_rate = int(sample_rate)
sdr.rx_lo = int(center_freq)
sdr.rx_enabled_channels = [0, 1]
sdr.rx_buffer_size = int(fft_size)
sdr.gain_control_mode_chan0 = 'manual'
sdr.gain_control_mode_chan1 = 'manual'
sdr.rx_hardwaregain_chan0 = int(60)
sdr.rx_hardwaregain_chan1 = int(60)

sdr.tx_lo = int(center_freq)
sdr.tx_enabled_channels = [0, 1]
sdr.tx_cyclic_buffer = True
sdr.tx_hardwaregain_chan0 = -88 #attenuated
sdr.tx_hardwaregain_chan1 = -0

#configure ramping PLL (ADF4159)
output_freq = 12.2e9
phaser.frequency = int(output_freq/4)
phaser.ramp_mode = 'disabled'
phaser.enable = 0

# Create a sinewave waveform
fs = int(sdr.sample_rate)
N = int(sdr.rx_buffer_size)
fc = int(signal_freq / (fs / N)) * (fs / N)
ts = 1 / float(fs)
t = np.arange(0, N * ts, ts)
i = np.cos(2 * np.pi * t * fc) * 2 ** 14
q = np.sin(2 * np.pi * t * fc) * 2 ** 14
iq = 1 * (i + 1j * q)

freq = np.linspace(-fs / 2, fs / 2, int(fft_size))

sampling_period = 1/sdr.sample_rate
print('Sampling period: ', sampling_period)
t = sampling_period*np.arange(fft_size)

#transmit data
sdr._ctx.set_timeout(0)
beat_freq_prev = 0
file = 'data.csv'

class SDRWorker(QObject):
    spectrogram_update = pyqtSignal(np.ndarray)
    end_of_run = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.spectrogram = np.zeros((fft_size, spectrogram_width))

    def run(self):
        samples = phaser.sdr.rx()
        samples = samples[0] + samples[1]
        window = np.blackman(len(samples))
        samples = samples * window
        psd = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples)))**2)
        freq_axis = np.linspace(-sample_rate/2, sample_rate/2, len(psd))

        #save data to csv file
        with open(file, 'a', newline='') as fl:
            writer = csv.writer(fl)
            writer.writerow(samples)
        
        #spectrogram
        self.spectrogram = np.roll(self.spectrogram, 1, axis=1)
        self.spectrogram[:, 0] = psd
        self.spectrogram_update.emit(self.spectrogram)
        self.end_of_run.emit()
        
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.sdr_thread = QThread()
        self.worker = SDRWorker()
        self.worker.moveToThread(self.sdr_thread)

        self.setWindowTitle('Doppler Radar')
        layout = QHBoxLayout()

        self.spectrogram_widget = QWidget()
        spectrogram = pg.PlotWidget(labels={'left': 'Time', 'bottom': 'Frequency'})
        self.imageitem = pg.ImageItem(axisOrder='col-major')
        spectrogram.addItem(self.imageitem)
        layout.addWidget(spectrogram)
        colorbar = pg.HistogramLUTWidget()
        colorbar.setImageItem(self.imageitem)
        colorbar.item.gradient.loadPreset('viridis')
        self.imageitem.setLevels((-30, 30))
        self.spectrogram_widget.setLayout(layout)

        main_widget = QWidget(self)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        self.worker.spectrogram_update.connect(self.spectrogram_callback)
        self.worker.end_of_run.connect(self.end_of_run_callback)
        self.sdr_thread.started.connect(self.worker.run)

        self.sdr_thread.start()

    def spectrogram_callback(self, spectrogram_data):
        self.imageitem.setImage(spectrogram_data, autoLevels=True)

    def end_of_run_callback(self):
        QTimer.singleShot(0, self.worker.run)

if __name__ == '__main__':
    print('Starting GUI')
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
