
// Designed for Arduino Mega

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
#define BUTTON_MDP_INC A8 // Mode switch
#define BUTTON_MDP_INC A8 // Mode switch
#define BUTTON_MDP_DEC A9 // Mode switch
#define BUTTON_MDS_INC A10 // Decrement submode
#define BUTTON_MDS_DEC A11 // Increment submode
#define BUTTON_BRS_DEC A12 // Decrement brightness
#define BUTTON_BRS_INC A13 // Increment brightness
#define BUTTON_SPD_DEC A14 // Decrement pattern speed
#define BUTTON_SPD_INC A15 // Increment pattern speed
#define MODEL_PIXELS WS2812B // WS2811, WS2812b
#define MODEL_STATUS WS2812B // WS2812b, WS2811
#define NUM_LEDS_H 16 // 16
#define NUM_LEDS_V 24 // 24
#define NUM_BUTTONS 8 // 8
#define NUM_STATUS_LEDS 12 // 4
#define BUTTON_WAIT 40 // time (ms) to wait for another buttoncheck
#define NUM_FPS_VSTREAM 25
#define WAITTIME_VSTREAM 40 // in ms for NES video stream
#define WAITTIME_ASTREAM 40 // in ms for beat detection stream
#define WAITTIME_ISTREAM 1000 // in ms for Image steram
#define NUM_BITS_VSTREAM 24 // 6
#define NUM_BYTES_VSTREAM 1152 // 288 // NUM_LEDS_H*NUM_LEDS_V*NUM_BITS_VSTREAM/8;
#define NUM_BYTES_ASTREAM NUM_LEDS_H*NUM_LEDS_V*3
#define NUM_BYTES_ISTREAM NUM_LEDS_H*NUM_LEDS_V*3

CRGB leds[NUM_LEDS_H][NUM_LEDS_V];
CRGB status_leds[NUM_STATUS_LEDS];

// modes: 0 = light patterns, 1 = image stream (24bit), 2 = music patterns, 3 = NES video stream
int mode = 0;
int modeMax = 4;
int submode [4] = {0, 0, 0, 0};
int submodeMax [4] = {64, 1, 1, 1}; // Used for all mode switches

int photoRSTState = 0;      // photo resistor for regulating brightness
float photoLeakeRate = 0.9; // for smoothing the photo resistor [0,1]
int buttonState [NUM_BUTTONS];         // current state of the button
int lastButtonState [NUM_BUTTONS];     // previous state of the button
int buttonsAvailable1 = 0;  // default: parental lock for all buttons enabled
int buttonsAvailable2 = 0;  // default: parental lock for the mode switch enabled

elapsedMillis elapsedTime;
int waitingTime = 0;

int pspeed = 2; // [0..4]
int cspeed = 255;
int brightness = 2; // [0..4]
const int valueBrightness [5] = {9, 17, 37, 95, 252}; // {3, 9, 27, 81, 243} // brightness for wall leds [0,255]
const int statusBrightness = 127;  // brightness for STATUS leds [0,255]
// const int valueb [5][4] = {{3, 9, 27, 81}, {4, 12, 36, 108}, {5, 15, 45, 135}, {7, 21, 63, 189}, {9, 27, 81, 243}};  // deprecated

int state = 0;

byte data[NUM_BYTES_VSTREAM];
//byte dataImage[NUM_BYTES_ISTREAM];
//byte dataImage[NUM_BYTES_ISTREAM];
// uint8_t data[NUM_BYTES_VSTREAM];
// uint8_t dataImage[NUM_BYTES_ISTREAM];
// for SPI:
volatile byte spi_pos;
volatile boolean process_it;

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

  //  Communication via UART
  // Use RX1 (18) & TX1 (19)!!!
  // Serial1.begin(230400); // 57600 115200 230400
  // Serial1.setTimeout(WAITTIME_VSTREAM); // ms 40 1000

  //  Communication via SPI
  // turn on SPI in slave mode
  SPCR |= bit (SPE);
  // have to send on master in, *slave out*
  pinMode(MISO, OUTPUT);
  pinMode(MOSI, OUTPUT);
  pinMode(SYNC_PIN, OUTPUT);
  // get ready for an interrupt
  spi_pos = 0;   // buffer empty
  process_it = false;
  // now turn on interrupts
  SPI.attachInterrupt();

  if (DEBUG_MODE) {
    Serial.begin(115200); // 57600 115200 230400
    Serial.setTimeout(33); 
    Serial.println("Go!");
  }

  // Set up LEDS
  if (NUM_LEDS_H > 0) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_0, GRB>(leds[0], NUM_LEDS_V);
  if (NUM_LEDS_H > 1) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_1, GRB>(leds[1], NUM_LEDS_V);
  if (NUM_LEDS_H > 2) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_2, GRB>(leds[2], NUM_LEDS_V);
  if (NUM_LEDS_H > 3) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_3, GRB>(leds[3], NUM_LEDS_V);
  if (NUM_LEDS_H > 4) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_4, GRB>(leds[4], NUM_LEDS_V);
  if (NUM_LEDS_H > 5) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_5, GRB>(leds[5], NUM_LEDS_V);
  if (NUM_LEDS_H > 6) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_6, GRB>(leds[6], NUM_LEDS_V);
  if (NUM_LEDS_H > 7) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_7, GRB>(leds[7], NUM_LEDS_V);
  if (NUM_LEDS_H > 8) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_8, GRB>(leds[8], NUM_LEDS_V);
  if (NUM_LEDS_H > 9) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_9, GRB>(leds[9], NUM_LEDS_V);
  if (NUM_LEDS_H > 10) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_10, GRB>(leds[10], NUM_LEDS_V);
  if (NUM_LEDS_H > 11) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_11, GRB>(leds[11], NUM_LEDS_V);
  if (NUM_LEDS_H > 12) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_12, GRB>(leds[12], NUM_LEDS_V);
  if (NUM_LEDS_H > 13) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_13, GRB>(leds[13], NUM_LEDS_V);
  if (NUM_LEDS_H > 14) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_14, GRB>(leds[14], NUM_LEDS_V);
  if (NUM_LEDS_H > 15) FastLED.addLeds<MODEL_PIXELS, LEDS_PIN_15, GRB>(leds[15], NUM_LEDS_V);

  // Set up Status LEDS
  FastLED.addLeds<MODEL_STATUS, STATUS_LEDS_PIN, GRB>(status_leds, NUM_STATUS_LEDS);

  for (int i = 0; i < NUM_STATUS_LEDS; i++) {
    status_leds[i] = CHSV(0, 0, 0);
  }

  for (int i = 0; i < NUM_BYTES_VSTREAM; i++) {
    data[i] = 0;
  }
  // setPaletteNES();

  delay(100);
}

bool sync_is_high = true;

// SPI interrupt routine
ISR (SPI_STC_vect) {
  byte c = SPDR;  // grab byte from SPI Data Register

  if (process_it) {
    return;
  }

  if (sync_is_high) {
    digitalWrite(SYNC_PIN, LOW);
    sync_is_high = false;
  }

  data[spi_pos++] = c;
  process_it = (spi_pos == NUM_BYTES_VSTREAM);
}
//  // add to buffer if room
//  if (spi_pos < sizeof data) {
//    data[spi_pos++] = c;
//
//    // example: newline means time to process buffer
//    // if (c == '\n')
//    //  process_it = true;
//    if (spi_pos == (NUM_BYTES_VSTREAM-1))
//      process_it = true;
//
//  } // end of room available
// } // end of interrupt routine SPI_STC_vect

void checkButtons() {

  // compare the buttonState to its previous state
  buttonsAvailable1 = digitalRead(SWITCH_PARENTAL_LOCK_1); // enable all buttons
  buttonsAvailable2 = digitalRead(SWITCH_PARENTAL_LOCK_2); // enable all buttons except the mode switch
  if (buttonsAvailable1 == LOW || buttonsAvailable2) {
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
          if (i == 0) if (buttonsAvailable1 == LOW) mode = (mode - 1 + modeMax) % modeMax;
          else if (i == 1) if (buttonsAvailable1 == LOW) mode = (mode + 1) % modeMax;
          else if (i == 2) submode[mode] = (submode[mode] - 1 + submodeMax[mode]) % submodeMax[mode];
          else if (i == 3) submode[mode] = (submode[mode] + 1) % submodeMax[mode];
          else if (i == 4) pspeed = min(pspeed + 1, 4);
          else if (i == 5) pspeed = max(pspeed - 1, 0);
          else if (i == 6) brightness = max(brightness - 1, 0);
          else if (i == 7) brightness = min(brightness + 1, 4);
          Serial.print((submode[mode] - 1) % submodeMax[mode]);Serial.print("|");Serial.print((submode[mode] - 1));Serial.print("|");;Serial.print(submodeMax[mode]);Serial.print("|");
        } else {
          // if the current state is HIGH then the button went from on to off:
        }
        lastButtonState[i] = buttonState[i];
        // Delay a little bit to avoid bouncing
      }    
    }
  }
}

void updateStatus() {

  // read photo sensor:
  photoRSTState = photoRSTState*photoLeakeRate + analogRead(PHOTO_RST_PIN)*(1.-photoLeakeRate);

  // set global brightness:
  FastLED.setBrightness((int)photoRSTState/1023.*valueBrightness[brightness]);

  // set Status LEDS:
  if (mode == 3) status_leds[0] = CHSV(60, 255, statusBrightness);
  else if (mode == 2) status_leds[0] = CHSV(96, 255, statusBrightness);
  else if (mode == 1) status_leds[0] = CHSV(160, 255, statusBrightness);
  else status_leds[0] = CHSV(0, 255, statusBrightness);
  
  status_leds[2] = CHSV(256/submodeMax[mode]*(submodeMax[mode]-submode[mode]-1)%256, 255, statusBrightness);
  status_leds[4] = CHSV(200/5*(5-brightness-1)%200, 255, statusBrightness);
  status_leds[6] = CHSV(200/5*pspeed%200, 255, statusBrightness);
}

void timedDelay(int waitingTime) {
  checkButtons();
  updateStatus();
  while ((waitingTime - (int)elapsedTime) > BUTTON_WAIT) {
    delay(BUTTON_WAIT);
    checkButtons();
    updateStatus();
  }
  delay(max(waitingTime - (int)elapsedTime, 0));
  waitingTime = 0; // for safety - TODO remove
}

void loop() {
  // checkButtons();
  // checkPoti();
  elapsedTime = 0;

  // mode - video stream: 25 frames per second with 6 bit/px
  if (mode == 3) {
    // Communication via UART:
    //Serial1.print("3");
    //if (Serial1.readBytes(data, NUM_BYTES_VSTREAM) == NUM_BYTES_VSTREAM) {
    // UART done.
    // Communication via SPI:
    SPI.transfer("30");
    if (process_it) {
      data[spi_pos] = 0;
      Serial.println(String(data[0]));
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j += 4) {
          leds[i][j] = CRGB(data[j * NUM_LEDS_H * 3 + i * 3 + 0], data[j * NUM_LEDS_H * 3 + i * 3 + 0], data[j * NUM_LEDS_H * 3 + i * 3 + 0]);
        }
      }

      state = 1;
      // Communication via SPI:
      spi_pos = 0;
      digitalWrite(SYNC_PIN, HIGH);
      process_it = false;
      sync_is_high = true;
    }
      //SPI done.
    else {
      if (state != 0) {
        state += 1;
        if (state >= 42) {
          // just timeout at some point and turn of all leds
          for (int i = 0; i < NUM_LEDS_H; i++) {
            for (int j = 0; j < NUM_LEDS_V; j++) {
              leds[i][NUM_LEDS_V - 1 - j] = CRGB(0, 0, 0);
            }
          }
          state = 0;
        }
      }
    }
    //Serial1.flush();
    waitingTime = WAITTIME_VSTREAM;
  }

  // mode - sound activation (hardcoded) - shows pattern accourding to a microphon signal
  else if (mode == 2) {
    // TODO
  }

  // mode - image stream: one frame with 24 bit/px (at max every 1000ms)
  else if (mode == 1) {
    SPI.transfer("30");
    if (process_it) {
      data[spi_pos] = 0;
      Serial.println(String(data[0]));
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j += 4) {
          leds[i][j] = CRGB(data[j * NUM_LEDS_H * 3 + i * 3 + 0], data[j * NUM_LEDS_H * 3 + i * 3 + 0], data[j * NUM_LEDS_H * 3 + i * 3 + 0]);
        }
      }

      state = 1;
      // Communication via SPI:
      spi_pos = 0;
      digitalWrite(SYNC_PIN, HIGH);
      process_it = false;
      sync_is_high = true;
    }
    waitingTime = WAITTIME_ISTREAM;
  }

  // mode - dynamic patterns (hardcoded) - perhaps via several sub-modes
  else { // mode == 0
    if (submode[0] == 63) {
    }
    else if (submode[0] == 62) {
      // copy this check for creating a new pattern
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
          leds[i][NUM_LEDS_V - 1 - j] = CHSV(((state + (rand() % 12 - 1) + j) - 1) % 256, 255, 255);
        }
      }
      state = (state + rand() % 8) % 256;
      waitingTime = pspeed * pspeed * 62 + 8;
    }
    else if (submode[0] == 3) {
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CHSV((rand() % 12 + 256 / NUM_LEDS_V * (state + (rand() % 5 - 1) + j) - 1) % 256, 255, 255);
        }
      }
      state = (state + 1) % NUM_LEDS_V;
      waitingTime = pspeed * pspeed * 62 + 8;
    }
    else if (submode[0] == 2) {
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CHSV((7 + 256 / NUM_LEDS_V * (state + i + j) - 1) % 256, 255, 255);
        }
      }
      state = (state + (-1 + (rand() % 4))) % NUM_LEDS_V;
      waitingTime = pspeed * pspeed * 62 + 8;
    }
    else if (submode[0] == 1) {
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CRGB((7 + 256 / NUM_LEDS_V * (state + i - j) - 1 + 256) % 256, (7 + 256 / NUM_LEDS_V * (state - i - j) - 1 + 256) % 256, (7 + 256 / NUM_LEDS_V * (state + i + j) - 1) % 256);
        }
      }
      state = (state + 1) % NUM_LEDS_V;
      waitingTime = pspeed * pspeed * 62 + 8;
    }
    else { // submode[0] == 0
      for (int i = 0; i < NUM_LEDS_H; i++) {
        for (int j = 0; j < NUM_LEDS_V; j++) {
          leds[i][NUM_LEDS_V - 1 - j] = CHSV((7 + 256 / NUM_LEDS_V * (state + i + j) - 1) % 256, 255, 255);
        }
      }
      state = (state + 1) % NUM_LEDS_V;
      waitingTime = pspeed * pspeed * 62 + 8;
    }
    // delay(cspeed);
  }
  if (DEBUG_MODE) {
    Serial.print("photo: "); Serial.print(photoRSTState); Serial.print(", ");
    Serial.print("brightness: "); Serial.print((int)(photoRSTState/1023.*valueBrightness[brightness])); Serial.print(", ");
    Serial.print("time proc/show (mode: ");
    Serial.print(mode); Serial.print(", submode: "); Serial.print(submode[mode]); Serial.print("/"); Serial.print(submodeMax[mode]); Serial.print("): ");
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


void rainbow(){

}

void rain(){

}

void glitter(){

}


// ------ Tools ------


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
