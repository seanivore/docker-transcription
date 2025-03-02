# Docker Transcriptions Project Map

## Project Overview
A self-hosted speech-to-text transcription service using Whisper AI and Docker. This service provides a web interface for uploading audio files, generating accurate transcriptions, and exporting them in various formats.

## Directory Structure
```text
/docker-transcriptions
├── docker-compose.yml     # Main Docker configuration
├── .env                   # Environment variables (if needed)
├── data/                  # Persistent storage for uploaded files and transcriptions
│   ├── uploads/           # Audio files uploaded by users
│   └── transcriptions/    # Generated transcription files
├── config/                # Configuration files (if needed)
└── docs/                  # Project documentation
    └── PROJECT_MAP.md     # This file
```

## Component Relationships
- Docker container running Whisper Web UI (whishper)
- Local filesystem for persistent storage
- Web interface accessible via browser

## Key Files
### Core Components
- `docker-compose.yml`: Main configuration file that defines the Docker service
- `.env`: (Optional) Environment variables for customization

### Configuration
- `config/`: May contain additional configuration files depending on customization needs

### Documentation
- `docs/PROJECT_MAP.md`: Overview of the project structure and workflow
- `docs/USAGE.md`: Instructions for using the transcription service (to be created)

## Integration Points
- Web browser for accessing the UI
- Audio files as input (MP3, WAV, etc.)
- Text files as output (TXT, SRT, VTT, etc.)

## Development Workflow
1. Modify docker-compose.yml as needed
2. Run/restart the Docker container
3. Access the web UI via browser
4. Upload audio files for transcription
5. Download or export transcription results

## Usage Workflow
1. Start the Docker container
2. Access the web interface via browser (typically http://localhost:8080)
3. Upload audio file
4. Adjust transcription settings if needed
5. Generate transcription
6. Edit transcription if needed
7. Export in desired format

## Deployment Architecture
- Runs locally via Docker
- Accessible via web browser
- Data persistence through Docker volumes
- No external API dependencies (fully self-contained)

## Technical Requirements
- Docker and Docker Compose installed
- Sufficient disk space for audio files and models
- Sufficient RAM for running Whisper AI models
- Network connectivity for initial Docker image download