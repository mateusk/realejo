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
  "May the wisdom of the reading guide you and the light of the future inspire you.",
  "You face the chaos, seeking wisdom’s glow, the omens will guide, let’s see where you’ll go."
]

def generate_speech(text_array):
    """Function to generate prerecorded TTS for the given text array"""
    for idx, text in enumerate(text_array):
        TTS.tts_to_file(text, speaker_wav="tts/voice-cloning/ref.wav", language="en", file_path=f"tts/pre-recorded/idle/output_{idx}.wav")

    print("Audio saved as output_*.wav")

def main():
    """Main function"""
    generate_speech(TEXT_ARRAY)

if __name__ == "__main__":
    main()

