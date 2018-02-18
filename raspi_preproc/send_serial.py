import serial
import time
import datetime
USBPORT = '/dev/ttyACM0' #check correct port first
NUM_LEDS_H = 12 #16
NUM_LEDS_V = 24 #24
FPS = 25

s = serial.Serial(USBPORT, 115200) #115200 230400
time.sleep(5)

leds = [[0 for i in range(NUM_LEDS_V)] for j in range(NUM_LEDS_H)]
counter = 0
delaycounter = 1
delay = 25

while True:
    timestart = datetime.datetime.now()
    
    for i in range(NUM_LEDS_H):
        for j in range(NUM_LEDS_V):
            leds[i][j] = 256/NUM_LEDS_V*((counter+i+j)%NUM_LEDS_V+1)-1
    if (delaycounter%delay == 0):    
        counter=(counter+1)%NUM_LEDS_V
    delaycounter=(delaycounter+1)%delay

    s.write("".join([chr(m) for n in leds for m in n]))
    s.flush()
    
    timefin = datetime.datetime.now()
    waittime = max(0.0,(1./FPS)-(0.000001*(timefin-timestart).microseconds))
    print(waittime, (timefin-timestart).microseconds)
    time.sleep(waittime)                        



