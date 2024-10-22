import matplotlib.pyplot as plt
import numpy as np

def psd(data):
    psd0 = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(data[0])))**2)
    psd1 = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(data[1])))**2)
    f = np.linspace(-30e6/2, 30e6/2, len(data[0]))
    plt.plot(f/1e6, psd0)
    plt.plot(f/1e6, psd1)
    plt.xlabel("Frequency [GHz]")
    plt.ylabel("Signal Strength [dB]")
    plt.show()

def polar(angles_of_arrival, powers):
    fig, ax = plt.subplots(subplot_kw={'projection' : 'polar'})
    ax.plot(np.deg2rad(angles_of_arrival), powers)
    ax.set_rticks([-40, -30, -20, -10, 0])  
    ax.set_thetamin(np.min(angles_of_arrival)) 
    ax.set_thetamax(np.max(angles_of_arrival))
    ax.set_theta_direction(-1) 
    ax.set_theta_zero_location('N') 
    ax.grid(True)
    plt.show()

    
