from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
import pyqtgraph as pg
import numpy as np
#import data_processing as dp
import adi
import sys
import csv


"""define constants"""
file_name = 'fmcw_data.csv'

#for phaser and sdr
signal_freq = 10.2e9 #RF
rx_lo = 1.9e9 #IF
phaser_lo = signal_freq + rx_lo #LO
sample_rate = 0.6e6
fft_size = 1024 * 4
spectrogram_width = 70

#for PLL (adf4159)

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


#SDR Configuration
sdr.sample_rate = int(sample_rate)
sdr.rx_lo = int(rx_lo)
sdr.rx_enabled_channels = [0, 1]
sdr.rx_buffer_size = int(fft_size)
sdr.gain_control_mode_chan0 = 'manual'
sdr.gain_control_mode_chan1 = 'manual'
sdr.rx_hardwaregain_chan0 = int(30)
sdr.rx_hardwaregain_chan1 = int(30)

sdr.tx_lo = int(rx_lo)
sdr.tx_enabled_channels = [0, 1]
sdr.tx_cyclic_buffer = True
sdr.tx_hardwaregain_chan0 = -88
sdr.tx_hardwaregain_chan1 = -0

#adf4159 configuration
output_freq = phaser_lo
num_steps = 1000
ramp_time = 1.2e3 #us
BW = 500e6
ramp_time_s = ramp_time/1e6
phaser.frequency = int(output_freq/4)
phaser.freq_dev_range = int(BW/4)
phaser.freq_dev_step = int((BW/4)/num_steps)
phaser.freq_dev_time = int(ramp_time)
phaser.delay_word = 4095
phaser.delay_clk = 'PFD'
phaser.ramp_delay_en = 0
phaser.delay_start_en = 0
phaser.trig_delay_en = 0
phaser.ramp_mode = 'continuous_triangular'
phaser.sing_ful_tri = (0)
phaser.tx_trig_en = 0
phaser.enable = 0

# Create a sinewave waveform
fs = int(sdr.sample_rate)
print("sample_rate:", fs)
N = int(sdr.rx_buffer_size)
fc = int(signal_freq / (fs / N)) * (fs / N)
ts = 1 / float(fs)
t = np.arange(0, N * ts, ts)
i = np.cos(2 * np.pi * t * fc) * 2 ** 14
q = np.sin(2 * np.pi * t * fc) * 2 ** 14
iq = 1 * (i + 1j * q)

class SDRWorker(QObject):
    psd_update = pyqtSignal(np.ndarray, np.ndarray)
    end_of_run = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.spectrogram = np.zeros((fft_size, spectrogram_width))
        self.freq_axis = np.linspace(-sample_rate/2, sample_rate/2, fft_size)

    def run(self):
        samples = phaser.sdr.rx()
        samples = samples[0] + samples[1]
        window = np.blackman(len(samples))
        samples_w = window * samples
        psd = 10 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples_w)))**2)
         
        self.psd_update.emit(self.freq_axis, psd)
        self.end_of_run.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.sdr_thread = QThread()
        self.worker = SDRWorker()
        self.worker.moveToThread(self.sdr_thread)

        self.setWindowTitle('FMCW Radar')
        main_layout = QVBoxLayout()

        psd_widget = QWidget()
        psd_plot = pg.PlotWidget(labels={'left':'Amplitude', 'bottom':'freuquency'})
        psd_curve = psd_plot.plot([])
        main_layout.addWidget(psd_plot)
        psd_widget.setLayout(main_layout)

        def end_of_run_callback():
            QTimer.singleShot(0, self.worker.run)

        def psd_callback(freq_axis, )

