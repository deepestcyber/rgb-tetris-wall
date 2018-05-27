import os
import argparse
import numpy as np
from time import sleep
from time import time

from pyv4l2.frame import Frame
from pyv4l2.control import Control

from lib.encoding import UYVY_RAW2RGB_PIL
from lib.visualization import send_visdom
from lib.cropping import extract_single_player_area
from lib.cropping import extract_colours

parser = argparse.ArgumentParser()

parser.add_argument('--width', type=int, default=720)
parser.add_argument('--height', type=int, default=576)
parser.add_argument('--scale', type=float, default=1.)
parser.add_argument('--visdom-server', type=str, default='http://localhost')
parser.add_argument('--visdom', action='store_true')
parser.add_argument('--device', type=str, default='/dev/video1')

args = parser.parse_args()

w = int(args.width // args.scale)
h = int(args.height // args.scale)

os.system('v4l2-ctl -d {device} --set-fmt-video width={w},height={h}'.format(
    device=args.device, w=w, h=h))

frame = Frame(args.device)

if args.visdom:
    import visdom
    vis = visdom.Visdom(server=args.visdom_server)


def send_pi(img):
    x_tl = 270/720 * img.width
    y_tl = 152/576 * img.height
    x_br = 475/720 * img.width
    y_br = 474/576 * img.height
    rect = (x_tl, y_tl, x_br, y_br)

    area = extract_single_player_area(img, rect)

    if args.visdom:
        send_visdom(vis, area.convert('RGBA'), win='crop img')

    colours = extract_colours(area)

    if args.visdom:
        send_visdom(vis, colours.convert('RGBA'), win='crop color img')

while True:
    time_in = time()
    frame_data = frame.get_frame()

    data = np.array(list(frame_data), dtype='uint8')
    time_cap = time()

    img = UYVY_RAW2RGB_PIL(data, w, h)

    #import pdb; pdb.set_trace()

    if args.visdom:
        send_visdom(vis, img.convert('RGBA'), win='cap img')

    send_pi(img)

    time_out = time()

    print('sent image, time image: {}, time cap: {}'.format(
        (time_out - time_in), (time_cap - time_in)))
