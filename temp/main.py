import numpy as np
import phaser as PHASER
import processing as pr
import matplotlib.pyplot as plt

phaser, sdr = PHASER.init()
samples = PHASER.rx_samples(sdr)
psd0, psd1 = pr.compute_PSD(samples)
pr.plot_PSD(psd0, psd1, sdr)

exit()

