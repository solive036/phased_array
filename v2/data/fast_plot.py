import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

# Initialize the application
app = QApplication(sys.argv)

# Create a window
win = pg.GraphicsLayoutWidget(show=True, title="Updating Polar Plot")
view = win.addViewBox()

# Create a polar plot item
polarPlot = pg.PlotCurveItem(pen='w')
view.addItem(polarPlot)

#create circles
theta = np.linspace(0, 2* np.pi, 100)
radius_1 = 4 
x_1 = radius_1 * np.cos(theta)
y_1 = radius_1 * np.sin(theta)
circle_1 = pg.PlotCurveItem(x_1, y_1, pen='w')
view.addItem(circle_1)


# Example data: replace these with your actual data
theta = np.linspace(0, 2 * np.pi, 100)  # Angles in radians
power_dB = np.random.rand(100) * 20 - 100  # Example power values in dB

# Initial plot: convert dB to linear scale for plotting
polarPlot.setData(power_dB * np.cos(theta), power_dB * np.sin(theta))

# Timer for updating the plot
def update():
    global power_dB
    # Simulate updating your data
    power_dB = np.random.rand(100) * 20 - 100  # Replace with your updated power values
    polarPlot.setData(power_dB * np.cos(theta), power_dB * np.sin(theta))

# Set up a timer to call the update function
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(100)  # Update every 100 ms

# Start the Qt application event loop
app.exec_()