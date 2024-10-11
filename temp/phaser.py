import numpy as np
import time
import pickle
from adi import ad9361, CN0566
from scipy.signal import sawtooth
import adi

def init():

    try:
        phaser = CN0566(uri='ip:localhost')
        sdr = ad9361(uri='ip:192.168.2.1')
        phaser.sdr = sdr
        print('Phaser and Pluto Connected...')
    except:
        print('Error Connecting to Phaser and Pluto... Exiting.')
        exit(-1)

    time.sleep(0.5)

    #load phaser calibration files
    phaser.configure(device_mode='rx')
    # phaser.load_gain_cal('~/pyadi-iio/examples/phaser/gain_cal_val.pkl')
    # phaser.load_phase_cal('~/pyadi-iio/examples/phaser/phase_cal_val.pkl')
    sdr.tx_hardwaregain_chan0 = int(-80)
    sdr.tx_hardwaregain_chan1 = int(-80)
    signal_freq = pickle.load(open("hb100_freq_val.pkl", "rb"))
    #apply gain to each antenna element
    gain_list = [64, 64, 64, 64, 64, 64, 64, 64]
    for i in range(0, len(gain_list)):
        phaser.set_chan_gain(i, gain_list[i], apply_cal=False)

    phaser.set_beam_phase_diff(0.0)

    d = 0.014
    sample_rate = 30e6
    center_freq = 2.2e9
    signal_freq = 100e3
    fft_size = 1024
    
    #sdr config rx
    sdr.sample_rate = int(sample_rate)
    sdr.rx_lo = int(center_freq)
    sdr.rx_enabled_channels = [0, 1]
    sdr.rx_buffer_size = int(fft_size)
    sdr.rx_rf_bandwidth = int(10e6)
    sdr.gain_control_mode_chan0 = 'manual'
    sdr.gain_control_mode_chan1 = 'manual'
    sdr.rx_hardwaregain_chan0 = int(10)
    sdr.rx_hardwaregain_chan1 = int(10)
    
    phaser.lo = int(signal_freq + sdr.rx_lo - 1000000)
    return phaser, sdr

def rx_samples(sdr):
    return sdr.rx()

