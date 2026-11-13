"""Audio del tutorial Velto "Crea tu tienda en menos de 5 minutos": música alegre original + efectos + voz de Ava.

Uso: VIDEO_BUILD=$PWD/velto/build_ep4 VO_TRIM=0.3 python3 velto/src/audio_ep4.py
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


def tap():
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    out = np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 90) * 0.5
    ck = AV.click(5)
    out[: len(ck)] += ck[:n] * 0.5
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

    mus = AV.music(total, drop=0.5)
    mus /= np.abs(mus).max() + 1e-9
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus *= duck * db(-18)

    sfx = np.zeros(n)
    place(sfx, impact(), 0.0, db(-11))
    place(sfx, A.pop(), w(0, 7) - 0.15, db(-18))                        # 5:00
    for i in range(1, 8):
        place(sfx, A.whoosh(0.5, seed=110 + i), st(i) - 0.2, db(-23))
    place(sfx, tap(), w(1, 7) - 0.1, db(-14))                           # crear mi tienda gratis
    place(sfx, A.pop(), w(2, 4) - 0.3, db(-18))                         # logo
    for j in range(15):
        place(sfx, AV.click(20 + j), w(2, 6) - 0.2 + j * 0.09, db(-26))  # escribe el nombre
    for j in range(4):
        place(sfx, tap(), w(2, 13) + j * 0.9, db(-17))                  # cambia colores
        place(sfx, A.shimmer(0.4, n=8, seed=30 + j, lo=3000, hi=6000), w(2, 13) + j * 0.9 + 0.05, db(-22))
    place(sfx, tap(), w(3, 2) - 0.6, db(-15))                           # + nuevo producto
    for j in range(6):
        place(sfx, A.pop(), w(3, 2) - 0.2 + j * 0.55, db(-20))           # caen las sudaderas
    for j in range(4):
        place(sfx, A.pop(), w(3, 8) - 0.2 + j * 0.12, db(-24))           # tallas
    place(sfx, AV.ding(), w(4, 4) - 0.2, db(-15))                       # nuevo pedido
    for j in (9, 11, 13):
        place(sfx, tap(), w(4, j) - 0.3, db(-16))                       # cambia el estado
    place(sfx, A.whoosh(1.2, seed=150), w(4, 11), db(-19))              # camioneta en camino
    place(sfx, AV.ping(1568, 2093), w(4, 13), db(-19))                  # entregado
    place(sfx, tap(), w(4, 15) - 0.3, db(-16))                          # contactar
    for j in range(14):
        place(sfx, AV.click(60 + j), w(5, 6) - 0.3 + j * 0.07, db(-27))  # contador de ventas
    place(sfx, tap(), w(6, 3) - 0.1, db(-13))                           # publicar tienda
    place(sfx, impact(), w(6, 3) + 0.3, db(-14))
    place(sfx, A.shimmer(1.6, n=60, seed=8, lo=2000, hi=7000), w(6, 3) + 0.3, db(-11))
    for j in range(6):
        place(sfx, AV.click(90 + j), w(7, 1) - 0.45 + j * 0.08, db(-20))
    for j in range(18):
        place(sfx, AV.ping(1320 + 40 * (j % 4), 1760 + 40 * (j % 4)), w(7, 1) + j * 0.15, db(-28))
    place(sfx, A.shimmer(1.4, n=50, seed=9, lo=2000, hi=7000), w(7, 4) - 0.1, db(-12))
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
