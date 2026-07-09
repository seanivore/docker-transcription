#!/usr/bin/env python3
"""
One-shot backfill: regenerate the clean ``{name}.md`` (and ``{name}_{ts}.srt``
if missing) for every existing transcript JSON in the transcriptions directory,
using the same formatters as the live service. Safe to re-run — it overwrites
the ``.md`` and only adds a ``.srt`` when one isn't already there.

Run inside the container:
    docker compose exec whisper python /app/backfill.py
"""

import glob
import json
import os
import re

import formats

TRANSCRIPTIONS_DIR = "/data/transcriptions"

# Strip a trailing _YYYYMMDD_HHMMSS timestamp to recover the clean source name.
TS_RE = re.compile(r"_\d{8}_\d{6}$")


def clean_name(json_basename: str) -> str:
    stem = os.path.splitext(json_basename)[0]
    return TS_RE.sub("", stem)


def main():
    json_files = sorted(glob.glob(os.path.join(TRANSCRIPTIONS_DIR, "*.json")))
    if not json_files:
        print("No .json transcripts found.")
        return

    md_count = srt_count = 0
    for jp in json_files:
        try:
            with open(jp, encoding="utf-8") as f:
                result = json.load(f)
        except Exception as e:
            print(f"  skip {os.path.basename(jp)}: {e}")
            continue
        if not result.get("segments"):
            print(f"  skip {os.path.basename(jp)}: no segments")
            continue

        name = clean_name(os.path.basename(jp))
        formats.write_markdown(result, os.path.join(TRANSCRIPTIONS_DIR, f"{name}.md"), name)
        md_count += 1

        srt_path = os.path.splitext(jp)[0] + ".srt"
        if not os.path.exists(srt_path):
            formats.write_srt(result, srt_path)
            srt_count += 1

        print(f"  {os.path.basename(jp)} -> {name}.md")

    print(f"\nBackfilled {md_count} .md file(s); wrote {srt_count} new .srt file(s).")


if __name__ == "__main__":
    main()
