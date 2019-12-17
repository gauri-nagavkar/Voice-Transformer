# Record

import pyaudio
import struct
import wave
import numpy as np

def record():

    WIDTH = 2 # Number of bytes per sample
    CHANNELS = 1 # mono
    RATE = 8000 # Sampling rate (frames/second)
    DURATION = 5 # duration of processing (seconds)
    BLOCKLEN = 1024      # Number of frames per block

    MAXVAL=2**15-1
    num_blocks = int(RATE / BLOCKLEN * DURATION)
    output_block = BLOCKLEN * [0]

    voice_wf = wave.open('voice_wf.wav', 'w') # Write a mono wave file voice_wf.setnchannels(CHANNELS) # mono
    voice_wf.setsampwidth(WIDTH) # two bytes per sample (8 bits per sampl e)
    voice_wf.setframerate(RATE) # samples per second
    voice_wf.setnchannels(CHANNELS) # set # channels

    # Open audio stream
    p = pyaudio.PyAudio()
    stream = p.open(
        format = p.get_format_from_width(WIDTH),channels = CHANNELS,
        rate = RATE,
        input = True,
        output = True)

    for i in range(0, num_blocks):
        input_bytes = stream.read(BLOCKLEN, exception_on_overflow = False)
        # Convert binary string to tuple of numbers
        input_tuple = struct.unpack('h'* BLOCKLEN, input_bytes)

        # Compute output value
        output_block = np.clip(input_tuple,-MAXVAL, MAXVAL)
        # Convert output value to binary string
        output_bytes = struct.pack('h' * BLOCKLEN, *output_block)
        # Write to file
        voice_wf.writeframes(output_bytes)

    print('* Finished')
    stream.stop_stream()
    stream.close()
    p.terminate()
    voice_wf.close()

    
