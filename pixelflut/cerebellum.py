import logging
import base64

from pygame.surfarray import array3d

#   DISPLAY=:0.0 python pixelflut.py spi_brain.py

# GPIO pin numbers
# canvas parameters
CANVAS_WIDTH = 16
CANVAS_HEIGHT = 24

log = logging.getLogger('brain')
log.debug('lol')


ticks = 0


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
    if ticks % 25 == 0:
        print('.')

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
    global send_canvas_over_spi
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
    global log, base64
    global send_canvas_over_spi
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
