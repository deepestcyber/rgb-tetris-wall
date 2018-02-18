import serial
import time
USBPORT = '/DEV/TTYama0' #check correct port first

s = serial.Serial(USBPORT, 115200)
s.open()
time.sleep(5)

