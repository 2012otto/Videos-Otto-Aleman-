"""Audio de "Te enamoró en la mañana… y en la tarde ya no": marimba alegre suave (original), efectos
(pop en cada corte, caja, atomizador, reloj, mareo, sellos, confeti) y la voz de David.

Uso: VIDEO_BUILD=$PWD/otto_serie/build_decant VO_TRIM=0.15 VO_GAP=0.2 VO_TAIL=1.8 python3 otto_serie/src/audio_decant_tarde.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "velto", "src"))
sys.path.insert(0, HERE)
from audio_ep4 import marimba_song  # noqa: E402
from audio_ep1 import A, timeline, SR, db, place  # noqa: E402
import audio_velto as AV  # noqa: E402


def tick():
    n = int(0.04 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 140) * 0.35


def thunk():
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    f = 160 * np.exp(-t * 8)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22) * 0.7


def rip(dur=0.5, seed=3):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    return A.highpass(r.standard_normal(n), 1800) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 40 * t))) * np.exp(-t * 3) * 0.3


def wobble(dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 300 + 120 * np.sin(2 * np.pi * 3 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / dur) * 0.2


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

    mus = marimba_song(total)[:n]
    mus /= np.abs(mus).max() + 1e-9
    tt = np.arange(n) / SR
    sad = ((tt >= st(4) + 1.0) & (tt < st(8))).astype(float)   # tarde y "error": más bajita
    sad = np.convolve(sad, np.ones(int(0.4 * SR)) / int(0.4 * SR), mode="same")
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus = mus * duck * db(-19) * (1 - 0.6 * sad)

    sfx = np.zeros(n)
    for i in range(1, len(vo)):
        place(sfx, A.pop(), st(i) + 0.02, db(-20))
    place(sfx, A.shimmer(0.8, seed=1), w(0, 0), db(-18))
    for j in range(3):
        place(sfx, A.pop(), w(1, 2 + j * 2), db(-17))
    place(sfx, AV.click(3), w(2, 4) + 0.15, db(-12))
    place(sfx, AV.ding(), w(2, 5), db(-18))
    place(sfx, thunk(), st(3) + 0.3, db(-12))                        # el paquete
    place(sfx, rip(), w(3, 3) - 0.2, db(-12))
    place(sfx, A.shimmer(1.0, seed=2), w(3, 5) + 0.3, db(-16))
    place(sfx, A.spray(), w(3, 8) - 0.1, db(-12))
    place(sfx, A.spray(), w(3, 9) + 0.1, db(-12))
    place(sfx, A.chime(), w(3, 13), db(-16))
    for j in range(24):
        place(sfx, tick(), st(4) + 0.2 + j * 0.11, db(-20))           # reloj
    place(sfx, A.swell(1.4), w(5, 7) - 0.5, db(-16))
    place(sfx, wobble(), w(5, 19) - 0.1, db(-12))                    # mareo
    place(sfx, A.pop(), w(6, 6), db(-15))
    place(sfx, AV.buzz(0.3), w(6, 7), db(-18))
    place(sfx, A.shimmer(1.2, seed=4), w(8, 3), db(-13))             # logo
    place(sfx, A.whoosh(0.5, seed=5), w(8, 8) - 0.3, db(-15))
    for j in range(5):
        place(sfx, A.spray(), w(8, 16) + j * 0.5, db(-17))
    place(sfx, AV.ding(), w(9, 2), db(-17))
    place(sfx, AV.buzz(0.25), w(9, 6), db(-20))
    place(sfx, thunk(), w(10, 8), db(-12))
    for j in range(6):
        place(sfx, AV.pluck(880 + 110 * j, 0.25), w(10, 11) - 0.2 + j * 0.13, db(-15))
    for j in range(6):
        place(sfx, thunk(), w(11, 8) - 0.6 + j * 0.16, db(-14))     # sellos
    place(sfx, AV.ding(), w(11, 19) - 0.05, db(-12))
    place(sfx, A.shimmer(1.2, seed=7), w(11, 19), db(-13))
    for j in range(14):
        place(sfx, AV.click(80 + j), w(12, 8) + j * 0.07, db(-24))  # tecleo
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
