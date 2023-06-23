# FFTdraw
Read an FFT frequency-intensity plot drawn by hand, and generate sound from it - v0.1

A little experiment with sounds. Not really user-friendly, well-optimized, or useful, but it is capable of making a wide range of strange sounds by changing the resolution parameter.

# Possible updates
* Made with Pydub and NumPy, might switch to Librosa. Now I'm still learning how to use it.
* An API to take input data and draw peaks automatically.
* An option to pad the input with zeros to increase frequency domain resolution.
* Customizable scaling of the FFT plot, possibly a logarithmic plot also.
* Clean up the code, wrap functions into classes, etc.

# Usage
* An fftdraw.png file is included in the repository. After downloading, open the file with your preferred image editing tool.
* Draw the line plots for the real and imaginary frequencies.
* Run the program and input parameters as guided.
* Listen to the sound.
* (Optional) Export the sound.

# Technical details
The program determines the intensity of each frequency as follows:
* Scan the plot of real part from left to right, finding the highest non-white pixel. Append its y coordinate in the subplot to an array. If no non-white pixels are found, default to 0. 
* Scan the plot of imaginary part in the same fashion.
* After the scan, calculate the resolution from the FFT length.
* For every ''resolution'' values, append the maximum among them to samples_fft.
* Calculate an inverse FFT on samples_fft, putting the result in samples_ifft.
* Take the real parts only of samples_ifft and add them to samples.
* Use AudioSegment._spawn(samples) to generate the sound.

The catch is that increasing the resolution of the frequency domain decreases the resolution of the time domain. I consider zero-padding a possible fix.
