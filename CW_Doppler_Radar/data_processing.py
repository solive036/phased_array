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
    print('Angle of max power: ', angle_max_power)
    return angle_max_power

#returns the angle where received samples have minimum power, in degrees
def get_min_power_angle(aoas, powers):
    min_power_index = np.argmin(powers)
    angle_min_power = aoas[min_power_index]
    print('Angle of min power: ', angle_min_power)
    return angle_min_power

def compute_psd(data, phaser):
    psd = 20*np.log10(np.abs(np.fft.fftshift(np.fft.fft(data)))**2)
    freq = np.fft.fftfreq(data.size, phaser.sdr.sample_rate/data.size)
    return psd, freq

def normalize(data):
    data = np.array(np.real(data))
    data_normalized = 2*((data-np.min(data))/(np.max(data)-np.min(data)))-1 #normalize data to between -1 and 1
    return data_normalized

def get_freq_max_power(psd, freq_axis):
    max_value = np.max(psd)
    index, = np.where(psd == max_value)
    frequency_of_occurance = freq_axis[index]
    return frequency_of_occurance

def compute_beat_freq(freq_max_power, f0):
    return np.round(np.abs(freq_max_power - f0))

def compute_velocity(f_beat, f0):
    c = 3e8
    v_target = (f_beat * c)/(2*f0)
    return v_target
    

    
    
    
    
