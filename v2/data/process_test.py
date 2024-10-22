import numpy as np
import matplotlib.pyplot as plt

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

def get_angle_max(aoas, powers):
    aoas = np.rad2deg(aoas)
    max_power_index = np.argmax(powers)  # Get the index of the maximum power
    angle_of_max = aoas[max_power_index]  # Retrieve the corresponding angle
    print('Angle of max power: ', angle_of_max)

aoas = np.load('aoas.npy')
powers = np.load('powers.npy')
get_angle_max(aoas, powers)

polar(aoas, powers)
