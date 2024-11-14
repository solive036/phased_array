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
fft_size = 1024 * 4

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

# Configure the ADF4159 Rampling PLL
output_freq = 12.145e9
BW = 500e6
num_steps = 500
ramp_time = 0.5e3  # us
phaser.frequency = int(output_freq / 4)  # Output frequency divided by 4
phaser.freq_dev_range = int(
    BW / 4
)  # frequency deviation range in Hz.  This is the total freq deviation of the complete freq ramp
phaser.freq_dev_step = int(
    (BW/4) / num_steps
)  # frequency deviation step in Hz.  This is fDEV, in Hz.  Can be positive or negative
phaser.freq_dev_time = int(
    ramp_time
)  # total time (in us) of the complete frequency ramp
print("requested freq dev time = ", ramp_time)
ramp_time = phaser.freq_dev_time
ramp_time_s = ramp_time / 1e6
print("actual freq dev time = ", ramp_time)
phaser.delay_word = 4095  # 12 bit delay word.  4095*PFD = 40.95 us.  For sawtooth ramps, this is also the length of the Ramp_complete signal
phaser.delay_clk = "PFD"  # can be 'PFD' or 'PFD*CLK1'
phaser.delay_start_en = 0  # delay start
phaser.ramp_delay_en = 0  # delay between ramps.
phaser.trig_delay_en = 0  # triangle delay
phaser.ramp_mode = "continuous_sawtooth"  # ramp_mode can be:  "disabled", "continuous_sawtooth", "continuous_triangular", "single_sawtooth_burst", "single_ramp_burst"

phaser.tx_trig_en = 0  # start a ramp with TXdata
phaser.enable = 0  # 0 = PLL enable.  Write this last to update all the registers

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

#transmit data
sdr._ctx.set_timeout(0)
results = []
try:
    sdr.tx([iq * 0.5, iq]) #2nd channel transmits

    data = phaser.sdr.rx()
    #dp.psd(data)
    data = data[0] + data[1]
    #data_norm = dp.normalize(data)
    #iq_norm = dp.normalize(iq)
    #plt.plot(t[0:200], data_norm[0:200])
    #plt.plot(t[0:200], iq_norm[0:200])
    plt.plot(np.real(data[0:200]))
    plt.show()
    #plt.show()
    
except KeyboardInterrupt:
    sdr.tx_destroy_buffer()
    print('Exiting')
