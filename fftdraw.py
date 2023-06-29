"""
This is the version before switching to matplotlib.
It used a png file (fftdraw.png) for input.
Extra parameter input prompts were scattered all around.
It worked too, though in a very inelegant way.
"""

from pydub import AudioSegment
from pydub.playback import play
import numpy as np
from array import array
from PIL import Image, ImageDraw

def file_not_found():
    print("""File not found. Please place fftdraw.png 
    in the same directory with fftdraw.py.""")
    exit(1)

def clear_canvas():
    #I'll spare the decorator for two usages
    try:
        plot = Image.open("./fftdraw.png").convert("L")
    except FileNotFoundError:
        file_not_found()
    p_draw = ImageDraw.Draw(plot)
    p_draw.rectangle((101,101,899,299), fill=255)
    p_draw.rectangle((101,401,899,599), fill=255)
    plot.save("fftdraw.png", format="png")
    plot.close()
    exit(0)

def lengthen_samples(samples, loops):
    s_out = array("h", [])
    for i in range(loops):
        s_out += samples
    return(s_out)

def change_volume(sound, v_final=0):  #hit top!
    if v_final>0:
        print("Final volume set above 0; may cause clipping.")
    volume = sound.max_dBFS
    sound = sound + v_final/volume
    return(sound)

def read_plot():
    def get_value(start, end): #{
        value = 0
        is_data = False
        for j in range(start, end, -1):
            value_pixel = plot.getpixel((i, j))
            if value_pixel<240:
                is_data = True
            if is_data==True and value_pixel>=240:
                value = start + 1 - j
                break   #read the highest non-background-color pixel
            
        return(value)
    #}
    try:
        plot = Image.open("./0-fftdraw.png").convert("L")
    except FileNotFoundError:
        file_not_found()

    values_real = array("h", [])
    values_imag = array("h", [])
    for i in range(101, 900):
        values_real.append(get_value(299, 101))
        values_imag.append(get_value(599, 401))
    plot.close()
    return(values_real, values_imag)

def make_fft_data(values, resolution=10):
    i = 0
    values_rar = array("h", [])
    while i<len(values):
        try:
            values_clip = values[i:i+resolution]
        except IndexError:
            values_clip = values[i:]
        values_rar.append(max(values_clip))     #preserve the peaks
        i += resolution
    return(values_rar)

option = input("y to clear canvas, any other key to decline [y/N] > ")
if option=="y":
    clear_canvas()

fft_length_input = input("Defaults to 4410 (0.1s). fft_length (int) > ")
try:
    fft_length = int(fft_length_input)
except:
    fft_length = 4410
resolution = 44100 // fft_length

values_real, values_imag = read_plot()
samples_real = make_fft_data(values_real, resolution)
samples_imag = make_fft_data(values_imag, resolution)

if sum(samples_imag)==0:
    print("Imaginary part is blank, defaulting to equate the real part")
    samples_imag = samples_real
samples_fft = np.zeros((fft_length,), dtype=complex)
#size is related to resolution
#The zeros should stay, so it's done this way
for i in range(len(samples_real)):
    samples_fft[i] = complex(10000*samples_real[i], 10000*samples_imag[i])

samples_ifft = np.fft.ifft(samples_fft)
samples = array("h", [int(i.real) for i in samples_ifft])
samples = lengthen_samples(samples, 20) #extend short samples to make audible
sound = AudioSegment.silent(1, frame_rate=44100)
sound = sound._spawn(samples)
option = input("Effects: f - fade out; n - normalization; fn - both > ")
if "n" in option:
    sound = change_volume(sound)
elif "f" in option:
    sound = sound.fade_out(len(sound))
play(sound)
print("Sound played for", len(sound), "ms,",
      "max volume was", round(sound.max_dBFS,2))
option = input("y to export the sound > ")
if option=="y":
    sound.export("fftdraw-sound.wav", format="wav")
