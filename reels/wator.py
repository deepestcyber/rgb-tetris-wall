"""
RGB Reel Wator Simulation

A reel implementing the Wator Simulation. Uses the energy based version for
the predators. When the simulation hits either final state it restarts.

TODO: configuration of parameters from outside (program args)
TODO: biased initialization
TODO: non-energy-based variant

See https://en.wikipedia.org/wiki/Wa-Tor

Created by kratenko
"""
import numpy as np
import random
import time
import math
import os
from PIL import Image

from fluter import Fluter

W, H = 16, 24

f = np.random.randint(-1, 2, size=(H, W), dtype=np.int16)

FISH_BREED = 3
FISH_ENERGY = 5
SHARK_STARVE = 2
SHARK_BREED = 10

fluter = Fluter()
img_skull = Image.open(os.path.join("img", "skull.png"))
img_fish = Image.open(os.path.join("img", "cheep-cheep-blue.png"))


def send(f):
    water = [0, 0, 0]
    fish = [0, 0, 0xff]
    shark = [0, 0xff, 0]
    d = np.zeros((H, W, 3), dtype=np.uint8)
    d[f<0] = shark
    d[f==0] = water
    d[f>0] = fish
    fluter.send_array(d)


def get_neigh(y, x):
    # no diagonal:
    return [((y - 1) % H, x), (y, (x + 1) % W), ((y + 1) % H, x), (y, (x - 1) % W)]


def dest_condition(f, y, x, condition):
    neigh = get_neigh(y, x)
    if condition == 0:
        conditioned = [a for a in neigh if f[a] == 0]
    elif condition == 1:
        conditioned = [a for a in neigh if f[a] > 0]
    else:
        conditioned = []
    if conditioned:
        return random.choice(conditioned)
    else:
        return None


def move_fish(f):
    moved = np.zeros((H, W), dtype=bool)
    for y in range(H):
        for x in range(W):
            if f[y, x] > 0:
                # fish
                if not moved[y, x]:
                    dest = dest_condition(f, y, x, 0)
                    if dest:
                        val = f[y, x] + 1
                        if val >= FISH_BREED:
                            f[dest] = 1
                            f[y, x] = 1
                        else:
                            f[dest] = val
                            f[y, x] = 0
                        moved[dest] = True
                    else:
                        f[y, x] = min(f[y, x] + 1, FISH_BREED)
                        moved[y, x] = True


def move_shark(f):
    moved = np.zeros((H, W), dtype=bool)
    for y in range(H):
        for x in range(W):
            if f[y, x] < 0:
                # shark
                if not moved[y, x]:
                    dest = dest_condition(f, y, x, 1)
                    if dest:
                        # find fish
                        f[dest] = f[y, x] - FISH_ENERGY
                        if f[dest] < -SHARK_BREED:
                            # breed new shark
                            val = f[dest]
                            f[dest] = math.floor(val/2)
                            f[y, x] = math.ceil(val/2)
                            moved[dest] = True
                            moved[y, x] = True
                        else:
                            f[y, x] = 0
                            moved[dest] = True
                    elif f[y, x] <= 1:
                        # starved to death:
                        f[y, x] = 0
                    else:
                        # no fish, just move
                        dest = dest_condition(f, y, x, 0)
                        if dest:
                            f[dest] = f[y, x] - 1
                            f[y, x] = 0
                            moved[dest] = True
                        else:
                            f[y, x] -= 1
                            moved[y, x] = True


def step(f):
    move_fish(f)
    move_shark(f)


fields = W * H
runs = 1
steps = 0

def redo():
    global f, steps, runs
    steps = 0
    runs += 1
    f = np.random.randint(-1, 2, size=(H, W), dtype=np.int16)


while True:
    fish = np.sum(f>0)
    sharks = np.sum(f<0)
    print("Run %d, Step %d -- Fish: %d, Sharks: %d" % (runs, steps, fish, sharks))
    send(f)
    # eval
    if fish == 0 and sharks == 0:
        fluter.send_image(img_skull)
        time.sleep(2)
        redo()
        continue
    elif fish == fields:
        fluter.send_image(img_fish)
        time.sleep(2)
        redo()
        continue
    step(f)
    steps += 1
    time.sleep(.2)
