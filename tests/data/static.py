from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow
from PyQt5.QtChart import QPolarChart, QChartView, QValueAxis, QScatterSeries
import numpy as np
class PolarChartWindow(QMainWindow):
    def __init__(self, aoas, powers):
        super().__init__()
        self.aoas = aoas
        self.powers = powers
        self.setWindowTitle("Polar Chart Example")
        self.setGeometry(100, 100, 1000, 1000)

        # Create the polar chart
        self.polar = QPolarChart()
        chartView = QChartView(self.polar)

        layout = QVBoxLayout()
        layout.addWidget(chartView)

        # Create container widget for our chart
        self.MyFrame = QtWidgets.QFrame(self)
        self.MyFrame.setLayout(layout)
        self.setCentralWidget(self.MyFrame)

        # Setting axes
        self.setupAxes()

        # Draw scatter series
        self.setupScatterSeries()

    def setupAxes(self):
        axisy = QValueAxis()
        axisx = QValueAxis()

        axisy.setRange(0, 500)
        axisy.setTickCount(4)
        self.polar.setAxisY(axisy)

        axisx.setRange(0, 360)
        axisx.setTickCount(5)
        self.polar.setAxisX(axisx)

    def setupScatterSeries(self):
        self.polar_series = QScatterSeries()
        self.polar_series.setMarkerSize(5.0)

        # Add points to the series
        self.polar_series.append(0, 0)
        self.polar_series.append(360, 500)

        # Draw Archimedes spiral
        for i in range(len(self.aoas)):
            self.polar_series.append(self.aoas[i], self.powers[i])

        self.polar.addSeries(self.polar_series)


if __name__ == "__main__":
    import sys
    aoas = np.load('aoas.npy')
    powers = np.load('powers.npy')
    app = QtWidgets.QApplication(sys.argv)
    window = PolarChartWindow(aoas, powers)
    window.show()
    sys.exit(app.exec_())
