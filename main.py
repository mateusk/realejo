"""
Modules:
- TTS: Text-to-Speech
- bleak: Bluetooth Low Energy
- requests: HTTP requests
- threading: Multithreading
- asyncio: Asynchronous I/O
- queue: Thread-safe queue
- serial: Serial communication
- pygame: Audio playback
- PIL: Image manipulation
"""

import json
import os
import sys
import time
import random
from enum import Enum
import threading
import asyncio
import queue
import requests
import serial
import pygame
from TTS.api import TTS
from bleak import BleakScanner, BleakClient
from PIL import Image, ImageFont, ImageDraw, ImageColor

# Set the device to use for TTS
TTS_DEVICE = "cpu"

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

class State(Enum):
    """Enum class to represent the state of the program"""
    IDLE = 1
    INTERACTION = 2

state = State.IDLE

DEBUG = True

FONT = "fonts/CrimsonPro-Regular.ttf"

# Set up the Arduinoserial connection variables
arduino: serial.Serial = None # type: ignore
ARDUINO_PORT = "/dev/tty.usbmodem14401"

# Track generated poem files
generated_poems_count = len(
    [f for f in os.listdir("tts/generated-poems") if f.endswith(".wav")])

stop_idle_event = threading.Event()
stop_button_event = threading.Event()
stop_audio_event = threading.Event()
state_lock = threading.Lock()

button_thread = None
idle_thread = None
audio_queue = queue.Queue()
audio_playback_thread = None
audio_playback_lock = threading.Lock()
current_audio_playback = None

# Init TTS
TTS = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(TTS_DEVICE)

PRINTER_DATA_FORMATTER = "m02_printer_data_formatter.py"

SKIP_TTS_PRINTING = False

# ------------- Poem generation and LLAMA3 API-related functions ---------------

def get_topic():
    """Select a random prompt from the pre-defined list"""
    return random.choice(TOPICS)

def get_llama3_response(prompt):
    """Make a POST request to LLAMA3 API"""
    api_endpoint = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "options": {"num_ctx": 4096}
    }

    try:
        if DEBUG:
            print("Sending request to LLAMA3 API...")
        response = requests.post(api_endpoint,
                                 headers=headers,
                                 json=payload,
                                 stream=True,
                                 timeout=100)

        if DEBUG:
            print("Response from LLAMA3 API:", response.status_code)
        return response
    except Exception as e:
        print(f"Error in get_llama3_response: {e}")
        return None

def parse_streamed_response(response):
    """Parse the streamed response from LLAMA3 API"""
    full_response = ""
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            json_obj = json.loads(decoded_line)
            if "response" in json_obj:
                full_response += json_obj["response"]
    return full_response

# ----------------------- TTS generation functions -----------------------------

def generate_tts(text):
    """Generate audio from text using TTS"""
    global generated_poems_count
    generated_poems_count += 1
    file_path = f"tts/generated-poems/poem-{generated_poems_count}.wav"
    try:
        TTS.tts_to_file(text, speaker_wav="tts/voice-cloning/ref.wav", language="en", file_path=file_path) # type: ignore
        if DEBUG:
            print(f"Audio saved as {file_path}")
    except Exception as e:
        print(f"Error generating speech: {e}")

# ----------------------- Printing-related functions ---------------------------

def generate_image_from_text(
    text: str,
    font_path: str):
    """Generate an image from text"""

    # Set the image size
    image_size = (256, 400)
    padding = 10

    font_size = 20

    # Set the font
    font = ImageFont.truetype(font_path, font_size)

    # Create the image
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)

    # Wrap the text
    wrapped_text = wrap_text(text, font, image_size[0] - 2 * padding)

    # Calculate text position
    text_position = (padding, padding)

    # Draw the text on the image
    draw.multiline_text(text_position, wrapped_text, font=font, fill=ImageColor.getrgb("black"))

    # Save the image
    image.save(f"generated-poems/img/poem-{generated_poems_count}.png")

    print(f"Text image saved with font size: {font_size}")

# Method to find the bluetooth printer device
async def find_printer():
    """Find the printer device"""
    if DEBUG:
        print("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover()

    target_device = None
    for device in devices:
        if device.name == "Mr.in_M02":
            target_device = device
            break

    if not target_device:
        return None

    if DEBUG:
        print("Found the printer:", target_device)
    return target_device

# Function to handle printing process
async def print_file(device, data_formatter_script_loc, file_path):
    """Try to print the file"""
    try:
        async with BleakClient(device) as client:
            if DEBUG:
                print("Connected to", device)

            # Discover services
            services = client.services

            #if DEBUG:
                #print("Services:", services)

            char0 = None
            char1 = None

            for service in services:
                for char in service.characteristics:
                    # if DEBUG:
                    #     print(f"Characteristic {char.uuid}: {char}")
                    # char0 should start with 0000ff01
                    if char.uuid.startswith("0000ff01"):
                        char0 = char.uuid
                    # char1 should start with 0000ff02
                    if char.uuid.startswith("0000ff02"):
                        char1 = char.uuid

            # if DEBUG:
            #     print("Characteristics:", char0, char1)

            # Write the data
            path_pho = file_path + ".pho"

            command = f"python3 {data_formatter_script_loc} {file_path} > {path_pho}"
            os.system(command)
            if DEBUG:
              print("Data written to printer")

            # Write data to characteristic

            with open(path_pho, "rb") as f:
                data = f.read()

                # if DEBUG:
                #     print("Data bytes:", len(data))
                #     print("Data:", data)

                # Write the data
                await client.write_gatt_char(char1, data, response=True) # type: ignore

                # Check if the data was written
                await client.read_gatt_char(char0) # type: ignore

            # Remove the file
            os.remove(path_pho)

    except Exception as e:
        print(f"Failed to connect or print: {e}")

# Function to wrap text to fit within the specified width,
# while still keeping original line breaks
def wrap_text(text, font, max_width):
    """Wrap text to fit within the specified width, while still keeping original line breaks"""
    lines = text.split("\n")
    wrapped_lines = []
    for line in lines:
        words = line.split()
        wrapped_line = ""
        for word in words:
            wrapped_line_test = wrapped_line + word + " "
            wrapped_line_test_bbox = font.getbbox(wrapped_line_test)
            if wrapped_line_test_bbox[2] <= max_width:
                wrapped_line = wrapped_line_test
            else:
                wrapped_lines.append(wrapped_line)
                wrapped_line = word + " "
        wrapped_lines.append(wrapped_line)
    return "\n".join(wrapped_lines)

# --------------- Audio thread and playback control functions -----------------

class AudioPlayer(threading.Thread):
    def __init__(self, stop_event, audio_queue, playback_lock):
        super().__init__()
        self.stop_event = stop_event
        self.audio_queue = audio_queue
        self.playback_lock = playback_lock
        self.current_audio_file = None
        pygame.mixer.init()

    def run(self):
        while not self.stop_event.is_set():
            try:
                # Try to get an audio file from the queue
                audio_file = self.audio_queue.get(timeout=1)
                if audio_file is None:
                    break

                self.play_audio(audio_file)
                self.audio_queue.task_done()
            except queue.Empty:
                # If the queue is empty, sleep briefly to avoid high CPU usage
                time.sleep(1)

        print("Audio playback thread exiting...")

    def play_audio(self, audio_file):
        """Play an audio file and handle stopping the current playback if needed."""
        try:
            with self.playback_lock:
                # Stop the current playback if it exists
                pygame.mixer.music.stop()

                # Load and play the new audio file
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                self.current_audio_file = audio_file
                
                # Wait for the playback to finish
                while pygame.mixer.music.get_busy():
                    if self.stop_event.is_set():
                        pygame.mixer.music.stop()
                        break
                    pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"Error playing audio file {audio_file}: {e}")

def start_audio_playback_thread():
    global audio_playback_thread, stop_audio_event, audio_queue, audio_playback_lock
    stop_audio_event.clear()
    audio_playback_thread = AudioPlayer(stop_audio_event, audio_queue, audio_playback_lock)
    audio_playback_thread.start()

def stop_audio_playback_thread():
    global audio_playback_thread, stop_audio_event
    if audio_playback_thread:
        stop_audio_event.set()
        # Ensure the thread exits if it's waiting on the queue
        audio_queue.put(None)  
        audio_playback_thread.join()
        print("Audio playback thread stopped.")

# --------------- Function to monitor button press from Arduino ----------------

def monitor_button_press():
    """Monitor the button press from Arduino"""
    global state, stop_button_event
    while not stop_button_event.is_set():
        try:
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').rstrip()
                # if DEBUG:
                #     print("Line from Arduino:", line)
                if line == "button pressed":
                    with state_lock:
                        if state == State.IDLE:
                            if DEBUG:
                                print("Button pressed!")
                            state = State.INTERACTION

                            # Set the stop event to stop the idle flow
                            stop_idle_event.set()  # Stop idle flow
                            stop_button_event.set()  # Stop button monitoring
                            
                            break
        except Exception as e:
            print(f"Error in monitor_button_press: {e}")

        time.sleep(0.1)

def start_button_monitoring():
    """Start the button monitoring thread"""
    global button_thread, stop_button_event

    stop_button_event.clear()

    if DEBUG:
        print("Starting the button monitoring thread...")
    button_thread = threading.Thread(target=monitor_button_press)
    button_thread.daemon = True
    button_thread.start()

def stop_button_monitoring():
    """Stop the button monitoring thread"""
    global stop_button_event

    if DEBUG:
        print("Stopping the button monitoring thread...")
    stop_button_event.set()
    if button_thread:
        button_thread.join()

# --------------- Idle flow and interaction flow functions ---------------------

def run_idle_flow():
    """Run the idle flow and ensure continuous playback."""
    try:
        while not stop_idle_event.is_set():
            if state == State.IDLE:
                # Create a list of .wav files from the audio folder
                audio_files = [f for f in os.listdir("audio/realejo") if f.endswith(".wav")]
                if audio_files:
                    audio_file = "audio/realejo/" + random.choice(audio_files)
                    audio_queue.put(audio_file)
                    time.sleep(1)  # Adjust the interval as needed

                # Change the list of audio files to the pre-recorded TTS files
                audio_files = [f for f in os.listdir("tts/pre-recorded") if f.endswith(".wav")]
                if audio_files:
                    audio_file = "tts/pre-recorded/" + random.choice(audio_files)
                    audio_queue.put(audio_file)
                    time.sleep(3)  # Adjust the interval as needed

    except Exception as e:
        if DEBUG:
            print(f"Error in run_idle_flow: {e}")


def start_idle_flow():
    """Start the idle flow thread"""
    global idle_thread, stop_idle_event

    stop_idle_event.clear()

    if DEBUG:
        print("Starting the idle flow thread...")
    idle_thread = threading.Thread(target=run_idle_flow)
    idle_thread.daemon = True
    idle_thread.start()

def stop_idle_flow():
    """Stop the idle flow thread"""
    global stop_idle_event

    if DEBUG:
        print("Stopping the idle flow thread...")
    stop_idle_event.set()
    if idle_thread:
        idle_thread.join()

async def run_interaction_flow():
    """Main flow of the program"""
    global state
    if DEBUG:
        print("Running the interaction flow...")
    topic = get_topic()
    prompt = PROMPT_PREFIX + topic + PROMPT_SUFFIX
    if DEBUG:
        print("Prompt to LLAMA3:", prompt)

    response = get_llama3_response(prompt)

    if response and response.status_code == 200:
        poem = parse_streamed_response(response)
        
        if DEBUG:
            print("Poem generated:", poem)
        
        # if DEBUG:
        #     print("Generating speech from response...")
        
        if not SKIP_TTS_PRINTING:
            if DEBUG:
                print("Generating speech from response...")
            generate_tts(poem)

            # Generate a .txt file with the poem
            if DEBUG:
                print("Saving the poem as a .txt file...")
            with open(f"generated-poems/txt/poem-{generated_poems_count}.txt",
                    "w", encoding="utf-8") as file:
                file.write(poem)

            # Generate a 256x256 image with the text of the poem
            if DEBUG:
                print("Generating an image from the poem...")
            generate_image_from_text(poem, FONT)

            # Print the poem
            if DEBUG:
                print("Printing the poem...")
            printer = await find_printer()

            # The printer is sometimes not found, so we need to loop
            # until it is found
            while not printer:
                print("Error: printer not found. Trying again...")
                printer = await find_printer()

            if printer:
                await print_file(
                  printer, PRINTER_DATA_FORMATTER,
                  f"generated-poems/img/poem-{generated_poems_count}.png")

    else:
        print("Failed to get a response from LLAMA3 or invalid response.",
              "Status code:", response.status_code if response else "N/A")

    if DEBUG:
        print("End of interaction flow.")

# ---------------------------- Main Function -----------------------------------

def main():
    """Main function"""
    global button_thread, audio_playback_thread, state, stop_idle_event, stop_button_event, arduino, idle_thread, audio_queue, state_lock
    
    try:
        arduino = serial.Serial(ARDUINO_PORT, 9600)
    except Exception as e:
        print(f"Failed to connect to Arduino: {e}")
        sys.exit(1)

    while True:
        try:
            if state == State.IDLE:
                # If audio playback thread is not running, start it
                if audio_playback_thread is None or not audio_playback_thread.is_alive():
                    start_audio_playback_thread()
                
                # If the button monitoring thread is not running, start it
                if button_thread is None or not button_thread.is_alive():
                    start_button_monitoring()

                # If the idle flow thread is not running, start it
                if idle_thread is None or not idle_thread.is_alive():
                    start_idle_flow()

            elif state == State.INTERACTION:
                if button_thread is not None and button_thread.is_alive():
                    stop_button_monitoring()

                if idle_thread is not None and idle_thread.is_alive():
                    stop_idle_flow()

                if audio_playback_thread is not None and audio_playback_thread.is_alive():
                    stop_audio_playback_thread()

                asyncio.run(run_interaction_flow())

                if DEBUG:
                    print("Resuming idle state...")
                with state_lock:
                    state = State.IDLE

            time.sleep(0.1)
            
        # On KeyboardInterrupt, break the loop and exit
        except KeyboardInterrupt:
            print("Exiting...")
            
            if arduino.is_open:
                arduino.close()
            
            if button_thread is not None and button_thread.is_alive():
                    stop_button_monitoring()

            if idle_thread is not None and idle_thread.is_alive():
                stop_idle_flow()

            if audio_playback_thread is not None and audio_playback_thread.is_alive():
                stop_audio_playback_thread()
                
            if audio_queue:
                audio_queue.put(None)
        
            break 
        
        except Exception as e:
            print(f"Error in main loop: {e}")
    
if __name__ == "__main__":
    main()
    
    # Close the serial connection
    if arduino.is_open:
        arduino.close()
    
    # Stop the audio playback thread
    if audio_playback_thread:
        stop_audio_playback_thread()
