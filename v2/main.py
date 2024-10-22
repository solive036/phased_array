import matplotlib.pyplot as plt
import adi
import sdr_functions as SDR
import phaser_functions as PHASER
import pickle
import data_processing as dp

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
phaser.lo = int(signal_freq +sdr.rx_lo - offset)

#receive samples
#data = SDR.rx_data(sdr)
aoas, powers = PHASER.DOA(phaser, signal_freq) #compute the DOA

#plot
#dp.psd(data)
dp.polar(aoas, powers)
dp.compute_max_angle(aoas, powers)
