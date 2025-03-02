#!/usr/bin/env python3
"""
A simple script to transcribe audio files using OpenAI's Whisper model.
"""

import os
import glob
import json
import whisper
import time
from datetime import datetime

UPLOADS_DIR = "/data/uploads"
TRANSCRIPTIONS_DIR = "/data/transcriptions"
MODEL_SIZE = "base"  # Options: tiny, base, small, medium, large

# Ensure transcriptions directory exists
os.makedirs(TRANSCRIPTIONS_DIR, exist_ok=True)

def transcribe_audio(file_path):
    """Transcribe an audio file using Whisper."""
    print(f"Loading Whisper model: {MODEL_SIZE}")
    model = whisper.load_model(MODEL_SIZE)
    
    print(f"Transcribing file: {file_path}")
    result = model.transcribe(file_path)
    
    # Create output filename
    base_name = os.path.basename(file_path)
    name_without_ext = os.path.splitext(base_name)[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_json = os.path.join(TRANSCRIPTIONS_DIR, f"{name_without_ext}_{timestamp}.json")
    output_txt = os.path.join(TRANSCRIPTIONS_DIR, f"{name_without_ext}_{timestamp}.txt")
    
    # Save the full result as JSON
    with open(output_json, "w") as f:
        json.dump(result, f, indent=2)
    
    # Save just the text as TXT
    with open(output_txt, "w") as f:
        f.write(result["text"])
    
    print(f"Transcription complete. Results saved to {output_json} and {output_txt}")
    
    # Move the processed file to a "processed" subdirectory
    processed_dir = os.path.join(UPLOADS_DIR, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    new_location = os.path.join(processed_dir, base_name)
    os.rename(file_path, new_location)
    print(f"Moved {file_path} to {new_location}")

def main():
    """Main function that watches for new files and transcribes them."""
    print("Starting Whisper transcription service...")
    print(f"Watching directory: {UPLOADS_DIR}")
    print(f"Using model: {MODEL_SIZE}")
    
    # First, process any existing files
    for ext in ["mp3", "wav", "m4a", "mp4", "mpeg", "mpga", "webm", "ogg"]:
        pattern = os.path.join(UPLOADS_DIR, f"*.{ext}")
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path) and not os.path.basename(file_path).startswith('.'):
                transcribe_audio(file_path)
    
    # Then enter watch mode
    print("Initial processing complete. Entering watch mode...")
    
    while True:
        for ext in ["mp3", "wav", "m4a", "mp4", "mpeg", "mpga", "webm", "ogg"]:
            pattern = os.path.join(UPLOADS_DIR, f"*.{ext}")
            for file_path in glob.glob(pattern):
                if os.path.isfile(file_path) and not os.path.basename(file_path).startswith('.'):
                    transcribe_audio(file_path)
        
        # Wait before checking again
        time.sleep(10)

if __name__ == "__main__":
    main() 