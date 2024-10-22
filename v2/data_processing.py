import matplotlib.pyplot as plt
import numpy as np

"""
Functions for plotting data
"""
#plots the PSD for the two receive channels
def psd(data):
    psd0 = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(data[0])))**2)
    psd1 = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(data[1])))**2)
    f = np.linspace(-30e6/2, 30e6/2, len(data[0]))
    plt.plot(f/1e6, psd0)
    plt.plot(f/1e6, psd1)
    plt.xlabel("Frequency [GHz]")
    plt.ylabel("Signal Strength [dB]")
    plt.show()

#plots power against AOA in polar plot
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

"""
process data
"""
def compute_max_angle(angles_of_arrival, powers):
    angles_of_arrival = np.array(angles_of_arrival)
    powers = np.array(powers)
    np.save('aoas.npy', angles_of_arrival)
    np.save('powers.npy', powers)
    min_value = np.min(powers)
    print('min value: ', min_value)
    index = np.where((angles_of_arrival == min_value))
    print('Index: ', index[0])
    #print('index: ', np.where((angles_of_arrival == min_value)[0]) 
    #print('Max. power value: ', np.min(powers))
    
    

    
