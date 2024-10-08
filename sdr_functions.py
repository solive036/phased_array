import adi
import pickle

def init_sdr(sdrIp, sampleRate, centerFreq, rxGain, bufferSize):
    sdr = adi.ad9361(uri=sdrIp)
    
    sdr._ctrl.debug_attrs["initialize"].value = "1"
    sdr.rx_enabled_channels = [0, 1]  # enable Rx1 (voltage0) and Rx2 (voltage1)
    sdr.gain_control_mode_chan0 = 'manual'
    sdr.gain_control_mode_chan1 = 'manual'
    sdr._rxadc.set_kernel_buffers_count(
        1
    )
    rx = sdr._ctrl.find_channel("voltage0")
    sdr.sample_rate = sampleRate
    sdr.rx_lo = int(centerFreq)
    sdr.rx_buffer_size = int(bufferSize)
    return sdr

def set_rx_gain(sdr, ccal, rxGain1, rxGain2):
    sdr.rx_hardwaregain_chan0 = int(rxGain1 + ccal[0])
    sdr.rx_hardwaregain_chan1 = int(rxGain2 + ccal[1])

def rx_samples(sdr):
    samples = sdr.rx()
    return samples
    
    
def load_channel_cal(filename="channel_cal_val.pkl"):
    """ Load Pluto Rx1 and Rx2 calibrated value, if not calibrated set all channel gain correction to 0.
        parameters:
            filename: type=string
                      Provide path of phase calibration file
    """

    try:
        with open(filename, "rb") as file:
            return pickle.load(file)  # Load channel cal values
    except:
        print("file not found, loading default (no channel gain shift)")
        return [0.0] * 2  # .append(0)  # if it fails load default value i.e. 0


    ccal = load_channel_cal()
    return ccal