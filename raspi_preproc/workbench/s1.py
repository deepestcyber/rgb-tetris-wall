import time
import pigpio

pi = pigpio.pi()

if not pi.connected:
    print("nope")
    exit(0)

h = pi.spi_open(0, 1152000)


n = 0

try:
    while True:
        n += 1
        s = "n:%04x\n" % n
        pi.spi_xfer(h, s)
        print(s)
        #time.sleep(0.01)
except KeyboardInterrupt:
    print("Byebye")

pi.spi_close(h)
pi.stop()


