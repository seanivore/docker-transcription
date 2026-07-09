# Auto-Transcribe — Architecture Overview

`docker-transcriptions` · a self-hosted, drop-a-file speech-to-text service.

**Last Updated**: 2026-07-09 · **Version**: v1.1.0 · **Status**: shipped (local Docker); v2.0 public web tool is [spec-only].

This is the living architecture / state / pitfalls doc — a future instance's project primer. When it disagrees with a *current* IMPLEMENT, the IMPLEMENT wins (and this doc was neglected — update it). When it disagrees with a *past* IMPLEMENT, this doc wins.

---

## Executive Summary

**Purpose.** Turn an audio/video file into a clean transcript with zero ceremony: drop a file into `data/uploads/`, and a background container transcribes it and writes the results to `data/transcriptions/`, then files the source under `data/uploads/processed/`.

**Use.** Sean's primary use is voice notes → transcript → fed to an agent as project context; also YouTube/personal video (~5 min) → a good `.srt`. Everything runs **locally** via Docker + Whisper — no API keys, no cost, no upload of private audio anywhere.

---

## How this doc relates to IMPLEMENT.md

- This doc = current *state* (what is true now). `assets/docs/archive/v2_0/v2_0_0_IMPLEMENT.md` = the *plan* for the public web version (a draft, gap-reviewed toward exclusively-executable over future sessions).
- `[spec-only]` marks anything planned but not shipped.

---

## Architecture Overview

```text
        drop a file                         watch loop (10s)
  ┌───────────────────┐   ┌───────────────────────────────────────────────┐
  │  data/uploads/     │──▶│  whisper-transcription container (Docker)      │
  │   yourfile.m4a     │   │   • faster-whisper (CTranslate2, CPU, int8)   │
  └───────────────────┘   │   • ffmpeg decodes any audio/video format     │
                          │   • model = $WHISPER_MODEL (default large-v3)  │
                          └───────────────┬───────────────────────────────┘
                                          │ writes 4 outputs, moves source
                    ┌─────────────────────┴───────────────────────────────┐
                    ▼                                                       ▼
      data/transcriptions/                                    data/uploads/processed/
        yourfile_{ts}.json   (full result, whisper schema)      yourfile.m4a  (the source)
        yourfile_{ts}.txt    (plain-text lump)
        yourfile_{ts}.srt    (subtitles)
        yourfile.md          (human-readable timestamped, CLEAN stable name)
```

- **Container running Python + faster-whisper**, watching the filesystem.
- **Local filesystem** for input and output (Docker bind mounts).
- **No external API dependencies** at runtime — fully self-contained and private.

---

## Project Overview

### What this is
A Dockerized folder-watcher that auto-transcribes with OpenAI's Whisper model (via the faster-whisper runtime). File in → transcript out.

### The core innovation
Frictionless: no CLI invocation per file, no accounts, no cost. The workflow is literally "drag file into folder."

### Message & purpose
Private, self-hosted transcription for turning spoken thought into agent-ready context.

---

## Strategic Roadmap (coarse direction — not a build queue)

| Version | Theme | Ship to | Status |
| ------- | ----- | ------- | ------ |
| v1.0    | Base tool (openai-whisper, base model, txt+json) | local | shipped (original) |
| v1.1    | faster-whisper, large-v3, `.md`+`.srt`, broad file types, prebuilt image, doc modernization | local | **shipped** |
| v2.0    | Free public web tool (browser-WASM or serverless) | public | [spec-only] — see v2_0_0_IMPLEMENT.md |

---

## Recent Changes

### 2026-07 — v1.1
- Engine swapped openai-whisper → **faster-whisper** (CTranslate2; ~2–4× faster on CPU, no PyTorch, smaller image).
- Model default **base → large-v3** (multilingual, top accuracy), via `WHISPER_MODEL` env knob.
- New outputs: `{name}.md` (human-readable timestamped, clean stable name) and `.srt` subtitles.
- File-type support broadened to everything ffmpeg decodes (incl. Apple Messages `.caf`).
- Runtime `apt/pip` install replaced by a **prebuilt Dockerfile** — immune to the clock-skew failure (below).
- Robustness: mid-copy guard + per-file error isolation + timestamped logs.

---

## Architecture Explained

### High-level
`docker-compose.yml` builds the `Dockerfile` (python:3.10-slim + ffmpeg + faster-whisper) and runs `app/transcribe.py`, which loads the model once and polls `data/uploads/` every 10s.

### Key decisions
- **faster-whisper over openai-whisper**: CTranslate2 int8 is markedly faster on CPU and pulls no PyTorch — a much smaller, quicker image. `app/formats.build_result_dict()` normalizes its output back to the openai-whisper JSON shape so the `.json` schema is stable.
- **Prebuilt image, not runtime install**: apt/pip run at *build* time only. This removes the network/clock dependency from every container start.
- **Model in a cache volume** (`whisper-cache:/root/.cache/huggingface`): the ~1–3 GB model downloads once and survives rebuilds.
- **Clean `.md` name** (`{name}.md`, no timestamp) so Sean's downstream usage points at a stable path; the `.json/.txt/.srt` keep `_{timestamp}` for history.

### How it actually works
`app/transcribe.py` (watch loop) → `formats.build_result_dict()` (normalize) → `formats.write_json/text/srt/markdown()` → `os.rename()` into `processed/`. `app/backfill.py` regenerates `.md`/`.srt` for pre-existing JSON using the same `formats` module.

---

## How to Run & Test Locally

### Prerequisites
- Docker Desktop running.

### Start
```bash
docker compose up -d --build      # first run downloads the model into the cache volume
docker compose logs -f whisper    # watch it work
```

### Use
Drop a file into `data/uploads/`. Within ~10s the container transcribes it; outputs land in `data/transcriptions/`; the source moves to `data/uploads/processed/`.

### Change the model
Edit `WHISPER_MODEL` in `docker-compose.yml` (`large-v3` · `medium` · `small` · `base` · `tiny`), then `docker compose up -d`. No rebuild needed.

### Backfill old transcripts (regenerate `.md`/`.srt`)
```bash
docker compose exec whisper python /app/backfill.py
```

### Update dependencies
```bash
docker compose build --pull       # refresh base image + ffmpeg + faster-whisper
```
(Or let Dependabot open weekly bump PRs — `.github/dependabot.yml`.)

---

## File Structure & Key Files

```text
docker-transcriptions/
├── Dockerfile              # python:3.10-slim + ffmpeg + faster-whisper (prebuilt)
├── docker-compose.yml      # service def, WHISPER_MODEL env, cache volume
├── requirements.txt        # pinned faster-whisper
├── app/
│   ├── transcribe.py       # watch loop + per-file transcription
│   ├── formats.py          # shared output formatters (md/srt/txt/json + normalize)
│   └── backfill.py         # one-shot: regenerate md/srt from existing json
├── data/                   # bind-mounted; contents gitignored (private)
│   ├── uploads/            #   drop files here  (processed/ = done sources)
│   └── transcriptions/     #   outputs land here
├── assets/docs/            # this doc + archive/ (versioned STATE / IMPLEMENT)
└── .agents/                # cross-project agent protocol (DEV_RULES etc.)
```

---

## Common Pitfalls & Important Notes

### Things that look like bugs but aren't
- **"Nothing transcribes; container is `Restarting`."** Historically this was **Docker Desktop VM clock drift** (the Mac slept, the VM clock fell hours behind). The *old* setup ran `apt-get update` on every start; a behind-clock made Debian's index look future-dated ("Release file is not valid yet"), apt errored, and the `&&` startup chain died before Whisper ran. **v1.1's prebuilt image removes apt from startup, so this can't recur.** If the *host* clock is ever wrong: on macOS toggle System Settings → Date & Time auto-set off/on, or restart Docker Desktop, or `docker run --rm --privileged alpine hwclock -s`. See `.agents/PROJECT_LESSONS.md`.
- **First run is slow.** The model (~1–3 GB for large-v3) downloads once into `whisper-cache`; subsequent starts are instant.
- **Long files take a while on CPU.** Turnaround scales with audio length × model size. Sean's files are short (voice notes, ≤~5 min), so large-v3 is comfortable; a 45-min file on large-v3 would take meaningfully longer — drop to `medium` if needed.

### Important conventions
- The `.md` uses a **clean, stable name** (`{name}.md`, overwritten on re-run); the `.json/.txt/.srt` carry `_{timestamp}`.
- `data/` contents are **gitignored** — this is a public repo; private audio/transcripts stay local.

### Performance
- `WHISPER_COMPUTE_TYPE=int8` (default) is lightest on CPU/RAM. large-v3 int8 wants ~1.5–3 GB RAM.

---

## Deployment

- **v1.1**: local only, via Docker Compose. Data persists through bind mounts; the model persists in a named volume.
- **Secondary (planned)**: publish the image to GHCR so others can `docker compose up` without building.
- **v2.0 (planned)**: a free public web tool — see the IMPLEMENT draft. Primary direction: run Whisper **in the browser via WebAssembly** (no backend, free static hosting, private).

---

## Quick Reference

### Env vars
- `WHISPER_MODEL` — `large-v3` (default) · `medium` · `small` · `base` · `tiny`.
- `WHISPER_COMPUTE_TYPE` — `int8` (default) · `int8_float16` · `float32`.
- `POLL_SECONDS` — watch-loop interval (default 10).

### CLI
```bash
docker compose up -d --build            # build + run
docker compose logs -f whisper          # logs
docker compose exec whisper python /app/backfill.py   # regenerate md/srt
docker compose down                     # stop
```

### Supported input
Any format ffmpeg decodes — mp3, wav, m4a, mp4, mov, mkv, webm, ogg, opus, flac, aac, **caf**, aiff, amr, wma, 3gp, and more.

---

## Key Principles — **REMEMBER THIS**
- Startup must never depend on the network or the clock (v1.0's lesson).
- Keep the `.json` schema whisper-compatible even if the engine changes.
- Private data never enters git.

## Related Documentation
- `README.md` — showcase/quick-start.
- `assets/docs/archive/v1_1/v1_1_1_STATE.md` — v1.1 milestone snapshot.
- `assets/docs/archive/v2_0/v2_0_0_IMPLEMENT.md` — public web tool plan (draft).
- `.agents/DEV_RULES.md` — cross-project build method.
- `.agents/PROJECT_LESSONS.md` — the clock-drift lesson + `&&`-chain fragility.

*Update this doc on every non-trivial change that ships.*
