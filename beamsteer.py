import adi
import matplotlib.pyplot as plt
import numpy as np

"""
Purpose: to detect the angle of peak signal and steer beam away from it

"""

def compute_fft(sdr, samples):
    PSD0 = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples[0])))**2)
    PSD1 = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples[1])))**2)
    
    return [PSD0, PSD1]

def plot_fft(sdr, psd):
    f = np.linspace(-sdr.sample_rate/2, sdr.sample_rate/2, len(psd[0]))

    plt.plot(f/1e6, psd[0])
    plt.plot(f/1e6, psd[1])
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Signal Strength [dB]')
    plt.show()

def compute_aoa():
    #look at 'performing beamforming in pysdr'
    return 0
