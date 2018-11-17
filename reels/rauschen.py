"""
Rauschen reel.

Just some randomly changing gray values, to emulate random noise on a television.

Created by kratenko.
"""
import numpy as np
import time
from fluter import Fluter

fluter = Fluter()

while True:
    # great gray pixels
    f = np.random.randint(256, size=(fluter.height, fluter.width), dtype=np.uint8)
    # rescale to rgb
    f = np.stack((f,)*fluter.depth, axis=-1)
    fluter.send_array(f)
    time.sleep(.01)
