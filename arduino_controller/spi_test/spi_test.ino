
#include <SPI.h>

#define BUFSZ 288
char buf [BUFSZ];
volatile byte pos;
volatile boolean processing;
int cnt = 0;
const int SYNC_PIN = 47;

void setup() {
  Serial.begin(115200);
  
  // turn on SPI in slave mode
  SPCR |= bit (SPE);

  // have to send on master in, *slave out*
  pinMode(MISO, OUTPUT);
  pinMode(SYNC_PIN, OUTPUT);

  // get ready for an interrupt 
  pos = 0;
  processing = false;

  // now turn on interrupts
  SPI.attachInterrupt();
  
  // give time to set up:
  delay(100);
}

volatile bool foo = false;

ISR (SPI_STC_vect)
{
  byte c = SPDR;  // grab byte from SPI Data Register

  if (processing) {
    return;
  }

  digitalWrite(SYNC_PIN, LOW);
  //digitalWrite(13, LOW);

  if (c == '\n') {
    processing = true;
    return;
  }

  if (pos < BUFSZ) {
    buf[pos++] = c;
  }
}


void loop (void)
{
  int i, c;
  
  if (processing) {
    /*
    if (!foo) {
      digitalWrite(13, HIGH);
      foo = !foo;
    } else {
      digitalWrite(13, LOW);
      foo = !foo;
    }
    */
    
    buf[pos] = 0;
    if (cnt == 0) {
      Serial.println(pos);
    }
    
    pos = 0;
    cnt = (cnt + 1) % 256;

    delay(12);
    digitalWrite(SYNC_PIN, HIGH);
    //digitalWrite(13, HIGH);

    processing = false;
  }
}

