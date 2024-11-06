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
try:
    #initialize hardware
    sdr_ip = "ip:192.168.2.1"
    phaser_ip = "ip:phaser.local"
    sdr = adi.ad9361(uri=sdr_ip)
    phaser = adi.CN0566(uri=phaser_ip, sdr=sdr)
    print('Phaser and Pluto Connected')
except:
    print('Error connecting phaser and sdr')
    exit()

#get signal frequency of HB100
#signal_freq = pickle.load(open("hb100_freq_val.pkl", "rb"))

phaser.configure(device_mode="rx")

#initialize ADAR1000
for i in range(0, 8):
    phaser.set_chan_phase(i, 0)

gain_list = [8, 34, 84, 127, 127, 84, 34, 8]

for i in range(0, len(gain_list)):
    phaser.set_chan_gain(i, gain_list[i], apply_cal=True)

# Setup Raspberry Pi GPIO states
try:
    phaser._gpios.gpio_tx_sw = 0 
    phaser._gpios.gpio_vctrl_1 = 1 # 1=Use onboard PLL/LO source
    phaser._gpios.gpio_vctrl_2 = 1 # 1=Send LO to transmit circuitry
except:
    phaser.gpios.gpio_tx_sw = 0  # 0 = TX_OUT_2, 1 = TX_OUT_1
    phaser.gpios.gpio_vctrl_1 = 1 # 1=Use onboard PLL/LO source  (0=disable PLL and VCO, and set switch to use external LO input)
    phaser.gpios.gpio_vctrl_2 = 1 # 1=Send LO to transmit circuitry  (0=disable Tx path, and send LO to LO_OUT)

#sdr settings
sample_rate = 0.6e6
center_freq = 2.1e9
signal_freq = 100e3
fft_size = 1024 * 64

sdr.sample_rate = int(sample_rate)
sdr.rx_lo = int(center_freq)
sdr.rx_enabled_channels = [0, 1]
sdr.rx_buffer_size = int(fft_size)
sdr.gain_control_mode_chan0 = 'manual'
sdr.gain_control_mode_chan1 = 'manual'
sdr.rx_hardwaregain_chan0 = int(30)
sdr.rx_hardwaregain_chan1 = int(30)

sdr.tx_lo = int(center_freq)
sdr.tx_enabled_channels = [0, 1]
sdr.tx_cyclic_buffer = True
sdr.tx_hardwaregain_chan0 = -88 #attenuated
sdr.tx_hardwaregain_chan1 = -0

#configure ramping PLL (ADF4159)
output_freq = 12.2e9
phaser.frequency = int(output_freq/4)
phaser.ramp_mode = 'disabled'
phaser.enable = 0

# Create a sinewave waveform
fs = int(sdr.sample_rate)
N = int(sdr.rx_buffer_size)
fc = int(signal_freq / (fs / N)) * (fs / N)
ts = 1 / float(fs)
t = np.arange(0, N * ts, ts)
i = np.cos(2 * np.pi * t * fc) * 2 ** 14
q = np.sin(2 * np.pi * t * fc) * 2 ** 14
iq = 1 * (i + 1j * q)


#transmit data
#sdr._ctx.set_timeout(0)
results = []
try:
    sdr.tx([iq * 0.5, iq]) #2nd channel transmits
    for i in range(0, 20):
        data = phaser.sdr.rx()
        #sum = data[0] + data[1]
        psd = dp.compute_psd(data)
        results.append(psd)
    np.save('psd.npy', results)
except KeyboardInterrupt:
    sdr.tx_destroy_buffer()
    print('Exiting')
    

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
    sdr.tx_destroy_buffer()
    sys.exit()

"""
