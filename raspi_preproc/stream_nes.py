import os
import base64
import numpy as np
#from pyv4l2.frame import Frame
from PyV4L2Camera.camera import Camera
from PIL import Image
from PIL import ImageFilter
from nes_tetris import NesTetris


""" Computational costs on raspi:
- grab the frame: 13-17 ms
- convert frame to RGB PIL img: 5 - 6 ms
- cut game area: 2-3 ms
- calculate led pixels from cutted rgb img (including smooth filters):  19 - 27 ms
overall costs: 40-52 ms
"""

class StreamNES:
    # -s, --set - standard = < num >
    # pal or pal - X(X=B / G / H / N / Nc / I / D / K / M / 60)(V4L2_STD_PAL)
    # ntsc or ntsc - X(X=M / J / K)(V4L2_STD_NTSC)
    # secam or secam - X(X=B / G / H / D / K / L / Lc)(V4L2_STD_SECAM)

    def __init__(self, _num_leds_h=16, _num_leds_v=24, _ntsc=True, feedback=False):
        self.num_leds_h = _num_leds_h
        self.num_leds_v = _num_leds_v
        self.ntsc = _ntsc
        self.leds = np.zeros((_num_leds_v, _num_leds_h, 3)) #should be not necessary
        self.b64dict = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        if self.ntsc:
            self.mode = 'NTSC'
            self.fps = 30
            self.width = 720
            self.height = 480
        else:
            self.mode = 'PAL-B'
            self.fps = 25
            self.width = 720
            self.height = 576
        self.format = 'UYVY'
        self.b = 3  # 3 2
        #self.color = '' #''smpte170'
        if (feedback):
            fb = 'verbose'
        else:
            fb = 'silent'

        self.scale = 1.
        self.device = '/dev/video0'
        self.w = int(self.width // self.scale)
        self.h = int(self.height // self.scale)

        self.game = NesTetris(_num_leds_h=_num_leds_h, _num_leds_v=_num_leds_v)

        #-p 25
        os.system(
        'v4l2-ctl -d {device} -s {m} --set-fmt-video width={w},height={h},pixelformat={pf} --{fb}'.format(
        #'v4l2-ctl -d {device} -p {fps} -s {m} --set-fmt-video width={w},height={h},pixelformat={pf} --{fb}'.format(
                device=self.device, fps=self.fps, m=self.mode, w=self.w, h=self.h, pf=self.format, fb=fb))
        #self.frame = Frame(self.device)
        self.frame = Camera(self.device)

    def Frame_UYVY2YCbCr_PIL(self, w, h, frame_data):
        data = np.fromstring(frame_data, dtype='uint8')
        y = Image.frombytes('L', (w, h), data[1::2].copy())
        u = Image.frombytes('L', (w, h), data[0::4].copy().repeat(2, 0))
        v = Image.frombytes('L', (w, h), data[2::4].copy().repeat(2, 0))
        return Image.merge('YCbCr', (y, u, v))

    def read_frame_dec(self):
        self.leds = self.read_frame()
        #TODO convert to 64 color palette, thus the remainder does not work
        data_b64 = ''.join(self.b64dict[m] for n in self.leds for m in n)
        data_dec = base64.b64decode(data_b64)

        return data_dec

    def read_frame(self):

        #get a frame from the device
        #frame_data = self.frame.get_frame()
        while True:
            frame_data = self.frame.get_frame()
            if len(frame_data) == self.w * self.h * self.b:
                break

        #img = self.Frame_UYVY2YCbCr_PIL(self.w, self.h, frame_data)
        img = Image.frombytes('RGB', (self.w, self.h), frame_data, 'raw', 'RGB')

        #cut the frame to game size (depending on game) ane transform it for the leds
        #img_game = self.game.extract_game_area(img).filter(ImageFilter.SMOOTH).convert("HSV")
        img_game = self.game.extract_game_area(img, ntsc=self.ntsc)
        img_leds = self.game.transform_frame(img_game)
        #img to array conversion
        self.leds = np.array(img_leds)

        #debug:
        #self.leds = img_leds
        #img_game.convert("RGB").save("nes_cut.png", "PNG")
        #img_leds.convert("RGB").save("leds.png", "PNG")

        return self.leds


    # for debug:
    def read_frame0(self):
        frame_data = self.frame.get_frame()
        return frame_data
    def read_frame1(self):
        #frame_data = self.frame.get_frame()
        while True:
            frame_data = self.frame.get_frame()
            if len(frame_data) == self.w * self.h * self.b:
                break
        else:
            print("debug - ", "frame not correct", "frame_data_len:",
                  len(frame_data))
        return frame_data
    def read_frame2(self, frame_data):
        #img = self.Frame_UYVY2YCbCr_PIL(self.w, self.h, frame_data)
        img = Image.frombytes('RGB', (self.w, self.h), frame_data, 'raw', 'RGB')
        return img
    def read_frame3(self, img):
        #img_game = self.game.extract_game_area(img).filter(ImageFilter.SMOOTH).convert("HSV")
        img_game = self.game.extract_game_area(img, ntsc=self.ntsc)
        return img_game
    def read_frame4(self, img_game):
        img_leds = self.game.transform_frame(img_game)
        self.leds = img_leds
        return self.leds
    # end for debug


#for debug
import time
import datetime
#import visdom
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

if __name__ == "__main__":
    iterations = 250
    is_visdom = False
    # command line:$ python3 -m visdom.server
    WAITTIME_VSTREAM = 1.0  #0.040  # 40 ms
    print("Start StreamNES...")
    stream = StreamNES(feedback=True)

    visd_server = 'http://localhost'
    if is_visdom:
        vis = visdom.Visdom(server=visd_server)

    print("Start reading frames...")
    for i in range(iterations):
        timestart = datetime.datetime.now()

        print("read frame...")

        #stream.read_frame()
        #print("...done")

        a = stream.read_frame1()
        print("...done1")
        timestart_a = datetime.datetime.now()
        b = stream.read_frame2(a)
        print("...done2")
        timestart_b = datetime.datetime.now()
        c = stream.read_frame3(b)
        print("...done3")
        timestart_c = datetime.datetime.now()
        d = stream.read_frame4(c)
        print("...done4")

        timefin = datetime.datetime.now()
        c.convert("RGB").save("nes_cut.png", "PNG")
        d.convert("RGB").save("leds.png", "PNG")
        if is_visdom:
            send_visdom(vis, c.convert('RGBA'), win='source')
            send_visdom(vis, d.resize((160,240)).convert('RGBA'), win='led-pixel-wall')

        waittime = max(0.0,(WAITTIME_VSTREAM)-(0.000001*(timefin-timestart).microseconds))

        time_a = timestart_a - timestart
        time_b = timestart_b - timestart_a
        time_c = timestart_c - timestart_b
        time_d = timefin - timestart_c
        time_total = time_a + time_b + time_c + time_d
        print("grab_t: {time_a}, conv_t: {time_b}, "
              "cut_t: {time_c}, smooth_trans_t: {time_d}, "
              "total_t: {time_total}, wait_t: {waittime} in ms".format(
                  time_a=time_a.microseconds / 1000,
                  time_b=time_b.microseconds / 1000,
                  time_c=time_c.microseconds / 1000,
                  time_d=time_d.microseconds / 1000,
                  time_total=time_total.microseconds / 1000,
                  waittime=waittime * 1000,
                ))

        time.sleep(waittime)



