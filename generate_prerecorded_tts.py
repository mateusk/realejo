# This script generates prerecorded TTS for the given text array
# using TTS API

"""
Modules :
1. TTS - TTS API
"""

from TTS.api import TTS

# Get DEVICE
DEVICE = "cpu"

# Init TTS
TTS = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

TEXT_ARRAY = [
  "Discover your future with a joyful poem! Step right up!",
  "Let a happy verse reveal what lies ahead for you!",
  "Brighten your day with a joyful glimpse into your future!",
  "A poem for your future, filled with joy and wonder!",
  "Curious about your future? Get a cheerful poem right here!",
  "Unlock the joy of your future with a delightful poem!",
  "Step closer and let a happy rhyme reveal your destiny!",
  "Embrace the future with a joyful verse! Come and see!",
  "Find out what joy the future holds with a personalized poem!",
  "A joyful future awaits! Let a poem show you the way!"
]

def generate_speech(text_array):
    """Function to generate prerecorded TTS for the given text array"""
    for idx, text in enumerate(text_array):
        TTS.tts_to_file(text, speaker_wav="tts/voice-cloning/ref.wav", language="en", file_path=f"tts/pre-recorded/output_{idx}.wav")

    print("Audio saved as output_*.wav")

def main():
    """Main function"""
    generate_speech(TEXT_ARRAY)

if __name__ == "__main__":
    main()
