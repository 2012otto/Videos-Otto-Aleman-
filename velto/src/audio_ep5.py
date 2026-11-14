"""Audio de "El balde roto" (Velto Studio): música original + efectos + voz de ElevenLabs (Fernando).

Uso: VIDEO_BUILD=$PWD/velto/build_ep5 VO_TRIM=0.3 python3 velto/src/audio_ep5.py
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

RNG = np.random.default_rng(5)


def clink(f=None):
    f = f or RNG.uniform(2600, 4200)
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t)) * np.exp(-t * 22) * 0.3


def buzzer():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 140 * t)) + np.sign(np.sin(2 * np.pi * 147 * t))
    return A.lowpass(s * 0.25, 900) * np.minimum(1, (0.45 - t) / 0.05)


def cha_ching():
    out = np.zeros(int(1.2 * SR))
    place(out, AV.click(3), 0.0, 0.8)
    place(out, A.bell(2093, 1.0), 0.08, 0.5)
    place(out, A.bell(2637, 1.0), 0.16, 0.5)
    return out


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

    mus = AV.music(total, drop=st(3) + 0.3)
    mus /= np.abs(mus).max() + 1e-9
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus *= duck * db(-17)

    sfx = np.zeros(n)
    place(sfx, impact(), 0.0, db(-11))
    for i in range(1, 8):
        place(sfx, A.whoosh(0.5, seed=200 + i), st(i) - 0.2, db(-23))
    place(sfx, AV.click(1), w(0, 5) - 0.1, db(-14))                    # toca "Promocionar"
    for j in range(10):
        place(sfx, clink(), w(0, 5) + 0.1 + j * 0.09, db(-22))          # monedas que se van volando
    for j in range(16):
        place(sfx, AV.click(30 + j), st(1) + 0.1 + j * 0.1, db(-28))    # contador de vistas
    place(sfx, buzzer(), w(1, 4) - 0.2, db(-17))                       # 0 ventas
    place(sfx, A.pop(), w(1, 6) - 0.2, db(-19))                        # ?
    for j in range(16):
        place(sfx, clink(), st(2) + 0.1 + j * 0.22, db(-24))           # monedas al balde y por el hoyo
    for j in range(4):
        place(sfx, A.pop(), st(2) + j * 0.75, db(-24))                 # pasan los meses
    place(sfx, A.shimmer(1.2, n=45, seed=3, lo=2000, hi=7000), st(3) + 0.2, db(-12))
    place(sfx, A.swell(1.4), st(3) + 0.3, db(-15))
    for j in (6, 7, 9):
        place(sfx, A.pop(), w(4, j) - 0.2, db(-20))
    place(sfx, cha_ching(), w(4, 9), db(-17))                          # nuevo pedido
    place(sfx, impact(), w(5, 4) - 0.25, db(-11))                      # VELTO STUDIO
    place(sfx, A.shimmer(1.6, n=60, seed=8, lo=2000, hi=7000), w(5, 4) - 0.25, db(-12))
    for j in range(3):
        place(sfx, A.pop(), w(5, 8) + j * 0.5, db(-21))                # tendencias
    for j in range(4):
        place(sfx, A.pop(), w(6, 3) - 0.2 + (0 if j < 2 else w(6, 5) - w(6, 3)) + (j % 2) * 0.25, db(-19))
    place(sfx, impact(), w(6, 9) - 0.2, db(-16))                       # parche en el hoyo
    for j in range(14):
        place(sfx, clink(), w(6, 9) + 0.1 + j * 0.12, db(-21))         # el balde se llena
    place(sfx, cha_ching(), w(6, 12), db(-16))
    for j in range(6):
        place(sfx, AV.click(90 + j), w(7, 5) - 0.45 + j * 0.08, db(-20))
    for j in range(16):
        place(sfx, AV.ping(1320 + 40 * (j % 4), 1760 + 40 * (j % 4)), w(7, 6) + j * 0.15, db(-28))
    place(sfx, A.shimmer(1.2, n=40, seed=9, lo=2000, hi=7000), w(7, 8) - 0.1, db(-13))
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
