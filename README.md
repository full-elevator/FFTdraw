# FFTdraw

Read an FFT frequency-intensity plot drawn by hand, and generate sound from it - v0.1

A little experiment with sounds. Not really user-friendly, well-optimized, or useful, but it is capable of making a wide range of strange sounds by changing the resolution parameter.

# Possible updates

* The program malfunctions when using a NumPy array to convert to sound in the final step (FFT is fine). I don't yet know why...
* No more fuss with MS Paint: switching to Matplotlib once I fix the integer overflow errors. It'll feature easier drawing, customizable scaling of the FFT plot, possibly a logarithmic option too.
* An API to take input data and draw peaks automatically.
* An option to pad the input with zeros to increase frequency domain resolution.

# Usage

* An fftdraw.png file is included in the repository. After downloading, open the file with your preferred image editing tool.
* Draw the line plots for the real and imaginary frequencies.
* Run the program and input parameters as guided.
* Listen to the sound.
* (Optional) Export the sound.

# Technical details

The program determines the intensity of each frequency as follows:
1. Scan the plot of real part from left to right, finding the highest non-white pixel. Append its y coordinate in the subplot to an array. If no non-white pixels are found, default to 0. 
2. Scan the plot of imaginary part in the same fashion.
3. After the scan, calculate the _resolution_ from the _fft_length_.
4. Extract a list of length _resolution_, and append the maximum _sample_ among them to _samples_fft_.
5. Calculate an inverse FFT on _samples_fft_, putting the result in _samples_ifft_.
6. Take the real parts only of _samples_ifft_ and add them to samples.
7. Use AudioSegment._spawn(samples) to generate the sound.

The catch is that increasing the resolution of the frequency domain decreases the resolution of the time domain. I consider zero-padding a possible fix.
