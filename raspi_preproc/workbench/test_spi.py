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
spi = pi.spi_open(0, 64000//2)

leds = [[0 for i in range(NUM_LEDS_V)] for j in range(NUM_LEDS_H)]
counter = 0
delaycounter = 1
delay = 1 #FPS 1 for testing
data_read = 0

print("Start sending")
cnt = 0
while True:
    timestart = datetime.datetime.now()

    #data_read = s.read(1)
    (num_bytes, data_read) = pi.spi_read(spi, 1)
    #(num_bytes, data_read) = (0,1)
    #data_read = int(data_read)
    # mode - video stream: 25 frames per second with 6 bit/px
    if (True or data_read==b'3'):
        for i in range(NUM_LEDS_H):
            for j in range(NUM_LEDS_V):
                #leds[i][j] = (4*(counter-i+j))%64
                #leds[i][j] = (4*(counter-i+j))%64
                #leds[i][j] = 256//NUM_LEDS_V*((counter+i+j)%NUM_LEDS_V)
                leds[i][j] = 1
        if (delaycounter%delay == 0):
            counter=(counter+1)%NUM_LEDS_H
        delaycounter=(delaycounter+1)%delay

        data_b64 = ''.join(b64dict[m] for n in leds for m in n)
        data_dec = base64.b64decode(data_b64)
        #print(len(data_b64),data_b64)
        #print(len(data_dec),data_dec)

        
        #pi.spi_write(spi, data_dec+b'\n')
        cnt+=1
        pi.spi_write(spi, bytes('Take this: %d\n\n' % cnt, encoding="utf-8"))
        print("CNT:", cnt)
        #pi.spi_xfer(spi, data_dec)
        #s.write(bytes([m for n in leds for m in n])) #undecoded format
        #spi.flush()

    timefin = datetime.datetime.now()
    waittime = max(0.0,(WAITTIME_VSTREAM)-(0.000001*(timefin-timestart).microseconds))
    print("arduino_mode:",data_read,"process_t:", 0.000001*(timefin-timestart).microseconds, "wait_t:", waittime)

    time.sleep(waittime)                        

pi.spi_close(spi)
pi.stop()
