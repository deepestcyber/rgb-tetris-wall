from six import BytesIO
import base64 as b64

def send_visdom(vis, im, win=None, env=None, opts=None):
    opts = {} if opts is None else opts

    opts['height'] = opts.get('height', im.height)
    opts['width'] = opts.get('width', im.width)

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
