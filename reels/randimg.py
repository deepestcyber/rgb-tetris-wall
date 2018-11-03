"""
Image sending reel using WL command.

Simple reel that sends random images from a directory to the Wall.
Uses our own WL-command to send complete picture in one go.

Created by kratenko.
"""
import os
import random
import time

from PIL import Image

from fluter import Fluter


def get_random_file(path):
    """
    Returns a random filename, chosen among the files of the given path.
    """
    files = os.listdir(path)
    index = random.randrange(0, len(files))
    return os.path.join(path, files[index])


fluter = Fluter()

while True:
    # prepare image (open, convert to rgba, resize, convert to array)
    fn = get_random_file("../images")
    print("sending image '{}'".format(fn))
    fluter.send_image(Image.open(fn))
    time.sleep(1)
