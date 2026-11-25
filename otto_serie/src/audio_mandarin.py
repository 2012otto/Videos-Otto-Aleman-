"""Audio de "Cómo crear un Mandarin Sky": marimba alegre (original), sonido de error chistoso en cada fallo,
campanita cuando se arregla, máquinas, líquidos, gotas, burbujas y la voz de David.

Uso: VIDEO_BUILD=$PWD/otto_serie/build_mandarin VO_TRIM=0.15 VO_GAP=0.3 VO_TAIL=2.0 python3 otto_serie/src/audio_mandarin.py
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
from audio_decant_tarde import thunk, tick, wobble  # noqa: E402

ERRORS = [(1, 5), (3, 7), (5, 9), (7, 4), (9, 18)]
FIXES = [(2, 3), (4, 7), (6, 4), (8, 4), (10, 11), (12, 2)]


def wah():
    """'wah-wah' de error."""
    out = np.zeros(int(1.2 * SR))
    for i, f0 in enumerate((392, 370, 349, 330)):
        n = int(0.28 * SR if i < 3 else 0.5 * SR)
        t = np.arange(n) / SR
        f = f0 * (1 - 0.04 * t / (n / SR))
        s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5
        s *= (1 + 0.3 * np.sin(2 * np.pi * 6 * t)) * np.minimum(1, t / 0.02) * np.clip((n / SR - t) / 0.05, 0, 1)
        place(out, A.lowpass(s, 1500) * 0.35, i * 0.28)
    return out


def pour(dur=1.5):
    return A.pour(dur, seed=5) if hasattr(A, "pour") else np.zeros(int(dur * SR))


def drip():
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    f = 900 + 1400 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * 0.35


def hum(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 60 * t) + 0.5 * np.sin(2 * np.pi * 120 * t)) * 0.12 * np.minimum(1, t / 0.2) * np.clip((dur - t) / 0.3, 0, 1)


def main():
    vo, total = timeline.load()
    n = int(total * SR)
    voice = np.zeros(n)
    for s in vo:
        place(voice, A.load_mp3(s["file"]), s["vo_start"])
    voice /= np.abs(voice).max() + 1e-9
    voice *= db(-2.5)
    st = lambda i: vo[i]["start"]  # noqa: E731
    w = lambda i, j: vo[i]["tokens"][min(j, len(vo[i]["tokens"]) - 1)]["s"]  # noqa: E731

    mus = marimba_song(total)[:n]
    mus /= np.abs(mus).max() + 1e-9
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus = mus * duck * db(-19)
    for si, _ in ERRORS:  # la música se "cae" en cada error
        a, b = int(st(si) * SR), int((st(si) + vo[si]["end"] - vo[si]["start"]) * SR)
        mus[a:b] *= 0.35

    sfx = np.zeros(n)
    for i in range(1, len(vo)):
        place(sfx, A.pop(), st(i) + 0.02, db(-20))
    place(sfx, thunk(), 0.5, db(-12))                                  # máquina de inyección
    place(sfx, hum(1.2), 0.2, db(-14))
    place(sfx, AV.click(2), w(0, 6) + 0.4, db(-10))                   # clic de la tapa
    for si, wi in ERRORS:
        place(sfx, wah(), w(si, wi) - 0.05, db(-11))
    for si, wi in FIXES:
        place(sfx, AV.ding(), w(si, wi), db(-17))
    place(sfx, A.spray(), w(1, 3), db(-14))
    place(sfx, pour(2.5), w(2, 3) - 0.2, db(-14))                     # alcohol
    for j in range(12):
        place(sfx, drip(), w(4, 31) + j * 0.35, db(-16))              # gota a gota
    place(sfx, A.swell(1.2), w(4, 13) - 0.4, db(-16))
    for j in range(24):
        place(sfx, tick(), st(5) + 0.3 + j * 0.08, db(-22))           # reloj
    for j, wi in enumerate((5, 7, 9)):
        place(sfx, drip(), w(6, wi), db(-14))
    for j, wi in enumerate((5, 6, 8)):
        place(sfx, drip(), w(8, wi), db(-14))
    place(sfx, A.shimmer(1.0, seed=4), w(8, 10), db(-15))
    place(sfx, hum(3.0), st(9) + 0.2, db(-12))                         # tanques
    place(sfx, A.spray(), w(9, 11), db(-13))
    place(sfx, wobble(), w(9, 15), db(-12))
    place(sfx, A.shimmer(1.2, seed=6), w(10, 20), db(-14))              # cristalino
    for j in range(16):
        place(sfx, thunk(), st(11) + 0.4 + j * 0.55, db(-24))          # línea de llenado
    place(sfx, A.shimmer(1.4, seed=8), w(12, 2), db(-12))
    place(sfx, AV.ding(), w(13, 12), db(-15))
    for j in range(10):
        place(sfx, AV.click(80 + j), w(14, 1) + j * 0.08, db(-24))
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
