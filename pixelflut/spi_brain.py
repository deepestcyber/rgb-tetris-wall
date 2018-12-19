import logging
import base64
import os

import pygame
import pigpio


DEBUG_MODE = False

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
    pi.set_mode(SYNC_PIN, pigpio.INPUT)  # define pulldown/pullup
    spi = pi.spi_open(0, 500000, 0)  # 243750 487500 975000 1950000
except:
    # Possibly the gpio daemon broke or we are not running on a pi.
    input('Continue?')
    pi = None
    spi = None


def decodeByte2Mode(byte):
    # first 3 bits code the mode and remaining 5 bits code the submode
    return byte >> 5, byte & ~(7 << 5)


def read_mode_SPI():
    global spi
    (num, byte) = pi.spi_read(spi, 1)
    if num == 1:
        mode, submode = decodeByte2Mode(byte[0])
        if DEBUG_MODE:
            print("debug -", "read mode", "received_data:", num, byte[0], "received_mode:", mode, "received_submode:", submode)
        return (mode, submode)
    return 0, 0


def send_SPI(data):
    global spi
    if DEBUG_MODE:
        print("debug -", "sending bytes:", len(data))
    pi.spi_write(spi, data)


def send_canvas_over_SPI(canvas):
    global array3d, pi
    global CANVAS_WIDTH, CANVAS_HEIGHT

    leds = array3d(canvas.screen).astype('uint8')
    leds = leds[:CANVAS_WIDTH, :CANVAS_HEIGHT, :]
    data = leds.transpose(1, 0, 2).flatten().tobytes()

    send_SPI(data)


@on('LOAD')
def load(canvas):
    log.debug('load event')

    return # remove if canvas should be resized as well

    global CANVAS_WIDTH, CANVAS_HEIGHT
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
    global send_canvas_over_SPI
    if ticks % 50 == 0:
        print('.')

    # just wait, until the sync pin is set
    while ((pi.read_bank_1() >> SYNC_PIN) & 1) != 1:
        pass

    if ((pi.read_bank_1() >> SYNC_PIN) & 1) == 1:

        (mode, submode) = read_mode_SPI()

        if (mode == 4):  #mode for pixelflut
            send_canvas_over_SPI(canvas)
        else:
            os.exit(1)

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


@on('COMMAND-WL')
def command_wl(canvas, client, *args):
    global log
    log.debug("wl command event %s %d args", client, len(args))
    w, h = canvas.size
    raw_size = w * h * canvas.depth
    b64_size = int(raw_size + raw_size/3)
    assert len(args) == 1
    base = args[0]
    assert len(base) == b64_size
    data = base64.b64decode(base)
    assert len(data) == raw_size

    for y in range(h):
        for x in range(w):
            p = (y*w + x) * 3
            canvas.set_pixel(x, y, data[p], data[p+1], data[p+2], 0xff)
    return True
