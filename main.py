"""
Modules :
1. json - to parse the streamed response from LLAMA3 API
2. requests - to make a POST request to LLAMA3 API
3. TTS.api - to generate audio from text using TTS
"""
import json
import requests
from TTS.api import TTS

# Get DEVICE
DEVICE = "cpu"

# Init TTS
TTS = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

# Function to get user input
def get_user_input():
    """Function to get user input"""
    return input("Enter your prompt for LLAMA3: ")

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

def main():
    """Main function"""
    user_input = get_user_input()
    response = get_llama3_response(user_input)

    if response.status_code == 200:
        full_response = parse_streamed_response(response)
        print("Response from LLAMA3:")
        print(full_response)
        generate_speech(full_response)
    else:
        print("Failed to get a response from LLAMA3. Status code:", response.status_code)

if __name__ == "__main__":
    main()
