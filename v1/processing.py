import numpy as np
import matplotlib.pyplot as plt

def compute_PSD(samples):
    psd0 = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples[0])))**2)
    psd1 = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples[1])))**2)

    return psd0, psd1

def plot_PSD(psd0, psd1, sdr):
    f = np.linspace(-sdr.sample_rate/2, sdr.sample_rate/2, len(psd0))
    plt.plot(f/1e6, psd0)
    plt.plot(f/1e6, psd1)
    plt.xlabel('frequency [GHz]')
    plt.ylabel('signal strength [dB]')
    plt.show()
