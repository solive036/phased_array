import adi
import sys
import pickle
import matplotlib.pyplot as plt
import numpy as np

import adar
import sdr_functions as SDR

sdrIp = '1p:192.168.2.1'
rpiIp = 'ip:phaser.local'

gainList = [100, 100, 100, 100, 100, 100, 100, 100]
phaseList = [0, 0, 0, 0, 0, 0, 0, 0]
refreshTime = 100 #ms

array = adar.init_adar_1000()
d = array.element_spacing

gpios = adi.one_bit_adc_dac(rpiIp)
gpios.gpio_vctrl_1 = 1  # 1=Use onboard PLL/LO source  (0=use external LO input)
gpios.gpio_vctrl_2 = 0  # 1=Send LO to transmit circuitry  (0=disable Tx path and send LO to LO_OUT)

# setup GPIOs to control if Tx is output on OUT1 or OUT2
gpios.gpio_div_mr = 1
gpios.gpio_div_s0 = 0
gpios.gpio_div_s1 = 0
gpios.gpio_div_s2 = 0

channelCal = SDR.load_channel_cal()
sdr = SDR.init_sdr(sdrIp, sampleRate, centerFreq, rxGain, bufferSize)
SDR.set_rx_gain(sdr, channelCal, -10, -10)
