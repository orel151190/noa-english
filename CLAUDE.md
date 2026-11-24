# CLAUDE.md – noa-english

English practice web app for a 6-year-old (first grade, Israel). UI in Hebrew (RTL); English words are spoken aloud.
Full goals, feature list, backlog and test plan: **STP.md** (read it first).

## Quick facts
- Single file `index.html` (vanilla HTML/CSS/JS, no build). Audio is embedded as base64 in `const AUDIO={...}`.
- Hosted on GitHub Pages: repo `orel151190/noa-english`, branch `main`, root → https://orel151190.github.io/noa-english/
  The repo must stay **public** (free Pages).
- Target device: Samsung tablet, Chrome. Test at 360px wide and on tablet sizes.

## Rules for changes
- The child must always end a task with success (retry hints, never a dead end). Star per task; 5 stars → overlay "mark a star on the challenge sheet".
- Every instruction is shown in Hebrew and spoken (Hebrew via parent recording or device TTS), then the English audio. Never overlap audio.
- New words need audio: generate with Piper (`tools/gen*.py`, voice `en-us-lessac-medium`, length_scale 1.4 / slow 2.0, ffmpeg compressor+limiter) and add keys `w:<word>` and `ws:<word>`.
- Letter sounds `S:<A-Z>` are real Jolly Phonics recordings (`assets/jolly-phonics`, CC BY-NC-ND) – do not modify them, keep the credit line.
- Do not use images from the class workbook (copyrighted). Use emoji or original SVG.
- Keep `localStorage` keys stable: noaStars, noaSet, noaCustom, noaPhon, noaSrAlone.
- Run the Playwright smoke tests (see STP §7.3) before every push.

## Adding a new lesson
The parent pastes the teacher's WhatsApp lesson summary. Then:
1. Add the new letter to `LETTERS`, `FRIENDS`, `EXAMPLE`, `GLYPH`.
2. Add words to `WORDS` as `[word, letter, emoji/svg, hebrew]`, and topic lists if any.
3. Generate the missing audio.
4. Add any new talk question to `TALK`.
5. Update STP.md §2.
