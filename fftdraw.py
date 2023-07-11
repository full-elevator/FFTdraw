from matplotlib import pyplot as plt
import matplotlib as mpl
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import normalize
import numpy as np
from array import array #pydub has issues with float32 or int64, see issue #293
import warnings

help_text = """
Input the parameters in the following order, separated by a space:
 right limit of x axis (default 800);
 n of sampling points in a single segment (default 4410);
 applied effects: f to fade out and/or n to normalize (default n);
 number of sampling points to plot: not plotted if 0 (default 0);
 export path: if omitted, no file is exported (default None).

When the plot window is focused:
"1" (the number) to add a solitary peak;
Hold down "1" and move the cursor to draw a line;
"r" or "(" to smoothen the real part curve;
"i" or ")" to smoothen the imaginary part curve;
and "Enter" to hear the sound.

The smooth curve is calculated based on the black X waypoints.

Try setting "800 800" for the parameters to remove jitter.
"""
print("FFTdraw: draw a spectrum and hear how it goes. Type help for help.")
def input_params():
    """Take a string to set parameters for the sound."""
    param_string = input("Parameters > ").lower()
    defaults = [800, 4410, "n", 0, None]
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
            warnings.warn(f"""The right limit {lim_x} is greater than
                the FFT length {fft_length}. Setting to {fft_length}""")
            lim_x = fft_length
            
        if out_path: #specify the format if missing
            if out_path[-4]!=".":
                out_path += ".wav"
                
        print("The parameters are", lim_x, fft_length, effects, plot_domain, out_path)
        return(lim_x, fft_length, effects, plot_domain, out_path)
    except:
        warnings.warn(f"""Invalid numberical values, or too many values to unpack.
            Using default values {defaults}.""")
        return(defaults)

def get_swipe_width(lim_x):
    """Determine how many adjacent values to set as event.ydata to prevent jags."""
    if 0<lim_x<=90: width = 0
    elif 90<lim_x<=200: width = 1
    elif 200<lim_x<=300: width = 2
    elif 300<lim_x<=400: width = 3
    elif 400<lim_x<=800: width = 4
    else: width = 5
    return(width)

class LineSegment:
    """Define a line segment in the plotting area."""
    def __init__(self, ax):
        self.ax = ax    #"ax1" for real, "ax2" for imag
        self.X = np.arange(0, lim_x, dtype=int)
        self.Y = np.zeros((lim_x,), dtype=float)
        self.vertices = {0:0.0, lim_x:0.0}
        #self.line = Line #matplotlib line2D object
        if ax==ax1:
            self.line, = ax.plot([], [], "b")
        elif ax==ax2:
            self.line, = ax.plot([], [], "C1")
        self.edges, = ax.plot([], [], "xk") #black X markers
        
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
        if not x or not y: return
        if 0<=x<=lim_x:
            for i in range(max(0,x-swipe_w), min(x+swipe_w,lim_x)):
                self.Y[i] = y

            self.line.set_data(self.X, self.Y)
                
    def make_smooth_curve(self):
        vertices_X, vertices_Y = bezier_smooth(self.vertices)
        #print("Vertices generated successfully.")
        self.Y = np.interp(self.X, vertices_X, vertices_Y)
        self.line.set_data(self.X, self.Y)

    def scale_data(self, resolution):
        """Scale the user input to calibrate to the desired frequency."""
        i = 0.0
        values_rar = array("h", [])
        while i<len(self.Y):
            try:
                values_clip = self.Y[int(i):int(i+resolution)]
            except IndexError:
                values_clip = self.Y[int(i):]
            values_rar.append(int(max(values_clip))) #max() preserves the peak
            i += resolution
        return(values_rar)

def detect_keyboard(event):
    """Detect key presses."""
    key = event.key
    
    if key=="(" or key=="r":
        Real.make_smooth_curve()
    elif key==")" or key=="i":
        Imag.make_smooth_curve()
    elif key=="enter":
        reals = Real.scale_data(44100 / fft_length)
        imags = Imag.scale_data(44100 / fft_length)
        if sum(imags)==0:
            warnings.warn("Imaginary part is empty, default to equate real part")
            imags = reals
        samples_fft = np.zeros((fft_length,), dtype=complex)
        vertical_scale = 60000 / lim_x     #prevent overflow
        for i in range(len(reals)):
            samples_fft[i] = complex(vertical_scale*reals[i],
                                     vertical_scale*imags[i])
            
        plt.close()
        convert_to_sound(samples_fft, fft_length)
        
    if event.inaxes==ax1: ax = "real"
    elif event.inaxes==ax2: ax = "imag"
    else: return
    
    if key=="1":
        lines[ax].draw_peak(int(event.xdata), event.ydata)
        #lines("vertices_"+ax).set_data(.keys(), D.values())     
    
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
    """Concatenate multiple samples to make the resulting sound audible."""
    s_out = array("h", [])
    for i in range(loops):
        s_out = s_out + samples
    return(s_out)

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
            warnings.warn("Converted non-complex input to complex.")
            samples_fft = np.array(samples_fft, dtype=complex)
            
    check(samples_fft)
    samples_ifft = np.fft.ifft(samples_fft)
    samples = np.array([], dtype=np.int32)
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
    if out_path!="None" and out_path: #not None or "None"
        sound.export(out_path, format="wav")

lim_x, fft_length, effects, plot_domain, out_path = input_params()
swipe_w = get_swipe_width(lim_x)
plt.ion()
fig, (ax1,ax2) = plt.subplots(2, 1, sharex=True, figsize=(4.2,5.6))
ax1.set(xlim=(0,lim_x), ylim=(0,10000), title="Real part")
ax2.set(xlim=(0,lim_x), ylim=(0,10000), title="Imaginary part")

line_imag, = ax2.plot([], [], color="C1")
Real = LineSegment(ax1)
Imag = LineSegment(ax2)
lines = {"real":Real, "imag":Imag}
fig.canvas.mpl_connect("key_press_event", detect_keyboard)
fig.canvas.mpl_connect("motion_notify_event", detect_swipe)
plt.show()
