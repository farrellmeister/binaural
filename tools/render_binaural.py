#!/usr/bin/env python3
"""Render a binaural-beats sleep session as a stereo WAV file.

Left ear: fixed 136 Hz carrier. Right ear: carrier + beat, where the beat
ramps 10 Hz (alpha) -> 6 (theta) -> 4 -> 2.5 Hz (delta) across the session.
Phase is integrated so frequency changes are click-free. 5 s fade-in,
60 s fade-out. Rendered in 60-second chunks so memory stays constant.
"""
import argparse
import wave

import numpy as np

STAGES = [  # (from_hz, to_hz, share-of-session)
    (10.0, 6.0, 0.3),   # Relax: alpha -> theta
    (6.0, 4.0, 0.3),    # Drowsy: theta
    (4.0, 2.5, 0.4),    # Deep sleep: delta
]
CARRIER = 136.0
SR = 8000
CHUNK = SR * 60


def beat_envelope(n, total, start=0):
    """Beat frequency at each sample, piecewise-linear across stages."""
    t = (np.arange(n, dtype=np.float64) + start) / total
    freq = np.zeros(n)
    acc = 0.0
    for i, (f0, f1, share) in enumerate(STAGES):
        lo = acc
        hi = 1.0 if i == len(STAGES) - 1 else acc + share
        m = (t >= lo) & (t < hi if i < len(STAGES) - 1 else t <= hi)
        frac = np.clip((t[m] - lo) / share, 0.0, 1.0)
        freq[m] = f0 + (f1 - f0) * frac
        acc += share
    return freq


def render(minutes, out):
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
            freq = beat_envelope(m, total, i)
            phase += 2 * np.pi * np.cumsum(freq) / SR
            t = idx / SR
            left = 0.5 * np.sin(2 * np.pi * CARRIER * t)
            right = 0.5 * np.sin(2 * np.pi * CARRIER * t + phase)
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
          f"beat {freq[0]:.1f}->{freq[-1]:.2f} Hz")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--minutes", type=float, default=30)
    p.add_argument("--out", default="binaural-sleep-30min.wav")
    a = p.parse_args()
    render(a.minutes, a.out)
