import socket
import numpy as np
import PIL
from PIL import Image
import os
import random
import base64

def get_random_file(path):
    """
    Returns a random filename, chosen among the files of the given path.
    """
    files = os.listdir(path)
    index = random.randrange(0, len(files))
    return os.path.join(path, files[index])


# server settings
HOST = 'localhost'
PORT = 1234
length = 16
height = 24
maxsize = (length, height)

# connect socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
send = sock.send

# prepare image (open, convert to rgba, resize, convert to array)
fn = get_random_file("../images")
img = Image.open(fn)
img = img.convert('RGB').resize(maxsize)
#img.thumbnail(maxsize, PIL.Image.ANTIALIAS)
by = img.tobytes()
bb = base64.b64encode(by)
print("{}: {}/{})".format(fn, len(by), len(bb)))
send(b"WL " + bb + b"\n")
