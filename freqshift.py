__author__ = 'brett'

# * Research *
# Granular Synthesis
# Device information
# Bandwidth parameters
# Gain envelope - raise gain at higher frequencies

import struct
import numpy as np
import time
import pyaudio
from pyaudio import paFloat32
from math import sin, pi
from scipy.signal import hilbert

#from sound_filter import sound_filter

CHANNELS = 1
RATE = 44100
CHUNK = 64
W = 2*pi*10000
GAIN = 1.0
DT = 1.0/float(RATE)

p = pyaudio.PyAudio()

total_frames = 0

def callback(in_data, frame_count, time_info, status):
    global total_frames
    signal = np.array(struct.unpack("%df" % frame_count, in_data))
    sig_out = range(frame_count)
    base_time = total_frames/float(RATE)
    for i in xrange(frame_count):
        sig_out[i] = signal[i]*GAIN*sin(W*(base_time+i*DT))
    raw_out = struct.pack("%df" % frame_count, *sig_out)
    total_frames += frame_count
    return raw_out, pyaudio.paContinue

def hilbert_callback(in_data, frame_count, time_info, status):
    global total_frames
    base_time = total_frames/float(RATE)
    signal = np.array(struct.unpack("%df" % frame_count, in_data))
    complex_sig = hilbert(signal)
    for i in xrange(frame_count):
        complex_sig[i] = complex_sig[i]*GAIN*np.exp(-1j*W*(base_time+i*DT))
    raw_out = struct.pack("%df" % frame_count, *complex_sig.real)
    return raw_out, pyaudio.paContinue

stream = p.open(format=paFloat32,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK,
                stream_callback=hilbert_callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()

"""
signal = np.array(struct.unpack("%df" % frame_count, in_data))
shift = 1
sig_fft = np.fft.fft(signal)
lower_fft = sig_fft[0:len(sig_fft)/2]
lower_fft = np.pad(lower_fft, (0, shift), 'constant')[shift:]
lower_fft[0] = 0
upper_fft = sig_fft[len(sig_fft)/2:]
upper_fft = np.pad(upper_fft, (shift, 0), 'constant')[:-shift]
upper_fft[-1] = 0
sig_fft = np.concatenate((lower_fft, upper_fft))
sig_out = np.fft.ifft(sig_fft).real
raw_out = struct.pack("%df" % frame_count, *sig_out)
"""