# upload the arduino sketch to the arduino using a standard usb port on the raspberry pi
/opt/arduino-1.8.5/arduino --port /dev/ttyACM0 --upload ~/rgb-tetris-wall/arduino_controller/control_ledstrips/control_ledstrips.ino --board arduino:avr:mega:cpu=atmega2560
