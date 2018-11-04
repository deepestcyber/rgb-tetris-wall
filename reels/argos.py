"""
Argos reel for LED wall.

Just some harmless eyes, looking around.

TODO: check if colours look decent on wall.

Created by kratenko.
"""
import numpy as np
import time
import random

from fluter import Fluter


iris = """
                -
      aaaa      -
     aaaaaa     -
    aaaooaaa    -
    aaooooaa    -
    aaooooaa    -
    aaaooaaa    -
     aaaaaa     -
      aaaa      -
                -
                -
"""

ball = """
                -
                -
wwwwwwwwwwwwwwww-
wwwwwwwwwwwwwwww-
wwwwwwwwwwwwwwww-
wwwwwwwwwwwwwwww-
wwwwwwwwwwwwwwww-
wwwwwwwwwwwwwwww-
wwwwwwwwwwwwwwww-

"""

lid1 = """
................-
.....vxxxxv.....-
...vxx    xxv...-
.vxx        xxv.-
vx            xv-
x              x-
vx            xv-
.vx          xv.-
..vxx      xxv..-
....vxxxxxxv....-
................-
"""

lid2 = """
................-
.....vxxxxv.....-
...vxxyyyyxxv...-
.vxx xxxxxx xxv.-
vx            xv-
x              x-
vx            xv-
.vx          xv.-
..vxx      xxv..-
....vxxxxxxv....-
................-
"""

lid3 = """
................-
.....vxxxxv.....-
...vxxyyyyxxv...-
.vxxyyyyyyyyxxv.-
vx  xxyyyyxx  xv-
x     xxxx     x-
vx            xv-
.vx          xv.-
..vxx      xxv..-
....vxxxxxxv....-
................-
"""

lid4 = """
................-
.....vxxxxv.....-
...vxxyyyyxxv...-
.vxxyyyyyyyyxxv.-
vxyyyyyyyyyyyyxv-
x xxyyyyyyyxxx x-
vx  xxxxxxxx  xv-
.vx          xv.-
..vxx      xxv..-
....vxxxxxxv....-
................-
"""

lid5 = """
................-
.....vxxxxv.....-
...vxxyyyyxxv...-
.vxxyyyyyyyyxxv.-
vxyyyyyyyyyyyyxv-
xyyyyyyyyyyyyyyx-
vxyyyyyyyyyyyyxv-
.vxyyyyyyyyyyxv.-
..vxxyyyyyyxxv..-
....vxxxxxxv....-
................-
"""

lids = [lid1, lid1, lid1, lid4, lid5]

cmap = {
    ".": [0x00, 0x00, 0x00],
    "w": [0xd8, 0xd8, 0xd8],
    "X": [0x80, 0x80, 0x80],
    "x": [0xea//2, 0xc0//2, 0x86//2],
    "v": [0xea//6, 0xc0//6, 0x86//6],
    "y": [0xea, 0xc0, 0x86],
    "b": [0xff, 0xff, 0xff],
}

c2map = [
    # blue
    {
        "a": [0x00, 0x6d, 0xcc],
        "o": [0x02, 0x24, 0x3d],
    },
    # green
    {
        "a": [0x02, 0xbb, 0x39],
        "o": [0x01, 0x3d, 0x09]
    },
    # yellow
    {
        "a": [0xac, 0xbc, 0x01],
        "o": [0x3b, 0x3c, 0x00]
    },
    # red
    {
        "a": [0xb5, 0x51, 0x03],
        "o": [0x3c, 0x16, 0x01]
    }
]


def draw(a, s, trans=None, colour=0):
    if trans is None:
        trans = (0, 0)
    h, w, d = np.shape(a)
    y = -1
    for line in s.split("\n"):
        if not line:
            continue
        y += 1
        if y >= h:
            break
        _y = y + trans[0]
        if not 0 <= _y < h:
            continue
        for x, c in enumerate(line):
            if x >= w:
                break
            _x = x + trans[1]
            if not 0 <= _x < w:
                continue
            if c in cmap:
                a[_y, _x] = cmap[c]
            else:
                if 0 <= colour < len(c2map):
                    if c in c2map[colour]:
                        a[_y, _x] = c2map[colour][c]


class Eye:
    blinking = [1, 2, 3, 4, 4, 4, 4, 3, 2, 1]

    def __init__(self):
        self.direction = (0, 0)
        self.colour = 0
        self.lid_pos = 0
        self.action = None
        self.progress = None
        self.idle_time = None
        self.idle_next = None
        self.start_action("idle")

    def update(self):
        self.progress += 1
        if self.action == "close":
            if self.progress <= 4:
                self.lid_pos = self.progress
            else:
                self.start_action("closed")
        elif self.action == "closed":
            if self.progress > 2:
                self.change_colour()
                self.start_action("open")
        elif self.action == "open":
            if 1 <= self.progress <= 4:
                self.lid_pos = 4 - self.progress
            else:
                self.start_action("idle")
        elif self.action == "move":
            self.change_direction()
            self.start_action("idle")
        elif self.action == "idle":
            if self.progress >= self.idle_time:
                self.start_action(self.idle_next)

    def start_action(self, action):
        self.action = action
        self.progress = 0
        if action == "idle":
            self.idle_time = random.randint(30, 120)
            if random.randint(1, 10) == 1:
                self.idle_next = "close"
            else:
                self.idle_next = "move"

    def change_direction(self):
        self.direction = (random.randint(-2, 2), random.randint(-3, 3))

    def change_colour(self):
        if random.randint(1, 5) == 1:
            self.colour = random.randint(0, len(c2map) - 1)

    def draw(self):
        a = np.zeros((11, 16, 3), dtype=np.uint8)
        draw(a, ball)
        draw(a, iris, self.direction, colour=self.colour)
        draw(a, lids[self.lid_pos])
        return a


fluter = Fluter()

top_off = (0, 0)

a = np.zeros((24, 16, 3), dtype=np.uint8)
top = Eye()
bot = Eye()

while True:
    a[:11,:,:] = top.draw()
    a[13:24,:,:] = bot.draw()
    fluter.send_array(a)
    top.update()
    bot.update()
    time.sleep(.05)
