from matplotlib import pyplot as plt
import matplotlib as mpl
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import normalize
import numpy as np
#pydub works with array but has issues with np.int32 or np.int64, see issue #293
from array import array
import warnings
from fftinput import *

def ms2sample(ms):
    return(ms/1000*rate)

class LineSegment:
    """Define a line segment in the plotting area."""
    def __init__(self, ax, Y_in=None):
        #The real line is in ax1, the imaginary line is in ax2.
        self.ax = ax   
        self.vertices = {0:0.0, lim_x:0.0}
        self.X = np.arange(0, lim_x, dtype=int)

        if type(Y_in) is np.ndarray:
            self.Y = Y_in
        else:
            self.Y = np.zeros((lim_x,), dtype=float)

        self.edges, = ax.plot([], [], "xk") #black X markers            
        if ax==ax1:
            self.line, = ax.plot(self.X, self.Y, "b")
        elif ax==ax2:
            self.line, = ax.plot(self.X, self.Y, "C1")
        
        
    def draw_peak(self, x, y):
        if x<0 or x>=lim_x:
            return
        elif int(self.Y[x])!=int(y):
            self.Y[x] = y
            self.line.set_data(self.X, self.Y)
            self.vertices[x] = y
            self.edges.set_data(list(self.vertices.keys()),
                                list(self.vertices.values()))
            #print(self.vertices)

    def draw_swipe(self, x, y):
        if not x or not y or x<0 or x>lim_x:
            return
        
        #print(max(0,x-params["swipe"]), min(params["swipe"],lim_x))
        for i in range(max(0,x-params["swipe"]), min(x+params["swipe"],lim_x)):
            self.Y[i] = y

        self.line.set_data(self.X, self.Y)
                
    def make_smooth_curve(self):
        vertices_X, vertices_Y = bezier_smooth(self.vertices)
        self.Y = np.interp(self.X, vertices_X, vertices_Y)
        self.line.set_data(self.X, self.Y)


def detect_keyboard(event):
    """Detect key presses."""
    key = event.key
    
    if key=="(" or key=="r":
        Real.make_smooth_curve()
    elif key==")" or key=="i":
        Imag.make_smooth_curve()
    elif key=="enter":
        reals = Real.Y
        imags = Imag.Y
        if sum(imags)==0:
            warnings.warn("Imaginary part is empty, default to equate real part")
            imags = reals
            
        samples_fft = np.zeros((fft_length,), dtype=complex)
        for i in range(len(reals)):
            samples_fft[i] = complex(y_scale*reals[i],
                                     y_scale*imags[i])
            
        plt.close()
        convert_to_sound(samples_fft, fft_length)
        
    if event.inaxes==ax1: ax = "real"
    elif event.inaxes==ax2: ax = "imag"
    else: return
    
    if key=="1":
        lines[ax].draw_peak(int(event.xdata), event.ydata)
    
def detect_swipe(event):
    """Detect cursor swipe motion."""
    if event.inaxes==ax1: ax = "real"
    elif event.inaxes==ax2: ax = "imag"
    else: return

    key = event.key
    if key=="1":
        lines[ax].draw_swipe(int(event.xdata), event.ydata)

def bezier_smooth(vertices_dict):
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

    #sort a dictionary based on its keys
    vertices_sorted = dict.fromkeys(sorted(vertices_dict))
    for item in vertices_sorted:
        vertices_sorted[item] = vertices_dict[item]
        
    vertices_X = list(vertices_sorted.keys())
    vertices_Y = list(vertices_sorted.values())
    
    midpoints_X = comb_append(vertices_X)
    midpoints_Y = comb_append(vertices_Y)
    #print(np.round_(midpoints_X,1), np.round_(midpoints_Y,1))
    
    X_out = np.array([0.0])
    Y_out = np.array([0.0])
    for i in range(1, len(midpoints_X)-2, 2):
        curve = mpl.bezier.BezierSegment(np.array([midpoints_X[i:i+3],
                                         midpoints_Y[i:i+3]]).T)
        T = np.linspace(0, 1, 20)
        curve_points = curve.point_at_t(T)
        X_curve, Y_curve = np.split(np.array(curve_points).T, 2)
        X_out = np.append(X_out, X_curve[0])  #np.split returns a nested array
        Y_out = np.append(Y_out, Y_curve[0])

    X_out = np.append(X_out, vertices_X[-1])
    Y_out = np.append(Y_out, vertices_Y[-1])
    return(X_out, Y_out)

def lengthen_samples(samples, loops):
    """Stream loop the ~0.1s sound to make it audible."""
    s_out = array("h", [])
    for i in range(loops):
        s_out = s_out + samples
    return(s_out)

def convert_to_sound(samples_fft, fft_length):
    """Convert FFT data to sound."""
    def plot_samples(end):
        fig = plt.figure(2, figsize=(8.0,5.4))
        Y = samples[:end]
        X = np.arange(end, dtype=int)
        plt.plot(X, Y, "r+")
        plt.show()

    def check(samples_fft):
        if samples_fft.dtype!="complex128":
            warnings.warn("Converted non-complex input to complex.")
            samples_fft = np.array(samples_fft, dtype=complex)
            
    check(samples_fft)
    samples_ifft = np.fft.ifft(samples_fft)
    samples = array("h", [int(i.real) for i in samples_ifft])

    #extend short samples (~0.1s) to make audible (~2s)
    samples = lengthen_samples(samples, 88200//fft_length)
    sound = AudioSegment.silent(1, frame_rate=rate)
    sound = sound._spawn(samples)
    if params["norm"]==1 or params["norm"]=="True":
        sound = normalize(sound)
    if params["fade"]==1 or params["fade"]=="True":
        sound = sound.fade_out(len(sound))
    print("Playing... ", end="")
    play(sound)
    print("Done, length of sound is", len(sound),
          "Loudness is", round(sound.max_dBFS,2))
    if "plot" in params:
        plot_samples(int(params["plot"]))
    if "y" in params:
        sound.export(params["y"], format="wav")

def get_sound_samples(fp, start=0, window=True):
    """Get mono sound. Start is measured in ms."""
    sound_orig = AudioSegment.from_wav(fp)
    sound_tracks = sound_orig.split_to_mono()
    #print("length of sound is", len(sound))
    samples = sound_tracks[0].get_array_of_samples()
    samples = samples[int(ms2sample(start)):int(ms2sample(start))+fft_length]
    
    if window:
        window_func = np.hanning(len(samples))
        samples *= window_func

    return(samples)

params = input_and_parse_params()
print("Parameters are", params)
lim_x = params["x"]
fft_length = params["l"]
rate = 44100 #Other sample rates may generate noise.
x_scale = rate / fft_length
y_scale = 60000 / lim_x     #prevent overflow
plt.ion()
fig, (ax1,ax2) = plt.subplots(2, 1, sharex=True, figsize=(4.2,5.6))
ax1.grid(True, "major", "x")
ax2.grid(True, "major", "x")

def conversion_to(x):
    return(x*x_scale)
def conversion_from(x):
    return(x/x_scale)
ax_axis = ax2.secondary_xaxis(-0.1, functions=(conversion_to, conversion_from))
ax_axis.set_xlabel("frequency [Hz]")
ax1.set(xlabel=None, xlim=(0,lim_x), title="Real part")
ax2.set(xlabel=None, xlim=(0,lim_x), title="Imaginary part")

if params["st"]=="fromfile" or params["st"]=="f":
    in_samples = get_sound_samples(params["i"], params["ss"], params["window"])
    in_fft = np.fft.fft(in_samples)[:lim_x]
    #print("len fft is ", len(in_fft))
    in_reals = in_fft.real / y_scale
    in_imags = in_fft.imag / y_scale

    y_max = max(max(abs(in_reals)), max(abs(in_imags)))
    ax1.set(ylim=(-y_max, y_max))
    ax2.set(ylim=(-y_max, y_max))

    Real = LineSegment(ax1, in_reals)
    Imag = LineSegment(ax2, in_imags)
else:
    Real = LineSegment(ax1)
    Imag = LineSegment(ax2)
    ax1.set_ylim(-5000,5000)
    ax2.set_ylim(-5000,5000)

lines = {"real":Real, "imag":Imag}
fig.canvas.mpl_connect("key_press_event", detect_keyboard)
fig.canvas.mpl_connect("motion_notify_event", detect_swipe)
plt.show()
