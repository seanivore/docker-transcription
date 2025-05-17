# Docker Transcriptions

A self-hosted speech-to-text transcription service using OpenAI's Whisper AI and Docker.

## Overview

This project provides a simple Docker-based solution for transcribing audio files using OpenAI's Whisper speech recognition model. It monitors a directory for new audio files, automatically transcribes them, and saves the results in both text and JSON formats.

## Features

- Simple file-based workflow
- Support for multiple audio formats (MP3, WAV, M4A, etc.)
- High-quality transcription using Whisper AI
- Multiple model sizes available for different accuracy/speed tradeoffs
- No API keys or external services required
- Fully self-hosted and private

## Requirements

- Docker and Docker Compose installed
- At least 2GB of RAM available
- Sufficient disk space for audio files and models

## Getting Started

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/docker-transcriptions.git
   cd docker-transcriptions
   ```

2. Create the necessary directories:
   ```bash
   mkdir -p data/uploads data/transcriptions
   ```

3. Start the service:
   ```bash
   docker-compose up -d
   ```

## Usage

1. Place your audio files in the `data/uploads` directory
2. The service automatically processes any audio files it finds
3. Transcriptions are saved in `data/transcriptions` as both JSON and TXT files
4. Processed files are moved to `data/uploads/processed`

### Supported Audio Formats

- MP3
- WAV
- M4A
- MP4
- MPEG
- MPGA
- WEBM
- OGG

### Changing the Model Size

To change the model size, edit the `MODEL_SIZE` variable in `app/transcribe.py`:

```python
MODEL_SIZE = "base"  # Options: tiny, base, small, medium, large
```

Larger models provide better accuracy but require more resources and are slower.

## Stopping the Service

To stop the service, run:
```bash
docker-compose down
```

## License

This project is open-source and available under the MIT License.

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) - The underlying speech recognition model