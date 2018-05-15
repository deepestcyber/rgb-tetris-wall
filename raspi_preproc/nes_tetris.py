from PIL import Image

class Nes_tetris:

    def __init__(self, _num_leds_h=16, _num_leds_v=24, _gray=64):
        self.num_h = _num_leds_h
        self.num_v = _num_leds_v
        self.gray = _gray
        self.img_leds = Image.new("RGB", (_num_leds_h, _num_leds_v), 0)

        # frame play area
        for y in range(2, 24):
            self.img_leds.putpixel((0, y), _gray)
            self.img_leds.putpixel((11, y), _gray)
        for x in range(0, 12):
            self.img_leds.putpixel((x, 2), _gray)
            self.img_leds.putpixel((x, 23), _gray)

        # frame next block area
        for x in range(12, 16):
            self.img_leds.putpixel((x, 10), _gray)
            self.img_leds.putpixel((x, 15), _gray)

        return


    def extract_single_player_area(im, area=None):
        if area is None:
            area = (95, 39, 95 + 2 + 10 * 8, 39 + 2 + 20 * 8)
        return im.crop(area)


    def extract_colours(self, img):
        #img.save("debug.png", "PNG")

        for y in range(20):
            for x in range(10):
                at = (1 + x * 8 + 3, 1 + y * 8 + 3)
                pix = img.getpixel(at)
                self.img_leds.putpixel((1 + x, 3 + y), pix)

        return


    def is_pix_not_black(self, pix):
        if (pix[0] or pix[1] or pix[2]) >= 10:
            return True
        return False


    def extract_next_block(self, img):
        #img.save("debug.png", "PNG")

        #read
        if self.is_pix_not_black(img.getpixel((2, 9))):
            next_block = 6
            next_block_col = img.getpixel((2, 9))
        elif self.is_pix_not_black(img.getpixel((6, 5))):
            if self.is_pix_not_black(img.getpixel((14, 13))):
                if self.is_pix_not_black(img.getpixel((22, 5))):
                    next_block = 0
                else:
                    next_block = 2
            else:
                if self.is_pix_not_black(img.getpixel((6, 13))):
                    next_block = 5
                else:
                    next_block = 1
            next_block_col = img.getpixel((6, 5))
        else:
            if self.is_pix_not_black(img.getpixel((22, 5))):
                next_block = 4
                next_block_col = img.getpixel((22, 5))
            else:
                next_block = 3
                next_block_col = img.getpixel((18, 5))

        #write
        if next_block == 0:
            for x in range(0, 3):
                self.img_leds.putpixel((12+x, 12), next_block_col)
            self.img_leds.putpixel((13, 13), next_block_col)
        elif next_block == 1:
            for x in range(0, 3):
                self.img_leds.putpixel((12+x, 12), next_block_col)
            self.img_leds.putpixel((14, 13), next_block_col)
        elif next_block == 2:
            for x in range(0, 2):
                self.img_leds.putpixel((12+x, 12), next_block_col)
                self.img_leds.putpixel((13+x, 13), next_block_col)
        elif next_block == 3:
            for x in range(0, 2):
                self.img_leds.putpixel((13+x, 12), next_block_col)
                self.img_leds.putpixel((13+x, 13), next_block_col)
        elif next_block == 4:
            for x in range(0, 2):
                self.img_leds.putpixel((13+x, 12), next_block_col)
                self.img_leds.putpixel((12+x, 13), next_block_col)
        elif next_block == 5:
            for x in range(0, 3):
                self.img_leds.putpixel((12+x, 12), next_block_col)
            self.img_leds.putpixel((12, 13), next_block_col)
        else:  #next_block == 6:
            for x in range(0, 4):
                self.img_leds.putpixel((12+x, 12), next_block_col)


    def transform_frame(self, img):
        # play area
        self.extract_colours(img.crop((95, 39, 96 + 10 * 8, 40 + 20 * 8)))

        # next block
        self.extract_next_block(img.crop((191, 111, 191 + 33, 111 + 17)))

        # score

        # number of lines

        # number of level

        return self.img_leds

#for debug
if __name__ == "__main__":
    im = Image.open("../streaming/nes2.png").convert("RGB")
    gray = im.getpixel((6,6))
    game = Nes_tetris(_gray=gray)
    leds = game.transform_frame(im)
    leds.save("leds.png", "PNG")

