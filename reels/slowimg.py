"""
Image sending reel using PX command.

Simple reel that sends random images from a directory to the Wall.
Uses the standard pixelflut PX command to send one pixel at a time.
This is very slow and you can see the image change.

Created by kratenko.
"""
import os
import random
import time

import numpy as np
from PIL import Image

from fluter import Fluter

fluter = Fluter()


def get_random_file(path):
    """
    Returns a random filename, chosen among the files of the given path.
    """
    files = os.listdir(path)
    index = random.randrange(0, len(files))
    return os.path.join(path, files[index])


def send(img):
    arr = np.array(img)
    for i in range(0, img.size[0]):
        for j in range(0, img.size[1]):
            fluter.send_pixel((i, j), arr[j, i])


while True:
    # prepare image (open, convert to rgba, resize, convert to array)
    fn = get_random_file("../images")
    print("sending image '{}'".format(fn))
    send(Image.open(fn))
    #time.sleep(1)
