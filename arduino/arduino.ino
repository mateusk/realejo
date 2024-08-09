const int buttonPin = 2;  // the pushbutton pin
const int ledsPin =  13;  // the LED pin

int buttonState;            // the current reading from the input pin
int lastButtonState = LOW;  // the previous reading from the input pin

int ledOutput = 0;
int ledSleepTimeIdle = 1000;
int ledSleepInteraction = 200;

bool buttonPressed = false;
unsigned long buttonPressedBlockTime = 10000;

int ledMaxOutput = 255;
int ledMinOutput = 0;

unsigned long lastDebounceTime = 0;  // the last time the output pin was toggled
unsigned long debounceDelay = 50;    // the debounce time; increase if the output flickers

unsigned long previousMillisLed = 0;
unsigned long previousMillisButton = 0;

void setup() {
  pinMode(buttonPin, INPUT);

  Serial.begin(9600);
}

void loop() {
  // read the state of the switch into a local variable:
  int reading = digitalRead(buttonPin);

  // check to see if you just pressed the button
  // (i.e. the input went from LOW to HIGH), and you've waited long enough
  // since the last press to ignore any noise:

  // If the switch changed, due to noise or pressing:
  if (reading != lastButtonState) {
    // reset the debouncing timer
    lastDebounceTime = millis();
  }

  updateLed();

  if(buttonPressed) {
      unsigned long currentMillis = millis();
      if (currentMillis - previousMillisButton >= buttonPressedBlockTime) {
        previousMillisButton = currentMillis;
        buttonPressed = false;
      }
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    // whatever the reading is at, it's been there for longer than the debounce
     // delay, so take it as the actual current state:

    // if the button state has changed:
    if (reading != buttonState && !buttonPressed) {
      buttonState = reading;

      // only toggle the LED if the new button state is HIGH
      if (buttonState == HIGH) {
        Serial.println("button pressed");
        buttonPressed = true;
      }
    }
  }

  // save the reading. Next time through the loop, it'll be the lastButtonState:
  lastButtonState = reading;
}

void updateLed() {
  int interval = buttonPressed ? ledSleepInteraction : ledSleepTimeIdle;

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillisLed >= interval) {

    // save the last time you blinked the LED
    previousMillisLed = currentMillis;

    // if the LED is off turn it on and vice-versa:
    if (ledOutput == ledMaxOutput) {
      ledOutput = ledMinOutput;
    } else {
      ledOutput = ledMaxOutput;
    }
  }

  analogWrite(ledsPin, ledOutput);

}