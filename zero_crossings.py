import numpy as np
import matplotlib.pyplot as plt

def zero_crossing(waveform):
    zero_crossings = np.where(np.diff(np.signbit(waveform)))[0] #returns the indicies of the zero crossings
    return zero_crossings

# Parameters
amplitude = 1  # Amplitude of the sine waves
frequency = 10.1  # Frequency of the sine waves in Hz
phase_shift = np.pi / 2  # Phase shift in radians (e.g., pi/4)
print('phase shift: ', round(phase_shift, 5), 'rad')
sampling_rate = 1000  # Number of samples per second
duration = 2  # Duration of the signal in seconds

# Time vector (from 0 to 'duration' with 'sampling_rate' samples per second)
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# Generate the two sine waves
wave1 = amplitude * np.sin(2 * np.pi * frequency * t)
wave2 = amplitude * np.sin(2 * np.pi * frequency * t + phase_shift)

#find the zero crossings for wave 1
zx = zero_crossing(wave1)
zx_1 = zx[0]
time_of_zx_1 = t[zx_1]
print('Time of first zero crossing for wave 1: ', time_of_zx_1)

#find the zero crossings for wave 2
zx = zero_crossing(wave2)
zx_2 = zx[0]
time_of_zx_2 = t[zx_2]
print('Time of first zero crossing for wave 2: ', time_of_zx_2)

time_diff = np.abs(time_of_zx_1 - time_of_zx_2)
print('Time diff: ',  time_diff)

#calculate the phase shift
lambda_ = 1/frequency
print('Phase shift: ', time_diff * frequency, 'rad')

#calculate the velocity based on the doppler shift

# Plot the sine waves
plt.figure(figsize=(10, 6))
plt.plot(t, wave1, label='Wave 1 (no phase shift)', color='blue')
plt.plot(t, wave2, label=f'Wave 2 (phase shift = {phase_shift} radians)', color='red', linestyle='--')

# Add labels and title
plt.title("Two Sine Waves with Phase Shift")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)
plt.show()
