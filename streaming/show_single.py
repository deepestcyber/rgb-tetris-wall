import numpy as np
import matplotlib.pyplot as plt

from encoding import UYVY_RAW2RGB_PIL

with open('test.raw', 'rb') as f:
    data = np.array(list(f.read()), dtype='uint8')

img = UYVY_RAW2RGB_PIL(data, 720, 576)
img.show()

#frame = data[1::2].reshape(720, 576)

#plt.imshow(frame)
#plt.show()
