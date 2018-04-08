
#include <SPI.h>

char buf [288];
volatile byte pos;
volatile boolean process_it;
int cnt = 0;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);
  
  // turn on SPI in slave mode
  SPCR |= bit (SPE);

  // have to send on master in, *slave out*
  pinMode(MISO, OUTPUT);

  // get ready for an interrupt 
  pos = 0;   // buffer empty
  process_it = false;

  // now turn on interrupts
  SPI.attachInterrupt();
  
  // give time to set up:
  delay(100);
}

// SPI interrupt routine
ISR (SPI_STC_vect)
{
byte c = SPDR;  // grab byte from SPI Data Register

  // add to buffer if room
  if (pos < sizeof buf)
    {
    buf [pos++] = c;

    // example: newline means time to process buffer
    if (c == '\n')
      process_it = true;

    }  // end of room available
}  // end of interrupt routine SPI_STC_vect

// main loop - wait for flag set in interrupt routine
void loop (void)
{
  int i, c;
  //delay(1);
  if (process_it)
  { buf[pos]=0;
    if (cnt == 0)
    {
      Serial.println(buf);
    }
    pos = 0;
    cnt = (cnt+1)%256;
    process_it = false;
  }  // end of flag set
}  // end of loop

