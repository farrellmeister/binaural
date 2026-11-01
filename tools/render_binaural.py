#!/usr/bin/env python3
"""Render binaural-beats sessions (sleep / focus) as stereo WAV files.

Left ear: fixed carrier. Right ear: carrier + beat, where the beat follows a
piecewise-linear stage ramp (mode-dependent). Phase is integrated so
frequency changes are click-free. 5 s fade-in, 60 s fade-out.
Rendered in 60-second chunks so memory stays constant.
"""
import argparse
import wave

import numpy as np

MODES = {
    "sleep": {  # awake -> calm -> deep sleep
        "stages": [
            (10.0, 6.0, 0.3),   # Relax: alpha -> theta
            (6.0, 4.0, 0.3),    # Drowsy: theta
            (4.0, 2.5, 0.4),    # Deep sleep: delta
        ],
        "carrier": 136.0,
    },
    "focus": {  # settle -> engage -> sustained concentration (beta band)
        "stages": [
            (10.0, 14.0, 0.2),  # Settle
            (14.0, 18.0, 0.5),  # Engage
            (18.0, 16.0, 0.3),  # Lock in
        ],
        "carrier": 200.0,
    },
}
SR = 8000
CHUNK = SR * 60


def beat_envelope(n, total, start, stages):
    """Beat frequency at each sample, piecewise-linear across stages."""
    t = (np.arange(n, dtype=np.float64) + start) / total
    freq = np.zeros(n)
    acc = 0.0
    for i, (f0, f1, share) in enumerate(stages):
        lo = acc
        hi = 1.0 if i == len(stages) - 1 else acc + share
        m = (t >= lo) & (t < hi if i < len(stages) - 1 else t <= hi)
        frac = np.clip((t[m] - lo) / share, 0.0, 1.0)
        freq[m] = f0 + (f1 - f0) * frac
        acc += share
    return freq


def render(minutes, out, mode="sleep"):
    stages = MODES[mode]["stages"]
    carrier = MODES[mode]["carrier"]
    total = int(minutes * 60 * SR)
    fin = min(5 * SR, total // 2)
    fout = min(60 * SR, total // 2)
    phase = 0.0
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        i = 0
        while i < total:
            m = min(CHUNK, total - i)
            idx = np.arange(i, i + m, dtype=np.float64)
            freq = beat_envelope(m, total, i, stages)
            inc = 2 * np.pi * np.cumsum(freq) / SR
            inc += phase  # broadcast scalar onto array
            phase = float(inc[-1])  # keep as scalar for the next chunk
            t = idx / SR
            left = 0.5 * np.sin(2 * np.pi * carrier * t)
            right = 0.5 * np.sin(2 * np.pi * carrier * t + inc)
            # envelope: fade-in then fade-out, applied multiplicatively
            env = np.ones(m)
            rel = idx / total
            head = rel * total < fin
            env[head] = (rel[head] * total) / fin
            tail = (1 - rel) * total < fout
            env[tail] *= ((1 - rel[tail]) * total) / fout
            audio = np.stack([left * env, right * env], axis=1)
            w.writeframes((audio * 32767).astype("<i2").tobytes())
            i += m
    print(f"wrote {out}: {minutes} min, {total} samples, "
          f"beat {freq[0]:.1f}->{freq[-1]:.2f} Hz, mode {mode}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--minutes", type=float, default=30)
    p.add_argument("--mode", default="sleep", choices=["sleep", "focus"])
    p.add_argument("--out", default="binaural-sleep-30min.wav")
    a = p.parse_args()
    render(a.minutes, a.out, a.mode)
