""""
Wireworld Reel

Implementation for Wireworld for our RGB-Wall

See https://en.wikipedia.org/wiki/Wireworld

TODO: multiple board layouts to chose from by program parm
TODO: set board layout by program parm

Created by kratenko
"""

import numpy as np
import time

from fluter import Fluter

fluter = Fluter()
W, H = 16, 24

EMPTY = 0
WIRE = 1
HEAD = 2
TAIL = 3

b_xor = """
..............x.
....x.....x...x.
...x.o...x.o..x.
...x.+...x.+..x.
...x.x...x.x..x.
...+.x...x.x..x.
...o.x...x.x..x.
...x.x...x.x..x.
...x.x...x.o..x.
...x.x...x.+..x.
....x.....x...x.
....x.....x...x.
....x.....x...x.
....x.....x...x.
....x.xxx.x...x.
.....xx.xx....x.
......x.x.....x.
......xxx.....x.
.......x......x.
.......x......x.
.......x......x.
.......x......x.
........xxxxxx..
................
"""


def build_field(s):
    f = np.zeros((H, W), dtype=np.uint8)
    y = -1
    for line in s.split("\n"):
        line = line.strip()
        if not line:
            continue
        y += 1
        if y >= H:
            break
        for x, c in enumerate(line):
            if x >= W:
                break
            t = EMPTY
            if c == "x":
                t = WIRE
            elif c == "+":
                t = HEAD
            elif c == "o":
                t = TAIL
            f[y, x] = t
    return f


def moore_neigh(pos):
    y, x = pos
    n = ((y - 1, x - 1), (y - 1, x), (y - 1, x + 1),
         (y, x - 1), (y, x + 1),
         (y + 1, x - 1), (y + 1, x), (y + 1, x + 1))
    n = tuple(pos for pos in n if 0 <= pos[1] < W and 0 <= pos[0] < H)
    return n


def count_neigh_heads(f, pos):
    n = moore_neigh(pos)
    s = 0
    for p in n:
        if f[p] == HEAD:
            s += 1
    return s


def step(f):
    o = f.copy()
    for y in range(0, H):
        for x in range(0, W):
            if f[y, x] == HEAD:
                o[y, x] = TAIL
            elif f[y, x] == TAIL:
                o[y, x] = WIRE
            elif f[y, x] == WIRE:
                if 1 <= count_neigh_heads(f, (y, x)) <= 2:
                    o[y, x] = HEAD
    return o


def send(f):
    empty = [0, 0, 0]
    wire = [0xff, 0xff, 0]
    head = [0, 0, 0xff]
    tail = [0xff, 0, 0]
    d = np.zeros((H, W, 3), dtype=np.uint8)
    d[f == EMPTY] = empty
    d[f == WIRE] = wire
    d[f == HEAD] = head
    d[f == TAIL] = tail
    fluter.send_array(d)


f = build_field(b_xor)

while True:
    send(f)
    f = step(f)
    time.sleep(.2)
