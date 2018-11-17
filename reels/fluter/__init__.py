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


class Fluter:
    DEFAULT_HOST = None

    def __init__(self, host=DEFAULT_HOST, width=16, height=24, depth=3):
        self.host, self.port = self._parse_host(host)
        self.width = width
        self.height = height
        self.depth = depth
        self.socket = None

    def _parse_host(self, host):
        if host is Fluter.DEFAULT_HOST:
            host = os.environ.get("PIXELFLUT_HOST", "localhost:1234")
        parts = host.split(":")
        if len(parts) == 2:
            return parts[0], int(parts[1])
        else:
            return parts[0], 1234

    def _connect(self):
        # TODO: add a reconnect mechanic
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))

    def send_pixel(self, pos, colour):
        """
        Set a single pixel on pixelflut server. Connects on demand.
        :param pos: (x, y) -- position of pixel to set
        :param colour: (r, g, b) or (r, g, b, a) -- colour to set pixel to
        :return:
        """
        assert len(pos) == 2
        assert 3 <= len(colour) <= 4
        self._connect()
        args = tuple(pos) + tuple(colour)
        if len(colour) == 3:
            self.socket.send(b"PX %d %d %02x%02x%02x\n" % args)
        else:
            self.socket.send(b"PX %d %d %02x%02x%02x%02x\n" % args)

    def send_raw(self, data):
        """
        Send 16x24 raw image data (RGB, uint8) to server.
        :param data:
        :return:
        """
        assert len(data) == self.width * self.height * self.depth
        self._connect()
        encoded = base64.b64encode(data)
        self.socket.send(b"WL " + encoded + b"\n")

    def send_image(self, image):
        """
        Send image to server (scales to 16x24).
        :param image:
        :return:
        """
        image = image.resize((self.width, self.height)).convert("RGB")
        self.send_raw(image.tobytes())

    def send_array(self, arr):
        """
        Send array data to server. Must have 16*24*3 uint8 values.
        :param arr:
        :return:
        """
        flat = np.array(arr).flatten()
        self.send_raw(flat)
