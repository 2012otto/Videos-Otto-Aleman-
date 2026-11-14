"""Audio del dato curioso "11 días sin dormir": piano original suave en la historia, ritmo de Velto en los anuncios.

Uso: VIDEO_BUILD=$PWD/velto/build_sueno VO_TRIM=0.3 python3 velto/src/audio_sueno.py
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


def tick():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 120) * 0.4


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
    ads = [(st(3), st(4)), (st(7), total)]

    story = A.music(total, bright_at=st(5))
    story /= np.abs(story).max() + 1e-9
    beat = AV.music(total, drop=0.0)
    beat /= np.abs(beat).max() + 1e-9
    tt = np.arange(n) / SR
    in_ad = np.zeros(n)
    for a0, a1 in ads:
        in_ad[(tt >= a0) & (tt < a1)] = 1.0
    sm = np.convolve(in_ad, np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus = (story[:n] * (1 - sm) * db(-17) + beat[:n] * sm * db(-18)) * duck

    sfx = np.zeros(n)
    place(sfx, A.shimmer(1.0, n=30, seed=2), 0.1, db(-17))
    for i in range(1, 8):
        place(sfx, A.whoosh(0.6, seed=300 + i), st(i) - 0.2, db(-23))
    for j in range(10):
        place(sfx, tick(), w(0, 8) + j * 0.09, db(-22))                 # calendario 1 -> 11
    place(sfx, A.pop(), w(1, 2) - 0.2, db(-21))
    place(sfx, A.swell(2.0), w(2, 14) - 0.3, db(-14))                  # alucinación
    for a0, _ in ads:
        place(sfx, impact(), a0 + 0.02, db(-14))                        # corte al anuncio
    place(sfx, AV.ding(), w(3, 19) - 0.05, db(-13))                    # $5
    place(sfx, A.shimmer(0.9, n=30, seed=7, lo=2000, hi=7000), w(3, 19), db(-14))
    place(sfx, A.whoosh(0.4, seed=91), st(4) + 0.02, db(-18))          # vuelta a la historia
    for j in range(12):
        place(sfx, tick(), st(5) + 0.3 + j * 0.25, db(-24))             # reloj de 14 horas
    place(sfx, impact(), w(6, 8) - 0.1, db(-15))                       # PELIGROSO
    for j in range(5):
        place(sfx, AV.click(80 + j), w(7, 14) - 0.4 + j * 0.08, db(-20))
    for j in range(14):
        place(sfx, AV.ping(1320 + 40 * (j % 4), 1760 + 40 * (j % 4)), w(7, 13) + j * 0.15, db(-28))
    place(sfx, AV.ding(), w(7, 21) - 0.05, db(-13))
    place(sfx, A.shimmer(0.9, n=30, seed=8, lo=2000, hi=7000), w(7, 21), db(-14))
    sfx = A.reverb(sfx, 1.2, 0.18, seed=9)

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
