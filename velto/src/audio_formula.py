"""Audio de "La fórmula de los mil millones": beat enérgico (audio_gta), tics de rodillos, golpes por paso.

Uso: VIDEO_BUILD=$PWD/velto/build_formula VO_TRIM=0.12 VO_GAP=0.15 VO_TAIL=1.2 python3 velto/src/audio_formula.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_gta as AG  # noqa: E402
import audio_velto as AV  # noqa: E402
from audio_velto import A, timeline, SR, db, place  # noqa: E402
from audio_ep2 import impact  # noqa: E402


def tick():
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 160) * 0.35


def main():
    vo, total = timeline.load()
    n = int(total * SR)
    voice = np.zeros(n)
    for s in vo:
        place(voice, A.load_mp3(s["file"]), s["vo_start"])
    voice /= np.abs(voice).max() + 1e-9
    voice *= db(-2.5)
    st = lambda i: vo[i]["start"]  # noqa: E731
    w = lambda i, j: vo[i]["tokens"][j]["s"]  # noqa: E731

    beat = AG.music(total + 1)[:n]
    beat /= np.abs(beat).max() + 1e-9
    tt = np.arange(n) / SR
    gate = np.ones(n)
    gate[(tt >= w(5, 0) - 0.15) & (tt < w(5, 3) - 0.1)] = 0.25   # cortes secos: casi silencio
    gate = np.convolve(gate, np.ones(int(0.02 * SR)) / int(0.02 * SR), mode="same")
    k = int(0.2 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.4 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus = beat * gate * duck * db(-16)
    mus[: int(1.0 * SR)] *= np.linspace(0.4, 1, int(1.0 * SR))

    sfx = np.zeros(n)
    for j in range(40):                                           # rodillos del contador
        place(sfx, tick(), 0.2 + j * (w(0, 12) / 40), db(-22))
    place(sfx, impact(), w(0, 0) - 0.05, db(-11))
    place(sfx, AV.ding(), w(0, 12), db(-15))
    for i in (1, 2, 3, 4, 6, 7):
        place(sfx, A.whoosh(0.4, seed=40 + i), st(i) - 0.1, db(-13))
    place(sfx, impact(), w(1, 0) - 0.05, db(-13))
    for j in range(3):
        place(sfx, AV.pluck(880 * (1.26 ** j), 0.3), w(1, 7) + j * 0.12, db(-12))   # fichas 1 2 3
    for i, wi in ((2, 3), (3, 3), (4, 4)):
        place(sfx, impact(), w(i, wi) - 0.08, db(-10))            # GANCHO. FECHA. BOTÓN.
        place(sfx, AV.pluck(1320, 0.3), w(i, 0), db(-14))
    for j in range(30):
        place(sfx, tick(), w(2, 13) - 0.2 + j * 0.035, db(-22))   # 90 millones
    for j in range(3):
        place(sfx, impact(), w(2, 20) + j * 0.12, db(-16))        # medallas
    place(sfx, A.shimmer(0.9, seed=3), w(2, 20), db(-15))
    place(sfx, A.whoosh(0.4, seed=77), w(3, 9) - 0.2, db(-15))     # hoja del calendario
    for j in range(16):
        place(sfx, AV.click(j), w(3, 14) + j * 0.1, db(-24))       # gente formándose
    place(sfx, impact(), w(4, 4) - 0.05, db(-8))                   # botón
    place(sfx, AV.ding(), w(4, 4), db(-14))
    for j in range(22):
        place(sfx, AV.click(50 + j), w(4, 7) + j * 0.15, db(-22))  # cajas apilándose
    place(sfx, A.shimmer(1.2, seed=5), w(4, 15), db(-13))          # trofeo
    for j in range(3):
        place(sfx, impact(), w(5, j) - 0.1, db(-9))                # cortes secos
    place(sfx, AG.riser(0.6), w(5, 6) - 0.6, db(-14))
    place(sfx, A.shimmer(1.0, seed=8), w(5, 8), db(-15))
    for j in range(36):
        place(sfx, AV.click(100 + j), w(6, 14) + j * 0.07, db(-26)) # tecleo en el chat
    place(sfx, A.whoosh(0.7, seed=90), w(6, 26), db(-13))          # la maqueta vuela al teléfono
    place(sfx, AV.ding(), w(6, 29), db(-15))
    for j in range(3):
        place(sfx, AV.click(150 + j), w(7, 1) + j * 0.08, db(-18))
    for j in range(14):
        place(sfx, AV.ping(1320 + 40 * (j % 4), 1760), w(7, 1) + j * 0.15, db(-28))
    place(sfx, AV.ding(), w(7, 5) - 0.05, db(-13))
    sfx = A.reverb(sfx, 1.0, 0.15, seed=9)

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
