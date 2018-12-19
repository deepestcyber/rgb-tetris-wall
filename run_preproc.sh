# run the whole raspi proprocessing pipeline for teh rgb-tetris-wall

cd /home/pi/rgb-tetris-wall/raspi_preproc/
. /home/pi/env/bin/activate

# needed for the pixelflut api:
x11vnc -forever -usepw -create &

python3 controller.py

