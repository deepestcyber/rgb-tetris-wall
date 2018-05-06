import argparse
import numpy as np
from time import sleep
from time import time

from pyv4l2.frame import Frame
from pyv4l2.control import Control

from encoding import UYVY_RAW2RGB_PIL
from visualization import send_visdom

parser = argparse.ArgumentParser()

parser.add_argument('--width', type=int, default=720)
parser.add_argument('--height', type=int, default=576)
parser.add_argument('--scale', type=float, default=1.)
parser.add_argument('--visdom-server', type=str, default='http://localhost')
parser.add_argument('--visdom', action='store_true')
parser.add_argument('--device', type=str, default='/dev/video1')

args = parser.parse_args()
frame = Frame(args.device)

w = int(args.width // args.scale)
h = int(args.height // args.scale)

if args.visdom:
    import visdom
    vis = visdom.Visdom(server=args.visdom_server)

while True:
    time_in = time()
    frame_data = frame.get_frame()

    data = np.array(list(frame_data), dtype='uint8')
    time_cap = time()

    img = UYVY_RAW2RGB_PIL(data, w, h)

    #import pdb; pdb.set_trace()

    if args.visdom:
        send_visdom(vis, img.convert('RGBA'), win='foo')

    time_out = time()

    print('sent image, time image: {}, time cap: {}'.format(
        (time_out - time_in), (time_cap - time_in)))
