import datetime
import numpy as np
import pigpio
import time
from stream_nes import StreamNES
from image_loader import ImageLoader
from audio_beatdetection import AudioBeatdetection

DEBUG_MODE = True

if DEBUG_MODE:
    print("debug -", "raspberry PI preprocessing - start")

USBPORT = '/dev/ttyACM0'  # check correct port first
# USBPORT = 'COM3' #check correct port first
NUM_LEDS_H = 16  # 16
NUM_LEDS_V = 24  # 24
FPS = 25
POLL_GRACE_PERIOD = 0.1  # mainly for debug.
waittime_until_next_image = 3.0  # change the random image every 5 minutes
time_last_istream_change = datetime.datetime.now()

b64dict = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

# initialise SPI
pi = pigpio.pi()
if not pi.connected:
    print("could not connect SPI")
    exit()
spi = pi.spi_open(0, 57600, 0)

# initialise pin to arduino for flagging synchronisation
SYNC_PIN = 24  # GPIO pin numbers
pi.set_mode(SYNC_PIN, pigpio.INPUT)  # define pulldown/pullup

leds = np.zeros((NUM_LEDS_H, NUM_LEDS_V, 3), dtype='uint8')
mode = 0
submode = [0 for n in range(256)]

iloader = ImageLoader(_num_leds_h=NUM_LEDS_H, _num_leds_v=NUM_LEDS_V)
strmnes = StreamNES(_num_leds_h=NUM_LEDS_H, _num_leds_v=NUM_LEDS_V)
abeatd = AudioBeatdetection(_num_leds_h=NUM_LEDS_H, _num_leds_v=NUM_LEDS_V)


def send_SPI(data):
    if DEBUG_MODE:
        print("debug -", "sending bytes:", len(data))
    pi.spi_write(spi, data)
    #pi.spi_xfer(spi, data_dec)
    #spi.flush()


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

            # (num_bytes, data_read) = pi.spi_read(spi, 2)
            (num_bytes, data_read) = (2, b'\x03\x00')

            if DEBUG_MODE:
                print("debug -", "num_bytes:", num_bytes, "data_read:", data_read)


            # check if the mode was unchanged (on arduino)
            is_modes_changed = True
            if num_bytes == 2:
                new_mode = int.from_bytes(data_read[0:1], byteorder='little')
                new_submode = int.from_bytes(data_read[1:2], byteorder='little')
                if mode == new_mode and submode[mode] == new_submode:
                    is_modes_changed = False
                if DEBUG_MODE:
                    print("debug -", "change:", is_modes_changed, "new_mode:", new_mode, "new_submode:", new_submode)
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
                        print("debug -", "new image:", submode[2],
                              "last_image_t:", "{0:.2f}".format(round((now - time_last_istream_change).seconds * 1000 + (now - time_last_istream_change).microseconds / 1000, 2)),
                              "wait_next_image_t:", "{0:.2f}".format(
                                round(waittime_until_next_image * 1000, 2)),
                              "(ms)")
                    if submode[2] == 0:
                        leds = iloader.load_random_image()
                    else:
                        leds = iloader.load_numbered_image(submode[2])
                    leds = iloader.load_numbered_image(6)
                    time_last_istream_change = datetime.datetime.now()
                    if DEBUG_MODE:
                        print("debug -", "leds:", leds.shape)

                if DEBUG_MODE:
                    timesend = datetime.datetime.now()
                data_enc = leds.transpose(1, 0, 2).flatten().tobytes()
                send_SPI(data_enc)
            else:  #mode == 0  # no stream
                if DEBUG_MODE:
                    print("debug -", "Nothing to see here")
                pass


        timefin = datetime.datetime.now()
        waittime = max(0.0, (POLL_GRACE_PERIOD) - ((timefin - timestart).microseconds*0.000001))

        if DEBUG_MODE:

            if timeproc > timesend:
                handshake_delta_t = (timesend - timestart).microseconds/1000
                proc_delta_t = (timeproc - timesend).microseconds/1000
                send_delta_t = (timefin - timeproc).microseconds/1000
            else:
                handshake_delta_t = (timeproc - timestart).microseconds/1000
                proc_delta_t = (timesend - timeproc).microseconds/1000
                send_delta_t = (timefin - timesend).microseconds/1000

            print("debug -", "arduino mode:", mode, "submode:", submode[0],
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

pi.spi_close(spi)
pi.stop()

