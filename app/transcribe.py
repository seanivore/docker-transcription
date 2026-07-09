#!/usr/bin/env python3
"""
Watch an uploads directory and transcribe any audio/video file dropped there,
using faster-whisper (CTranslate2 — CPU, no PyTorch). Writes four outputs per
file, then moves the source into ``processed/``.

Outputs for a source ``name.ext``:
  - ``{name}_{timestamp}.json``   full result (whisper-compatible schema)
  - ``{name}_{timestamp}.txt``    plain-text lump
  - ``{name}_{timestamp}.srt``    subtitles
  - ``{name}.md``                 human-readable timestamped transcript (clean, stable name)

Model is chosen by the WHISPER_MODEL env var (default ``large-v3``).
"""

import glob
import os
import time
from datetime import datetime

from faster_whisper import WhisperModel

import formats

UPLOADS_DIR = "/data/uploads"
TRANSCRIPTIONS_DIR = "/data/transcriptions"
PROCESSED_DIR = os.path.join(UPLOADS_DIR, "processed")

MODEL_SIZE = os.getenv("WHISPER_MODEL", "large-v3")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "10"))

# Everything ffmpeg can decode. ffmpeg (baked into the image) does the actual
# decoding, so this list is broad on purpose — incl. Apple Messages ``.caf``.
AUDIO_EXTS = [
    "mp3", "wav", "m4a", "m4b", "mp4", "m4v", "mov", "mkv", "avi", "wmv",
    "mpeg", "mpga", "mp2", "webm", "ogg", "oga", "opus", "spx", "flac",
    "aac", "caf", "aiff", "aif", "amr", "wma", "3gp", "ts", "flv",
]

os.makedirs(TRANSCRIPTIONS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def log(msg: str) -> None:
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def is_stable(file_path: str, wait: float = 2.0) -> bool:
    """Avoid grabbing a file mid-copy: skip it if its size is still changing."""
    try:
        size1 = os.path.getsize(file_path)
        time.sleep(wait)
        size2 = os.path.getsize(file_path)
    except OSError:
        return False
    return size1 == size2 and size1 > 0


def transcribe_audio(model: WhisperModel, file_path: str) -> None:
    base_name = os.path.basename(file_path)
    name = os.path.splitext(base_name)[0]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    log(f"Transcribing: {base_name}")
    segments, info = model.transcribe(file_path)
    result = formats.build_result_dict(segments, info)
    log(f"  language={info.language} ({info.language_probability:.2f}), "
        f"duration={info.duration:.0f}s, segments={len(result['segments'])}")

    stem = os.path.join(TRANSCRIPTIONS_DIR, f"{name}_{ts}")
    formats.write_json(result, stem + ".json")
    formats.write_text(result, stem + ".txt")
    formats.write_srt(result, stem + ".srt")
    formats.write_markdown(result, os.path.join(TRANSCRIPTIONS_DIR, f"{name}.md"), name)
    log(f"  wrote {name}_{ts}.json/.txt/.srt + {name}.md")

    os.rename(file_path, os.path.join(PROCESSED_DIR, base_name))
    log(f"  moved {base_name} -> processed/")


def pending_files():
    for ext in AUDIO_EXTS:
        for file_path in sorted(glob.glob(os.path.join(UPLOADS_DIR, f"*.{ext}"))):
            base = os.path.basename(file_path)
            if os.path.isfile(file_path) and not base.startswith("."):
                yield file_path


def main():
    log("Starting Whisper transcription service (faster-whisper).")
    log(f"Watching: {UPLOADS_DIR}  |  model={MODEL_SIZE}  compute={COMPUTE_TYPE}")
    log("Loading model (first run downloads it to the cache volume; instant after).")
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type=COMPUTE_TYPE)
    log("Model ready. Entering watch loop.")

    while True:
        for file_path in pending_files():
            if not is_stable(file_path):
                log(f"Skipping (still copying?): {os.path.basename(file_path)}")
                continue
            try:
                transcribe_audio(model, file_path)
            except Exception as e:
                log(f"ERROR on {os.path.basename(file_path)}: {e}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
