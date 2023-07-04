from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import normalize
import numpy as np
from array import array
from matplotlib import pyplot as plt
import matplotlib as mpl

help_text = """
Input the parameters in the following order, separated by a space:
 right limit of x axis (default 800);
 n of sampling points in a single segment (default 4410);
 applied effects: "f" to fade out and/or "n" to normalize (default "n");
 number of sampling points to plot: not plotted if 0 (default 0);
 export path: if omitted, no file is exported (default None).

Left click to add a data point;
Right click to add a solitary peak;
Press "r" or "(" to smoothen the real part curve;
Press "i" or ")" to smoothen the imaginary part curve;
Enter to hear the sound.

Try setting "800 800" for the parameters to remove jitter.
"""

print("FFTdraw: draw a spectrum and hear how it goes. Type help for help.")
def input_params():
    """Take a string to set parameters for the sound."""
    param_string = input("Parameters > ").lower()
    defaults = ["800", "4410", "n", "0", "None"]
    params = param_string.split(" ")
    #remove the empty string
    if not params[0]:
        params.pop(0)
    try:
        while len(params)!=5:
            params.append(defaults[len(params)])
        
        if params[0]=="help":
            print(help_text)
            return(input_params())
        lim_x = int(params[0])
        fft_length = int(params[1])
        effects = params[2]
        plot_domain = int(params[3])
        out_path = params[4]
        if lim_x>fft_length:
            print("The right limit must be smaller than or equal to the FFT length.")
            return(input_params())
        if out_path[-4]!="." and out_path!="None":
            out_path += ".wav"
        print("The parameters are", params)
        return(lim_x, fft_length, effects, plot_domain, out_path)
    except:
        print("Invalid numberical values, or too many values to unpack.")
        return(input_params())

class LineSegment:
    """Defines the two line segments in the plotting area."""
    def __init__(self, Line):
        self.X = [0, lim_x]
        self.Y = [0.0, 0.0]
        self.line = Line #matplotlib line2D object
        
    def linearize_data(self):
        """Interpolate the waypoints to an array."""
        freq_scale = np.arange(0, lim_x, dtype=int)
        results = np.interp(freq_scale, xp=self.X, fp=self.Y)
        results_scaled = scale_data(results, resolution)
        return(results_scaled)
    
    def insert_value(self, x, y):
        """Insert a waypoint at (x,y). Called on left click."""
        index = 0
        while x>self.X[index] and index<len(self.X)-1:
            index += 1
        if x in self.X:
            self.X[index] = x
            self.Y[index] = y
        else:
            self.X = np.insert(self.X, index, x)
            self.Y = np.insert(self.Y, index, y)
        self.line.set_data(self.X, self.Y)

    def insert_peaks(self, x, y):
        """
        Insert a solitary peak at (x,y).
        Called on right click when there are no defined values in x-1, x, or x+1.
        """
        index = 0
        while x>self.X[index] and index<len(self.X)-1:
            index += 1
        if x in self.X or x-1 in self.X or x+1 in self.X:
            self.X[index] = x
            self.Y[index] = y
        else:
            self.X = np.insert(self.X, index, [x-1,x,x+1])
            self.Y = np.insert(self.Y, index, [0,y,0])
        self.line.set_data(self.X, self.Y)

    def make_smooth_curve(self):
        self.X, self.Y = bezier_smooth(self.X, self.Y)
        self.line.set_data(self.X, self.Y)

def detect_keyboard(event):
    """
    Detect (, ), r, i key presses to smoothen the curve, and
    detect the Enter key press to terminate the drawing.
    """
    if event.key=="(" or event.key=="r":
        print("Making the Real part smooth...")
        Real.make_smooth_curve()
    elif event.key==")" or event.key=="i":
        print("Making the Imaginary part smooth...")
        Imag.make_smooth_curve()
    elif event.key=="enter":
        print("Finished drawing with", len(Real.X), "points")
        reals = Real.linearize_data()
        imags = Imag.linearize_data()
        if sum(imags)==0:
            print("Imaginary part is empty, default to equate real part")
            imags = reals
        samples_fft = np.zeros((fft_length,), dtype=complex)
        vertical_scale = 80000 / lim_x     #prevent overflow
        for i in range(len(reals)):
            samples_fft[i] = complex(vertical_scale*reals[i],
                                     vertical_scale*imags[i])
        plt.close()
        convert_to_sound(samples_fft, fft_length)
        
def detect_mouse(event):
    """Detect any mouse clicks in the drawing area."""
    if event.inaxes==ax1:
        ax = "real"
    elif event.inaxes==ax2:
        ax = "imag"
    else:
        return
    x = int(event.xdata)
    y = int(event.ydata)
    if event.button==mpl.backend_bases.MouseButton.LEFT:
        lines[ax].insert_value(x, y)
    elif event.button==mpl.backend_bases.MouseButton.RIGHT:
        lines[ax].insert_peaks(x, y)
    else:
        #No dragging action, because it makes the plot glitchy
        #and occasionally freezes the window.
        pass

def bezier_smooth(X, Y):
    """Smoothen the line segments with a composite Bézier curve."""
    def comb_append(A):
        """
        Calculate the midpoints between peaks
        to be used as the two ends of a curvelet.
        """
        ln = len(A)
        A_out = np.empty((ln*2-1,))
        for i in range(ln - 1):
            A_out[i*2] = A[i]
            A_out[i*2+1] = (A[i]+A[i+1])/2
        A_out[-1] = A[-1]
        return(A_out)

    X_midpoints = comb_append(X)
    Y_midpoints = comb_append(Y)
    X_out = np.array([int(X[0])], dtype=int)
    Y_out = np.array([Y[0]], dtype=float)
    for i in range(1, len(X_midpoints)-2, 2):
        curve = mpl.bezier.BezierSegment(np.array([X_midpoints[i:i+3],
                                         Y_midpoints[i:i+3]]).T)
        T = np.linspace(0, 1, 20)
        curve_dal = curve.point_at_t(T)
        X_curve, Y_curve = np.split(np.array(curve_dal).T, 2)
        X_out = np.append(X_out, X_curve[0])  #np.split returns a nested array
        Y_out = np.append(Y_out, Y_curve[0])

    X_out = np.append(X_out, X[-1])
    Y_out = np.append(Y_out, Y[-1])
    return(X_out, Y_out)

def lengthen_samples(samples, loops):
    """Concatenate multiple samples to make the resulting sound audible."""
    s_out = array("h", [])
    for i in range(loops):
        s_out = s_out + samples
    return(s_out)

def scale_data(values, resolution=10):
    """Scales the user input to calibrate to the desired frequency."""
    i = 0
    values_rar = array("h", [])
    while i<len(values):
        try:
            values_clip = values[i:i+resolution]
        except IndexError:
            values_clip = values[i:]
        values_rar.append(int(max(values_clip))) #max() preserve the peak
        i += resolution
    return(values_rar)

def convert_to_sound(samples_fft, fft_length):
    """Convert scaled data to sound."""
    def plot_samples(start, end):
        fig = plt.figure(2, figsize=(8.0,5.4))
        Y = samples[start:end]
        X = array("h", [i for i in range(len(Y))])
        plt.plot(X, Y, "r+")
        plt.show()

    def check(samples_fft):
        if samples_fft.dtype!="complex128":
            print("Converting input to complex...")
            samples_fft = np.array(samples_fft, dtype=complex)
            
    check(samples_fft)
    samples_ifft = np.fft.ifft(samples_fft)
    samples = array("h", [int(i.real) for i in samples_ifft])
    samples = lengthen_samples(samples, 88200//fft_length)
    #extend short samples (~0.1s) to make audible (~2s)
    sound = AudioSegment.silent(1, frame_rate=44100)
    sound = sound._spawn(samples)
    if "n" in effects:
        sound = normalize(sound)
    elif "f" in effects:
        sound = sound.fade_out(len(sound))
    print("Playing... ", end="")
    play(sound)
    print("Done, length of sound is", len(sound),
          "Loudness is", round(sound.max_dBFS,2))
    if plot_domain!=0:
        plot_samples(0, int(plot_domain))
    if out_path!="None":
        sound.export(out_path, format="wav")

lim_x, fft_length, effects, plot_domain, out_path = input_params()
resolution = 44100 // fft_length
plt.ion()
fig, (ax1,ax2) = plt.subplots(2, 1, sharex=True, figsize=(4.2,5.6))
ax1.set(xlim=(0,lim_x), ylim=(0,10000), title="Real part")
ax2.set(xlim=(0,lim_x), ylim=(0,10000), title="Imaginary part")
line_real, = ax1.plot([], [])
line_imag, = ax2.plot([], [], color="C1")
Real = LineSegment(line_real)
Imag = LineSegment(line_imag)
lines = {"real":Real, "imag":Imag}
fig.canvas.mpl_connect("key_press_event", detect_keyboard)
fig.canvas.mpl_connect("button_press_event", detect_mouse)
plt.show()
