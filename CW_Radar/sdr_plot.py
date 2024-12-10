from PyQt6 import QtCore, QtWidgets
import pyqtgraph as pg
import adi
import numpy as np
import sys
import pickle
import sdr_functions as SDR
import phaser_functions as PHASER
import data_processing as dp

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, phaser, signal_freq):
        super().__init__()
        self.phaser = phaser
        self.signal_freq = signal_freq
        
        self.plot = pg.PlotWidget()
        self.setCentralWidget(self.plot)
        self.plot.setBackground('w')
        pen = pg.mkPen(color=(255,255,255))

        self.plot.setTitle('CW Radar', color='b', size='20pt')
        self.plot.setLabel('bottom', 'Time')
        self.plot.setLabel('left', 'Beat Frequency')
        self.setYRange(-2, 2)
        self.time = list(range(10))
        self.beat_frequencies = [0]*10

        #create the line
        self.line = self.plot.plot(
            self.time,
            self.beat_frequencies
            name='Beat Frequency'
            pen = pen
        )

        self.timer = QtCore.QTimer()
        self.timer.timer(300)
        self.timer.timeout.connect(self.get_data)
        self.timer.start()
        

        def get_data(self):
            data = self.phaser.sdr.rx()
            data = data[0] + data[1]
            psd, freq = dp.compute_psd(data, self.phaser)
            f_d = dp.get_freq_max_power(psd, freq)
            beat_freq = dp.compute_beat_freq(f_d, self.signal_freq)
            beat_freq = (beat_freq - self.signal_freq)

            self.time = self.time[1:]
            self.time.append(self.time[-1] + 1)
            self.beat_frequencies = self.beat_frequencies[1:]
            self.beat_freq.append(beat_freq)
            self.line.setData(self.time, self.beat_frequencies)


app = QtWidgets.QApplication([])
main = MainWindow()
main.show()
sys.exit(app.exec())