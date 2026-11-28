"""Audio de "¡Esto SÍ son ofertas!" (Black Friday navideño): tienda gris con zumbido triste, vidrio que se rompe,
marimba alegre con cascabeles navideños, impactos y efectos por acción; voz al frente.

Uso: VIDEO_BUILD=$PWD/otto_serie/build_bf VO_TRIM=0.15 VO_GAP=0.22 VO_TAIL=0.6 python3 otto_serie/src/audio_blackfriday.py
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
sys.modules.pop("audio_ep4", None)
from audio_ep4 import marimba_song  # noqa: E402
from audio_ep1 import A, timeline, SR, db, place  # noqa: E402
import audio_velto as AV  # noqa: E402
from audio_decant_tarde import thunk, tick, wobble  # noqa: E402
from audio_elixir import impact  # noqa: E402
from audio_mandarin import wah  # noqa: E402


def bells(dur, bpm=126):
    """Cascabeles navideños en corcheas."""
    n = int(dur * SR)
    out = np.zeros(n)
    r = np.random.default_rng(3)
    step = 60 / bpm / 2
    k = int(0.12 * SR)
    t = np.arange(k) / SR
    for i in range(int(dur / step)):
        hit = A.highpass(r.standard_normal(k), 6000) * np.exp(-t * (30 if i % 2 else 18))
        for f in (5200, 6900, 8300):
            hit += 0.3 * np.sin(2 * np.pi * f * t + r.random() * 6) * np.exp(-t * 25)
        place(out, hit * (1.0 if i % 2 == 0 else 0.6), i * step)
    return out


def glass(seed=4):
    r = np.random.default_rng(seed)
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    out = A.highpass(r.standard_normal(n), 3000) * np.exp(-t * 6) * 0.6
    for _ in range(40):
        p = r.random() * 1.0
        k = int(0.08 * SR)
        tt = np.arange(k) / SR
        tink = np.sin(2 * np.pi * (3000 + 5000 * r.random()) * tt) * np.exp(-tt * 50) * 0.3
        place(out, tink, p)
    return out


def buzz(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 120 * t) + 0.3 * np.sin(2 * np.pi * 240 * t)) * 0.08 * (0.7 + 0.3 * (np.sin(2 * np.pi * 7 * t) > 0))


def womp():
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = 220 * np.exp(-t * 0.8)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.5) * 0.5


def main():
    vo, total = timeline.load()
    n = int(total * SR)
    voice = np.zeros(n)
    for s in vo:
        place(voice, A.load_mp3(s["file"]), s["vo_start"])
    voice /= np.abs(voice).max() + 1e-9
    voice *= db(-2.0)
    st = lambda i: vo[i]["start"]  # noqa: E731
    w = lambda i, j: vo[i]["tokens"][min(j, len(vo[i]["tokens"]) - 1)]["s"]  # noqa: E731
    br = w(0, 4) - 0.15                     # se rompe la tienda gris

    mus = marimba_song(total + 2)[:n]
    mus /= np.abs(mus).max() + 1e-9
    tt = np.arange(n) / SR
    bass = np.sin(2 * np.pi * 55 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * (126 / 60) * tt)) * 0.25
    jb = bells(total + 1)[:n] * 0.35
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.5 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus = (mus + bass + jb) * duck * db(-18)
    b0 = int(br * SR)
    mus[:b0] = 0                                                        # la tienda gris: sin música
    f = int(0.05 * SR)
    mus[b0:b0 + f] *= np.linspace(0, 1, f)
    a0, a1 = int((w(2, 0) - 0.25) * SR), int(w(2, 0) * SR)              # silencio antes de NAVIDEÑO
    mus[a0:a1] *= np.linspace(1, 0.1, a1 - a0)
    mus[-f:] *= np.linspace(1, 0, f)

    sfx = np.zeros(n)
    place(sfx, buzz(br), 0.0, db(-16))
    place(sfx, womp(), w(0, 3), db(-12))
    place(sfx, glass(), br, db(-8))
    place(sfx, impact(), br + 0.05, db(-9))                             # ¡ESTO SÍ SON OFERTAS!
    place(sfx, A.shimmer(1.2, seed=3), br + 0.1, db(-13))
    for i in range(1, len(vo)):
        place(sfx, A.whoosh(0.35, seed=20 + i), st(i) - 0.08, db(-18))
    for j in range(6):
        place(sfx, tick(), st(1) + 0.1 + j * 0.13, db(-20))             # neón
    place(sfx, impact(), w(2, 0) - 0.03, db(-7))                         # ¡NAVIDEÑO!
    place(sfx, A.shimmer(1.4, seed=4), w(2, 0), db(-11))
    place(sfx, AV.ding(), w(3, 2), db(-14))
    place(sfx, impact(), w(4, 0) - 0.03, db(-10))                        # 3x2
    place(sfx, A.whoosh(0.5, seed=7), w(4, 3) - 0.4, db(-14))           # cae el tercero
    place(sfx, thunk(), w(4, 4), db(-10))
    for j in range(2):
        place(sfx, thunk(), st(5) + 0.2 + j * (w(5, 1) - st(5)), db(-12))
    place(sfx, thunk(), w(5, 6) - 0.1, db(-8))                          # sello GRATIS
    place(sfx, AV.ding(), w(5, 6), db(-11))
    place(sfx, A.shimmer(1.2, seed=5), w(5, 6), db(-12))
    for wi in (3, 5, 9):
        place(sfx, A.whoosh(0.4, seed=40 + wi), w(6, wi) - 0.35, db(-14))
    place(sfx, AV.ding(), w(7, 1), db(-15))
    place(sfx, AV.ding(), w(7, 3), db(-14))
    place(sfx, wah(), w(7, 7), db(-13))                                 # frasco completo tachado
    for j in range(10):
        place(sfx, A.whoosh(0.25, seed=60 + j), st(8) + 0.1 + j * 0.12, db(-20))
    for j in range(12):
        place(sfx, AV.ding(), st(9) + 0.15 + j * 0.14, db(-24))         # burbujas de mensajes
    place(sfx, impact(), w(10, 2) - 0.03, db(-9))                        # ¡SÍ son ofertas!
    place(sfx, A.shimmer(1.4, seed=9), w(10, 2), db(-12))
    sfx = A.reverb(sfx, 1.0, 0.15, seed=9)

    bed = mus + sfx
    d = int(0.012 * SR)
    out = np.stack([voice + bed, voice + np.concatenate([np.zeros(d), bed[:-d]])], 1)
    out /= max(1.0, np.abs(out).max() / db(-1))
    raw = os.path.join(timeline.BUILD, "audio_raw.wav")
    with wave.open(raw, "wb") as fh:
        fh.setnchannels(2)
        fh.setsampwidth(2)
        fh.setframerate(SR)
        fh.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())
    dst = os.path.join(timeline.BUILD, "audio.wav")
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "acompressor=threshold=-20dB:ratio=2.5:attack=10:release=150,loudnorm=I=-14:TP=-1.5:LRA=9",
                           "-ar", str(SR), dst])
    print(dst, f"{total:.2f}s")


if __name__ == "__main__":
    main()
