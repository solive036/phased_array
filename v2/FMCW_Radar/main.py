import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from matplotlib import style
import adi
import numpy as np
import sys
import sdr_functions as SDR
import phaser_functions as PHASER
import pickle
import data_processing as dp

fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(-10, 10)


def init_plot():
    line.set_data([], [])
    return line,

def update(frame, y_value):
    x = np.linspace(0, 10, 10)
    y = [y_value] * len(x)
    line.set_data(x, y)
    return line,

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

fft_size = 1024 * 64
freq = np.linspace(-fs / 2, fs / 2, int(fft_size))

sampling_period = 1/sdr.sample_rate
print('Sampling period: ', sampling_period)
t = sampling_period*np.arange(fft_size)

#initalize plot
fig, ax = plt.subplots()
line, = ax.plot([],[])
ax.set_xlim([0, 10])
plt.ion()

#transmit data
sdr._ctx.set_timeout(0)
beat_freq_prev = 0

try:
    sdr.tx([iq * 0.5, iq]) #2nd channel transmits

    while True:
        data = phaser.sdr.rx()
        data = data[0] + data[1]
        psd, freq = dp.compute_psd(data, phaser)
        f_d = dp.get_freq_max_power(psd, freq)
        beat_freq = dp.compute_beat_freq(f_d, signal_freq)
        beat_freq = (beat_freq - signal_freq)

        beat_freq_difference = (beat_freq - beat_freq_prev) * 1000000
        #print(beat_freq_difference)

        """
        #plotting
        plt.axhline(y=0)
        plt.axhline(beat_freq_difference)
        
        fig.canvas.draw()
        fig.canvas.flush_events
        plt.pause(0.001)

        plt.show()
        """
        ani = FuncAnimation(fig, update, init_func=init_plot, fargs=(beat_freq_difference,),blit=True, interval=200)
        plt.show()
        
        #print(beat_freq_difference)
        beat_freq_prev = beat_freq 
        
        
        

    """
    data = phaser.sdr.rx()
    #dp.psd(data)
    data = data[0] + data[1]
    data_norm = dp.normalize(data)
    iq_norm = dp.normalize(iq)
    plt.plot(t[0:200], data_norm[0:200])
    plt.plot(t[0:200], iq_norm[0:200])
    plt.show()
    np.save('rx_data.npy', data_norm)
    np.save('tx_data.npy', iq_norm)
    #plt.show()
    """


    
except KeyboardInterrupt:
    sdr.tx_destroy_buffer()
    print('Exiting')
