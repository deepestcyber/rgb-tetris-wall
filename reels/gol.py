import numpy as np
import time
from fluter import send_raw

w = 16
h = 24

glider = [[1, 0, 0],
          [0, 1, 1],
          [1, 1, 0]]

f = np.random.randint(2, size=(h, w), dtype=np.uint8)
f = np.zeros((h, w), dtype=np.uint8)
f[:3, :3] = glider

def neigh(f, pos):
    x, y = pos
    xa = (x - 1) % w
    xb = x
    xc = (x + 1) % w
    ya = (y - 1) % h
    yb = y
    yc = (y + 1) % h
    n = 0
    n += f[ya, xa] + f[ya, xb] + f[ya, xc]
    n += f[yb, xa] + 0 + f[yb, xc]
    n += f[yc, xa] + f[yc, xb] + f[yc, xc]
    return n


def next_gen(fin):
    fout = fin.copy()
    for y in range(h):
        for x in range(w):
            n = neigh(fin, (x, y))
            if fin[y, x]:
                fout[y, x] = 1 if 1 < n < 4 else 0
            else:
                fout[y, x] = 1 if n == 3 else 0
    return fout


def to_raw(fin):
    dead = b"\x00\x00\x80"
    live = b"\x00\xff\x00"
    d = []
    for y in range(h):
        for x in range(w):
            d += [live] if f[y, x] else [dead]
    return b"".join(d)


while True:
    send_raw(to_raw(f))
    f = next_gen(f)
    time.sleep(.2)

