# FFTdraw

Read an FFT frequency-intensity plot drawn by hand, and generate sound from it - v0.3

A little experiment with sounds. Not really user-friendly, well-optimized, or useful, but it is capable of making a wide range of strange sounds by changing the plot and the _fft_length_ parameter. I'll gladly accept any bug reports.

# Possible updates

 - [x] An option to smoothen the lines and make the sound wider/deeper/mellower, ideally after setting up all the waypoints.
 - [ ] The program malfunctions when using a NumPy array to convert to sound in the final step (FFT is fine). I don't yet know why...
 - [x] No more fuss with MS Paint: switching to Matplotlib. It'll feature easier drawing, customizable scaling of the FFT plot, and an option to display the waveform.
 - [ ] An API to take input data and draw peaks automatically.
 - [x] An option to pad the input with zeros to increase frequency domain resolution. Achieved by inputing different _lim_x_ and _fft_length_ parameters.

# Usage

Input the parameters in the following order, separated by a space:
1. right limit of x axis (default 800);
2. n of sampling points in a single segment (default 4410);
3. applied effects: f to fade out and/or n to normalize (default n);
4. number of sampling points to plot: not plotted if 0 (default 0);
5. export path: if omitted, no file is exported (default None).

After the inputs are processed, a Matplotlib window with two subplots will pop up. In the subplots:
* Left click to add a data point;
* Right click to add a solitary peak;
* Press "r" or "(" to smoothen the real part curve;
* Press "i" or ")" to smoothen the imaginary part curve;
* Enter to hear the sound.

# Technical details

The program works as follows:
1. Take the data from the two Line2D objects. 
2. Scale the data based on the _fft_length_ given, to calibrate the sound to the correct frequency.
    1. Calculate the _resolution_ from the _fft_length_.
    2. Get a slice with length _resolution_, and append the maximum _sample_ among them to _samples_fft_.
    3. Loop until the end of the values array.
3. Calculate an inverse FFT on _samples_fft_, putting the result in _samples_ifft_.
4. Take the real parts only of _samples_ifft_ and add them to samples.
5. Use _AudioSegment._spawn(samples)_ to generate the sound.


License: MIT license.
