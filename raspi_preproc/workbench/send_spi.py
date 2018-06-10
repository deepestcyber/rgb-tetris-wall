import serial
import time
import datetime
import base64
import pigpio

USBPORT = '/dev/ttyACM0' #check correct port first
#USBPORT = 'COM3' #check correct port first
NUM_LEDS_H = 16 #16
NUM_LEDS_V = 24 #24
FPS = 25
WAITTIME_VSTREAM = 0.040 #40 ms
WAITTIME_ISTREAM = 1.0 #40 ms

b64dict = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

#s = serial.Serial(USBPORT, 115200) #57600 dc115200 230400
pi = pigpio.pi()
if not pi.connected:
    print("could not connect spi")
    exit()

#spi = pi.spi_open(0, 115200)
spi = pi.spi_open(0, 320000, 0)

leds = [[0 for i in range(NUM_LEDS_V)] for j in range(NUM_LEDS_H)]
counter = 0
delaycounter = 1
delay = 1 #FPS 1 for testing
data_read = 0

wait_buffer = bytes([n for n in range(20)])

#gp = pigpio.pi()
SYNC_PIN = 18 # GPIO pin numbers
pi.set_mode(SYNC_PIN, pigpio.INPUT)
#pi.set_pull_up_down(SYNC_PIN, pigpio.PUD_DOWN)

import PIL.Image
ref_img = PIL.Image.open('d.png').convert('RGB')

cnt = 0
print("Start sending")
while True:
    timestart = datetime.datetime.now()

    for i in range(NUM_LEDS_H):
        for j in range(NUM_LEDS_V):
            #leds[i][j] = 12
            leds[i][j] = (4*(cnt-i+j))%64
            #px = ref_img.getpixel((i, j))
            #leds[i][j] = 3 if sum(px) > 0 else 55
    if (delaycounter%delay == 0):
        counter=(counter+1)%NUM_LEDS_H
    delaycounter=(delaycounter+1)%delay

    #data_b64 = ''.join(b64dict[m] for n in leds for m in n)
    #data_dec = base64.b64decode(data_b64)
    data_dec = bytes([m for n in leds for m in n])

    print("sending bytes:", len(data_dec))

    pi.spi_write(spi, data_dec)

    wait = True

    while wait:
        v = (pi.read_bank_1() >> SYNC_PIN) & 1
        if v == 1:
            wait = False
        else:
            #print(cnt, "wait for sync", v)
            pass

    cnt += 1
    timefin = datetime.datetime.now()
    waittime = max(0.0,(WAITTIME_VSTREAM)-(0.000001*(timefin-timestart).microseconds))
    print("arduino_mode:",data_read,"process_t:", 0.000001*(timefin-timestart).microseconds, "wait_t:", waittime)

    time.sleep(waittime)                        

pi.spi_close(spi)
pi.stop()
