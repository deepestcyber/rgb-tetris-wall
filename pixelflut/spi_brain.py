import logging

import pigpio
import numpy as np

from pygame.surfarray import array3d


# GPIO pin numbers
SYNC_PIN = 24
# canvas parameters
CANVAS_WIDTH = 16
CANVAS_HEIGHT = 24

log = logging.getLogger('brain')
log.debug('lol')


ticks = 0

try:
    pi = pigpio.pi()
    spi = pi.spi_open(0, 500000, 0)  # 243750 487500 975000 1950000
    pi.set_mode(SYNC_PIN, pigpio.INPUT)  # define pulldown/pullup
except:
    # Possibly the gpio daemon broke or we are not running on a pi.
    input('Continue?')
    pi = None
    spi = None


def send_canvas_over_spi(canvas):
    global spi, array3d, pi
    global CANVAS_WIDTH, CANVAS_HEIGHT

    leds = array3d(canvas.screen).astype('uint8')
    leds = leds[:CANVAS_WIDTH, :CANVAS_HEIGHT, :]
    #leds = np.zeros((NUM_LEDS_H, NUM_LEDS_V, 3), dtype='uint8')
    data = leds.transpose(1, 0, 2).flatten().tobytes()

    # just wait, until the sync pin is set
    while ((pi.read_bank_1() >> SYNC_PIN) & 1) != 1:
        pass

    pi.spi_write(spi, data)


@on('LOAD')
def load(canvas):
    log.debug('load event')

    return # remove if canvas should be resized as well

    global CANVAS_WIDTH, CANVAS_HEIGHT
    import pygame
    size = CANVAS_WIDTH, CANVAS_HEIGHT
    canvas.screen = pygame.display.set_mode(size, canvas.flags)
    canvas.width, canvas.height = size

@on('RESIZE')
def resize(canvas):
    global log
    log.debug('resize event')

@on('QUIT')
def quit(canvas):
    global log
    log.debug('quit event')

@on('TICK')
def tick(canvas):
    global log
    global ticks
    global send_canvas_over_spi
    if ticks % 50 == 0:
        print('.')

    send_canvas_over_spi(canvas)

    ticks += 1

@on('CONNECT')
def connect(canvas, client):
    global log
    log.debug('connect event %s', client)

@on('DISCONNECT')
def disconnect(canvas, client):
    global log
    log.debug('disconnect event %s', client)

@on('COMMAND-PX')
def command_px(canvas, client, *args):
    global log
    log.debug('px command event %s %s', client, args)
    assert len(args) == 3

    x, y, c = args
    c = c.lower().strip('#')

    assert x.isdecimal()
    assert y.isdecimal()
    assert 6 <= len(c) <= 8

    # pad optional alpha
    c += 'f' * (8 - len(c))

    x, y = int(x), int(y)
    r, g, b, a = tuple(int(c[i:i+2], 16) for i in (0, 2, 4, 6))

    canvas.set_pixel(x, y, r, g, b, a)
    return True
