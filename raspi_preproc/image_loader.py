import numpy as np
from os import listdir
from os.path import isfile, join
import random
from PIL import Image

_FORMAT = "RGB"

class ImageLoader:

    def __init__(self, _num_leds_h=16, _num_leds_v=24):
        self.num_leds_h = _num_leds_h
        self.num_leds_v = _num_leds_v
        self.leds = np.zeros((_num_leds_v, _num_leds_h, 3)) #should be not necessary

        self.black = (0, 0, 0)
        self.ipath = "../images"
        self.default_image_name = "black.png"
        self.image_name = self.default_image_name
        self.get_image_list()
        self.img_leds = Image.new(_FORMAT, (self.num_leds_h, self.num_leds_v), self.black)

        self.load_image(self.default_image_name)

    def get_image_list(self):
        self.image_list = [f for f in listdir(self.ipath) if isfile(join(self.ipath, f))]

        return

    def load_image(self, name):
        if any(name in n for n in self.image_list):
            self.img_leds = Image.open(self.ipath+"/"+name).\
                resize((self.num_leds_h, self.num_leds_v))

        self.leds = np.array(self.img_leds)
        return self.leds

    def load_random_image(self):
        self.image_name = self.image_list[random.randint(0, len(self.image_list)-1)]

        return self.load_image(self.image_name)

    def load_next_image(self):

        pos = self.image_list.index(self.image_name)
        self.image_name = self.image_list[(pos+1)%len(self.image_list)]

        return self.load_image(self.image_name)

    def load_prev_image(self):

        pos = self.image_list.index(self.image_name)
        self.image_name = self.image_list[(len(self.image_list)+pos-1)%len(self.image_list)]

        return self.load_image(self.image_name)

    def load_numbered_image(self, number):

        self.image_name = self.image_list[(number+len(self.image_list))%len(self.image_list)]

        return self.load_image(self.image_name)


#for debug:
if __name__ == "__main__":

    iload = ImageLoader()

    leds = iload.load_random_image()
    print(iload.ipath+"/"+iload.image_name)
    print("debug -", "leds:", leds.shape)
    Image.fromarray(leds).save("leds.png", "PNG")

    #img.convert("RGB").save("leds.png", "PNG")
