
//Designed for Arduino Mega

#include "FastLED.h"
#include "elapsedMillis.h"

#define DEBUG_MODE 0

#define LEDS_PIN_0 A0
#define LEDS_PIN_1 A1
#define LEDS_PIN_2 2
#define LEDS_PIN_3 3
#define LEDS_PIN_4 4
#define LEDS_PIN_5 5
#define LEDS_PIN_6 6
#define LEDS_PIN_7 7
#define LEDS_PIN_8 8
#define LEDS_PIN_9 9
#define LEDS_PIN_10 10
#define LEDS_PIN_11 11
#define LEDS_PIN_12 12
#define LEDS_PIN_13 13
#define LEDS_PIN_14 20
#define LEDS_PIN_15 21
#define FEEDBACK_PIN_1 17
#define FEEDBACK_PIN_2 16
#define BUTTON_PIN_0 A7 //Mode switch
#define BUTTON_PIN_1 A8 //Decrement submode
#define BUTTON_PIN_2 A9 //Increment submode
#define BUTTON_PIN_3 A10 //Decrement pattern speed
#define BUTTON_PIN_4 A11 //Increment pattern speed
#define BUTTON_PIN_5 A12 //Decrement brightness
#define BUTTON_PIN_6 A13 //Increment brightness
#define POTI_PIN_0 A5 //just for testing
#define MODEL WS2812B //WS2811, WS2812b
#define NUM_LEDS_H 16 //16
#define NUM_LEDS_V 24 //24
#define NUM_BUTTONS 7 //7
#define BUTTON_WAIT 50 //time (ms) to wait for another buttoncheck
#define NUM_POTI 1 //just for testing
#define NUM_BITS_VSTREAM 6 //6
#define NUM_FPS_VSTREAM 50
#define WAITTIME_VSTREAM 40 //20 1000/NUM_FRAMES_VSTREAM
#define WAITTIME_ISTREAM 2000 //20 1000/NUM_FRAMES_VSTREAM
#define NUM_BYTES_VSTREAM 288 //288 //NUM_LEDS_H*NUM_LEDS_V*NUM_BITS_VSTREAM/8;

CRGB leds[NUM_LEDS_H][NUM_LEDS_V];

//modes: 0 = light patterns, 1 = music patterns, 2 = image stream (24bit), 3 = video stream
int mode = 3;
int submode [4] = {0, 0, 0, 0};
int submodeMax [4] = {128, 1, 1, 1}; //Used for all mode switches

int buttonState [NUM_BUTTONS];         // current state of the button
int lastButtonState [NUM_BUTTONS];     // previous state of the button
elapsedMillis elapsedTime;
int waitingTime = 0;

int pspeed = 2; //[0..4]
int cspeed = 255;
int brightness = 2; //[0..4]
const int valueb [5][4] = {{3, 9, 27, 81}, {4, 12, 36, 108}, {5, 15, 45, 135}, {7, 21, 63, 189}, {9, 27, 81, 243}};
int state = 0;

//TODO: define a good color palette - perhaps like NES?
extern const CHSV currentPalette [64] = {CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216)};

byte data[NUM_BYTES_VSTREAM];
//uint8_t data[NUM_BYTES_VSTREAM];
//uint8_t dataImage[NUM_LEDS_H*NUM_LEDS_V*3];

void setup() {
  for (int i = 0; i < NUM_BUTTONS; i++) {
    buttonState[i] = 0;
    lastButtonState[i] = 0;
  }
  pinMode(BUTTON_PIN_0, INPUT_PULLUP);
  pinMode(BUTTON_PIN_1, INPUT_PULLUP);
  pinMode(BUTTON_PIN_2, INPUT_PULLUP);
  pinMode(BUTTON_PIN_3, INPUT_PULLUP);
  pinMode(BUTTON_PIN_4, INPUT_PULLUP);
  pinMode(BUTTON_PIN_5, INPUT_PULLUP);
  pinMode(BUTTON_PIN_6, INPUT_PULLUP);

  Serial.begin(115200); //57600 115200 230400
  Serial.setTimeout(WAITTIME_VSTREAM); //ms 40 1000

  if (NUM_LEDS_H > 0) FastLED.addLeds<MODEL, LEDS_PIN_0, GRB>(leds[0], NUM_LEDS_V);
  if (NUM_LEDS_H > 1) FastLED.addLeds<MODEL, LEDS_PIN_1, GRB>(leds[1], NUM_LEDS_V);
  if (NUM_LEDS_H > 2) FastLED.addLeds<MODEL, LEDS_PIN_2, GRB>(leds[2], NUM_LEDS_V);
  if (NUM_LEDS_H > 3) FastLED.addLeds<MODEL, LEDS_PIN_3, GRB>(leds[3], NUM_LEDS_V);
  if (NUM_LEDS_H > 4) FastLED.addLeds<MODEL, LEDS_PIN_4, GRB>(leds[4], NUM_LEDS_V);
  if (NUM_LEDS_H > 5) FastLED.addLeds<MODEL, LEDS_PIN_5, GRB>(leds[5], NUM_LEDS_V);
  if (NUM_LEDS_H > 6) FastLED.addLeds<MODEL, LEDS_PIN_6, GRB>(leds[6], NUM_LEDS_V);
  if (NUM_LEDS_H > 7) FastLED.addLeds<MODEL, LEDS_PIN_7, GRB>(leds[7], NUM_LEDS_V);
  if (NUM_LEDS_H > 8) FastLED.addLeds<MODEL, LEDS_PIN_8, GRB>(leds[8], NUM_LEDS_V);
  if (NUM_LEDS_H > 9) FastLED.addLeds<MODEL, LEDS_PIN_9, GRB>(leds[9], NUM_LEDS_V);
  if (NUM_LEDS_H > 10) FastLED.addLeds<MODEL, LEDS_PIN_10, GRB>(leds[10], NUM_LEDS_V);
  if (NUM_LEDS_H > 11) FastLED.addLeds<MODEL, LEDS_PIN_11, GRB>(leds[11], NUM_LEDS_V);
  if (NUM_LEDS_H > 12) FastLED.addLeds<MODEL, LEDS_PIN_12, GRB>(leds[12], NUM_LEDS_V);
  if (NUM_LEDS_H > 13) FastLED.addLeds<MODEL, LEDS_PIN_13, GRB>(leds[13], NUM_LEDS_V);
  if (NUM_LEDS_H > 14) FastLED.addLeds<MODEL, LEDS_PIN_14, GRB>(leds[14], NUM_LEDS_V);
  if (NUM_LEDS_H > 15) FastLED.addLeds<MODEL, LEDS_PIN_15, GRB>(leds[15], NUM_LEDS_V);

  for (int i = 0; i < NUM_BYTES_VSTREAM; i++) {
    data[i] = 0;
  }
  //setPaletteNES();
}

void checkPoti() {
  cspeed = analogRead(POTI_PIN_0);
}

void checkButtons() {

  // compare the buttonState to its previous state
  for (int i = 0; i < NUM_BUTTONS; i++) {
    if (i == 0) buttonState[i] = digitalRead(BUTTON_PIN_0);
    else if (i == 1) buttonState[i] = digitalRead(BUTTON_PIN_1);
    else if (i == 2) buttonState[i] = digitalRead(BUTTON_PIN_2);
    else if (i == 3) buttonState[i] = digitalRead(BUTTON_PIN_3);
    else if (i == 4) buttonState[i] = digitalRead(BUTTON_PIN_4);
    else if (i == 5) buttonState[i] = digitalRead(BUTTON_PIN_5);
    else if (i == 6) buttonState[i] = digitalRead(BUTTON_PIN_6);

    if (buttonState[i] != lastButtonState[i]) {
      // if the state has changed, increment the counter
      if (buttonState[i] == LOW) {
        // if the current state is LOW then the button went from off to on:
        if (i == 0) mode = (mode + 1) % 4;
        else if (i == 1) submode[mode] = (submode[mode] - 1) % submodeMax[mode];
        else if (i == 2) submode[mode] = (submode[mode] + 1) % submodeMax[mode];
        else if (i == 3) pspeed = min(pspeed + 1, 4);
        else if (i == 4) pspeed = max(pspeed - 1, 0);
        else if (i == 5) brightness = max(brightness - 1, 0);
        else if (i == 6) brightness = min(brightness + 1, 4);
      } else {
        // if the current state is HIGH then the button went from on to off:
      }
      lastButtonState[i] = buttonState[i];
      // Delay a little bit to avoid bouncing
    }
  }
}

void timedDelay(int waitingTime) {
  checkButtons();
  while ((waitingTime - (int)elapsedTime) > BUTTON_WAIT) {
    delay(BUTTON_WAIT);
    checkButtons();
  }
  delay(max(waitingTime - (int)elapsedTime, 0));
  waitingTime = 0; //for safety - TODO remove
}

void loop() {
  //checkButtons();
  //checkPoti();
  elapsedTime = 0;

  //mode - video stream: 25 frames per second with 6 bit/px
  if (mode == 3) {
    //if (Serial.available()) {
    //    int got = Serial.readBytes(data, NUM_BYTES_VSTREAM);
    //    if ( got == NUM_BYTES_VSTREAM ) {
    //      digitalWrite(FEEDBACK_PIN_1, LOW);
    //      digitalWrite(FEEDBACK_PIN_2, HIGH);
    //    } else {
    //      digitalWrite(FEEDBACK_PIN_1, HIGH);
    //      digitalWrite(FEEDBACK_PIN_2, LOW);
    //    }
    //}
    //Serial.readBytes(data, NUM_BYTES_VSTREAM);
    Serial.print("3");
    if (Serial.readBytes(data, NUM_BYTES_VSTREAM) == NUM_BYTES_VSTREAM) {
      int k = 0;
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j += 4) {
          leds[i][NUM_LEDS_V - 1 - j - 0] = CHSV((uint8_t)(data[k] >> 2) * 4, 255, valueb[brightness][3]);
          leds[i][NUM_LEDS_V - 1 - j - 1] = CHSV((uint8_t)(((data[k] & 0x03) << 4) | (data[k + 1] >> 4)) * 4, 255, valueb[brightness][3]);
          leds[i][NUM_LEDS_V - 1 - j - 2] = CHSV((uint8_t)(((data[k + 1] & 0x0f) << 2) | (data[k + 2] >> 6)) * 4, 255, valueb[brightness][3]);
          leds[i][NUM_LEDS_V - 1 - j - 3] = CHSV((uint8_t)(data[k + 2] & 0x3f) * 4, 255, valueb[brightness][3]);
          //leds[i][NUM_LEDS_V - 1 - j - 0] = currentPalette[data[k] >> 2]
          //leds[i][NUM_LEDS_V - 1 - j - 1] = currentPalette[((data[k] & 0x03) << 4) | (data[k + 1] >> 4)]
          //leds[i][NUM_LEDS_V - 1 - j - 2] = currentPalette[((data[k + 1] & 0x0f) << 2) | (data[k + 2] >> 6)]
          //leds[i][NUM_LEDS_V - 1 - j - 3] = currentPalette[data[k + 2] & 0x3f]
          k += 3;
        }
      }
      state = 1;
    }
    else {
      if (state != 0) {
        state += 1;
        if (state >= 42) {
          //just timeout at some point and turn of all leds
          for (int i = 0; i < NUM_LEDS_H; i++) {
            for (int j = 0; j < NUM_LEDS_V; j++) {
              leds[i][NUM_LEDS_V - 1 - j] = CRGB(0, 0, 0);
            }
          }
          state = 0;
        }
      }
    }
    Serial.flush();
    waitingTime = WAITTIME_VSTREAM;
  }

  //mode - image stream: one frames with 24 bit/px (at max every 80ms)
  else if (mode == 2) {
    Serial.print("2");
    //TODO
    Serial.flush();
    waitingTime = WAITTIME_ISTREAM;
  }

  //mode - sound activation (hardcoded) - shows pattern accourding to a microphon signal
  else if (mode == 1) {
    //TODO
  }

  //mode - dynamic patterns (hardcoded) - perhaps via several sub-modes
  else { //mode == 0
    if (submode[0] == 127) {
    }
    else if (submode[0] == 126) {
      //copy this check for creating a new pattern
    }
    else if (submode[0] == 6) {
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CRGB(((brightness) * 60 + 3) % 256, ((brightness) * 60 + 3) % 256, ((brightness) * 60 + 3) % 256);
        }
      }
      waitingTime = 1000;
    }
    else if (submode[0] == 5) {
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CHSV(rand() % 256, (pspeed * 64) % 256, (brightness * 64 - 1) % 256);
        }
      }
      waitingTime = 1000;
    }
    else if (submode[0] == 4) {
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CHSV(((state + (rand() % 12 - 1) + j) - 1) % 256, 255, valueb[brightness][3]);
        }
      }
      state = (state + rand() % 8) % 256;
      waitingTime = pspeed * pspeed * 62 + 8;
    }
    else if (submode[0] == 3) {
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CHSV((rand() % 12 + 256 / NUM_LEDS_V * (state + (rand() % 5 - 1) + j) - 1) % 256, 255, valueb[brightness][3]);
        }
      }
      state = (state + 1) % NUM_LEDS_V;
      waitingTime = pspeed * pspeed * 62 + 8;
    }
    else if (submode[0] == 2) {
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CHSV((7 + 256 / NUM_LEDS_V * (state + i + j) - 1) % 256, 255, valueb[brightness][3]);
        }
      }
      state = (state + (-1 + (rand() % 4))) % NUM_LEDS_V;
      waitingTime = pspeed * pspeed * 62 + 8;
    }
    else if (submode[0] == 1) {
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CRGB((7 + 256 / NUM_LEDS_V * (state + i - j) - 1) % 256, (7 + 256 / NUM_LEDS_V * (state - i - j) - 1) % 256, (7 + 256 / NUM_LEDS_V * (state + i + j) - 1) % 256);
        }
      }
      state = (state + 1) % NUM_LEDS_V;
      waitingTime = pspeed * pspeed * 62 + 8;
    }
    else { //submode[0] == 0
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CHSV((7 + 256 / NUM_LEDS_V * (state + i + j) - 1) % 256, 255, valueb[brightness][3]);
        }
      }
      state = (state + 1) % NUM_LEDS_V;
      waitingTime = pspeed * pspeed * 62 + 8;
    }
    //delay(cspeed);
  }
  if (DEBUG_MODE) {
    Serial.print("time proc/show (mode: ");
    Serial.print(mode); Serial.print(", submode: "); Serial.print(submode[mode]); Serial.print("): ");
    Serial.print(elapsedTime);
  }
  FastLED.show();
  if (DEBUG_MODE) {
    Serial.print("/");
    Serial.println(elapsedTime);
    Serial.flush();
  }
  timedDelay(waitingTime);
}

// ------ Tools ------

