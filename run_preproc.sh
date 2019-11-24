# run the whole raspi proprocessing pipeline for teh rgb-tetris-wall

cd /home/pi/rgb-tetris-wall/raspi_preproc/
. /home/pi/env/bin/activate
DISPLAY=:0.0
python3 controller.py
