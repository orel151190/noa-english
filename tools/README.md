# Audio tools
Voice: Piper `en-us-lessac-medium` — download once:
  curl -L -o v.tgz https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-lessac-medium.tar.gz && tar xzf v.tgz
  pip install piper-tts ; ffmpeg required
Scripts expect the voice at /tmp/voice/en-us-lessac-medium.onnx (edit the path).
gen.py  – base words/phrases (writes audio.js)   gen2.py/gen3.py/add.py – later batches (write *.json: key -> data URI)
snd2.py – old synthetic letter sounds (replaced by assets/jolly-phonics, kept for reference)
Merge a JSON batch into index.html by updating the `const AUDIO={...}` object.
