from PIL import Image
from PIL import ImageFilter

_FORMAT = "HSV"


class NesTetris:


    def __init__(self, _num_leds_h=16, _num_leds_v=24, _gray=(95, 7, 128)):
        self.num_h = _num_leds_h
        self.num_v = _num_leds_v
        self.gray = _gray
        self.black = (0, 0, 0)

        self.img_leds = Image.new(_FORMAT, (_num_leds_h, _num_leds_v), 0)

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
        # score/lines/level areas
        for x in range(12, 16):
            self.img_leds.putpixel((x, 2), _gray)
            self.img_leds.putpixel((x, 23), _gray)

        return


    def reset_areas(self):
        # play area
        for y in range(3, 23):
            for x in range(1, 11):
                self.img_leds.putpixel((x, y), self.black)
        # next block area
        for y in range(11, 15):
            for x in range(12, 16):
                self.img_leds.putpixel((x, y), self.black)
        # lines areas
        for y in range(3, 10):
            for x in range(12, 16):
                self.img_leds.putpixel((x, y), self.black)
        # level areas
        for y in range(16, 23):
            for x in range(12, 16):
                self.img_leds.putpixel((x, y), self.black)

        return


    def is_pix_white(self, pix):
        #if (pix[0] and pix[1] and pix[2]) >= 128: #RGB
        if (pix[2]) >= 128: #HSV
                return True
        return False


    def is_pix_not_black(self, pix):
        #if (pix[0] or pix[1] or pix[2]) >= 20: #RGB
        if (pix[2]) >= 48: #HSV
                return True
        return False


    def get_number(self, img):
        #img.convert("RGB").save("debug.png", "PNG")
        number = 0

        #read
        if not self.is_pix_white(img.getpixel((12, 4))):
            if self.is_pix_white(img.getpixel((2, 2))):
                if self.is_pix_white(img.getpixel((17, 2))):
                    number = 7
                else:
                    number = 5
            elif self.is_pix_white(img.getpixel((2, 8))):
                if self.is_pix_white(img.getpixel((17, 6))):
                    number = 8
                else:
                    number = 6
            else:
                if self.is_pix_white(img.getpixel((17, 14))):
                    number = 2
                else:
                    number = 9
        else:
            if self.is_pix_white(img.getpixel((12, 12))):
                if self.is_pix_white(img.getpixel((17, 14))):
                    number = 1
                else:
                    number = 4
            else:
                if self.is_pix_white(img.getpixel((17, 2))):
                    number = 3
                else:
                    number = 0

        #print("debug number:", str(number))

        return number


    def test_tetris_runnig(self, img):
        if self.is_pix_not_black(img.getpixel((54, 59))):
            return False
        if self.is_pix_not_black(img.getpixel((197, 142))):
            return False
        if self.is_pix_not_black(img.getpixel((484, 350))):
            return False
        if self.is_pix_not_black(img.getpixel((536, 101))):
            return False
        if not self.is_pix_white(img.getpixel((546, 321))):
            return False
        if not self.is_pix_white(img.getpixel((370, 53))):
            return False
        if not self.is_pix_white(img.getpixel((67, 154))):
            return False
        if not self.is_pix_white(img.getpixel((109, 387))):
            return False

        return True


    def extract_game_area(self, im, area=None):
        if area is None:
            area = (41, 42, 41 + 642, 42 + 478)
        return im.crop(area)


    def extract_colours(self, img):
        #img.convert("RGB").save("debug.png", "PNG")

        for y in range(20):
            for x in range(10):
                at = (1 + x * 20 + 10, 1 + y * 16 + 9)
                if self.is_pix_not_black(img.getpixel(at)):
                    pix = img.getpixel(at)
                else:
                    pix = self.black
                self.img_leds.putpixel((1 + x, 3 + y), pix)

        return


    def extract_next_block(self, img):
        img.convert("RGB").save("debug.png", "PNG")

        #read
        if self.is_pix_not_black(img.getpixel((5, 18))):
            next_block = 6
            next_block_col = img.getpixel((5, 18))
        elif self.is_pix_not_black(img.getpixel((15, 9))):
            if self.is_pix_not_black(img.getpixel((35, 26))):
                if self.is_pix_not_black(img.getpixel((55, 9))):
                    next_block = 0
                else:
                    next_block = 2
            else:
                if self.is_pix_not_black(img.getpixel((15, 26))):
                    next_block = 5
                else:
                    next_block = 1
            next_block_col = img.getpixel((15, 9))
        else:
            if self.is_pix_not_black(img.getpixel((60, 9))):
                next_block = 4
                next_block_col = img.getpixel((60, 9))
            else:
                next_block = 3
                next_block_col = img.getpixel((50, 9))

        #write
        for x in range(0, 4):
            self.img_leds.putpixel((12+x, 12), self.black)
            self.img_leds.putpixel((12+x, 13), self.black)
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


    def extract_score(self, img):
        #img.convert("RGB").save("debug.png", "PNG")
        #read
        score = 0 \
                + 100000 * self.get_number(img.crop((0, 0, 20, 16))) \
                + 10000 * self.get_number(img.crop((20, 0, 20 + 20, 16))) \
                + 1000 * self.get_number(img.crop((41, 0, 41 + 20, 16))) \
                + 100 * self.get_number(img.crop((61, 0, 61 + 20, 16))) \
                + 10 * self.get_number(img.crop((82, 0, 82 + 20, 16))) \
                + self.get_number(img.crop((102, 0, 102 + 20, 16)))

        #write
        for i in range(max(int(score/12500), 0), 32):
            self.img_leds.putpixel((0 + int(i/2), 0 + i%2), self.black)
        for i in range(min(int(score/12500), 32)):
            self.img_leds.putpixel((0 + int(i/2), 0 + i%2), (max(186-i*6, 0), 255, 128))

        #print("debug score", score)


    def extract_level(self, img):
        #img.convert("RGB").save("debug.png", "PNG")
        #read
        level = 0 \
                + 10 * self.get_number(img.crop((0, 0, 20, 16))) \
                + self.get_number(img.crop((20, 0, 40, 16)))
        #write
        for i in range(max(level, 0), 28):
            self.img_leds.putpixel((12 + int(i/7), 16 + i%7), self.black)
        for i in range(min(level+1,28)):
            self.img_leds.putpixel((12 + int(i/7), 16 + i%7), (max(180-i*6, 0), 255, 128))

        #print("debug level", level)


    def extract_lines(self, img):
        #img.convert("RGB").save("debug.png", "PNG")
        #read
        lines = 0 \
                + 100 * self.get_number(img.crop((0, 0, 20, 16))) \
                + 10 * self.get_number(img.crop((20, 0, 40, 16))) \
                + self.get_number(img.crop((41, 0, 61, 16)))
        #write
        for i in range(max(int(lines/10), 0), 28):
            self.img_leds.putpixel((12 + int(i/7), 3 + i%7), self.black)
        for i in range(min(int(lines/10)+1, 28)):
            self.img_leds.putpixel((12 + int(i/7), 3 + i%7), (max(180-i*6, 0), 255, 128))

        #print("debug lines", lines)


    def transform_frame(self, img):
        # check if game is running
        if not self.test_tetris_runnig(img):
            self.reset_areas()
            return self.img_leds

        # play area
        self.extract_colours(img.crop((239, 93, 240 + 10 * 20, 94 + 20 * 16)).filter(ImageFilter.SMOOTH))

        # next block
        self.extract_next_block(img.crop((482, 237, 482 + 81, 237 + 33)).filter(ImageFilter.SMOOTH))

        # number of lines
        self.extract_lines(img.crop((380, 45, 380 + 61, 45 + 16)).filter(ImageFilter.SMOOTH))

        # score
        self.extract_score(img.crop((481, 125, 481 + 122, 125 + 16)).filter(ImageFilter.SMOOTH))

        # number of level
        self.extract_level(img.crop((522, 333, 522 + 40, 333 + 16)).filter(ImageFilter.SMOOTH))

        return self.img_leds

#for debug
if __name__ == "__main__":
    im = Image.open("nes_cut.png").convert(_FORMAT)
    gray = im.getpixel((6,6))
    print("debug gray", gray)
    game = NesTetris(_gray=gray)
    leds = game.transform_frame(im).convert("RGB")
    leds.save("leds.png", "PNG")
    im.convert("RGB").save("debug1.png", "PNG")

