# Docker Transcriptions

A self-hosted speech-to-text transcription service using Whisper AI and Docker.

## Overview

This project provides a simple Docker-based solution for transcribing audio files using OpenAI's Whisper speech recognition model. It features a web interface where you can upload audio files, generate accurate transcriptions, and export them in various formats.

## Features

- Web-based user interface
- Support for multiple audio formats
- High-quality transcription using Whisper AI
- Export options (TXT, SRT, VTT)
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

2. Create the data directory:
   ```bash
   mkdir -p data
   ```

3. Start the service:
   ```bash
   docker-compose up -d
   ```

4. Access the web interface:
   Open your browser and navigate to http://localhost:8080

5. Upload your audio file, configure settings if needed, and start transcription

## Usage

1. **Upload**: Select an audio file from your computer
2. **Configure**: Adjust settings if needed (model size, language, etc.)
3. **Transcribe**: Start the transcription process
4. **Edit**: Make corrections to the transcription if needed
5. **Export**: Download the transcription in your preferred format

## Stopping the Service

To stop the service, run:
```bash
docker-compose down
```

## Project Structure

See the [PROJECT_MAP.md](PROJECT_MAP.md) file for details about the project structure and components.

## License

This project is open-source and available under the MIT License.

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) - The underlying speech recognition model
- [Whishper](https://github.com/pluja/whishper) - The web interface for Whisper