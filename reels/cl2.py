from PIL import Image
import os
import random

from fluter import send_image


def get_random_file(path):
    """
    Returns a random filename, chosen among the files of the given path.
    """
    files = os.listdir(path)
    index = random.randrange(0, len(files))
    return os.path.join(path, files[index])


# prepare image (open, convert to rgba, resize, convert to array)
fn = get_random_file("../images")
print("sending image '{}'".format(fn))
send_image(Image.open(fn))
