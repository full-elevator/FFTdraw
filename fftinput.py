import warnings
import time

help_texts = {
"generic": """The input command uses a batch-like syntax.
Input "fromblank -x 882 -fade 1 -plot 1000" for a quick start.
A plot window will pop up. Press "1" in the plotting area
to add a peak at the position of the mouse. "Enter" to hear the sound.

Note: Please turn down your volume. The sounds generated can be harsh.

"help" - Print this message.
"help draw" - More drawing options, such as curve smoothening.
"help syntax" - Details about the command syntax.
"help examples" - A few examples.

""",

"draw": """Press "1" (the number) to add a solitary peak;
Hold down "1" and move the cursor to draw a line;
"r" or "(" to smoothen the real part curve;
"i" or ")" to smoothen the imaginary part curve;
and "Enter" to hear the sound.
Use the built-in matplotlib tools to zoom and pan the plot.

The smooth curve is calculated based on the black X waypoints,
which are not the actual data points.

""",

"syntax":"""[mode] -[option 1] [value 1] -[option 2] [value 2] ...
modes:
 "fromblank" or "b" - draw on a blank canvas
 "fromfile" or "f" - import a file, show its FFT in the given range, and edit it
options:
 "-x [lim_x]" - Right limit of x axis. (Default 800)
 "-l [fft_length]" - Sampling points in a single segment.
                     Used for zero padding. (Default 4410)
 "-norm [bool]" - Apply normalization. (Default 1)
 "-fade [bool]" - Apply fade out effect. (Default 0)
 "-plot [n_samples]" Plot the waveform for n sampling points.
                 If omitted, no plot will be shown.
 "-y [fp]" - The path and filename for the output wav file.
             If [fp] is omitted, the file name will be "fftdraw"+[local time].
 "-swipe [n]" When holding down "1" and moving the mouse at x,
              flatten the curve between x-n and x+n. (Default 0, or no flatten)
options for "fromfile" mode only:
 "-i [fp]" - The path and filename for the input wav file.
 "-ss [start time]" - The starting time in milliseconds.
 "-window [bool]" - Apply a Hann window function. (Default 1)
                    The window makes the peaks more distinct,
                    but may cause stutter in the output.

""",

"examples": """fromblank -x 4410 -l 4410 -fade 1 -y
 Draw a spectrum on a blank canvas with x_lim and fft_length as 4410
 to remove jitter, then apply a fade effect,
 and export to fftdraw-[current time stamp].wav
 The sound will be different with different x_lim and fft_length.
 When fft_length is too small, the frequency scale resolution will be very low;
 when fft_length is too big, the resulting audio may sound choppy.
 The default 4410 (0.1s) is usually suitable, but you may need to tinker
 with the settings when the result sounds wrong.
fromblank -x 2000 -l 4410 -swipe 5
 Edit the spectrum over the full audible range,
 and enable 11-value swipes to ease editing.
 Note: straight lines may also be created with curve smoothening.
fromfile -i d:/music.wav -ss 1234 -x 441
 Import D:/music.wav and take 1234ms to 1244ms as the input
 to edit the spectrum.
 Note: the resulting sound is stream looped to 2s to make it audible.
 
"""}
print("FFTdraw: draw a spectrum and hear how it goes. Type help for help.")

    
def input_and_parse_params():
    """Take a string to set parameters for the sound."""
    param_string = input("Parameters > ")
    defaults = {"st":"b", "x":100, "l":4410, "norm":1, "fade":0,
                "window":1, "ss":0, "swipe":0}
    #use default if no value is given after option
    defaults_if_omitted = {"y":time.strftime("fftdraw-%Y%m%d-%H%M%S.wav"),
                "i":"missing-filename", "plot":1000}

    params = {}
    params_list = param_string.split(" ")
    setting = "1st"
    for word in params_list:
        word = word.strip(" ")
        if len(word)==0: continue
        
        if word[0]=="-":
            setting = word
            params[setting[1:]] = ""    #use default if no value given
        else:
            try:
                params[setting[1:]] = int(word)
            except:
                params[setting[1:]] = word

    mode = params["st"].lower()
    allowed_modes = ["fromblank", "b", "fromfile", "f"]
    #print(mode)
    if param_string[:4]=="help":
        print(help_texts.get(mode, help_texts["generic"]))
        return(input_and_parse_params())
    
    if mode not in allowed_modes:
        warnings.warn(f"Unknown draw mode {mode}. Using default values.")
        return(defaults)

    for option in defaults_if_omitted:
        #if option not in defaults:
        #    warnings.warn(f"Unrecognized option {option}.")
        if option in params and not params[option]:
            params[option] = defaults_if_omitted[option]

    for option in defaults:
        if option not in params:
            params[option] = defaults[option]

    return(params)
