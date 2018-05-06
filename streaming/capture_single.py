from pyv4l2.frame import Frame
from pyv4l2.control import Control

frame = Frame('/dev/video1')
frame_data = frame.get_frame()
control = Control("/dev/video1")
#control.get_controls()
#control.get_control_value(9963776)
#control.set_control_value(9963776, 8)

with open('test.raw', 'wb') as f:
    f.write(frame_data)
