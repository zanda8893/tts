#!./venv/bin/python3
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
import sys


def read(f, normalized=False):
    """WAV to numpy array"""
    a = AudioSegment.from_wav(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        return a.frame_rate, np.float32(y) / 2 ** 15
    else:
        return a.frame_rate, y


samplerate, data = read(sys.argv[1])  # row[1][1:] + ".wav")
duration = len(data) / samplerate
timerange = np.arange(0, duration, 1 / samplerate)

# Plotting the Graph using Matplotlib
plt.plot(timerange, data)
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.title(sys.argv[1])
plt.show()