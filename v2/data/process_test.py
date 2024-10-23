import numpy as np
import matplotlib.pyplot as plt

def polar(angles_of_arrival, powers, angle_max_power):
    fig, ax = plt.subplots(subplot_kw={'projection' : 'polar'})
    ax.plot(np.deg2rad(angles_of_arrival), powers)
    ax.set_rticks([-40, -30, -20, -10, 0])  
    ax.set_thetamin(np.min(angles_of_arrival)) 
    ax.set_thetamax(np.max(angles_of_arrival))

    # Convert the angle of max power to radians for plotting
    angle_of_max_rad = np.deg2rad(angle_max_power)
    
    # Plot the point where power is greatest
    max_power = np.max(powers)
    ax.plot(angle_of_max_rad, max_power, 'o', color='red')

    ax.set_theta_direction(-1) 
    ax.set_theta_zero_location('N') 
    ax.grid(True)
    plt.show()

#aoas are given in degrees, originally
def get_peak_power_angle(aoas, powers):
    max_power_index = np.argmax(powers)  # Get the index of the maximum power
    angle_max_power = aoas[max_power_index]  # Retrieve the corresponding angle
    print('Angle of max power: ', angle_max_power)
    return angle_max_power #return angle where most power is coming from in degrees

#returns the angle where received samples have minimum power, in degrees
def get_min_power_angle(aoas, powers):
    min_power_index = np.argmin(powers)
    angle_min_power = aoas[min_power_index]
    print('Angle of min power: ', angle_min_power)
    return angle_min_power

def get_peak_power(powers):
    return np.max(powers)

def plot(angles_of_arrival, powers):
    fig, ax = plt.subplots(subplot_kw={'projection' : 'polar'})
    ax.plot(np.deg2rad(angles_of_arrival), powers)
    ax.set_rticks([-40, -30, -20, -10, 0])  
    ax.set_thetamin(np.min(angles_of_arrival)) 
    ax.set_thetamax(np.max(angles_of_arrival))

    min_angle = get_min_power_angle(angles_of_arrival, powers)
    max_angle = get_peak_power_angle(angles_of_arrival, powers)

    ax.plot(np.deg2rad(min_angle), np.min(powers), 'o', color='red')
    ax.plot(np.deg2rad(max_angle), 0, 'o', color='green')
    ax.set_theta_direction(-1) 
    ax.set_theta_zero_location('N') 
    ax.grid(True)
    plt.show()

aoas = np.load('aoas.npy')
powers = np.load('powers.npy')
angle_max_power = get_peak_power_angle(aoas, powers)
print(get_peak_power(powers))
polar(aoas, powers, angle_max_power)
plot(aoas, powers)
