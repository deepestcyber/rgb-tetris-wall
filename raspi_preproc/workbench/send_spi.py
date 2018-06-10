import serial
import time
import datetime
import base64
import pigpio
import numpy as np

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
spi = pi.spi_open(0, 800000, 0)


counter = 0
delaycounter = 1
delay = 1 #FPS 1 for testing
data_read = 0

#gp = pigpio.pi()
SYNC_PIN = 18 # GPIO pin numbers
pi.set_mode(SYNC_PIN, pigpio.INPUT)

import PIL.Image
ref_img = PIL.Image.open('../mario.png').convert('RGB')
#ref_img = PIL.Image.open('d.png').convert('RGB')

for j in range(NUM_LEDS_V):
    for i in range(NUM_LEDS_H):
        px = ref_img.getpixel((i, j))
        print(1 if sum(px) > 0 else 0, end='')
    print('')

leds = np.zeros((NUM_LEDS_H, NUM_LEDS_V, 3), dtype='uint8')

cnt = 0
print("Start sending")
while True:
    timestart_proc = datetime.datetime.now()

    for x in range(NUM_LEDS_H):
        for y in range(NUM_LEDS_V):
            #leds[i][j] = 12
            #leds[i][j] = (4*(cnt-i+j))%64
            px = ref_img.getpixel((x, y))
            leds[x, NUM_LEDS_V - y - 1] = px
    if (delaycounter%delay == 0):
        counter=(counter+1)%NUM_LEDS_H
    delaycounter=(delaycounter+1)%delay

    data_dec = leds.transpose(1, 0, 2).flatten().tobytes()

    timestart_send = datetime.datetime.now()

    print("sending bytes:", len(data_dec))
    pi.spi_write(spi, data_dec)
    
    timestart_render = datetime.datetime.now()

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
    waittime = max(0.0,(WAITTIME_VSTREAM)-(0.000001*(timefin-timestart_proc).microseconds))
    
    time_proc = timestart_send - timestart_proc
    time_send = timestart_render - timestart_send
    time_render = timefin - timestart_render
    time_total = time_send + time_render + time_proc
    print("time_proc: {time_proc}, time_send: {time_send}, "
          "time_render: {time_render}, time_total: {time_total}, "
          "wait_t: {waittime}".format(
              time_proc=time_proc.microseconds / 1000,
              time_send=time_send.microseconds / 1000,
              time_render=time_render.microseconds / 1000,
              time_total=time_total.microseconds / 1000,
              waittime=waittime,
            ))

    time.sleep(waittime)                        

pi.spi_close(spi)
pi.stop()
