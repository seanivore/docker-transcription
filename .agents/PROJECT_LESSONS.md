# Project Lessons — docker-transcriptions

In-repo, git-tracked, **not** fleet-synced (per DEV_RULES routing). Hard-won, project-specific lessons that should travel with anyone who clones this repo.

---

## The clock-drift outage (2026-07-09) — root cause + fix

**Symptom.** Files dropped into `data/uploads/` weren't transcribed; the container sat in `Restarting (100)` (exit 100 = apt failure), crash-looping.

**Root cause.** Docker Desktop's Linux VM clock drifted **~5h43m behind** real time (the Mac had slept/shut down; the VM clock didn't re-sync on wake). The **old** setup ran, on *every* container start:
```
apt-get update && apt-get install -y ffmpeg && pip install openai-whisper && python /app/transcribe.py
```
With a behind clock, Debian's `bookworm-updates` index looked future-dated, so apt hard-failed: *"E: Release file … is not valid yet (invalid for another 5h 42min). Updates for this repository will not be applied."* Because the command chains with `&&`, the failure of step 1 killed the whole chain — Whisper never ran. `restart: unless-stopped` then re-ran the same failing command in a loop.

**Two failure modes, both now fixed in v1.1:**
1. **Clock skew breaking apt** → the prebuilt `Dockerfile` runs apt at *build* time only (with `-o Acquire::Check-Date=false` for good measure), so a drifted clock can never break startup again.
2. **`&&`-chain fragility** → startup is now just `python /app/transcribe.py`; there's no install step to fail.

**If the host clock is ever wrong again** (unrelated to this tool): macOS System Settings → Date & Time, toggle "Set automatically" off then on; or restart Docker Desktop; or force a VM re-sync with `docker run --rm --privileged alpine hwclock -s`. Sean's machine shuts down randomly and lands with a wrong clock on wake — the auto-set toggle is his known fix.

**Lesson (general):** startup must never depend on the network or the wall clock. Bake dependencies into the image; keep the container's `CMD` to running the app.

---

## faster-whisper vs openai-whisper

- v1.1 uses **faster-whisper** (CTranslate2, CPU int8): ~2–4× faster on CPU, no PyTorch, much smaller image, same accuracy.
- Its `model.transcribe()` returns a **generator** of Segment objects + a TranscriptionInfo — iterating the generator is what actually runs the work. `app/formats.build_result_dict()` normalizes that back into the **openai-whisper JSON shape** (`text`, `language`, `segments:[{id, seek, start, end, text, …}]}`) so the `.json` output schema stays stable for anything downstream.
- It is NOT the paid OpenAI API. No key, no cost, no network at inference — fully local. (The `OPENAI_API_KEY` in `.env` is unused by this tool.)

---

## Privacy

This is a **public** GitHub repo. `data/uploads/` and `data/transcriptions/` are gitignored — the audio and transcripts (personal voice notes, business notes) must never be committed. Only `.gitkeep` placeholders are tracked.
