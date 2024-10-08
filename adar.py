import numpy as np
import matplotlib.pyplot as plt
import adi

#cn0566 has 2 ADAR1000s

def init_adar_1000():
    #Initialize ADAR1000 receive array
    array = adi.adar1000_array (
        chip_ids=["BEAM0", "BEAM1"],
        device_map=[[1], [2]],
        element_map=[[1, 2, 3, 4, 5, 6, 7, 8]],
        device_element_map={
            1: [7, 8, 5, 6],
            2: [3, 4, 1, 2],
        },

        rpi_ip = 'ip:phaser.local'
    )

    array.reset()
    array._ctrl.reg_write(
        0x400, 0x55
    )

    array.sequencer_enable = False
    array.beam_mem_enable = False
    array.bias_mem_enable = False
    array.pol_state = False
    array.pol_switch_enable = (
        False
    )
    array.tr_source = 'spi'
    array.tr_spi = (
        'rx'
    )
    array.tr_switch_enable = True
    array.external_tr_polarity = True
    array.rx_vga_enable = True  # Enables Rx VGA, reg 0x2E, bit 0.
    array.rx_vm_enable = True  # Enables Rx VGA, reg 0x2E, bit 1.
    array.rx_lna_enable = True  # Enables Rx LNA, reg 0x2E, bit 2.
    array.rx_lna_bias_current = 8  # Sets the LNA bias to the middle of its range
    array.rx_vga_vm_bias_current = 22  # Sets the VGA and vector modulator bias.

    #set frequency and array element spacing
    array.frequency = 10.25e9
    array.element_spacing = 0.014

    for device in array.devices.values():
        device.mode = "rx"

        SELF_BIASED_LNAs = True
        if SELF_BIASED_LNAs:
            device.lna_bias_out_enable = False
        else:
            device.lna_bias_on = -0.7

        for channel in device.channels:
            channel.rx_enable = True

    return array

#steer ADAR1000s
def steer_array(array, az, el):
    array.steer_rx(azimuth=az, elevation=el)

    for element in array.elements.values():
        element.rx_gain = 0x67
    
    array.latch_rx_settings()

def set_taper(array, gainList):
    for index, element in enumerate(array.elements.values()):
        element.rx_gain = int(gainList[index] * 127/100)
        element.rx_attenuator = not bool(gainList[index])
    array.latch_rx_settings()



