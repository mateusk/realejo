"""
Modules :
1. json - to parse the streamed response from LLAMA3 API
2. requests - to make a POST request to LLAMA3 API
3. TTS.api - to generate audio from text using TTS
"""
import json
import random
import requests
from TTS.api import TTS
import serial

# Get DEVICE
DEVICE = "cpu"

# Set pre-defined topics to generate poems
TOPICS = [
    "a rainy day at a sex shop in Berlin",
    "a toaster that does not work",
    "a one eyed cat looking through an eyewear shop window",
    "stomach ache after an incredible meal",
    "the line at the Döner Kebab shop",
    "a washed-up and unreadable note in the pocket of some jeans",
    "a second hand pullover in summer, standing in the sun",
    "someone's first day at a sauna",
    "a yellowed-leaf monstera plant in a butcher shop",
    "a silly origami bird left in a S-Bahn",
    "a weird TikTok trend",
]

PROMPT_PREFIX = "Write a short, joyful 5 line poem about "
PROMPT_SUFFIX = ". Do not give me any comments from your side. Just write the poem."

ARDUINO = serial.Serial('/dev/tty.usbmodem141101', 9600)

tts_output_file_counter = 0

can_generate = True

# Init TTS
TTS = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

# Select random topic from the pre-defined list
def get_topic():
    """Function to select a random prompt from the pre-defined list"""
    return random.choice(TOPICS)

# Function to make a POST request to LLAMA3 API
def get_llama3_response(prompt):
    """Function to make a POST request to LLAMA3 API"""
    api_endpoint = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
      "model": "llama3",
      "prompt": prompt,
      "options": {
        "num_ctx": 4096
      }
    }

    response = requests.post(api_endpoint, headers=headers, json=payload, stream=True, timeout=10)
    return response
   

def parse_streamed_response(response):
    """Function to parse the streamed response from LLAMA3 API"""
    full_response = ""

    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            json_obj = json.loads(decoded_line)
            if "response" in json_obj:
                full_response += json_obj["response"]

    return full_response

def generate_speech(text):
    """Function to generate audio from text using TTS"""
    TTS.tts_to_file(text, speaker_wav="InGhetto.wav", language="en", file_path="output.wav")

    print("Audio saved as output.wav")

def read_serial():
    """Function to read serial data from Arduino"""
    if ARDUINO.in_waiting > 0:
        line = ARDUINO.readline().decode('utf-8').rstrip()
        print("Line from Arduino:", line)
        if line == "1":
            return True

    else:
        return False

def run_main_flow():
    """Main flow of the program"""
    topic = get_topic()
    prompt = PROMPT_PREFIX + topic + PROMPT_SUFFIX
    print("Prompt to LLAMA3:")
    print(prompt)

    response = get_llama3_response(prompt)

    if response.status_code == 200:
        full_response = parse_streamed_response(response)
        print("Response from LLAMA3:")
        print(full_response)
        generate_speech(full_response)

    else:
        print("Failed to get a response from LLAMA3. Status code:", response.status_code)


def main():
    """Main function"""
    global can_generate
    
    while True: # monitor button
        if can_generate:
            button_pressed = read_serial()
        print("Button pressed:", button_pressed)
        if button_pressed and can_generate:

            can_generate = False
            run_main_flow()
            can_generate = True

if __name__ == "__main__":
    main()
