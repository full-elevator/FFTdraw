# FFTdraw

Read an FFT frequency-intensity plot drawn by hand, and generate sound from it - v0.5

A little experiment with sounds. Not really user-friendly, well-optimized, or useful, but it is capable of making a wide range of strange sounds by changing the plot and the `-l` (`fft_length`) parameter. I'll gladly accept any bug reports.

# This commit

 - Removed a process which scales up the spectrum before plotting to make the x-axis values match the frequencies, and scales down again before generating the sound. This process makes all previous sounds __inaccurate__. This version uses a secondary axis which indicates the frequency. However, you may need to zoom the plot if `-x` (`lim_x`) is big.
 - Added an option to take a short audio segment as input and edit its spectrum.<br>
   `fromfile -i D:/path/to/file/example.wav -ss 1000`<br>
 - Changed the command to a batch-like syntax. Note to self: if ever doing a project of this size, determine the mode of input early instead of keep changing it along the route...

# Previous commits

## 0.4

 - Changed the method of interaction. Now, peaks are drawn at the position of the cursor whenever the key `1` is pressed, allowing use of the built-in zoom and pan tools in matplotlib.
 - Added a display for waypoints used in curve smoothening.
 - Rewrote a few clumsy chunks of code.

## 0.3

 - Added an option to pad the input with zeros to increase frequency domain resolution.
 - Added line smoothening.
 - Removed the MS Paint-based input (bad!) in the initial commit.

# Usage

## Basic

`fromblank -x 882 -fade 1 -plot 1000` for a quick start.

A plot window will pop up. Press "1" in the plotting area to add a peak at the position of the mouse. "Enter" to hear the sound.

Note: Please turn down the volume. The sounds generated can be harsh.

When the plot window is focused:
 - Press `1` (the number) to add a solitary peak;
 - Hold down `1` and move the cursor to draw a line;
 - `r` or `(` to smoothen the real part curve;
 - `i` or `)` to smoothen the imaginary part curve;
 - and "Enter" to hear the sound.

The smooth curve is calculated based on the black X waypoints, which are not part of the actual spectrum data.

## Full syntax

`mode` -`option 1` `value 1` -`option 2` `value 2` ...

### Modes

 -  "fromblank" or "b" - draw on a blank canvas
 -  "fromfile" or "f" - import a file, show its FFT in the given range, and edit it

### Options

 - "-x `lim_x`" - Right limit of x axis. (Default 800)
 - "-l `fft_length`" - Sampling points in a single segment. Used for zero padding. (Default 4410)
 - "-norm `bool`" - Apply normalization. (Default 1)
 - "-fade `bool`" - Apply fade out effect. (Default 0)
 - "-plot `n_samples`" Plot the waveform for n sampling points. If omitted, no plot will be shown.
 - "-y `fp`" - The path and filename for the output wav file. If `fp` is omitted, the file name will be "fftdraw"+`local time`.
 - "-swipe `n`" When holding down "1" and moving the mouse at x, flatten the curve between x-n and x+n. (Default 0, or no flatten)

### Options for "fromfile" mode only
 - "-i `fp`" - The path and filename for the input wav file.
 - "-ss `start time`" - The starting time in milliseconds.
 - "-window `bool`" - Apply a Hann window function. (Default 1) The window makes the peaks more distinct, but may cause stutter in the output.

In the last step, the code malfunctions when _samples_ is a NumPy ndarray, generating noise. Using array.array to store the samples fixes the issue.

License: MIT license.
