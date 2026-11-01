# 🌙 Binaural Sleep

A single-page binaural beats web app that guides you from awake to calm, deep sleep.

## How it works

- **Carrier tone:** 136 Hz sine (low, gentle, pleasant)
- **Beat ramp:** 10 Hz (alpha — relaxed wake) → 6 Hz (theta — drowsy) → 4 Hz → 2.5 Hz (delta — deep sleep)
- **Sleep timer:** default 30 minutes, adjustable 5–120 minutes, with gentle fade-in and fade-out
- **Zero dependencies** — one `index.html` file, pure Web Audio API

## Use

1. **Put on headphones** — binaural beats only work in stereo (each ear hears a different frequency; your brain perceives the difference as the "beat").
2. Set the timer (default 30 min) and volume.
3. Press **Start session** and lie down. The beat frequency slowly ramps down through the session; playback fades out and stops automatically at the end of the timer.

## Run locally / host

Just open `index.html` in any modern browser, or serve it statically:

```bash
python3 -m http.server 8000
```

## GitHub Pages

To publish as a public page: **Settings → Pages → Deploy from a branch → main / (root)**. The site will be live at `https://farrellmeister.github.io/binaural/`.

> Note: binaural beats are a relaxation aid, not a medical treatment. Effects vary by person. Never use while driving.
