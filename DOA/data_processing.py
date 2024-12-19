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
def polar_plot(angles_of_arrival, powers):
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
#returns where the peak power occurs, in degrees
def get_peak_power_angle(aoas, powers):
    max_power_index = np.argmax(powers) 
    angle_max_power = aoas[max_power_index] 
    return angle_max_power

#returns the angle where received samples have minimum power, in degrees
def get_min_power_angle(aoas, powers):
    min_power_index = np.argmin(powers)
    angle_min_power = aoas[min_power_index]
    return angle_min_power


    

    
