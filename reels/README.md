# LED Wall Reels
Reels are scripts that create animations for the LED Wall. Images are sent 
using our extended Pixelflut protocol (that has an additional command to 
send the whole content for the wall in one go in about 1.6kB).

A module named `fluter` is provided to make it dead easy to write reels;
just import the function you need from `fluter` and send pixels, 
PIL-images, RAW-RGB-image-bytestrings, or arrays (numpy or native).

Look at the basic examples, like `randimg.py` or `gol.py`, to find out 
how to use the module.
