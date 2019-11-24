
// Designed for Arduino Mega

#include "Adafruit_NeoPixel.h"
#include "hsv2rgb.h"
#include "FastLED.h"
#include "elapsedMillis.h"
#include "SPI.h"

#define DEBUG_MODE 0

#define LEDS_PIN_0 0 // A1
#define LEDS_PIN_1 1 // A2
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
#define SYNC_PIN 47 // SPI sync
#define STATUS_LEDS_PIN A0
#define MICROPHONE_A_PIN A2
#define MICROPHONE_B_PIN A3
#define PHOTO_RST_PIN A4
#define SWITCH_PARENTAL_LOCK_1 A6 // Switch to turn off all buttons
#define SWITCH_PARENTAL_LOCK_2 A7 // Switch to turn off mode button
#define BUTTON_MDP_DEC A8 // Decrement Mode
#define BUTTON_MDP_INC A9 // Increment Mode
#define BUTTON_MDS_DEC A10 // Decrement submode
#define BUTTON_MDS_INC A11 // Increment submode
#define BUTTON_BRS_DEC A12 // Decrement brightness
#define BUTTON_BRS_INC A13 // Increment brightness
#define BUTTON_SPD_DEC A14 // Decrement pattern speed
#define BUTTON_SPD_INC A15 // IncremNUM_STATUS_LEDSent pattern speed
#define MODEL_PIXELS WS2811 // WS2811, WS2812b // Fastled
#define MODEL_STATUS NEO_GRB + NEO_KHZ800 // NEO_GRB + NEO_KHZ800 // NeoPixel
#define NUM_LEDS_H 16 // 16
#define NUM_LEDS_V 24 // 24
#define NUM_BUTTONS 8 // 8
#define NUM_STATUS_LEDS 9 // 4
#define BUTTON_WAIT 40 // time (ms) to wait for another buttoncheck
#define WAITTIME_PSTREAM 40 // in ms for pixelflut stream -> 1 - 25 fps
#define WAITTIME_VSTREAM 40 // in ms for NES video stream -> 25 fps
#define WAITTIME_ASTREAM 40 // in ms for beat detection stream -> 25 fps
#define WAITTIME_ISTREAM 100 // in ms for Image stream -> 10 fps
#define TIMEOUT_PSTREAM 2000 // in ms for NES video stream
#define TIMEOUT_VSTREAM 2000 // in ms for NES video stream
#define TIMEOUT_ASTREAM 2000 // in ms for beat detection stream
#define TIMEOUT_ISTREAM 10000 // in ms for Image stream
#define NUM_BITS_VSTREAM 24 // 6
#define NUM_BYTES_STREAM 1152 // 288 // NUM_LEDS_H*NUM_LEDS_V*NUM_BITS_VSTREAM/8;

CRGB leds[NUM_LEDS_H][NUM_LEDS_V];

// Set up Status LEDS
//CRGB status_leds[NUM_STATUS_LEDS];
Adafruit_NeoPixel status_leds = Adafruit_NeoPixel(NUM_STATUS_LEDS, STATUS_LEDS_PIN, NEO_GRB + NEO_KHZ800);

// modes: 0 = light patterns, 1 = image stream (24bit), 2 = pixelflut, 3 = NES video stream, 4 = music patterns
uint8_t mode = 0;
uint8_t modeMax = 5;
uint8_t submode [5] = {2, 0, 0, 0, 0};
uint8_t submodeMax [5] = {20, 41, 1, 1, 4}; // Used for all mode switches

int photoRSTState = 0;      // photo resistor for regulating brightness
float photoLeakeRate = 0.9; // for smoothing the photo resistor [0,1]
int buttonState [NUM_BUTTONS];         // current state of the button
int lastButtonState [NUM_BUTTONS];     // previous state of the button
bool buttonsAvailable1 = false;  // default: parental lock for all buttons enabled
bool buttonsAvailable2 = false;  // default: parental lock for the mode switch enabled

elapsedMillis elapsedTime;
int waitingTime = 0;
int loopsUntilTimeOut = 100;

uint8_t pspeed = 2; // [0..4]
uint8_t cspeed = 255;
uint8_t brightness = 2; // [0..4]
const uint8_t valueBrightness [5] = {12, 25, 54, 118, 254}; // brightness for wall leds [0,255] // {9, 17, 37, 95, 252} {3, 9, 27, 81, 243}
const uint8_t statusBrightness = 127;  // brightness for STATUS leds [0,255]
// const int valueb [5][4] = {{3, 9, 27, 81}, {4, 12, 36, 108}, {5, 15, 45, 135}, {7, 21, 63, 189}, {9, 27, 81, 243}};  // deprecated

int state = 30;

byte data[NUM_BYTES_STREAM];

// for SPI:
volatile int spi_pos = 0;
volatile bool process_it = false;
volatile bool sync_is_high = false;

void setup() {
  for (int i = 0; i < NUM_BUTTONS; i++) {
    buttonState[i] = 0;
    lastButtonState[i] = 0;
  }
  pinMode(BUTTON_MDP_DEC, INPUT_PULLUP);
  pinMode(BUTTON_MDP_INC, INPUT_PULLUP);
  pinMode(BUTTON_MDS_DEC, INPUT_PULLUP);
  pinMode(BUTTON_MDS_INC, INPUT_PULLUP);
  pinMode(BUTTON_SPD_DEC, INPUT_PULLUP);
  pinMode(BUTTON_SPD_INC, INPUT_PULLUP);
  pinMode(BUTTON_BRS_DEC, INPUT_PULLUP);
  pinMode(BUTTON_BRS_INC, INPUT_PULLUP);
  pinMode(SWITCH_PARENTAL_LOCK_1, INPUT_PULLUP);
  pinMode(SWITCH_PARENTAL_LOCK_2, INPUT_PULLUP);

  //  Communication via SPI
  // turn on SPI in slave mode
  SPCR |= _BV(SPE);
  // turn on interrupts
  SPCR |= _BV(SPIE);
  // have to send on master in, *slave out*
  pinMode(MISO, OUTPUT);
  //pinMode(MOSI, OUTPUT);
  pinMode(SYNC_PIN, OUTPUT);
  digitalWrite(SYNC_PIN, LOW);
  //SPI.attachInterrupt();

//  if (DEBUG_MODE) {
//    Serial.begin(115200); // 57600 115200 230400
//    Serial.setTimeout(33);
//    Serial.println("Go!");
//  }

  // Set up LEDS
  if (NUM_LEDS_H > 0) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_0, BRG>(leds[0], NUM_LEDS_V);
  if (NUM_LEDS_H > 1) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_1, BRG>(leds[1], NUM_LEDS_V);
  if (NUM_LEDS_H > 2) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_2, BRG>(leds[2], NUM_LEDS_V);
  if (NUM_LEDS_H > 3) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_3, BRG>(leds[3], NUM_LEDS_V);
  if (NUM_LEDS_H > 4) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_4, BRG>(leds[4], NUM_LEDS_V);
  if (NUM_LEDS_H > 5) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_5, BRG>(leds[5], NUM_LEDS_V);
  if (NUM_LEDS_H > 6) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_6, BRG>(leds[6], NUM_LEDS_V);
  if (NUM_LEDS_H > 7) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_7, BRG>(leds[7], NUM_LEDS_V);
  if (NUM_LEDS_H > 8) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_8, BRG>(leds[8], NUM_LEDS_V);
  if (NUM_LEDS_H > 9) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_9, BRG>(leds[9], NUM_LEDS_V);
  if (NUM_LEDS_H > 10) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_10, BRG>(leds[10], NUM_LEDS_V);
  if (NUM_LEDS_H > 11) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_11, BRG>(leds[11], NUM_LEDS_V);
  if (NUM_LEDS_H > 12) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_12, BRG>(leds[12], NUM_LEDS_V);
  if (NUM_LEDS_H > 13) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_13, BRG>(leds[13], NUM_LEDS_V);
  if (NUM_LEDS_H > 14) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_14, BRG>(leds[14], NUM_LEDS_V);
  if (NUM_LEDS_H > 15) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_15, BRG>(leds[15], NUM_LEDS_V);

  // Set up Status LEDS
//  FastLED.addLeds<MODEL_STATUS, STATUS_LEDS_PIN, GRB>(status_leds, NUM_STATUS_LEDS);
//  for (int i = 0; i < NUM_STATUS_LEDS; i++) {
//    status_leds[i] = CHSV(0, 0, 0);
//    status_leds.setPixelColor(i, 0, 0, 0);
//  }
  status_leds.begin();
  status_leds.show();
  updateStatus();

  for (int i = 0; i < NUM_LEDS_H; i++) {
    for (int j = 0; j < NUM_LEDS_V; j++) {
      leds[i][NUM_LEDS_V - 1 - j] = CRGB::Black;
    }
  }
  FastLED.show();

  for (int i = 0; i < NUM_BYTES_STREAM; i++) {
    data[i] = 0;
  }

  // setPaletteNES();

  delay(100);

  spi_pos = 0;   // buffer empty
  process_it = false;
  SPDR = encodeMode2Byte();
  sync_is_high = true;
  digitalWrite(SYNC_PIN, HIGH);
}

void loop() {

  // mode - sound activation (hardcoded) - shows pattern accourding to a microphon signal
  if (mode == 4) {
    // TODO
    elapsedTime = 0;
    timedDelay(WAITTIME_ASTREAM);
  }

  // mode - video stream: up to 25 frames per second with 24 bit/px
  else if (mode == 3) {
    waitingTime = WAITTIME_VSTREAM;
    loopsUntilTimeOut = TIMEOUT_VSTREAM/WAITTIME_VSTREAM;
    showStream();
  }

  // mode - pixelflut stream: up to 25 frames per second with 24 bit/px
  else if (mode == 2) {
    waitingTime = WAITTIME_PSTREAM * (1+pspeed) * (1+pspeed) ;
    loopsUntilTimeOut = TIMEOUT_PSTREAM/WAITTIME_PSTREAM;
    showStream();
  }

  // mode - image stream: one frame with 24 bit/px (at max every 80ms)
  else if (mode == 1) {
    waitingTime = WAITTIME_ISTREAM * (1+pspeed) * (1+pspeed) ;
    loopsUntilTimeOut = TIMEOUT_ISTREAM/WAITTIME_ISTREAM;
    showStream();
  }

  // mode - dynamic patterns (hardcoded) - perhaps via several sub-modes
  else { // mode == 0
    showPatterns();
  }
  /*
  if (DEBUG_MODE) {
    Serial.print("photo: "); Serial.print(photoRSTState); Serial.print(", ");
    Serial.print("brightness: "); Serial.print((int)(photoRSTState/1023.*valueBrightness[brightness])); Serial.print(", ");
    Serial.print("time proc/show (mode: ");
    Serial.print(mode); Serial.print(", submode: "); Serial.print(submode[mode]); Serial.print("/"); Serial.print(submodeMax[mode]); Serial.print("): ");
    Serial.print(elapsedTime);
  }

  if (DEBUG_MODE) {
    Serial.print("/");
    Serial.println(elapsedTime);
    Serial.flush();
  }*/
}

// SPI interrupt routine
ISR (SPI_STC_vect) {
// https://arduino.stackexchange.com/questions/16348/how-do-you-use-spi-on-an-arduino
// https://i.imgur.com/vN4xzvh.gif
// https://arduino.stackexchange.com/questions/33086/how-do-i-send-a-string-from-an-arduino-slave-using-spi

  byte c = SPDR;  // grab byte from SPI Data Register

  if (sync_is_high) {
    // if the slave is in this state, the master is supposed to only read one byte
    // from the register that is encoding the current mode and submode
    // afterwards the slave is ready for receiving the real data
    digitalWrite(SYNC_PIN, LOW);
    sync_is_high = false;
  }
  else {
      if (process_it) {
        return;
      }

      if (spi_pos < NUM_BYTES_STREAM) {
        data[spi_pos++] = c;
        process_it = (spi_pos == NUM_BYTES_STREAM);
      }
  }

  //SPDR = SPI_mode; // put current mode and submode as byte to SPI Data Register

  return;
}

byte encodeMode2Byte() {
  // first two bits code the mode and remaining 6 bits code the submode
  return ((mode << 6) | submode[mode]);
}

void delayAwake(int time) {

  int start = (int)elapsedTime;
  while (true) {
    if ((int)elapsedTime-start >= time) break;
  }
  return;
}

void checkButtons() {

  // compare the buttonState to its previous state
  buttonsAvailable1 = digitalRead(SWITCH_PARENTAL_LOCK_1) == LOW; // enable all buttons
  buttonsAvailable2 = digitalRead(SWITCH_PARENTAL_LOCK_2) == LOW; // enable all buttons except the mode switch
  if (buttonsAvailable1 || buttonsAvailable2) {
    for (int i = 0; i < NUM_BUTTONS; i++) {
      if (i == 0) buttonState[i] = digitalRead(BUTTON_MDP_DEC);
      else if (i == 1) buttonState[i] = digitalRead(BUTTON_MDP_INC);
      else if (i == 2) buttonState[i] = digitalRead(BUTTON_MDS_DEC);
      else if (i == 3) buttonState[i] = digitalRead(BUTTON_MDS_INC);
      else if (i == 4) buttonState[i] = digitalRead(BUTTON_SPD_DEC);
      else if (i == 5) buttonState[i] = digitalRead(BUTTON_SPD_INC);
      else if (i == 6) buttonState[i] = digitalRead(BUTTON_BRS_DEC);
      else if (i == 7) buttonState[i] = digitalRead(BUTTON_BRS_INC);
  
      if (buttonState[i] != lastButtonState[i]) {
        // if the state has changed, increment the counter
        if (buttonState[i] == LOW) {
          // if the current state is LOW then the button went from off to on:
          if (i == 0) {
            if (buttonsAvailable1) mode = (mode - 1 + modeMax) % modeMax;
          }
          else if (i == 1) {
            if (buttonsAvailable1) mode = (mode + 1) % modeMax;
          }
          else if (i == 2) submode[mode] = (submode[mode] - 1 + submodeMax[mode]) % submodeMax[mode];
          else if (i == 3) submode[mode] = (submode[mode] + 1) % submodeMax[mode];
          else if (i == 4) pspeed = min(pspeed + 1, 4);
          else if (i == 5) pspeed = max(pspeed - 1, 0);
          else if (i == 6) brightness = max(brightness - 1, 0);
          else if (i == 7) brightness = min(brightness + 1, 4);
          // Serial.print((submode[mode] - 1) % submodeMax[mode]);Serial.print("|");Serial.print((submode[mode] - 1));Serial.print("|");;Serial.print(submodeMax[mode]);Serial.print("|");
        } else {
          // if the current state is HIGH then the button went from on to off:
        }
        lastButtonState[i] = buttonState[i];
      }
    }
  }
}

void updateStatus() {

  // read photo sensor:
  //photoRSTState = photoRSTState*photoLeakeRate + analogRead(PHOTO_RST_PIN)*(1.-photoLeakeRate);
  // disable light sensor for now:
  photoRSTState = 1023;

  // set global brightness:
  FastLED.setBrightness((int)(photoRSTState+211.)/1234.*valueBrightness[brightness]);

  // set Status LEDS:

//  //FastLED:
//  if (mode == 3) status_leds[0] = CHSV(60, 255, statusBrightness);
//  else if (mode == 2) status_leds[0] = CHSV(96, 255, statusBrightness);
//  else if (mode == 1) status_leds[0] = CHSV(160, 255, statusBrightness);
//  else status_leds[0] = CHSV(0, 255, statusBrightness);
//
//  status_leds[2] = CHSV(256/submodeMax[mode]*(submodeMax[mode]-submode[mode]-1)%256, 255, statusBrightness);
//  status_leds[4] = CHSV(200/5*(5-brightness-1)%200, 255, statusBrightness);
//  status_leds[6] = CHSV(200/5*pspeed%200, 255, statusBrightness);

  //NeoPixel:
  if (mode == 4) status_leds.setPixelColor(1, getNeoPixelWheel(42 & 255));
  else if (mode == 3) status_leds.setPixelColor(1, getNeoPixelWheel(85 & 255));
  else if (mode == 2) status_leds.setPixelColor(1, getNeoPixelWheel(171 & 255));
  else if (mode == 1) status_leds.setPixelColor(1, getNeoPixelWheel(206 & 255));
  else status_leds.setPixelColor(1, getNeoPixelWheel(0 & 255));

  status_leds.setPixelColor(3, getNeoPixelWheel((256/submodeMax[mode]*(submodeMax[mode]-submode[mode]-1)%256) & 255));
  status_leds.setPixelColor(5, getNeoPixelWheel((180/5*(5-brightness-1)%180) & 255));
  status_leds.setPixelColor(7, getNeoPixelWheel((180/5*pspeed%180) & 255));

  status_leds.setBrightness((int)photoRSTState/1023.*valueBrightness[brightness]*0.33);
  if (mode == 0 || process_it) status_leds.show();
}

//void sssetNeoPixelHSV(

void timedDelay(int waitTime) {
  checkButtons();
  updateStatus();
  while ((waitTime - (int)elapsedTime) > BUTTON_WAIT) {
    //delay(BUTTON_WAIT);
    delayAwake(BUTTON_WAIT);
    checkButtons();
    updateStatus();
  }
  //delay(max(waitTime - (int)elapsedTime, 0));
  delayAwake(max(waitTime - (int)elapsedTime, 0));
  waitingTime = 0; // for safety - TODO remove
}

void showStream() {
  // mode: video (NES) stream or image stream - receive RGB frames via SPI

  elapsedTime = 0;

  if (process_it) {
    // full data package was successfull received
    for (int i = 0; i < NUM_LEDS_H; i++) {
      for (int j = 0; j < NUM_LEDS_V; j++) {
        leds[i][NUM_LEDS_V - 1 - j] = CRGB(data[(i * NUM_LEDS_V + j) * 3 + 0], data[(i * NUM_LEDS_V + j) * 3 + 1], data[(i * NUM_LEDS_V + j) * 3 + 2]);
      }
    }
    FastLED.show();
    state = 1;
    spi_pos = 0;
    process_it = false;
    // get ready to receive the next request
    SPDR = encodeMode2Byte();
    sync_is_high = true;
    digitalWrite(SYNC_PIN, HIGH);
  }
  else {
    state += 1;
    if (state >= loopsUntilTimeOut) {
      //just timeout at some point and turn of all leds
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CRGB::Black;
        }
      }
      FastLED.show();
      updateStatus();
      state = 1;
      spi_pos = 0;
      // get ready to retry another request
      SPDR = encodeMode2Byte();
      sync_is_high = true;
      digitalWrite(SYNC_PIN, HIGH);
    }
  }

  timedDelay(waitingTime);
}

void rainbow(int state, uint8_t chance=0) {
  for (int i = 0; i < NUM_LEDS_H; i++) {
    for (int j = 0; j < NUM_LEDS_V; j++) {
      leds[i][NUM_LEDS_V - 1 - j] = CHSV((7 + 256 / NUM_LEDS_V * (state + random8(chance) + i + j) - 1) % 256, 255, 255);
    }
  }
}

void rgbCurtain(int state, uint8_t chance=5) {
  for (int i = 0; i < NUM_LEDS_H; i++) {
    for (int j = 0; j < NUM_LEDS_V; j++) {
      leds[i][NUM_LEDS_V - 1 - j] = CHSV((rand() % 12 + 256 / NUM_LEDS_V * (state + (random8(chance) - 1) + j) - 1) % 256, 255, 255);
    }
  }
}

void fire(uint8_t color=10, uint8_t chanceOfNew=64, uint8_t fadeStrength=200, uint8_t chanceOfFade=20) {
  // percentage to fade to black: 192/256 => 75%
  for (int i = 0; i < NUM_LEDS_H; i++) {
    for (int j = NUM_LEDS_V-1; j > 0; j--) {
      leds[i][j] = leds[i][j-1].nscale8(fadeStrength-chanceOfFade+random8(chanceOfFade*2));
    }
    leds[i][0] = CHSV(color, 255-chanceOfNew+random8(chanceOfNew-1), 255-chanceOfNew+random8(chanceOfNew-1));
  }
}

void rain(uint8_t color=170, uint8_t chanceOfNew=128, uint8_t fadeStrength=210, uint8_t chanceOfFade=24) {
  // percentage to fade to black: 192/256 => 75%
  for (int i = 0; i < NUM_LEDS_H; i++) {
    for (int j = 0; j < (NUM_LEDS_V-1); j++) {
      leds[i][j] = leds[i][j+1].nscale8(fadeStrength-chanceOfFade+random8(chanceOfFade*2));
    }
    leds[i][NUM_LEDS_V-1] = CHSV(color, 255-chanceOfNew+random8(chanceOfNew-1), 255-chanceOfNew+random8(chanceOfNew-1));
  }
}

void addGlitter(uint8_t chanceOfGlitter=128, uint8_t maxNumberOfGlitter=1) {
  for (int k=0; k<maxNumberOfGlitter; k++) {
    if(random8() < chanceOfGlitter) {
      leds[random8(NUM_LEDS_H)][random8(NUM_LEDS_V)] += CRGB::White;
    }
  }
}

int plasma(int state, uint8_t chance=4, uint8_t magnitude=2, uint8_t fadeStrength=200, uint8_t chanceOfFade=0) {
  int y = state%NUM_LEDS_V;
  int x = (state-y)/NUM_LEDS_V;

  uint8_t hue = (rgb2hsv_approximate(leds[x][y]).hue + random8(chance) + 1) % 256;
  
  int new_x = (x + (random8(1+2*magnitude)-magnitude) + NUM_LEDS_H) % NUM_LEDS_H;
  int new_y = (y + (random8(1+2*magnitude)-magnitude) + NUM_LEDS_V) % NUM_LEDS_V;

  for (int i = 0; i < NUM_LEDS_H; i++) {
    for (int j = 0; j < NUM_LEDS_V; j++) {
      leds[i][NUM_LEDS_V - 1 - j] = CRGB(0, 0, 0);
    }
  }
	
  //leds[new_x][new_y] = CHSV(hue, 255, 255).nscale8(255);
  leds[new_x][new_y] = CHSV(hue, 255, 255);
	  
  for (int j = 1; j <= (NUM_LEDS_V/2); j++) {
    leds[new_x][(new_y+j)%NUM_LEDS_V] = leds[new_x][(new_y-1+j)%NUM_LEDS_V].nscale8(fadeStrength-chanceOfFade+random8(chanceOfFade*2));
    leds[new_x][(new_y-j+NUM_LEDS_V)%NUM_LEDS_V] = leds[new_x][(new_y+1-j+NUM_LEDS_V)%NUM_LEDS_V].nscale8(fadeStrength-chanceOfFade+random8(chanceOfFade*2));
  }
  for (int i = 1; i <= (NUM_LEDS_H/2); i++) {
    leds[(new_x+i)%NUM_LEDS_H][new_y] = leds[(new_x-1+i)%NUM_LEDS_H][new_y].nscale8(fadeStrength-chanceOfFade+random8(chanceOfFade*2));
    leds[(new_x-i+NUM_LEDS_H)%NUM_LEDS_H][new_y] = leds[(new_x+1-i+NUM_LEDS_H)%NUM_LEDS_H][new_y].nscale8(fadeStrength-chanceOfFade+random8(chanceOfFade*2));
    for (int j = 1; j <= (NUM_LEDS_V/2); j++) {
      leds[(new_x+i)%NUM_LEDS_H][(new_y+j)%NUM_LEDS_V] = leds[(new_x+i)%NUM_LEDS_H][(new_y-1+j)%NUM_LEDS_V].nscale8(fadeStrength+(i)*(j-1)-chanceOfFade+random8(chanceOfFade*2));
      leds[(new_x+i)%NUM_LEDS_H][(new_y-j+NUM_LEDS_V)%NUM_LEDS_V] = leds[(new_x+i)%NUM_LEDS_H][(new_y+1-j+NUM_LEDS_V)%NUM_LEDS_V].nscale8(fadeStrength+(i)*(j-1)-chanceOfFade+random8(chanceOfFade*2));
      leds[(new_x-i+NUM_LEDS_H)%NUM_LEDS_H][(new_y+j)%NUM_LEDS_V] = leds[(new_x-i+NUM_LEDS_H)%NUM_LEDS_H][(new_y-1+j)%NUM_LEDS_V].nscale8(fadeStrength+(i)*(j-1)-chanceOfFade+random8(chanceOfFade*2));
      leds[(new_x-i+NUM_LEDS_H)%NUM_LEDS_H][(new_y-j+NUM_LEDS_V)%NUM_LEDS_V] = leds[(new_x-i+NUM_LEDS_H)%NUM_LEDS_H][(new_y+1-j+NUM_LEDS_V)%NUM_LEDS_V].nscale8(fadeStrength+(i)*(j-1)-chanceOfFade+random8(chanceOfFade*2));
	  }
  }

  state = new_x*NUM_LEDS_V + new_y;
  return state;
}

int blob(int state, uint8_t chance=2, uint8_t magnitude=2, uint8_t fadeStrength=200, uint8_t chanceOfFade=0) {
  int y = state%NUM_LEDS_V;
  int x = (state-y)/NUM_LEDS_V;

  uint8_t hue = (rgb2hsv_approximate(leds[x][y]).hue + random8(chance) + 1) % 256;
  
  int new_x = (x + (random8(1+2*magnitude)-magnitude) + NUM_LEDS_H) % NUM_LEDS_H;
  int new_y = (y + (random8(1+2*magnitude)-magnitude) + NUM_LEDS_V) % NUM_LEDS_V;

  for (int i = 0; i < NUM_LEDS_H; i++) {
    for (int j = 0; j < NUM_LEDS_V; j++) {
      uint8_t h_shift = (NUM_LEDS_H/2)-abs((NUM_LEDS_H/2)-abs(i-new_x));
      uint8_t v_shift = (NUM_LEDS_V/2)-abs((NUM_LEDS_V/2)-abs(j-new_y));
	    leds[i][j] = CHSV((hue + (h_shift+v_shift) * 8 - ((h_shift-1)*(v_shift-1))) % 256, 255, 255);
    }
  }
	
  state = new_x*NUM_LEDS_V + new_y;
  return state;
}

void dancingNote(int state) {
  int x = random(3)+random(2)-random(2)-random(2);
  int y = random(5)-random(5);

  for (int i = 0; i < NUM_LEDS_H; i++) {
    for (int j = 0; j < NUM_LEDS_V; j++) {
      leds[i][NUM_LEDS_V - 1 - j] = CRGB(0, 0, 0);
    }
  }

  leds[2 + x][6 + y] = CHSV(state, 255, 255);
  for (int j = 0; j < 3; j++) {
    leds[3 + x][5 + j + y] = CHSV(state, 255, 255);
  }
  for (int j = 0; j < 5; j++) {
    for (int i = 0; i < 3; i++) {
        leds[4 + i + x][4 + j +y] = CHSV(state, 255, 255);
    }
  }
  for (int j = 0; j < 3; j++) {
    leds[7 + x][5 + j + y] = CHSV(state, 255, 255);
  }
  for (int j = 0; j < 14; j++) {
    leds[8 + x][6 + j + y] = CHSV(state, 255, 255);
  }
  for (int j = 0; j < 3; j++) {
    leds[9 + x][17 + j + y] = CHSV(state, 255, 255);
  }
  leds[10 + x][16 + y] = CHSV(state, 255, 255);
  leds[11 + x][15 + y] = CHSV(state, 255, 255);
  for (int j = 0; j < 2; j++) {
    leds[12+x][13 + j + y] = CHSV(state, 255, 255);
  }
}

void showPatterns() {
  // mode - dynamic patterns (hardcoded) - via several sub-modes

  elapsedTime = 0;

  if (submode[0] == 63) {
  }
  else if (submode[0] == 62) {
    // copy this check for creating a new pattern
  }
//  else if (submode[0] == 11) {
//    for (int i = 0; i < NUM_LEDS_H; i++) {
//      for (int j = 0; j < NUM_LEDS_V; j++) {
//      leds[i][NUM_LEDS_V - 1 - j] = CRGB(((brightness) * 60 + 3) % 256, ((brightness) * 60 + 3) % 256, ((brightness) * 60 + 3) % 256);
//      }
//    }
//    waitingTime = 1000;
//  }
//  else if (submode[0] == 10) {
//    for (int i = 0; i < NUM_LEDS_H; i++) {
//      for (int j = 0; j < NUM_LEDS_V; j++) {
//        leds[i][NUM_LEDS_V - 1 - j] = CHSV(rand() % 256, (pspeed * 64) % 256, (brightness * 64 - 1) % 256);
//      }
//    }
//    waitingTime = 1000;
//  }
  else if (submode[0] == 19) {
    state = blob(state, 12, 1, 230, 8);
    waitingTime = pspeed * pspeed * 250 + 8;
  }
  else if (submode[0] == 18) {
    state = blob(state, 8, 2, 220, 0);
    waitingTime = pspeed * pspeed * 125 + 8;
  }
  else if (submode[0] == 17) {
    state = plasma(state, 12, 1, 230, 8);
    waitingTime = pspeed * pspeed * 250 + 8;
  }
  else if (submode[0] == 16) {
    state = plasma(state, 8, 2, 220, 0);
    waitingTime = pspeed * pspeed * 125 + 8;
  }
  else if (submode[0] == 15) {
    state = (state + random8(12) - 1 + 256) % 256;
    dancingNote(state);
    waitingTime = pspeed * pspeed * 160 + 8;
  }
  else if (submode[0] == 14) {
    state = (state + random8(8) - 1 + 256) % 256;
    dancingNote(state);
    waitingTime = pspeed * pspeed * 187 + 8;
  }
  else if (submode[0] == 13) {
    fire(24, 96, 192, 24);
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 12) {
    fire(8, 64, 210, 10);
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 11) {
    rain(160, 160, 220, 32);
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 10) {
    rain(172, 138, 204, 42);
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 9) {
    state = (state + random8(8)) % 256;
    for (int i = 0; i < NUM_LEDS_H; i++) {
      for (int j = 0; j < NUM_LEDS_V; j++) {
        leds[i][NUM_LEDS_V - 1 - j] = CHSV(((state + (rand() % 12 - 1) + j) - 1) % 256, 255, 255);
      }
    }
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 8) {
    state = (state + 1) % NUM_LEDS_V;
    for (int i = 0; i < NUM_LEDS_H; i++) {
      for (int j = 0; j < NUM_LEDS_V; j++) {
      leds[i][NUM_LEDS_V - 1 - j] = CRGB((7 + 256 / NUM_LEDS_V * (state + i - j) - 1 + 256) % 256, (7 + 256 / NUM_LEDS_V * (state - i - j) - 1 + 256) % 256, (7 + 256 / NUM_LEDS_V * (state + i + j) - 1) % 256);
      }
    }
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 7) {
    state = (state + (-1 + random8(4))) % NUM_LEDS_V;
    rainbow(state, 0);
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 6) {
    state = (state + 1) % NUM_LEDS_V;
    rainbow(state, 3);
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 5) {
    state = (state + 1) % NUM_LEDS_V;
    rainbow(state, 0);
    addGlitter(128, 10);
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 4) {
    state = (state + 1) % NUM_LEDS_V;
    rainbow(state, 0);
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 3) {
    state = (state + 1) % NUM_LEDS_V;
    rgbCurtain(state, 5);
    addGlitter(96, 12);
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 2) {
    state = (state + 1) % NUM_LEDS_V;
    rgbCurtain(state, 5);
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else if (submode[0] == 1) {
    state = (state + 1) % NUM_LEDS_V;
    rgbCurtain(state, 2);
    waitingTime = pspeed * pspeed * 62 + 8;
  }
  else { // submode[0] == 0
    state = (state + 1) % NUM_LEDS_V;
    for (int i = 0; i < NUM_LEDS_H; i++) {
      for (int j = 0; j < NUM_LEDS_V; j++) {
        leds[i][NUM_LEDS_V - 1 - j] = CRGB::Black;
      }
    }
    waitingTime = pspeed * pspeed * 62 + 8;
  }

  FastLED.show();
  timedDelay(waitingTime);
}

// ------ Tools ------

//Method from NeoPixel to get display a certain hue value
// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
uint32_t getNeoPixelWheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if(WheelPos < 85) {
    return status_leds.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if(WheelPos < 170) {
    WheelPos -= 85;
    return status_leds.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return status_leds.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}

// ------ Depricated code ------
// TODO: define a good color palette - perhaps like NES? // depricated
//extern const CHSV currentPalette [64] = {CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216)};

void setLedsFromBase64Data(byte *data) {
  //method is no longer needed 
  int k = 0;
  for (int i = 0; i < NUM_LEDS_H; i++) {
    for (int j = 0; j < NUM_LEDS_V; j += 4) {
      leds[i][NUM_LEDS_V - 1 - j - 0] = CHSV((uint8_t)(data[k] >> 2) * 4, 255, 255);
      leds[i][NUM_LEDS_V - 1 - j - 1] = CHSV((uint8_t)(((data[k] & 0x03) << 4) | (data[k + 1] >> 4)) * 4, 255, 255);
      leds[i][NUM_LEDS_V - 1 - j - 2] = CHSV((uint8_t)(((data[k + 1] & 0x0f) << 2) | (data[k + 2] >> 6)) * 4, 255, 255);
      leds[i][NUM_LEDS_V - 1 - j - 3] = CHSV((uint8_t)(data[k + 2] & 0x3f) * 4, 255, 255);
      // leds[i][NUM_LEDS_V - 1 - j - 0] = currentPalette[data[k] >> 2]
      // leds[i][NUM_LEDS_V - 1 - j - 1] = currentPalette[((data[k] & 0x03) << 4) | (data[k + 1] >> 4)]
      // leds[i][NUM_LEDS_V - 1 - j - 2] = currentPalette[((data[k + 1] & 0x0f) << 2) | (data[k + 2] >> 6)]
      // leds[i][NUM_LEDS_V - 1 - j - 3] = currentPalette[data[k + 2] & 0x3f]
      k += 3;
    }
  }
}


//  if (mode == 3) {
//    // Communication via UART:
//    //Serial1.print("3");
//    //if (Serial1.readBytes(data, NUM_BYTES_VSTREAM) == NUM_BYTES_VSTREAM) {
//    // UART done.
//    // Communication via SPI:
//    SPI.transfer16(mode<<8 | submode[mode]);
//    if (process_it) {
//      // data[spi_pos] = 0;
//      // Serial.println(String(data[0]));
//      for (int i = 0; i < NUM_LEDS_H; i++) {
//        for (int j = 0; j < NUM_LEDS_V; j += 4) {
//          leds[i][j] = CRGB(data[j * NUM_LEDS_H * 3 + i * 3 + 0], data[j * NUM_LEDS_H * 3 + i * 3 + 0], data[j * NUM_LEDS_H * 3 + i * 3 + 0]);
//        }
//      }
//
//      state = 1;
//      // Communication via SPI:
//      spi_pos = 0;
//      digitalWrite(SYNC_PIN, HIGH);
//      sync_is_high = true;
//      process_it = false;
//    }
//      //SPI done.
//    else {
//      if (state != 0) {
//        state += 1;
//        if (state >= 42) {
//          // just timeout at some point and turn of all leds
//          for (int i = 0; i < NUM_LEDS_H; i++) {
//            for (int j = 0; j < NUM_LEDS_V; j++) {
//              leds[i][NUM_LEDS_V - 1 - j] = CRGB(0, 0, 0);
//            }
//          }
//          state = 0;
//        }
//      }
//    }
//    //Serial1.flush();
//    waitingTime = WAITTIME_VSTREAM;

//// under development by Peer & Rey
//void showStream() {
//  elapsedTime = 0;
//  static bool waiting_for_image = false;
//  static uint32_t image_timeout_counter = 0;
//  if (process_it) {
//    //data[spi_pos] = 0;
//    //Serial.println(String(data[0]));
//    for (int i = 0; i < NUM_LEDS_V; i++) {
//      for (int j = 0; j < NUM_LEDS_H; j++) {
//        int firstByte = ((j*NUM_LEDS_V + i) * 3);
//        leds[j][NUM_LEDS_V-i-1] = CRGB(data[firstByte+0], data[firstByte+1], data[firstByte+2]);
//      }
//    }
//    FastLED.show();
//
//    state = 1;
//    // Communication via SPI:
//    spi_pos = 0;
////    digitalWrite(SYNC_PIN, HIGH);
////    sync_is_high = true;
//    process_it = false;
//    waiting_for_image = false;
//  } else if ( !waiting_for_image ) {
//    sync_is_high = true;
//    // SPI.transfer16(mode<<8 | submode[mode]);
//    spi_pos = 0;
//    digitalWrite(SYNC_PIN, HIGH);
//    waiting_for_image = true;
//    image_timeout_counter = 0;
//  } else if (image_timeout_counter>2) {
//    // reset spi stuff:
//    spi_pos = 0;
//    process_it = false;
//    image_timeout_counter = 0;
//    sync_is_high = false;
//    digitalWrite(SYNC_PIN, LOW);
//    waiting_for_image = false;
//  } else {
//    image_timeout_counter+=1;
//  }
//
//  timedDelay(waitingTime);
//}
