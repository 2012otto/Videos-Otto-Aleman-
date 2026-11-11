"""Audio de la serie Otto Aleman — Ep. 1 (piano original + efectos + voz de Andrew).

Uso: VIDEO_BUILD=$PWD/otto_serie/build_ep1 VO_TRIM=0.3 python3 otto_serie/src/audio_ep1.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "src"))
import audio as A  # noqa: E402
import timeline  # noqa: E402
from audio import SR, db, place  # noqa: E402


def hit():
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    f = 55 + 90 * np.exp(-t * 25)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * 0.8
    return boom + A.shimmer(1.0, n=25, seed=2)[:n] * 0.6


def tick():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 120) * 0.4


def main():
    vo, total = timeline.load()
    n = int(total * SR)
    voice = np.zeros(n)
    for s in vo:
        place(voice, A.load_mp3(s["file"]), s["vo_start"])
    voice /= np.abs(voice).max() + 1e-9
    voice *= db(-3)
    st = lambda i: vo[i]["start"]  # noqa: E731
    w = lambda i, j: vo[i]["tokens"][j]["s"]  # noqa: E731

    mus = A.music(total, bright_at=st(5))
    mus /= np.abs(mus).max() + 1e-9
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus *= duck * db(-17)

    sfx = np.zeros(n)
    place(sfx, hit(), 0.0, db(-11))                                  # golpe del gancho
    place(sfx, A.shimmer(1.0, n=30, seed=4), w(0, 13) - 0.2, db(-15))  # "3 datos"
    for i in range(1, 7):
        place(sfx, A.whoosh(0.7, seed=30 + i), st(i) - 0.25, db(-21))
    for i in (1, 2, 3):
        place(sfx, A.pop(), st(i) + 0.1, db(-19))                    # etiqueta DATO n
    for j in range(10):
        place(sfx, tick(), w(1, 4) + j * 0.22, db(-26))              # medidor bajando
    place(sfx, A.pop(), w(1, 17) - 0.15, db(-18))                    # no te eches más
    for j in range(3):
        place(sfx, A.shimmer(0.7, n=14, seed=40 + j, lo=2500, hi=6000), w(2, 5) - 0.3 + j * 0.12, db(-18))
    for j in (6, 12, 14):
        place(sfx, A.pop(), w(3, j) - 0.2, db(-21))                  # pirámide
    place(sfx, A.spray(), w(4, 8), db(-14))                          # un solo spray
    place(sfx, A.swell(1.6), w(4, 12) - 0.3, db(-15))
    place(sfx, A.pop(), w(4, 12) - 0.1, db(-18))                     # ¿apuesta?
    for j in (6, 7, 8):
        place(sfx, A.spray(seed=j), w(5, j), db(-17))                # rocía cada día
    place(sfx, A.chime(), st(6) + 0.2, db(-17))                      # campanita tienda
    for j in range(5):
        place(sfx, tick(), w(6, 4) - 0.45 + j * 0.09, db(-20))       # teclea AROMA
    place(sfx, A.shimmer(1.4, n=50, seed=8), w(6, 9) - 0.1, db(-11))  # 10%
    sfx = A.reverb(sfx, 1.6, 0.22, seed=9)

    bed = mus + sfx
    d = int(0.012 * SR)
    out = np.stack([voice + bed, voice + np.concatenate([np.zeros(d), bed[:-d]])], 1)
    out /= max(1.0, np.abs(out).max() / db(-1))
    raw = os.path.join(timeline.BUILD, "audio_raw.wav")
    with wave.open(raw, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())
    dst = os.path.join(timeline.BUILD, "audio.wav")
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                           "-ar", str(SR), dst])
    print(dst, f"{total:.2f}s")


if __name__ == "__main__":
    main()
