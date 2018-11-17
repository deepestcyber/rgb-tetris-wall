import logging
log = logging.getLogger('brain')

log.debug('lol')

ticks = 0


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
    if ticks % 50 == 0:
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
    import base64
    global log
    log.debug("wl command event %s %d args", client, len(args))
    w, h = canvas.size
    raw_size = w * h * canvas.depth
    b64_size = int(raw_size + raw_size/3)
    assert len(args) == 1
    base = args[0]
    assert len(base) == b64_size
    data = base64.b64decode(base)
    assert len(data) == w * h * canvas.depth

    for y in range(h):
        for x in range(w):
            p = (y*w + x) * 3
            canvas.set_pixel(x, y, data[p], data[p+1], data[p+2], 0xff)
    return True
