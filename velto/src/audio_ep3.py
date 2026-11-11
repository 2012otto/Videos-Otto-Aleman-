"""Audio del episodio 3 de Velto ("No son tus seguidores").

Uso: VIDEO_BUILD=$PWD/velto/build_ep3 VO_TRIM=0.3 python3 velto/src/audio_ep3.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_velto as AV  # noqa: E402
from audio_velto import A, timeline, SR, db, place  # noqa: E402
from audio_ep2 import impact  # noqa: E402


def error_buzz():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.5 + np.sign(np.sin(2 * np.pi * 116 * t)) * 0.5
    return A.lowpass(s, 900) * np.minimum(1, (0.35 - t) / 0.05) * 0.3


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

    mus = AV.music(total, drop=st(5) + 0.05)
    mus /= np.abs(mus).max() + 1e-9
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.4 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus *= duck * db(-16)

    sfx = np.zeros(n)
    place(sfx, impact(), 0.0, db(-10))
    place(sfx, A.whoosh(0.4, seed=1), w(0, 7) - 0.1, db(-17))      # tachón de seguidores
    for i in range(1, 8):
        place(sfx, A.whoosh(0.6, seed=60 + i), st(i) - 0.25, db(-22))
    place(sfx, impact(), w(1, 4) - 0.1, db(-13))                    # "3 errores"
    place(sfx, A.pop(), w(1, 5) + 0.15, db(-20))
    for i in (2, 3, 4):
        place(sfx, error_buzz(), st(i) + 0.15, db(-17))             # "ERROR n"
    place(sfx, A.pop(), w(2, 2) - 0.15, db(-18))                    # sticker
    place(sfx, A.pop(), w(2, 8) - 0.15, db(-22))                    # nube
    for j in range(10):
        place(sfx, AV.click(j), st(3) + 0.4 + j * 0.45, db(-27))    # scroll
    place(sfx, AV.ding(), w(3, 13), db(-21))                        # lo encuentra
    for j in range(6):
        place(sfx, AV.ping(1320 + 40 * (j % 3), 1760 + 40 * (j % 3)), st(4) + 1.0 + j * 0.55, db(-21))
    place(sfx, A.swell(1.8), w(5, 6) - 0.3, db(-15))                # balanza
    place(sfx, A.pop(), w(5, 6), db(-18))
    for j in (4, 6, 11):
        place(sfx, AV.ping(1568, 2093), w(6, j), db(-20))           # checks
    for j in range(7):
        place(sfx, AV.click(80 + j), w(7, 1) - 0.5 + j * 0.09, db(-21))
    for j in range(18):
        place(sfx, AV.ping(1320 + 40 * (j % 4), 1760 + 40 * (j % 4)), w(7, 1) + j * 0.15, db(-28))
    place(sfx, A.shimmer(1.4, n=50, seed=8, lo=2000, hi=7000), w(7, 7) - 0.1, db(-12))
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
