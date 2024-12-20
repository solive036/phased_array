import matplotlib.pyplot as plt
import adi
import numpy as np
import sys
import phaser_functions as PHASER
import pickle
import data_processing as dp
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg

"""
HARDWARE SETUP
"""
#initialize hardware
sdr_ip = "ip:192.168.2.1"
phaser_ip = "ip:phaser.local"
sdr = adi.ad9361(uri=sdr_ip)
phaser = adi.CN0566(uri=phaser_ip, sdr=sdr)

#get signal frequency of HB100
signal_freq = pickle.load(open("hb100_freq_val.pkl", "rb"))

phaser.configure(device_mode='rx')
phaser.load_gain_cal()
phaser.load_phase_cal()
for i in range(0, 8):
    phaser.set_chan_phase(i, 0)

gain_list = [8, 34, 84, 127, 127, 84, 34, 8]  # Blackman taper
for i in range(0, len(gain_list)):
    phaser.set_chan_gain(i, gain_list[i], apply_cal=True)

sdr._ctrl.debug_attrs["adi,frequency-division-duplex-mode-enable"].value = "1"
sdr._ctrl.debug_attrs["adi,ensm-enable-txnrx-control-enable"].value = "0" # Disable pin control so spi can move the states
sdr._ctrl.debug_attrs["initialize"].value = "1"
sdr.rx_enabled_channels = [0, 1] # enable Rx1 and Rx2
sdr._rxadc.set_kernel_buffers_count(1) # No stale buffers to flush
sdr.tx_hardwaregain_chan0 = int(-80) # Make sure the Tx channels are attenuated (or off)
sdr.tx_hardwaregain_chan1 = int(-80)

#sdr parameters
sample_rate = int(30e6)
center_freq = 2.2e9
fft_size  = 1024

#sdr setup
sdr.sample_rate = int(sample_rate)
sdr.rx_lo = int(2.2e9)
sdr.rx_enabled_channels = [0, 1]
sdr.rx_buffer_size = int(fft_size)
sdr.gain_control_mode_chan0 = "manual"  # manual or slow_attack
sdr.gain_control_mode_chan1 = "manual"  # manual or slow_attack
sdr.rx_hardwaregain_chan0 = int(30)  # must be between -3 and 70
sdr.rx_hardwaregain_chan1 = int(30)  # must be between -3 and 70

offset = 1000000
phaser.lo = int(signal_freq + sdr.rx_lo - offset)

class Worker(QObject):
    def __init__(self):
        super().__init__()

        doa_plot_update = pyqtSignal(np.ndarray, np.ndarray)
        end_of_run = pyqtSignal()

        def run(self):
            aoas, powers = PHASER.DOA(phaser, signal_freq)
            doa_plot_update.emit(aoas, powers)
            end_of_run.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.thread = QThread()
        worker = Worker()
        worker.moveToThread(self.thread)

        ###GUI Setup
        self.setWindowTitle('Direction of Arrival')
        main_layout = QVBoxLayout()

        #setup plot
        doa_plot = pg.PlotWidget(labels={'top':'Direction of Arrival', 'left':'Amplitude', 'bottom':'Angle'})
        doa_plot.setMouseEnabled(x=False, y=False)
        c1 = doa_plot.plot()
        main_layout.addWidget(doa_plot)
        
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        #define callbacks
        def doa_plot_callback(axis, data):
            self.c1.setData(axis, data)

        def end_of_run_callback():
            QTimer.singleShot(0, self.worker.run)

        self.worker.doa_plot_update.connect(doa_plot_callback)
        self.worker.end_of_run.connect(end_of_run_callback) 
        self.sdr_thread.started.connect(self.worker.run)
        self.sdr_thread.start()


if __name__ == '__main__':
    print('Starting GUI')
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

