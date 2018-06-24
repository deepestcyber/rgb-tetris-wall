import os
import base64
import numpy as np
from pyv4l2.frame import Frame
from nes_tetris import Nes_tetris

class Video_stream:

    def __init__(self, _num_leds_h=16, _num_leds_v=24):
        self.num_leds_h = _num_leds_h
        self.num_leds_v = _num_leds_v
        self.leds = [[0 for i in range(_num_leds_v)] for j in range(_num_leds_h)]
        self.b64dict = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        self.width = 720
        self.height = 576
        self.scale = 1.
        self.device = '/dev/video1'
        self.w = int(self.width // self.scale)
        self.h = int(self.height // self.scale)

        self.game = Nes_tetris()

        self.visdom_server = 'http://localhost'
        self.visdom = 'store_true'

        os.system(
        'v4l2-ctl -d {device} --set-fmt-video width={w},height={h}'.format(
            device=self.device, w=w, h=h))
        self.frame = Frame(self.device)

    def UYVY_RAW2RGB_PIL(data, w, h):
        y = Image.frombytes('L', (w, h), data[1::2].copy())
        u = Image.frombytes('L', (w, h),
                            data[0::4].reshape(w // 2, h).copy().repeat(2, 0))
        v = Image.frombytes('L', (w, h),
                            data[2::4].reshape(w // 2, h).copy().repeat(2, 0))
        return Image.merge('YCbCr', (y, u, v))

    def read_frame(self):

        #get a frame from the device
        frame_data = self.frame.get_frame()
        data = np.array(list(frame_data), dtype='uint8')
        img = self.UYVY_RAW2RGB_PIL(data, self.w, self.h)

        #cut the frame to nes size (256x224) ane transform it for the leds
        #rect = (270 / 720 * img.width, 152 / 576 * img.height,
        #        475 / 720 * img.width, 474 / 576 * img.height)
        rect = (41, 42, 642, 478)
        img_cut = self.game.extract_single_player_area(img, rect)
        img_leds = self.game.transform_frame(img_cut)
        self.leds = img_leds #TODO: img to array conversion

        return self.leds

    def read_frame_dec(self):
        self.leds = self.read_frame()
        data_b64 = ''.join(self.b64dict[m] for n in self.leds for m in n)
        data_dec = base64.b64decode(data_b64)

        return data_dec
