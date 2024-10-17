import adi
from adi.cn0566 import CN0566
import numpy as np

def set_phase(phaser):
    phase = np.arange(-180, 180, 2)
    for p in phase:
 
        for i in range(8):
            channel_phase = (phase * i) % 360
            phaser.elements.get(i + 1).rx_phase = channel_phase
        phaser.latch_rx_settings()

def print_channel_phase(phaser):
    for i in range(0, 8):
        print(phaser.elements.get(i+1).rx_phase)

