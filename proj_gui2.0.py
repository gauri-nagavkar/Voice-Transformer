#  Main
# -------

import tkinter as Tk
from tkinter import HORIZONTAL,OptionMenu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pyaudio
import struct
import numpy as np
from matplotlib import pyplot as plt
import AudioLib
import record
import play_audio
import os.path
from math import sin, cos, pi
import pandas as pd
from scipy import signal
import AudioLib 
import wave

from scipy.io import wavfile
fps, guitar_wf = wavfile.read("guitar_wf.wav")

def fun_effect(stvar):

    instrument = stvar
    data= pd.read_csv("Notes_Freq_Match.csv")
    data= np.asarray(data)

    freq_notes={}

    for r in range(data.shape[0]):
        for n in range(int(data[r,2]), data[r,3]+1):
            freq_notes.update( {n : data[r,0]} )

    freq_map={}
    for r in range(data.shape[0]):
        for n in range(int(data[r,2]), data[r,3]+1):
            freq_map.update( {n : data[r,1]} )


    MAXVALUE = 2**15-1  # Maximum allowed output signal value (because WIDTH = 2)
    WIDTH     = 2         # bytes per sample
    CHANNELS  = 1         # mono
    RATE      = 8000     # Sampling rate (samples/second)
    BLOCKSIZE = 8000     # length of block (samples)
    DURATION  = 10        # Duration (seconds)

    voice_mod_wf = wave.open('voice_piano_wf.wav', 'w') # Write a mono wave file 
    voice_mod_wf.setnchannels(CHANNELS) # mono 
    voice_mod_wf.setsampwidth(WIDTH) # two bytes per sample
    voice_mod_wf.setframerate(RATE)# samples per second

    voice_wf = wave.open('voice_wf.wav', 'w') # Write a mono wave file 
    voice_wf.setnchannels(CHANNELS) # mono 
    voice_wf.setsampwidth(WIDTH) # two bytes per sample
    voice_wf.setframerate(RATE)# samples per second

    NumBlocks = int( DURATION * RATE / BLOCKSIZE )
    output_block = BLOCKSIZE * [0]
        
    Ta= 5
    r = 0.01**(1.0/(Ta*RATE))

    # Filter coefficients
    ORDER = 2

    f = [[]] * data.shape[0]
    a = [[]] * data.shape[0]
    b = [[]] * data.shape[0]
    x = [[]] * data.shape[0]
    y = [[]] * data.shape[0]
    om = [[]] * data.shape[0]
    states = [[]] * data.shape[0]
    new_states = [[]] * data.shape[0]

    for i in range(data.shape[0]):
        f[i] = data[i,1]
        om[i] = 2 * pi * f[i]/RATE
        a[i] = [1, -2*r*cos(om[i]), r**2]
        b[i] = [r*sin(om[i])]
        states[i] = np.zeros(ORDER)
        new_states[i] = np.zeros(ORDER)
        x[i] = np.zeros(BLOCKSIZE)
        y[i] = np.zeros(BLOCKSIZE)
        yout = np.zeros(BLOCKSIZE)

    DBscale = True

    # Initialize plot window:
    plt.ion()           # Turn on interactive mode so plot gets updated
    fig = plt.figure(1)

    [g1] = plt.plot([], [], 'red')
    [g2] = plt.plot([], [], 'blue')

    g1.set_label('Input')
    g2.set_label('Output')
    plt.legend()

    g1.set_xdata(RATE/BLOCKSIZE * np.arange(0, BLOCKSIZE))
    g2.set_xdata(RATE/BLOCKSIZE * np.arange(0, BLOCKSIZE))
    plt.xlim(0, 0.5*RATE)

    plt.xlabel('Frequency (Hz)')
    plt.ylim(0, 150)

    # Open audio device:
    p = pyaudio.PyAudio()
    PA_FORMAT = p.get_format_from_width(WIDTH)

    stream = p.open(
        format    = PA_FORMAT,
        channels  = CHANNELS,
        rate      = RATE,
        input     = True,
        output    = True,
        frames_per_buffer = 256)

    for i in range(0, NumBlocks):
        input_bytes = stream.read(BLOCKSIZE, exception_on_overflow = False)                     # Read audio input stream

        input_tuple = struct.unpack('h' * BLOCKSIZE, input_bytes)  # Convert
        X = np.fft.fft(input_tuple)

        freqs = np.fft.fftfreq(len(X))

        idx = np.argmax(np.abs(X))
        freq = freqs[idx]
        freq_in_hertz = int(abs(freq * RATE))

        f_mapped = freq_map[freq_in_hertz]
        idx = np.where(data== f_mapped)[0]
        idx = int(idx)

        if ((freq_in_hertz>= 200) & (freq_in_hertz <= data[71,1])):
            x[idx][0] = 1000

        if (instrument == "Piano"):
            
            for j in range (0,data.shape[0]):
                [y[j], new_states[j]] = signal.lfilter(b[j], a[j], x[j], zi = states[j])
                if (j< data.shape[0]-1):
                    states[j+1] = new_states[j] 
                x[j][0] = 0.0
                yout += y[j]

        elif ((instrument == "Guitar" ) & (freq_in_hertz>= 200)):
            
            n = freq_in_hertz - 262
            yout = AudioLib.set_stretch(guitar_wf, 10, 200, 50)
            
            if len(yout != BLOCKSIZE):
                yout = np.pad(yout, (0, BLOCKSIZE- len(yout)), 'constant')

        else:
            print("Frequency not suitable for guitar transformation. Try higher frequncies next time")
        
    
        #for j in range (0,data.shape[0]):
        #    yout += y[j]
        #    y[j] = np.zeros(BLOCKSIZE)

        yout = AudioLib.bpf(yout, f_mapped-10, f_mapped+10)
        output_block = np.clip(yout.astype(int), -MAXVALUE, MAXVALUE)

        Y = np.fft.fft(output_block)

        # Convert values to binary data
        output_bytes = struct.pack('h' * BLOCKSIZE, *output_block)

        # Write binary data to audio output stream
        stream.write(output_bytes)

        voice_mod_wf.writeframes(output_bytes)
        voice_wf.writeframes(input_bytes)

        # Update y-data of plot
        g1.set_ydata(20 * np.log10(np.abs(X)))
        plt.pause(0.001)
        g2.set_ydata(20 * np.log10(np.abs(Y)))
        plt.pause(0.001)

        yout = np.zeros(BLOCKSIZE)
        output_block = BLOCKSIZE * [0]

    plt.close()
    stream.stop_stream()
    stream.close()
    p.terminate()
    print('* Finished')

def fun_rec():
    print('Recording...')
    record.record()

def fun_effect2(stvar2):
    if (os.path.isfile('voice_wf.wav')):
        play_audio.create_effect(stvar2)
    else:
        print('Record audio file first!')

def fun_play():
    if (os.path.isfile('voice_mod.wav')):
        play_audio.play_effect()
    else:
        print('Choose effect first!')


def fun_quit():
    print('Good bye')
    # root.quit()      
    root.destroy()
    
class Gui():
    def __init__(self, root):
        self.root=root
        root.title('Filter voice as musical instrument')
        
        # Define Tk variables
        gain = Tk.DoubleVar()       # floating point value, gain
        stvar = Tk.StringVar()          # text string
        stvar2 = Tk.StringVar()          # text string

        self.canvas=Tk.Canvas(root, width=200, height=200, background='white')
        self.canvas.grid(row=0,column=1)
        
        frame = Tk.Frame(self.root)
        frame.grid(row=0,column=0, sticky="n")

        Label1=Tk.Label(frame,text="Real Time User Audio Processing",
                        font='Helvetica 18 bold').grid(row = 0,column = 0, sticky = "w", pady=10)
        Label2=Tk.Label(frame, text="Choose Effect:").grid(row=2,column=0, sticky="w")
        self.option=Tk.OptionMenu(frame, stvar,"Piano","Guitar",
                                  command = fun_effect).grid(row=2,column=0, sticky="nw",padx=100)


        Label3=Tk.Label(frame,text="Audio File Processing",
                        font='Helvetica 18 bold').grid(row = 0,column = 1, sticky = "w", pady=10, padx=100)
        Button2=Tk.Button(frame,text="Record", command = fun_rec).grid(row = 2,column = 1, sticky = "w", padx=100)
        Label4=Tk.Label(frame, text="Choose Effect:").grid(row=3,column=1, sticky="w",padx=100)
        self.option2=Tk.OptionMenu(frame, stvar2,"Darth-Vader", "Echo","Chipmunk",
                                   command = fun_effect2).grid(row=3,column=1, sticky="nw",padx=200)
        Button3=Tk.Button(frame,text="Play", command=fun_play).grid(row = 4,column = 1, sticky = "w", padx=100)

        
        Button4 = Tk.Button(root, text = 'Quit',command = fun_quit).grid(row = 6,
                                            column = 0, sticky = "w",pady=10, padx=300)
        


        
if __name__== '__main__':
    root=Tk.Tk()
    gui=Gui(root)
    root.mainloop()
