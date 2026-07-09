FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ffmpeg decodes every audio/video format Whisper ingests.
# `-o Acquire::Check-Date=false` makes the build resilient to Docker Desktop VM
# clock skew — the exact failure that took the old run-apt-on-every-start setup
# down (Debian's "Release file is not valid yet"). apt now only runs at BUILD
# time, so a drifted clock can no longer break transcription at startup.
RUN apt-get -o Acquire::Check-Date=false update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Bake the app in so a published image is self-contained; docker-compose also
# bind-mounts ./app for local hot-editing (the mount wins when present).
COPY app/ /app/

WORKDIR /app
CMD ["python", "/app/transcribe.py"]
