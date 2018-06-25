import os
import base64
import numpy as np
from pyv4l2.frame import Frame
from PIL import Image
from PIL import ImageFilter
from nes_tetris import NesTetris

class VideoStream:

    def __init__(self, _num_leds_h=16, _num_leds_v=24):
        self.num_leds_h = _num_leds_h
        self.num_leds_v = _num_leds_v
        self.leds = [[0 for i in range(_num_leds_v)] for j in range(_num_leds_h)]
        self.b64dict = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        self.mode = 'pal-B'
        self.width = 720
        self.height = 576
        self.format = 'UYVY'
        self.color = '' #''smpte170'

        self.scale = 1.
        self.device = '/dev/video2'
        self.w = int(self.width // self.scale)
        self.h = int(self.height // self.scale)

        self.game = NesTetris()

        self.visdom_server = 'http://localhost'
        self.visdom = 'store_true'

        os.system(
        'v4l2-ctl -d {device} -s {m} --set-fmt-video width={w},height={h},pixelformat={f},colorspace={c}'.format(
            device=self.device, m=self.mode, w=self.w, h=self.h, f=self.format, c=self.color))
        self.frame = Frame(self.device)

    def UYVY_RAW2RGB_PIL(self, data, w, h):
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
        #img_debug = Image.frombytes("UYVY", (self.w, self.h), frame_data)
        img = self.UYVY_RAW2RGB_PIL(data, self.w, self.h)

        #cut the frame to nes size (256x224) ane transform it for the leds
        #rect = (270 / 720 * img.width, 152 / 576 * img.height,
        #        475 / 720 * img.width, 474 / 576 * img.height)
        #rect = (41, 42, 642, 478)
        img_cut = self.game.extract_game_area(img)
        #debug:
        img_cut.convert("RGB").save("nes_cut.png", "PNG")
        img_leds = self.game.transform_frame(img_cut)
        self.leds = img_leds #TODO: img to array conversion

        #debug:
        img_leds.convert("RGB").save("leds.png", "PNG")

        return self.leds

    def read_frame_dec(self):
        self.leds = self.read_frame()
        data_b64 = ''.join(self.b64dict[m] for n in self.leds for m in n)
        data_dec = base64.b64decode(data_b64)

        return data_dec

#for debug

if __name__ == "__main__":
    stream = VideoStream()
    stream.read_frame()

    #img = Image.open("../streaming/nes.jpg").convert("HSV")
    #im = img.crop((41,42,642,478)).filter(ImageFilter.SMOOTH)
    #im.convert("RGB").save("nes_cut.png", "PNG")
    #game = NesTetris()



