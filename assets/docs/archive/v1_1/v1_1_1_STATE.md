# v1.1 — Project State Snapshot

**Version**: v1.1.1 · **Date**: 2026-07-09 · **Type**: milestone state record (point-in-time)

A concise snapshot of where the tool stands at the v1.1 milestone — the baseline the v2.0 public-web initiative builds from. The living, always-current detail is in `assets/docs/AUTO_TRANSCRIBE.md`; this file is the fixed record of the v1.1 cut.

---

## What shipped in v1.1

Started from v1.0 (openai-whisper, `base` model, `.txt`+`.json` only, deps installed on every container start). v1.1 delivered:

- **Engine:** openai-whisper → **faster-whisper** (CTranslate2, CPU int8; no PyTorch).
- **Model:** `base` → **`large-v3`** default (multilingual, top accuracy), via `WHISPER_MODEL` env knob.
- **New outputs:** `{name}.md` (human-readable timestamped, `[HH:MM:SS – HH:MM:SS] text`, clean stable filename) and `{name}_{ts}.srt` subtitles — alongside the existing `.json` and `.txt`.
- **File types:** broadened to everything ffmpeg decodes (added `.caf`, `.aac`, `.flac`, `.opus`, `.mov`, `.mkv`, `.aiff`, `.amr`, `.wma`, and more).
- **Packaging:** runtime `apt`/`pip` replaced by a **prebuilt Dockerfile** + pinned `requirements.txt` + model cache volume; immune to the clock-skew startup failure. Dependabot for weekly dep bumps.
- **Robustness:** mid-copy file guard, per-file error isolation, timestamped logs.
- **Old `scripts/transcript_formatter/`** folded into `app/formats.py` and deleted.

## Docs / repo modernization (also v1.1)

- Instantiated the `assets/docs/` convention: `AUTO_TRANSCRIBE.md` (living), `archive/v1_1/` (this), `archive/v2_0/` (IMPLEMENT draft).
- README rewritten to the showcase template; `.env` private data gitignored; `.agents/DEV_RULES.md` bumped to v4.2.0 (Vercel/Cloudflare + Claude Design + no-human-items conventions).
- `.agents/PROJECT_LESSONS.md` records the clock-drift outage.

## Known state / carry-forward
- Runs local Docker only. GHCR image publish is planned but not done.
- v2.0 (public web tool) is a **draft IMPLEMENT** — not gap-reviewed or built.
- Surfaced to Sean (open): whether to remove the unused `OPENAI_API_KEY` from `.env`.
