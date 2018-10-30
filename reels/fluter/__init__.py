"""
Module for sending to deep pixelflut server.

Simple functions to send to a pixelflut server from a python script.
Handles connecting to the server on its own (but does never disconnect).
In addition to setting individual pixels it supports a command "WL" to
send a complete picture to our LED-Tetris-Wall.

To specify host/port of target server, set environment variable
PIXELFLUT_HOST to "hostname" or to "hostname:port".

Created by deep cyber -- the deepest of all cybers.
"""

import socket
import base64
import numpy as np
import os

HOST = "localhost"
PORT = 1234
WIDTH = 16
HEIGHT = 24
DEPTH = 3

# connect socket
sock = None


def config():
    global HOST, PORT
    if "PIXELFLUT_HOST" in os.environ:
        host = os.environ["PIXELFLUT_HOST"]
        parts = host.split(":")
        if len(parts) == 2:
            HOST, PORT = parts[:2]
        else:
            HOST = parts[0]


def connect():
    """
    Connect to pixelflut server. Called automatically on demand.

    You should not need to ever call this function directly.
    :return:
    """
    global sock
    if sock:
        return
    config()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))


def send_pixel(pos, colour):
    """
    Set a single pixel on pixelflut server. Connects on demand.
    :param pos: (x, y) -- position of pixel to set
    :param colour: (r, g, b) or (r, g, b, a) -- colour to set pixel to
    :return:
    """
    assert len(pos) == 2
    assert 3 <= len(colour) <= 4
    connect()
    if len(colour) == 3:
        sock.send(b"PX %d %d %02x%02x%02x\n" % pos + colour)
    else:
        sock.send(b"PX %d %d %02x%02x%02x%0x2\n" % pos + colour)


def send_raw(data):
    """
    Send 16x24 raw image data (RGB, uint8) to server.
    :param data:
    :return:
    """
    assert len(data) == WIDTH * HEIGHT * DEPTH
    connect()
    encoded = base64.b64encode(data)
    sock.send(b"WL " + encoded + b"\n")


def send_image(image):
    """
    Send image to server (scales to 16x24).
    :param image:
    :return:
    """
    image = image.resize((WIDTH, HEIGHT)).convert("RGB")
    send_raw(image.tobytes())


def send_array(arr):
    """
    Send array data to server. Must have 16*24*3 uint8 values.
    :param arr:
    :return:
    """
    flat = np.array(arr).flatten()
    send_raw(flat)
