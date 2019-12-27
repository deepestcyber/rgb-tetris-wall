"""
RGB-reel exploring the mandelbrot set.

Displays a visualisation of the mandelbrot set and randomly zooms in on details.
"""
import numpy as np
import matplotlib.colors
import random

import time

from fluter import Fluter


def mandelbrot(c, maxiter):
    z = c
    for n in range(maxiter):
        if abs(z) > 2:
            return n
        z = z * z + c
    return 0


def mandelbrot_set(xmin, xmax, ymin, ymax, width, height, maxiter):
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    n3 = np.empty((width, height))
    for i in range(width):
        for j in range(height):
            n3[i, j] = mandelbrot(r1[i] + 1j * r2[j], maxiter)
    return r1, r2, n3


def single_val(i, m=1000):
    if i:
        h = min(i/m, 1.0)
        c = matplotlib.colors.hsv_to_rgb([h, 1, 1])
        c *= 255
#        print(h, c)
        return c
    else:
        return [0, 0, 0]


def draw(g_in):
    """
    Create image data from mandelbrot set values.
    :param g_in:
    :return:
    """
    a = np.zeros((24, 16, 3), dtype=np.uint8)
    # apply log to get more interesting colour distribution
    g = np.log2(g_in)
    # fix errors created by log (for 0 and 1)
    g[g_in == 0] = 0
    g[g_in == 1] = 0.0000000001
    m = g.max()
    for y in range(24):
        for x in range(16):
            a[y, x] = single_val(g[y, x], m)
    return a


def zoom_pos(r1, r2, n3):
    """
    Find new zoom position.

    Select a portion of the current zoomed position to zoom in further. Tries and find an interesting spot by always
    selecting a position that is partially within the mandelbrot set (so a partly black part).
    :param r1:
    :param r2:
    :param n3:
    :return:
    """
    nw = 4
    nh = 6
    tries = 0
    while True:
        nx = random.randint(0, 15 - nw)
        ny = random.randint(0, 23 - nh)
        sub = n3[ny:ny+nh, nx:nx+nw]
        in_set = np.sum(sub == 0)
        partial = in_set / (nw * nh)
        print("%02d:%02d,%02d:%02d: %f" % (nx,nx+nw,ny,ny+nw,partial))
        tries += 1
        if 0.1 <= partial <= 0.6:
            print(nx, ny)
            print(sub)
            coords = [nx, ny, nx+nw, ny+nh]
            limits = [r1[ny], r1[ny+nh], r2[nx], r2[nx+nw]]
            return coords, limits


fluter = Fluter()

minx, maxx = -1.7, .7
miny, maxy = -1.0, 1.0
zoom = 1
maxiter = 100
while True:
    r1, r2, n3 = mandelbrot_set(minx, maxx, miny, maxy, 24, 16, maxiter)
    #r1, r2, n3 = mandelbrot_set(-1.7, .7, -1.0, 1.0, 24, 16, 100)
    #r1, r2, n3 = mandelbrot_set(-.8, -.7, 0, .2, 24, 16, 100)
    print(n3)
    #print(r1)
    #print(r2)

    a = draw(n3)
    fluter.send_array(a)
    time.sleep(2)

    coords, limits = zoom_pos(r1, r2, n3)
    (x1, y1, x2, y2) = coords
    y2-=1
    x2-=1
    a[y1, x1:x2] = [255, 255, 255]
    a[y2, x1:x2+1] = [255, 255, 255]
    a[y1:y2, x1] = [255, 255, 255]
    a[y1:y2, x2] = [255, 255, 255]

    minx, maxx, miny, maxy = limits
    zoom += 1
    maxiter = int(n3.max() * 2)
    if maxiter < 50000:
        fluter.send_array(a)
        time.sleep(1)
    else:
        minx, maxx = -1.7, .7
        miny, maxy = -1.0, 1.0
        zoom = 1
        maxiter = 100

