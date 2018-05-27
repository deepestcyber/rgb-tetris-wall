# QnD extraction pixels from screenshot
from PIL import Image


def extract_single_player_area(im, area=None):
    if area is None:
        area = (96, 40, 96+10*8, 40+20*8)
    return im.crop(area)

def extract_square(im, coords):
    sx, sy = coords
    square = (sx*8, sy*8, (sx+1)*8, (sy+1)*8)
    return im.crop(square)

def extract_colours(area):
    a = area.crop((0, 0, 10, 20)).copy()
    for y in range(20):
        for x in range(10):
            at = (x*8 + 3, y*8 + 3)
            pix = area.getpixel(at)
            a.putpixel((x, y), pix)
    return a

if __name__ == "__main__":
    im = Image.open("img/Tetris (USA)-10.png")
    area = extract_single_player_area(im)
    extract_colours(area).resize((8*10, 8*20)).show()
