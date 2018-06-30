== Synopsis: ==


== Hardware: ==

- WS2811 5050 LED strips (60leds/m, 20ics/m)
- 12V power supply (HP 750W HSTNS-PL18), provides 62.5A/12V
- Arduino Mega
- Raspberry PI 3 B
- EasyCAP USB grabber with Syntek STK1160 chip set
- Microphone
- Switches, Buttons, Photo-resistor, 

Photo-resistor:
- Measures light for regulating the overall brightness of the leds
- Basic photo-resistor with voltage divider via 5k1ohm resistor for input pulldown

Microphone:
- Measures sound for simple beat detection that can get visualised
- Basic line-in microphone
- Microphone amplifier (with poti) Iduino SE019


== Software: ==

= Arduino: =
Purpose:

Libraries (C):
- https://playground.arduino.cc/Code/ElapsedMillis
- https://github.com/FastLED/FastLED

= Raspberry PI =
Purpose:

Libraries (python):
- pyserial