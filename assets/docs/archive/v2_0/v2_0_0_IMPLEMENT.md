# v2.0.0 Implementation Plan — Public Web Transcription Tool

**Initiative**: a free, portfolio-grade public web version of the transcription tool — no ads, no signup, no junk (the reason Sean built the local one).
**Revision driven by**: initial draft (v0 → to be pushed toward exclusively-executable over future gap-review sessions).
**Required reading first**: `assets/docs/AUTO_TRANSCRIBE.md` · `README.md` · `.agents/DEV_RULES.md` (§ Deployment, § Collaborating with Claude Design)
**If you find missing context**: AUTO_TRANSCRIBE.md is living — confirm with Sean and update it; don't paper over the gap here.

> ⚠ **This is a first draft, not an executable plan.** It is direction + open decisions. It must go through Sean's gap-review loop (fresh-instance A/B/C[/D]) toward *exclusively executable* before any build. Human-decision items are listed explicitly at the bottom — they get resolved in chat, not buried here.

---

## Roadmap (coarse direction — NOT a build queue)

A single-page vanilla HTML/CSS/JS web app where anyone can transcribe a file for free, privately, with a Claude-Design-quality UI. Milestones (direction, not ships):

1. **Decide the engine architecture** (the load-bearing fork — see Imminent slice).
2. **Design phase** — run the multi-winner design funnel → Sean selects → hand to Claude Design → wire the returned UI.
3. **Build the transcription flow** — upload/pick file → decode → transcribe → show + download `.txt`/`.srt`/`.md` (+ timestamped view).
4. **Deploy** — Vercel dev preview → prod on an `august.style` subdomain (Cloudflare DNS).

---

## Imminent slice — the architecture fork (decide first; everything hangs off it)

The one decision that shapes the whole build. **Documented both ways; Sean/​gap-review picks.**

### Option A (recommended) — Browser-side WASM, no backend
Whisper runs **in the visitor's browser** via WebAssembly — [`@huggingface/transformers`](https://huggingface.co/docs/transformers.js) (Whisper via ONNX/WASM) or `whisper.cpp` compiled to WASM.
- **Pros:** no server compute → **stays free on static hosting** (Vercel/Cloudflare Pages); **fully private** (audio never leaves the device — matches the self-hosted ethos); no upload step; no cold-start/timeouts.
- **Cons:** model size/speed bounded by the visitor's device; large models are heavy in-browser (favor `tiny`/`base`/`small`/`distil` client-side); needs audio decoded to PCM in-browser (Web Audio API, or `ffmpeg.wasm` for exotic formats like `.caf`).
- **Model selection = a UI dropdown** (speed↔accuracy), since capability varies by device. This is where Sean's "let the person choose / multilingual is impressive" note lands.

### Option B — Serverless backend
Upload → a serverless function (Vercel) transcribes server-side (faster-whisper or a hosted API).
- **Pros:** big models regardless of device; consistent speed.
- **Cons:** needs compute + temp storage → **hard to keep free**; serverless **timeout/size limits** bite on long audio; audio leaves the device (privacy + a file-handling surface). Would likely need Cloudflare or a queue for anything non-trivial.

**Recommendation:** **A** — it's the only path that is simultaneously free, private, and backend-less, and it makes a clean portfolio demo. B stays documented as the fallback if in-browser accuracy proves insufficient. *Decision deferred to gap-review / Sean.*

---

## Design phase (once the engine fork is settled)

Per DEV_RULES § *Collaborating with Claude Design*:
1. **Design funnel** (`parallel_volley_funnel` pattern) — generate rendered vanilla-HTML option mocks; **surface 2–3 finalist winners** (not one) for Sean to pick by poking the rendered HTML. Input: a self-contained REQUIREMENTS brief (who it's for, the aesthetic bar — classic/timeless/hipster-edge, the file→transcript→download flow, mobile-first). *Pattern reference:* `everlastings-website/assets/docs/archive/v3_5/portal-design-funnel/`.
2. **Handoff to Claude Design (Direction A — new UI):** `brief.md` (thesis + the chosen `controls.html`/`tokens.css` anchor + pages), `data-flow.md` (the client-side state contract — file states, progress, results), annotated `reference/`. CD returns `out/` (self-contained vanilla UI) + `INTEGRATION.md`/`CHANGELOG_GAPS.md`/`OPEN_QUESTIONS.md`.
3. **Wire** the returned UI to the WASM engine (the `data.js` SEAM becomes the real transcription calls), running through gap reviews.

---

## Later (direction only — detail arrives as each nears the gate)

- Broad file-type support in-browser (ffmpeg.wasm decode path for `.caf` etc.).
- Result UX: the three views — plain text, timestamped `.md`, `.srt` — with copy/download; drag-drop + file-picker.
- Model dropdown with a clear speed/accuracy + turnaround disclaimer for long files.
- Deploy: Vercel dev preview (SSO off during dev), prod on an `august.style` subdomain via Cloudflare CLI.
- Optional: a "how it works — runs in your browser, nothing uploaded" trust note (privacy is a feature).
- Reuse: the `.md`/`.srt` formatting logic mirrors `app/formats.py` (port to JS).

---

## Open decisions (surfaced for Sean — resolve in chat, never buried at build time)

- **Engine fork:** confirm Option A (browser-WASM) vs B (serverless).
- **Domain:** which `august.style` subdomain.
- **Design direction:** picked from the funnel's multiple finalists (a Sean call by design).
- **Scope of v1 launch:** which file types / model options ship first.

## Cross-references
- Architecture/state → `assets/docs/AUTO_TRANSCRIBE.md`
- Deployment (Vercel/Cloudflare), Claude Design workflow → `.agents/DEV_RULES.md`
- Design funnel worked example → `everlastings-website/assets/docs/archive/v3_5/portal-design-funnel/`
- Formatting logic to port to JS → `app/formats.py`
