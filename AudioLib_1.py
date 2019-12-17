import sys, wave
import numpy as np
from numpy import array, int16
from scipy.signal import lfilter, butter
from scipy.io.wavfile import read,write
from scipy import signal


sample_freq = 8000
BLOCKLEN = 1024

def set_echo(audio_data, delay):
    output_audio = np.zeros(len(audio_data))
    output_delay = delay * sample_freq
    for count, e in enumerate(audio_data):
        output_audio[count] = e + audio_data[count - int(output_delay)]
    return(output_audio)

def set_audio_speed(audio_data, speed_factor):
    temp = len(audio_data)
    audio_data=array(audio_data, dtype = int16)
    sound_index = np.round(np.arange(0, len(audio_data), speed_factor))
    output_audio = audio_data[sound_index[sound_index < len(audio_data)].astype(int)]

    if temp == BLOCKLEN: arrlen = BLOCKLEN
    if temp > BLOCKLEN: arrlen = len(output_audio)
    return(output_audio[:arrlen])

def set_reverse(audio_data):
    output_audio = audio_data[::-1]
    return(output_audio)

def set_volume(audio_data, level):
    output_audio = np.zeros(len(audio_data))
    for count, e in enumerate(audio_data):
        output_audio[count] = (e * level)
    return(output_audio)

def set_lowpass(audio_data, cutoff_low, order=5):
    nyquist = sample_freq / 2.0
    cutoff = cutoff_low / nyquist
    x, y = signal.butter(order, cutoff, btype='lowpass', analog=False)
    output_audio = signal.filtfilt(x, y, audio_data)
    return(output_audio)

def set_highpass(audio_data, cutoff_high, order=5):
    nyquist = sample_freq / 2.0
    cutoff = cutoff_high / nyquist
    x, y = signal.butter(order, cutoff, btype='highpass', analog=False)
    output_audio = signal.filtfilt(x, y, audio_data)
    return(output_audio)

def set_bandpass(audio_data, cutoff_low, cutoff_high, order=5):
    cutoff = np.zeros(2)
    nyquist = sample_freq / 2.0
    cutoff[0] = cutoff_low / nyquist
    cutoff[1] = cutoff_high / nyquist
    x, y = signal.butter(order, cutoff, btype='bandpass', analog=False)
    output_audio = signal.filtfilt(x, y, audio_data)
    return(output_audio)

def bpf(input_audio, lcf,hcf):
    sound = set_bandpass(input_audio, lcf,hcf)
    return(sound)


def set_stretch(audio_data, factor, window_size, h):
    phase = np.zeros(window_size)
    hanning_window = np.hanning(window_size)
    result = np.zeros(int(len(audio_data) / factor + window_size))

    for i in np.arange(0, BLOCKLEN - (window_size + h), h*factor):
        # Two potentially overlapping subarrays
        a1 = audio_data[int(i): int(i + window_size)]
        a2 = audio_data[int(i + h): int(i + window_size + h)]

        # The spectra of these arrays
        s2 = np.fft.fft(hanning_window * a1)
        s1 = np.fft.fft(hanning_window * a2)

        # Rephase all frequencies

        if(s1.all!=0):
            phase = (phase + np.angle(np.real(s2)/np.real(s1))) % 2*np.pi
        else:
           phase = (phase) % 2*np.pi 
        a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(1j*phase))
        i2 = int(i / factor)
        result[i2: i2 + window_size] += hanning_window*a2_rephased.real

    # normalize (16bit)
    result = ((2 ** (16 - 4)) * result/result.max())
    output_audio = result.astype('int16')
    
    return(output_audio)


def set_audio_pitch(audio_data, n, window_size=200, h=50):
    factor = 2 ** (1.0 * n / 12.0)
    set_stretch(audio_data,1.0 / factor, window_size, h)
    output_audio = audio_data[window_size:]
    output_audio =set_audio_speed(audio_data,factor)
    audio_size = len(output_audio)
    return(output_audio)

#Effects:

def darth_vader(input_audio):
    sound=set_audio_speed(input_audio, .7)
    sound=set_echo(sound,0.02)
    sound=set_lowpass(sound,2500)
    return(sound)

def echo(input_audio):
    sound=set_echo(input_audio,0.1)
    return(sound)

def chipmunk(input_audio):
    sound = set_audio_pitch(input_audio, 10)
    return(sound)
   



	    


