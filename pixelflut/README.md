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

	$ python pixelflut.py canvas_brain.py
