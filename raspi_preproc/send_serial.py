import serial
import time
import datetime
import base64
USBPORT = '/dev/ttyACM0' #check correct port first
NUM_LEDS_H = 16 #16
NUM_LEDS_V = 24 #24
FPS = 25

b64dict = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

s = serial.Serial(USBPORT, 115200) #57600 dc115200 230400
time.sleep(2)

leds = [[0 for i in range(NUM_LEDS_V)] for j in range(NUM_LEDS_H)]
counter = 0
delaycounter = 1
delay = FPS #1 for testing

print("Start sending")
while True:
    timestart = datetime.datetime.now()
    
    for i in range(NUM_LEDS_H):
        for j in range(NUM_LEDS_V):
            #leds[i][j] = (4*(counter+i+j))%64
            #leds[i][j] = 256//NUM_LEDS_V*((counter+i+j)%NUM_LEDS_V)
            leds[i][j] = 63
    if (delaycounter%delay == 0):
        counter=(counter+1)%NUM_LEDS_V
    delaycounter=(delaycounter+1)%delay
                             
    data_b64 = ''.join(b64dict[m] for n in leds for m in n)                      
    data_dec = base64.b64decode(data_b64)
    #print(len(data_b64),data_b64)
    #print(len(data_dec),data_dec)

    s.write(bytes([m for n in leds for m in n]))
    s.flush()
    
    timefin = datetime.datetime.now()
    waittime = max(0.0,(1./FPS)-(0.000001*(timefin-timestart).microseconds))
    print(waittime, 0.000001*(timefin-timestart).microseconds)
    time.sleep(waittime)                        



