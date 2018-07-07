""" This is the terminal output:

debug - waiting for SPI pi.read_bank_1: 536921599
debug - requested mode received_data: 1 64 received_mode: 1 received_submode: 0
debug - change: True new_mode: 1 new_submode: 0 prev_mode: 0 prev_submode: 0
debug - new image: 0 last_image_t: 10002.64 wait_next_image_t: 500.00 (ms)
debug - leds: (24, 16, 3)
debug - sending bytes: 1152
debug - arduino mode: 1 submode: 0 handshake_t: 9880.26 process_t: 2.29 send_t: 20.56 wait_t: 0.00 (ms)
debug - waiting for SPI pi.read_bank_1: 536921599
debug - requested mode received_data: 1 0 received_mode: 0 received_submode: 0
debug - change: True new_mode: 0 new_submode: 0 prev_mode: 1 prev_submode: 0
debug - Nothing to see here
debug - arduino mode: 0 submode: 0 handshake_t: 56.98 process_t: 0.00 send_t: 0.26 wait_t: 42.76 (ms)
debug - waiting for SPI pi.read_bank_1: 536921599

"""

import datetime
import numpy as np
import pigpio
import time
import sys
from utils_ui import Logger
from stream_nes import StreamNES
from image_loader import ImageLoader
from audio_beatdetection import AudioBeatdetection

DEBUG_MODE = True

exptime = datetime.datetime.now()
log_out_file = "logs/log_" + exptime.strftime("%y%m%d%H%M") + ".txt"
sys.stdout = Logger(output_file=log_out_file)
is_first_loop = True

print("rgb-tetris-wall raspi reprocessing - start -", exptime.strftime("%y%m%d%H%M"))

if DEBUG_MODE:
    print("debug -", "raspberry PI preprocessing - start")

USBPORT = '/dev/ttyACM0'  # check correct port first
# USBPORT = 'COM3' #check correct port first
NUM_LEDS_H = 16  # 16
NUM_LEDS_V = 24  # 24
FPS = 25
POLL_GRACE_PERIOD = 0.001  # mainly for debug.
waittime_until_next_image = 30.0  # change the random image every 5 minutes
time_last_istream_change = datetime.datetime.now()

b64dict = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

# initialise SPI
pi = pigpio.pi()
if not pi.connected:
    print("could not connect SPI")
    exit()
spi = pi.spi_open(0, 500000, 0)  # 243750 487500 975000 1950000

# initialise pin to arduino for flagging synchronisation
SYNC_PIN = 24  # GPIO pin numbers
pi.set_mode(SYNC_PIN, pigpio.INPUT)  # define pulldown/pullup

leds = np.zeros((NUM_LEDS_H, NUM_LEDS_V, 3), dtype='uint8')
mode = 0
submode = [0 for n in range(256)]

iloader = ImageLoader(_num_leds_h=NUM_LEDS_H, _num_leds_v=NUM_LEDS_V)
strmnes = StreamNES(_num_leds_h=NUM_LEDS_H, _num_leds_v=NUM_LEDS_V)
abeatd = AudioBeatdetection(_num_leds_h=NUM_LEDS_H, _num_leds_v=NUM_LEDS_V)

time.sleep(0.4)  # some needed initial delay

def decodeByte2Mode(byte):
    # first two bits code the mode and remaining 6 bits code the submode
    return byte >> 6, byte & ~(3 << 6)

# def request_mode_SPI():
#     (num, byte) = pi.spi_xfer(spi, b'\x07')
#     if num == 1:
#         mode, submode = decodeByte2Mode(byte[0])
#         if DEBUG_MODE:
#             print("debug -", "requested mode", "received_data:", num, byte[0], "received_mode:", mode, "received_submode:", submode)
#         return (mode, submode)
#     return 0, 0

def read_mode_SPI():
    (num, byte) = pi.spi_read(spi, 1)
    if num == 1:
        mode, submode = decodeByte2Mode(byte[0])
        if DEBUG_MODE:
            print("debug -", "read mode", "received_data:", num, byte[0], "received_mode:", mode, "received_submode:", submode)
        return (mode, submode)

def send_SPI(data):
    if DEBUG_MODE:
        print("debug -", "sending bytes:", len(data))
    pi.spi_write(spi, data)

while True:
    try:
        timestart = datetime.datetime.now()
        if DEBUG_MODE:
            timeproc = timesend = timestart

        if DEBUG_MODE:
            print("debug -", "waiting for SPI", "pi.read_bank_1:", pi.read_bank_1())

        while ((pi.read_bank_1() >> SYNC_PIN) & 1) != 1:
            pass  # just wait, until the sync pin is set

        if ((pi.read_bank_1() >> SYNC_PIN) & 1) == 1:

            #(new_mode, new_submode) = request_mode_SPI()
            #time.sleep(0.001)
            (new_mode, new_submode) = read_mode_SPI()

            is_modes_changed = True
            if mode == new_mode and submode[mode] == new_submode:
                is_modes_changed = False
            if DEBUG_MODE:
                print("debug -", "change:", is_modes_changed, "new_mode:", new_mode, "new_submode:", new_submode, "prev_mode:", mode, "prev_submode:", submode[mode])
            else:
                if (is_first_loop):  #just for logging
                    is_first_loop = False
                    print("first read mode byte from arduino -", "new_mode:", new_mode, "new_submode:", new_submode)

            mode = new_mode
            submode[mode] = new_submode

            if (mode == 3):  #mode for stream from NES/video

                """ in the NES mode the new frame needs to get determined 
                    WHILE the arduino is writing the old frame to the leds
                    in order to parallelise these two expensive computations
                    and meet the speed requirements of max 40ms per frame """

                if DEBUG_MODE:
                    timesend = datetime.datetime.now()
                if not is_modes_changed:
                    # last turn the mode was the same, thus the calculated frame should be valid

                    data_enc = leds.transpose(1, 0, 2).flatten().tobytes()
                    #decode pixels from 24-bit into 6-bit (64-colour palette)
                    #data_b64 = ''.join(b64dict[m] for n in leds for m in n)
                    #data_dec = base64.b64decode(data_b64)
                    #print("debug -", "len(data_b64):", len(data_b64), "data_b64:", data_b64)
                    #print("debug -", "len(data_dec):", len(data_dec), "data_dec:", data_dec)
                    send_SPI(data_enc)

                # calculate new frame:
                if DEBUG_MODE:
                    timeproc = datetime.datetime.now()
                leds = strmnes.read_frame()
                if DEBUG_MODE:
                    print("debug -", "leds:", leds.shape)


            elif (mode == 2):  # mode for stream of beat-patterns

                if DEBUG_MODE:
                    timeproc = datetime.datetime.now()

                #TODO calculate LEDS
                leds = np.zeros((NUM_LEDS_H, NUM_LEDS_V, 3), dtype='uint8')

                if DEBUG_MODE:
                    timesend = datetime.datetime.now()
                data_enc = leds.transpose(1, 0, 2).flatten().tobytes()
                send_SPI(data_enc)


            elif (mode == 1):  # mode for stream of images
                if DEBUG_MODE:
                    timeproc = datetime.datetime.now()

                now = datetime.datetime.now()
                if is_modes_changed or ((now - time_last_istream_change).seconds + (now - time_last_istream_change).microseconds*0.000001 > waittime_until_next_image):
                    if DEBUG_MODE:
                        print("debug -", "new image:", submode[1],
                              "last_image_t:", "{0:.2f}".format(round((now - time_last_istream_change).seconds * 1000 + (now - time_last_istream_change).microseconds / 1000, 2)),
                              "wait_next_image_t:", "{0:.2f}".format(
                                round(waittime_until_next_image * 1000, 2)),
                              "(ms)")
                    if submode[1] == 0:
                        leds = iloader.load_random_image()
                    else:
                        leds = iloader.load_numbered_image(submode[1])
                    time_last_istream_change = datetime.datetime.now()

                if DEBUG_MODE:
                    print("debug -", "leds:", leds.shape)
                if DEBUG_MODE:
                    timesend = datetime.datetime.now()
                data_enc = leds.transpose(1, 0, 2).flatten().tobytes()
                send_SPI(data_enc)


            else:  #mode == 0  # no stream
                if DEBUG_MODE:
                    timeproc = datetime.datetime.now()
                if DEBUG_MODE:
                    print("debug -", "Nothing to see here")
                pass
                leds = np.zeros((NUM_LEDS_H, NUM_LEDS_V, 3), dtype='uint8')
                if DEBUG_MODE:
                    timesend = datetime.datetime.now()
                data_enc = leds.transpose(1, 0, 2).flatten().tobytes()
                send_SPI(data_enc)


        timefin = datetime.datetime.now()
        waittime = max(0.0, (POLL_GRACE_PERIOD) - ((timefin - timestart).microseconds*0.000001 + (timefin - timestart).seconds))

        if DEBUG_MODE:

            if timeproc > timesend:
                handshake_delta_t = (timesend - timestart).microseconds/1000 + (timesend - timestart).seconds*1000
                send_delta_t = (timeproc - timesend).microseconds/1000 + (timeproc - timesend).seconds*1000
                proc_delta_t = (timefin - timeproc).microseconds/1000 + (timefin - timeproc).seconds*1000
            else:
                handshake_delta_t = (timeproc - timestart).microseconds/1000 + (timeproc - timestart).seconds*1000
                proc_delta_t = (timesend - timeproc).microseconds/1000 + (timesend - timeproc).seconds*1000
                send_delta_t = (timefin - timesend).microseconds/1000 + (timefin - timesend).seconds*1000

            print("debug -", "arduino mode:", mode, "submode:", submode[mode],
                  "handshake_t:", "{0:.2f}".format(round(handshake_delta_t,2)),
                  "process_t:", "{0:.2f}".format(round(proc_delta_t,2)),
                  "send_t:", "{0:.2f}".format(round(send_delta_t,2)),
                  "wait_t:", "{0:.2f}".format(round(waittime*1000,2)),
                  "(ms)")

        time.sleep(waittime)
    except KeyboardInterrupt:
        break

if DEBUG_MODE:
    print("debug -", "raspberry PI preprocessing - closing")

time.sleep(0.2)
pi.spi_close(spi)
time.sleep(0.2)
pi.stop()

