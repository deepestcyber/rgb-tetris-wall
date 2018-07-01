
//Designed for Arduino Mega

#include "FastLED.h"
#include "elapsedMillis.h"
#include "SPI.h"

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
#define SYNC_PIN 47 // SPI SYNC
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
#define WAITTIME_ISTREAM 1000 //20 1000/NUM_FRAMES_VSTREAM
#define NUM_BYTES_VSTREAM 1152
#define NUM_BYTES_ISTREAM NUM_LEDS_H*NUM_LEDS_V*3

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
//extern const CHSV currentPalette [64] = {CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216), CHSV(255, 255, 8), CHSV(255, 255, 24), CHSV(255, 255, 72), CHSV(255, 255, 216)};

byte data[NUM_BYTES_VSTREAM];
byte dataImage[NUM_BYTES_ISTREAM];
// for SPI:
volatile int spi_pos;
volatile boolean process_it;
bool sync_is_high = false;

void setup() {
  //  Communication via UART
  // Use RX1 (18) & TX1 (19)!!!
  Serial.begin(115200); //57600 115200 230400

  // turn on SPI in slave mode
  SPCR |= bit (SPE);

  // have to send on master in, *slave out*
  pinMode(MISO, OUTPUT);
  pinMode(SYNC_PIN, OUTPUT);
  digitalWrite(SYNC_PIN, LOW);

  // get ready for an interrupt
  spi_pos = 0;
  process_it = false;

  // now turn on interrupts
  SPI.attachInterrupt();

  //Set up LEDS
  if (NUM_LEDS_H > 0) FastLED.addLeds<MODEL, LEDS_PIN_0, GRB>(leds[0], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 1) FastLED.addLeds<MODEL, LEDS_PIN_1, GRB>(leds[1], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 2) FastLED.addLeds<MODEL, LEDS_PIN_2, GRB>(leds[2], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 3) FastLED.addLeds<MODEL, LEDS_PIN_3, GRB>(leds[3], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 4) FastLED.addLeds<MODEL, LEDS_PIN_4, GRB>(leds[4], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 5) FastLED.addLeds<MODEL, LEDS_PIN_5, GRB>(leds[5], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 6) FastLED.addLeds<MODEL, LEDS_PIN_6, GRB>(leds[6], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 7) FastLED.addLeds<MODEL, LEDS_PIN_7, GRB>(leds[7], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 8) FastLED.addLeds<MODEL, LEDS_PIN_8, GRB>(leds[8], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 9) FastLED.addLeds<MODEL, LEDS_PIN_9, GRB>(leds[9], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 10) FastLED.addLeds<MODEL, LEDS_PIN_10, GRB>(leds[10], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 11) FastLED.addLeds<MODEL, LEDS_PIN_11, GRB>(leds[11], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 12) FastLED.addLeds<MODEL, LEDS_PIN_12, GRB>(leds[12], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 13) FastLED.addLeds<MODEL, LEDS_PIN_13, GRB>(leds[13], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 14) FastLED.addLeds<MODEL, LEDS_PIN_14, GRB>(leds[14], NUM_LEDS_V).setCorrection(TypicalLEDStrip);
  if (NUM_LEDS_H > 15) FastLED.addLeds<MODEL, LEDS_PIN_15, GRB>(leds[15], NUM_LEDS_V).setCorrection(TypicalLEDStrip);

  for (int i = 0; i < NUM_BYTES_VSTREAM; i++) {
    data[i] = 0;
  }
  //setPaletteNES();

  delay(100);
  digitalWrite(SYNC_PIN, HIGH);
  sync_is_high = true;
}


ISR (SPI_STC_vect)
{
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

#define RGB_ENCODING 1

void loop() {
  if (process_it) {

#ifdef RGB_ENCODING
    uint8_t r, g, b;
    for (int y = 0; y < NUM_LEDS_V; y++) {
      for (int x = 0; x < NUM_LEDS_H; x++) {
        r = data[y * NUM_LEDS_H * 3 + x * 3 + 0];
        g = data[y * NUM_LEDS_H * 3 + x * 3 + 1];
        b = data[y * NUM_LEDS_H * 3 + x * 3 + 2];
        leds[x][y] = CHSV(r, g, b);
      }
    }
#else
    for (int i = 0; i < NUM_LEDS_H; i++) {
      for (int j = 0; j < NUM_LEDS_V; j += 1) {
        leds[i][j] = CHSV(data[i * NUM_LEDS_V + j], 255, valueb[brightness][3]);
      }
    }
#endif
    state = 1;
    spi_pos = 0;

    FastLED.show();

    process_it = false;
    digitalWrite(SYNC_PIN, HIGH);
    sync_is_high = true;
  }
}

