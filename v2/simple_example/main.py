import matplotlib.pyplot as plt
import adi
import numpy as np
import sys
import sdr_functions as SDR
import phaser_functions as PHASER
import pickle
import data_processing as dp

"""
HARDWARE SETUP
"""
#initialize hardware
sdr_ip = "ip:192.168.2.1"
phaser_ip = "ip:phaser.local"
sdr = adi.ad9361(uri=sdr_ip)
phaser = adi.CN0566(uri=phaser_ip, sdr=sdr)

#get signal frequency of HB100
signal_freq = pickle.load(open("hb100_freq_val.pkl", "rb"))

phaser.configure(device_mode='rx')
phaser.load_gain_cal()
phaser.load_phase_cal()
for i in range(0, 8):
    phaser.set_chan_phase(i, 0)

gain_list = [8, 34, 84, 127, 127, 84, 34, 8]  # Blackman taper
for i in range(0, len(gain_list)):
    phaser.set_chan_gain(i, gain_list[i], apply_cal=True)

sdr._ctrl.debug_attrs["adi,frequency-division-duplex-mode-enable"].value = "1"
sdr._ctrl.debug_attrs["adi,ensm-enable-txnrx-control-enable"].value = "0" # Disable pin control so spi can move the states
sdr._ctrl.debug_attrs["initialize"].value = "1"
sdr.rx_enabled_channels = [0, 1] # enable Rx1 and Rx2
sdr._rxadc.set_kernel_buffers_count(1) # No stale buffers to flush
sdr.tx_hardwaregain_chan0 = int(-80) # Make sure the Tx channels are attenuated (or off)
sdr.tx_hardwaregain_chan1 = int(-80)

#sdr parameters
sample_rate = int(30e6)
center_freq = 2.2e9
fft_size  = 1024

#sdr setup
sdr.sample_rate = int(sample_rate)
sdr.rx_lo = int(2.2e9)
sdr.rx_enabled_channels = [0, 1]
sdr.rx_buffer_size = int(fft_size)
sdr.gain_control_mode_chan0 = "manual"  # manual or slow_attack
sdr.gain_control_mode_chan1 = "manual"  # manual or slow_attack
sdr.rx_hardwaregain_chan0 = int(30)  # must be between -3 and 70
sdr.rx_hardwaregain_chan1 = int(30)  # must be between -3 and 70

offset = 1000000
phaser.lo = int(signal_freq + sdr.rx_lo - offset)

"""
Use the Phaser 
"""
angles_of_arrival = []
powers = []

#Initialize the plot
fig, ax = plt.subplots(subplot_kw={'projection' : 'polar'})
line, = ax.plot([], [], lw=2)
min_point, = ax.plot([], [], 'o')
max_point, = ax.plot([], [], 'o')
ax.set_rticks([-40, -30, -20, -10, 0])  
ax.set_theta_direction(-1) 
ax.set_theta_zero_location('N') 
ax.grid(True)

#real time plot
try: 
    while True:
        angles_of_arrival, powers = PHASER.DOA(phaser, signal_freq)
        
        #get AOA of min and max power
        angle_min_power = dp.get_min_power_angle(angles_of_arrival, powers)
        angle_max_power = dp.get_peak_power_angle(angles_of_arrival, powers)

        #update the line
        line.set_data(np.deg2rad(angles_of_arrival), powers)


        #plot points of minimum and maximum power
        min_point.set_data(np.deg2rad(angle_min_power), np.min(powers))
        max_point.set_data(np.deg2rad(angle_max_power), 0)

        ax.set_thetamin(np.min(angles_of_arrival)) 
        ax.set_thetamax(np.max(angles_of_arrival))
        
        ax.relim()
        ax.autoscale_view()

        plt.draw()
        plt.pause(0.001)


except KeyboardInterrupt:
    print('Exiting...')
    sys.exit()
