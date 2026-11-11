"""Audio del episodio 2 de Velto (música original + efectos + voz de Ava).

Uso: VIDEO_BUILD=$PWD/velto/build_ep2 VO_TRIM=0.3 python3 velto/src/audio_ep2.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_velto as AV  # noqa: E402
from audio_velto import A, timeline, SR, db, place  # noqa: E402


def impact():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    k = np.zeros(n)
    place(k, AV.kick(), 0, 1.0)
    return k + np.sin(2 * np.pi * 45 * t) * np.exp(-t * 3) * 0.5


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

    mus = AV.music(total, drop=st(3) + 0.05)
    mus /= np.abs(mus).max() + 1e-9
    env = np.convolve(np.abs(voice), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    duck = 1 - 0.4 * np.clip(env / (env.max() * 0.35), 0, 1)
    duck = np.convolve(duck, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    mus *= duck * db(-16)

    sfx = np.zeros(n)
    place(sfx, impact(), 0.0, db(-10))                       # golpe del gancho
    for j in range(15):
        place(sfx, AV.click(j), 0.15 + j * 0.065, db(-24))   # tecleo en el buscador
    for j in range(3):
        place(sfx, A.pop(), 1.2 + j * 0.15, db(-24))
    place(sfx, AV.buzz(0.45), 2.0, db(-16))                  # "0 resultados"
    for i in range(1, 7):
        place(sfx, A.whoosh(0.6, seed=40 + i), st(i) - 0.25, db(-22))
    for j in range(3):
        place(sfx, A.pop(), st(1) + 0.05 + j * 0.15, db(-23))
    for j in range(3):
        place(sfx, A.pop(), w(2, 11) - 0.15 + j * 0.22, db(-19))  # stickers
    place(sfx, A.whoosh(0.6, seed=90), w(2, 14) - 0.1, db(-16))   # se va
    place(sfx, AV.ding(), w(2, 16) - 0.2, db(-19))
    place(sfx, A.pop(), w(3, 1) - 0.1, db(-20))                    # "ojo"
    place(sfx, A.whoosh(0.4, seed=91), w(3, 6) - 0.1, db(-18))     # tachón
    place(sfx, impact(), w(3, 8) - 0.1, db(-14))                   # "3"
    for j in (0, 7, 14):
        place(sfx, A.pop(), w(4, j) - 0.1, db(-19))
    for j in (6, 13, 20):
        place(sfx, AV.ping(1568, 2093), w(4, j), db(-21))          # checks
    place(sfx, A.shimmer(1.2, n=40, seed=5, lo=2000, hi=7000), w(5, 6) - 0.2, db(-14))
    for j in range(8):
        place(sfx, AV.click(50 + j), st(5) + 0.4 + j * 0.2, db(-26))
    for j in range(3):
        place(sfx, AV.click(80 + j), w(6, 1) - 0.35 + j * 0.12, db(-20))
    for j in range(18):
        place(sfx, AV.ping(1320 + 40 * (j % 4), 1760 + 40 * (j % 4)), w(6, 1) + j * 0.16, db(-28))
    place(sfx, A.shimmer(1.4, n=50, seed=8, lo=2000, hi=7000), w(6, 7) - 0.1, db(-12))
    sfx = A.reverb(sfx, 1.4, 0.2, seed=9)

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
