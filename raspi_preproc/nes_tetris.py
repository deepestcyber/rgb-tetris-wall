from PIL import Image

class Nes_tetris:

    def __init__(self, _num_leds_h=16, _num_leds_v=24, _gray=64):
        self.num_h = _num_leds_h
        self.num_v = _num_leds_v
        self.gray = _gray
        self.img_leds = Image.new(0, (_num_leds_h, _num_leds_v), 0)

        # frame play area
        for y in range(0, 22):
            self.img_leds.putpixel((0, y), _gray)
            self.img_leds.putpixel((11, y), _gray)
        for x in range(0, 12):
            self.img_leds.putpixel((x, 0), _gray)
            self.img_leds.putpixel((x, 21), _gray)

        # frame next block area
        for x in range(12, 16):
            self.img_leds.putpixel((x, 8), _gray)
            self.img_leds.putpixel((x, 13), _gray)

        return


    def extract_single_player_area(im, area=None):
        if area is None:
            area = (96, 40, 96 + 10 * 8, 40 + 20 * 8)
        return im.crop(area)


    def extract_colours(self, img):
        for y in range(20):
            for x in range(10):
                at = (96 + x * 8 + 3, 40 + y * 8 + 3)
                pix = img.getpixel(at)
                self.img_leds.putpixel((x, y), pix)
        return


    def is_pix_not_black(pix):
        if pix == 10:
            return True
        return False


    def extract_next_block(self, img):
        next_block = 0 #
        next_block_col = 0 #

        #read
        #TODO
        if self.is_pix_not_black(img.getpixel((0,9))):
            next_block = 6
        elif self.is_pix_not_black(img.getpixel((5,13))):
            next_block = -1
        else:
            if self.is_pix_not_black(img.getpixel((24,13))):
                next_block = 4
            else:
                next_block = 3

        #write
        if next_block == 0:
            for x in range(0, 3):
                self.img_leds.putpixel((12+x, 11), next_block_col)
            self.img_leds.putpixel((13, 12), next_block_col)
        elif next_block == 1:
            for x in range(0, 3):
                self.img_leds.putpixel((12+x, 11), next_block_col)
            self.img_leds.putpixel((14, 11), next_block_col)
        elif next_block == 2:
            for x in range(0, 2):
                self.img_leds.putpixel((12+x, 11), next_block_col)
                self.img_leds.putpixel((13+x, 11), next_block_col)
        elif next_block == 3:
            for x in range(0, 2):
                self.img_leds.putpixel((13+x, 11), next_block_col)
                self.img_leds.putpixel((13+x, 11), next_block_col)
        elif next_block == 4:
            for x in range(0, 2):
                self.img_leds.putpixel((13+x, 11), next_block_col)
                self.img_leds.putpixel((12+x, 11), next_block_col)
        elif next_block == 5:
            for x in range(0, 3):
                self.img_leds.putpixel((12+x, 11), next_block_col)
            self.img_leds.putpixel((12, 11), next_block_col)
        else:  #next_block == 6:
            for x in range(0, 4):
                self.img_leds.putpixel((12+x, 11), next_block_col)


    def transform_frame(self, img):
        # play area
        self.extract_colours(img)
        # next block

        # score

        # number of lines

        return self.img_leds
