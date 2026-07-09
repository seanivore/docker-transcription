# docker-transcriptions — Project Map

A self-hosted, drop-a-file speech-to-text service: Docker + faster-whisper (OpenAI Whisper). Drop audio/video into `data/uploads/`; get `.md` / `.srt` / `.txt` / `.json` transcripts in `data/transcriptions/`; the source moves to `data/uploads/processed/`. Fully local, private, no API keys, no cost.

## Living docs (read these first)
- **Architecture / state / pitfalls** → `assets/docs/AUTO_TRANSCRIBE.md` — the source of truth.
- **Agent build method** → `.agents/DEV_RULES.md`; agent personality/context → `.agents/AGENTS.md`.
- **Project lessons** (the clock-drift gotcha) → `.agents/PROJECT_LESSONS.md`.
- **v2.0 public web tool** (draft plan) → `assets/docs/archive/v2_0/v2_0_0_IMPLEMENT.md`.

## Key files
- `app/transcribe.py` — watch loop + per-file transcription.
- `app/formats.py` — output formatters (md / srt / txt / json + result-dict normalization).
- `app/backfill.py` — regenerate `.md`/`.srt` from existing JSON.
- `Dockerfile` · `docker-compose.yml` (`WHISPER_MODEL` env, model cache volume) · `requirements.txt`.

## Run
`docker compose up -d --build` → drop files in `data/uploads/` → results in `data/transcriptions/`.
Change model: `WHISPER_MODEL` in `docker-compose.yml`. Backfill: `docker compose exec whisper python /app/backfill.py`.

## Guardrails
- `data/` is **gitignored** — private audio/transcripts must never be committed (this is a public repo).
- Startup must never depend on the network or the wall clock (the v1.0 clock-drift lesson — see `PROJECT_LESSONS.md`).
- Keep the `.json` output whisper-compatible even if the engine changes.
