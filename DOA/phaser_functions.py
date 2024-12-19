import adi
from adi.cn0566 import CN0566
import numpy as np
import matplotlib.pyplot as plt

def DOA(phaser, signal_freq):
    powers = []
    aoas = []
    for phase in np.arange(-180, 180, 2):
        for i in range(8):
            channel_phase = (phase * i) % 360
            phaser.elements.get(i+1).rx_phase = channel_phase
        phaser.latch_rx_settings()
        steer_angle = np.degrees(np.arcsin(max(min(1, (3e8 * np.radians(phase)) / (2 * np.pi * signal_freq * phaser.element_spacing)), -1)))
        aoas.append(steer_angle)
        data = phaser.sdr.rx()
        data_sum = data[0] + data[1]
        power_db = 10*np.log10(np.sum(np.abs(data_sum) **2))
        powers.append(power_db)

    powers -= np.max(powers)
    return aoas, powers

def steer_beam(phaser, signal_freq, steer_angle):
    powers = []
    for i in range(8):
        d = phaser.element_spacing * i
        phi = (2.0*np.pi*signal_freq*d) * (np.sin(np.radians(steer_angle)))
        channel_phase = phi % 360
        phaser.elements.get(i+1).rx_phase = channel_phase
    phaser.latch_rx_settings()
    data = phaser.sdr.rx()
    data_sum = data[0] + data[1]
    power_db = 10*np.log10(np.sum(np.abs(data_sum) **2))
    powers.append(power_db)



        
