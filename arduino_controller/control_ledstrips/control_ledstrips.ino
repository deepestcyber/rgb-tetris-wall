
#include "FastLED.h"

#define BUTTON_PIN_0 A0
#define BUTTON_PIN_1 A1
#define BUTTON_PIN_2 A2
#define BUTTON_PIN_3 A3
#define LEDS_PIN_0 2
#define LEDS_PIN_1 3
#define LEDS_PIN_2 4
#define LEDS_PIN_3 5
#define LEDS_PIN_4 6
#define LEDS_PIN_5 7
#define LEDS_PIN_6 8
#define LEDS_PIN_7 9
#define LEDS_PIN_8 10
#define LEDS_PIN_9 11
#define LEDS_PIN_10 12
#define LEDS_PIN_11 13
#define LEDS_PIN_12 14
#define LEDS_PIN_13 15
#define LEDS_PIN_14 18
#define LEDS_PIN_15 19
#define MODEL WS2812B //WS2811, WS2812b
#define NUM_LEDS_H 12 //16
#define NUM_LEDS_V 24 //24
#define NUM_BITS_VSTREAM 6
#define NUM_FPS_VSTREAM 50
#define WAITTIME_VSTREAM 20 //1000/NUM_FRAMES_VSTREAM
#define NUM_BYTES_VSTREAM 288 //NUM_LEDS_H*NUM_LEDS_V*NUM_BITS_VSTREAM/8;

CRGB leds[NUM_LEDS_H][NUM_LEDS_V];

//modes: 0 = light patterns, 1 = music patterns, 2 = image stream (24bit), 3 = video stream
int mode = 3;
//TODO: define a good color palette - perhaps like NES?
extern const CHSV currentPalette [64] = {CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216), CHSV(255,255,8), CHSV(255,255,24), CHSV(255,255,72), CHSV(255,255,216)};
//String data = "////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////";
//String data = "";

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200); //115200 230400

  FastLED.addLeds<MODEL, LEDS_PIN_0, RGB>(leds[0], NUM_LEDS_V);
  FastLED.addLeds<MODEL, LEDS_PIN_1, RGB>(leds[1], NUM_LEDS_V);
  FastLED.addLeds<MODEL, LEDS_PIN_2, RGB>(leds[2], NUM_LEDS_V);
  FastLED.addLeds<MODEL, LEDS_PIN_3, RGB>(leds[3], NUM_LEDS_V);
  FastLED.addLeds<MODEL, LEDS_PIN_4, RGB>(leds[4], NUM_LEDS_V);
  FastLED.addLeds<MODEL, LEDS_PIN_5, RGB>(leds[5], NUM_LEDS_V);
  FastLED.addLeds<MODEL, LEDS_PIN_6, RGB>(leds[6], NUM_LEDS_V);
  FastLED.addLeds<MODEL, LEDS_PIN_7, RGB>(leds[7], NUM_LEDS_V);
  FastLED.addLeds<MODEL, LEDS_PIN_8, RGB>(leds[8], NUM_LEDS_V);
  FastLED.addLeds<MODEL, LEDS_PIN_9, RGB>(leds[9], NUM_LEDS_V);
  FastLED.addLeds<MODEL, LEDS_PIN_10, RGB>(leds[10], NUM_LEDS_V);
  FastLED.addLeds<MODEL, LEDS_PIN_11, RGB>(leds[11], NUM_LEDS_V);
  //FastLED.addLeds<MODEL, LEDS_PIN_12, RGB>(leds[12], NUM_LEDS_V);
  //FastLED.addLeds<MODEL, LEDS_PIN_13, RGB>(leds[13], NUM_LEDS_V);
  //FastLED.addLeds<MODEL, LEDS_PIN_14, RGB>(leds[14], NUM_LEDS_V);
  //FastLED.addLeds<MODEL, LEDS_PIN_15, RGB>(leds[15], NUM_LEDS_V);

  //setPaletteNES();
}

void loop() {
  // put your main code here, to run repeatedly:

  //mode - video stream: 50fps a frames with 6 bit/px
  if (mode == 3){
    //String data = "////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////";
    char data[NUM_BYTES_VSTREAM];
    if (Serial.available()) {
      Serial.readBytes(data, NUM_BYTES_VSTREAM);
      //data = buf;//Convert.ToBase64String(buf);
    }
  
    for(int i=0; i<NUM_LEDS_H; i++){
      for(int j=0; j<NUM_LEDS_V; j++){ 
        //TODO: still need to convert to sixbits
        //leds[i][NUM_LEDS_V-1-j] = currentPalette[(int)data[i*NUM_LEDS_V+j]];
        leds[i][NUM_LEDS_V-1-j] = CHSV((int)data[i*NUM_LEDS_V+j], 255, 64);
      }
    }
  }
  //mode - image stream: one frames with 24 bit/px (at max every 80ms)
  else if (mode == 2){
    //TODO
  }
  //mode - sound activation (hardcoded) - shows pattern accourding to a microphon signal
  else if (mode == 1){
    //TODO
  }
  //mode - dynamic patterns (hardcoded) - perhaps via several sub-modes
  else { //mode == 0
  }

  FastLED.show();
  //delay(WAITTIME);    
}


