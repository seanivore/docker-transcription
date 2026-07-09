# Auto-Transcribe

**Drop an audio or video file into a folder — get a clean, timestamped transcript back. Local, private, free.**

A self-hosted speech-to-text service built on OpenAI's Whisper (via the fast [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) runtime) and Docker. No API keys, no cloud, no cost — your audio never leaves your machine.

---

## What Makes This Special

- **Zero-ceremony workflow** — no commands to run per file. Drop a file in `data/uploads/`; the transcript appears in `data/transcriptions/`.
- **Private by design** — everything runs locally in Docker. No accounts, no uploads, no third-party service ever sees your audio.
- **Human-readable output** — alongside raw JSON, you get a clean timestamped Markdown transcript and standard `.srt` subtitles.

---

## Quick Start

```bash
# Clone
git clone https://github.com/seanivore/docker-transcriptions.git
cd docker-transcriptions

# Build + run (first launch downloads the model into a cache volume)
docker compose up -d --build

# Watch it work
docker compose logs -f whisper
```

Then just **drop a file into `data/uploads/`**. Within ~10 seconds it's transcribed.

---

## Key Features

- **Any format** — anything ffmpeg decodes: mp3, wav, m4a, mp4, mov, mkv, webm, ogg, opus, flac, aac, **caf** (Apple Messages audio), aiff, and more.
- **Four outputs per file** — `.md` (human-readable, timestamped), `.srt` (subtitles), `.txt` (plain text), `.json` (full result).
- **Accuracy dial** — defaults to the multilingual `large-v3` model; swap to a lighter one with one env var, no rebuild.
- **Robust & self-contained** — a prebuilt image means startup never depends on the network or the clock; a bad file is logged and skipped, never crashing the loop.

The timestamped Markdown looks like this:

```
# my-voice-note

[00:00:00 – 00:00:25] The types of science findings that come out that end up contradicting everything…

[00:01:52 – 00:01:59] It might even be statistically significant depending on how many people you have at work. You should do it. I love science.
```

---

## Project Structure

```text
docker-transcriptions/
├── Dockerfile              # python:3.10-slim + ffmpeg + faster-whisper
├── docker-compose.yml      # service, WHISPER_MODEL env, model cache volume
├── requirements.txt        # pinned dependencies
├── app/
│   ├── transcribe.py       # watch loop + transcription
│   ├── formats.py          # output formatters (md / srt / txt / json)
│   └── backfill.py         # regenerate md/srt from existing transcripts
├── data/                   # your files (gitignored)
│   ├── uploads/            #   drop files here → processed/ when done
│   └── transcriptions/     #   results appear here
└── assets/docs/            # architecture + roadmap docs
```

**Full documentation**: [`assets/docs/AUTO_TRANSCRIBE.md`](assets/docs/AUTO_TRANSCRIBE.md)

---

## Documentation

| Document                                                     | Description                                      |
| ------------------------------------------------------------ | ------------------------------------------------ |
| [Architecture](assets/docs/AUTO_TRANSCRIBE.md)               | Complete technical reference, run/test, pitfalls |
| [v2.0 roadmap](assets/docs/archive/v2_0/v2_0_0_IMPLEMENT.md) | Draft plan for a free public web version         |
| [Agent protocols](.agents/DEV_RULES.md)                      | Cross-project build method & conventions         |

---

## Usage Notes

- **Change the model**: edit `WHISPER_MODEL` in `docker-compose.yml` (`large-v3` · `medium` · `small` · `base` · `tiny`), then `docker compose up -d`.
- **Backfill old transcripts** with the new formats: `docker compose exec whisper python /app/backfill.py`.
- **Update dependencies**: `docker compose build --pull` (or let Dependabot open weekly PRs).
- **Turnaround** scales with audio length × model size. Short clips are quick; a long file on `large-v3` will take a while on CPU — drop to `medium` if needed.

### Remember

  Same as always — drop a file in data/uploads/. To change accuracy: edit WHISPER_MODEL in
  docker-compose.yml (→ medium if RAM ever feels tight) and docker compose up -d. Re-format old
  transcripts anytime: docker compose exec whisper python /app/backfill.py

---

## Technology Stack

- **Transcription**: OpenAI Whisper via faster-whisper (CTranslate2, CPU int8)
- **Media decoding**: ffmpeg
- **Runtime**: Python 3.10, Docker + Docker Compose

---

## License

MIT — see [LICENSE](/LICENSE).

---

## About

**Auto-Transcribe** was built by **Sean August Horvath** to turn spoken thought — voice notes, videos — into clean, agent-ready text without ads, signups, or sending private audio to anyone.

- Contact: sean@august.style
- Web: [august.style](https://august.style)
