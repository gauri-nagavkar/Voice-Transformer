# play audio with sound effect

import wave
import numpy as np
import pyaudio
import struct
import AudioLib
from scipy.io.wavfile import read,write

def create_effect(effect_type):

    input_file_path = 'voice_wf.wav'
    output_name = 'voice_mod.wav'
    BLOCKLEN = 1024      # Number of frames per block

    samp_freq, audio_data = read(input_file_path) 
    
    if(effect_type == "Darth-Vader"):
        output_audio = AudioLib.darth_vader(audio_data)
        write(output_name,samp_freq,np.array(output_audio, dtype = np.int16))

    if(effect_type == "Echo"):
        output_audio = AudioLib.echo(audio_data)
        write(output_name,samp_freq,np.array(output_audio, dtype = np.int16))
        
    print('* Finished')
    

def play_effect():

    BLOCKLEN = 1024      # Number of frames per block
    WIDTH = 2 # Number of bytes per sample
    CHANNELS = 1 # mono
    RATE = 8000 # Sampling rate (frames/second)
    DURATION = 5 # duration of processing (seconds)
    
    #open a wav format music
    voice_wf_mod = wave.open('voice_mod.wav',"rb")

    #instantiate PyAudio
    p = pyaudio.PyAudio()
    #open stream
    stream = p.open(format = p.get_format_from_width(WIDTH),
                    channels = CHANNELS,
                    rate = RATE,
                    input = False,
                    output = True)
    #read data
    input_data = voice_wf_mod.readframes(BLOCKLEN)
    #play stream
    while input_data:
        stream.write(input_data)
        input_data = voice_wf_mod.readframes(BLOCKLEN)
    #stream.write(voice_wf_mod) 
    #stop stream
    stream.stop_stream()
    stream.close()
    #close PyAudio
    p.terminate()
    voice_wf_mod.close()
    print('* Finished')

