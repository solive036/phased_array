import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import random

fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(-10, 10)
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')
ax.set_title('Animated Horizontal Line')

line, = ax.plot([], [], lw=2)

def init():
    line.set_data([], [])
    return line,

def update(frame):
    y = random.uniform(-10, 10)
    x = np.linspace(0, 10, 100)
    y_values = [y] * len(x)
    line.set_data(x, y_values)
    return line,

ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=200)

plt.show()
