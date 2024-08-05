#include <SCServo.h>
#include <SoftwareSerial.h>

const int buttonPin = 2;    // Pin connected to the button

// Define the RX and TX pins for SoftwareSerial
const int servoRxPin = 13;
const int servoTxPin = 12;

// Initialize the SoftwareSerial for servo communication
SoftwareSerial mySerial(servoRxPin, servoTxPin);

// Create an instance of the SCSCL class
SCSCL sc;

void setup() {
  // Initialize serial communication for debugging
  Serial.begin(9600);
  Serial.println("Serial Monitor");

  // Initialize SoftwareSerial communication with the servo
  mySerial.begin(1000000);
  sc.pSerial = &mySerial; // Set the serial interface for the SCServo library

  // Set the button pin as input
  pinMode(buttonPin, INPUT);

  // Wait for a short period to allow everything to initialize
  delay(2000);

  // Enable torque on the servo
  int result = sc.EnableTorque(1, 1); // Enable torque on servo with ID 1
  if (result == -1) {
    Serial.println("Failed to enable torque");
  } else {
    Serial.println("Torque enabled");
  }

  // Check if the servo is connected and responding
  int pingResult = sc.Ping(1);
  if (pingResult == -1) {
    Serial.println("Failed to ping servo");
  } else {
    Serial.println("Servo ping successful");
  }

  // Debugging message
  Serial.println("Setup complete");
}

void loop() {
  // Get button state
  int buttonState = digitalRead(buttonPin);

  // Print out the state of the button
  Serial.println(buttonState);
  delay(100); // Delay in between reads for stability

  // If button is pressed
  if (buttonState == HIGH) {
    Serial.println("Button pressed. Moving servo to 1000.");
    int result = sc.WritePos(1, 1000, 0, 1500); // Move to position 1000
    if (result == -1) {
      Serial.println("Failed to move to position 1000");
    } else {
      Serial.println("Moved to position 1000");
    }
    delay(754); // Wait for the movement to complete

    Serial.println("Moving servo to 20.");
    result = sc.WritePos(1, 20, 0, 1500); // Move to position 20
    if (result == -1) {
      Serial.println("Failed to move to position 20");
    } else {
      Serial.println("Moved to position 20");
    }
    delay(754); // Wait for the movement to complete
  }

  delay(100); // Small delay for stability
}