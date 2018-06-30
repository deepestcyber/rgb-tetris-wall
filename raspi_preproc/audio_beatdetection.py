import datetime
import numpy as np


class AudioBeatdetection:

    def __init__(self, _num_leds_h=16, _num_leds_v=24):
        self.num_leds_h = _num_leds_h
        self.num_leds_v = _num_leds_v
        self.leds = np.zeros((_num_leds_v, _num_leds_h, 3))

        self.last_measurement = datetime.datetime.now()

    #TODO

    def generate_frame(self, pattern=0):

        # TODO trigger the measurements for beat detection

        # TODO trigger some neat visualisations (based on pattern arg)

        return self.leds

