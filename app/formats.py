#!/usr/bin/env python3
"""
Shared output formatters for the transcription service.

Turns a Whisper-shaped result dict (top-level ``text`` + a ``segments`` list of
``{start, end, text, ...}``) into the human- and machine-readable output files.
Imported by both transcribe.py (live) and backfill.py (regenerate from existing
JSON), so the formatting lives in exactly one place.
"""

import json


def hms(seconds: float) -> str:
    """Seconds -> human-readable ``HH:MM:SS`` (rounded to the nearest second)."""
    total = int(round(float(seconds)))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def seconds_to_srt_time(seconds: float) -> str:
    """Seconds -> SRT timestamp ``HH:MM:SS,mmm`` (ported from scripts/transcript_formatter)."""
    total_ms = round(float(seconds) * 1000)
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_markdown(result: dict, path: str, title: str) -> None:
    """Human-readable timestamped transcript: ``[HH:MM:SS – HH:MM:SS] text`` per segment."""
    segments = result.get("segments", [])
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        for seg in segments:
            start = hms(seg["start"])
            end = hms(seg["end"])
            text = seg["text"].strip()
            f.write(f"[{start} – {end}] {text}\n\n")


def write_srt(result: dict, path: str) -> None:
    """Standard SubRip (.srt) subtitles."""
    segments = result.get("segments", [])
    blocks = []
    for i, seg in enumerate(segments, start=1):
        start = seconds_to_srt_time(seg["start"])
        end = seconds_to_srt_time(seg["end"])
        text = seg["text"].strip()
        blocks.append(f"{i}\n{start} --> {end}\n{text}\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(blocks))


def write_text(result: dict, path: str) -> None:
    """Plain-text lump (the full transcript)."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(result.get("text", "").strip() + "\n")


def write_json(result: dict, path: str) -> None:
    """Full result as JSON (whisper-compatible schema)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


def build_result_dict(segments, info) -> dict:
    """
    Normalize faster-whisper output into the openai-whisper JSON shape, so the
    ``.json`` schema stays stable for anything downstream that already reads it.

    ``segments`` is the iterable of faster_whisper Segment objects returned by
    ``model.transcribe()`` (iterating it is what actually runs the transcription);
    ``info`` is the accompanying TranscriptionInfo.
    """
    seg_dicts = []
    text_parts = []
    for seg in segments:
        seg_dicts.append({
            "id": seg.id,
            "seek": seg.seek,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text,
            "avg_logprob": seg.avg_logprob,
            "compression_ratio": seg.compression_ratio,
            "no_speech_prob": seg.no_speech_prob,
        })
        text_parts.append(seg.text)
    return {
        "text": "".join(text_parts).strip(),
        "language": info.language,
        "duration": round(info.duration, 3),
        "segments": seg_dicts,
    }
