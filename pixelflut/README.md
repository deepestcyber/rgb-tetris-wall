# Pixelflut @ tetriswall

## Setup

    $ virtualenv -p python3 flut
	$ . flut/bin/activate
	$ pip install -r requirements.txt

Debian packages you might need:

- `libcairo2-dev`

## Running in canvas mode

Canvas mode is just a dummy server to draw pixels on a cairo canvas.
Start:

    $ python pixelflut.py canvas_brain.py

## Running in SPI mode

This mode is for the tetris wall and makes sure that the dimensions
of the wall are respected.
Start:

	$ python pixelflut.py spi_brain.py

## Quick test

Set one pixel at x=10, y=10 to green:

	$ echo 'PX 10 10 #00AA00' | nc -q1 localhost 1234

Draw some lines:

	$ for j in `seq 0 5 100`; do for i in {0..640}; do echo "px $i $j #AA0000"; echo "px $j $i #00AA00ff"; done; done | nc -q1 localhost 1234

