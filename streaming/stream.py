import numpy as np
from time import sleep
from time import time

from pyv4l2.frame import Frame
from pyv4l2.control import Control

from encoding import UYVY_RAW2RGB_PIL

frame = Frame('/dev/video1')

import visdom
vis = visdom.Visdom()

def send(im, win=None, env=None, opts=None):
    from six import BytesIO
    import base64 as b64

    opts = {} if opts is None else opts
    buf = BytesIO()
    im.save(buf, format='PNG')
    b64encoded = b64.b64encode(buf.getvalue()).decode('utf-8')

    data = [{
        'content': {
            'src': 'data:image/png;base64,' + b64encoded,
            'caption': opts.get('caption'),
        },
        'type': 'image',
    }]

    return vis._send({
        'data': data,
        'win': win,
        'eid': env,
        'opts': opts,
    })

while True:
    time_in = time()
    frame_data = frame.get_frame()

    data = np.array(list(frame_data), dtype='uint8')
    time_cap = time()

    img = UYVY_RAW2RGB_PIL(data, 720, 576)

    #vis.image(np.array(img).transpose(2, 0, 1), win='foo')
    #send(img.convert('RGBA'), win='foo')
    #img.convert('RGBA').save('foo.png', 'png')
    time_out = time()

    print('sent image, time image: {}, time cap: {}'.format(
        (time_out - time_in), (time_cap - time_in)))

    sleep(12 / 60)
