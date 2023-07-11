# FFTdraw

Read an FFT frequency-intensity plot drawn by hand, and generate sound from it - v0.4

A little experiment with sounds. Not really user-friendly, well-optimized, or useful, but it is capable of making a wide range of strange sounds by changing the plot and the _fft_length_ parameter. I'll gladly accept any bug reports.

# Possible updates

 - [ ] An option to take a short audio segment as input and edit its spectrum.

# This commit

 - Changed the method of interaction. Now, peaks are drawn at the position of the cursor whenever the key _1_ is pressed, allowing use of the built-in zoom and pan tools in matplotlib.
 - Added a display for waypoints used in curve smoothening.
 - Rewrote a few clumsy chunks of code.

# Previous commits

 - Added an option to pad the input with zeros to increase frequency domain resolution. Achieved by inputing different _lim_x_ and _fft_length_ parameters.
 - Added line smoothening to make the sound wider/deeper/mellower.
 - Removed the MS Paint-based input (bad!) in the initial commit.

# Usage

Input the parameters in the following order, separated by a space:
 - right limit of x axis (default 800);
 - n of sampling points in a single segment (default 4410);
 - applied effects: f to fade out and/or n to normalize (default n);
 - number of sampling points to plot: not plotted if 0 (default 0);
 - export path: if omitted, no file is exported (default None).

When the plot window is focused:
 - "1" (the number) to add a solitary peak;
 - Hold down "1" and move the cursor to draw a line;
 - "r" or "(" to smoothen the real part curve;
 - "i" or ")" to smoothen the imaginary part curve;
 - and "Enter" to hear the sound.

The smooth curve is calculated based on the black X waypoints.

Try setting "800 800" for the parameters to remove jitter.

# Technical details

The program works as follows:
1. Take the data from the two Line2D objects. 
2. Scale the data based on the _fft_length_ given, to calibrate the sound to the correct frequency.
    1. Calculate the _resolution_ from the _fft_length_.
    2. Get a slice with length _resolution_, and append the maximum _sample_ among them to _samples_fft_.
    3. Loop until the end of the values array.
3. Calculate an inverse FFT on _samples_fft_, putting the result in _samples_ifft_.
4. Take the real part of _samples_ifft_ and add them to _samples_.
5. Use _AudioSegment._spawn(samples)_ to generate the sound.

In the last step, the code malfunctions when _samples_ is a NumPy ndarray, generating noise. Using array.array to store the samples fixes the issue.

License: MIT license.
