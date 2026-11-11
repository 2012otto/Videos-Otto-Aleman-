"""Audio de la serie Otto Aleman — Ep. 2 (perfumes árabes): piano original + efectos + voz de Andrew.

Uso: VIDEO_BUILD=$PWD/otto_serie/build_ep2 VO_TRIM=0.3 python3 otto_serie/src/audio_ep2.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_ep1 import A, timeline, SR, db, place, hit, tick  # noqa: E402


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

    mus = A.music(total, bright_at=st(4))
    mus /= np.abs(mus).max() + 1e-9
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus *= duck * db(-17)

    sfx = np.zeros(n)
    place(sfx, hit(), 0.0, db(-11))                                   # gancho
    place(sfx, hit(), w(0, 6) - 0.1, db(-12))                         # sello MITO
    for i in range(1, 7):
        place(sfx, A.whoosh(0.7, seed=50 + i), st(i) - 0.25, db(-21))
    place(sfx, A.pour(5.0), st(1) + 0.3, db(-20))                     # alambique
    place(sfx, A.pop(), w(1, 4) - 0.2, db(-19))
    place(sfx, A.pop(), w(1, 9) - 0.2, db(-19))
    for j in (4, 7, 9):
        place(sfx, A.shimmer(0.6, n=12, seed=60 + j, lo=2500, hi=6000), w(2, j) - 0.2, db(-18))
    place(sfx, A.shimmer(1.4, n=45, seed=7), w(2, 17) - 0.2, db(-12))  # oro líquido
    place(sfx, A.swell(1.6), w(3, 12) - 0.3, db(-15))                 # ambroxan
    place(sfx, A.pop(), w(3, 12), db(-19))
    place(sfx, A.whoosh(0.5, seed=71), w(3, 18), db(-19))             # flecha ballena
    place(sfx, hit(), w(4, 1) - 0.1, db(-15))                         # COPIA PIRATA
    for j in range(3):
        place(sfx, A.pop(), w(4, 9) - 0.2 + j * 0.2, db(-20))
    place(sfx, A.chime(), w(4, 11) - 0.1, db(-18))                    # ORIGINAL
    for j in range(3):
        place(sfx, A.whoosh(0.8, seed=80 + j), w(5, 6) + j * 0.2, db(-20))  # globos
    for j in range(3):
        place(sfx, A.pop(), w(6, 5) - 0.2 + j * 0.15, db(-21))
    for j in range(5):
        place(sfx, tick(), w(6, 11) - 0.45 + j * 0.09, db(-20))       # teclea ÁRABE
    place(sfx, A.shimmer(1.4, n=50, seed=8), w(6, 16) - 0.1, db(-11))  # 20%
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
