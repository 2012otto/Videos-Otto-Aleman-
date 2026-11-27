"""Audio de "Estás haciendo esto mal con tu perfume": marimba alegre (original) con más cuerpo, efectos por
acción (atomizador, antifaz, interruptor, alarma, tos, sello de mito, checks, caja registradora) y la voz al frente.

Uso: VIDEO_BUILD=$PWD/otto_serie/build_nariz VO_TRIM=0.15 VO_GAP=0.25 VO_TAIL=0.8 python3 otto_serie/src/audio_nariz.py
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


def alarm(dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 700 + 300 * (np.sin(2 * np.pi * 3 * t) > 0)
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.12 * np.minimum(1, (dur - t) / 0.2)


def cough(seed=1):
    r = np.random.default_rng(seed)
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    return A.lowpass(r.standard_normal(n), 1800) * np.exp(-t * 12) * 0.5


def switch_click():
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 90) * 0.5


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

    mus = marimba_song(total + 2)[:n]
    mus /= np.abs(mus).max() + 1e-9
    # bajo suave debajo de la marimba para darle cuerpo
    tt = np.arange(n) / SR
    bass = np.sin(2 * np.pi * 55 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * (126 / 60) * tt)) * 0.25
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.5 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus = (mus + bass) * duck * db(-19)
    a0, a1 = int(st(7) * SR), int(st(8) * SR)
    mus[a0:a1] *= 0.5                                                  # el error
    f = int(0.25 * SR)
    mus[:f] *= np.linspace(0, 1, f)
    mus[-f:] *= np.linspace(1, 0, f)

    sfx = np.zeros(n)
    for j in range(3):
        place(sfx, A.spray(), 0.2 + j * 0.45, db(-13))
    place(sfx, impact(), w(0, 0) - 0.05, db(-12))                       # ¡LO ESTÁS HACIENDO MAL!
    for i in range(1, len(vo)):
        place(sfx, A.whoosh(0.35, seed=20 + i), st(i) - 0.08, db(-19))
    place(sfx, A.spray(), st(1) + 0.3, db(-13))
    for j in range(14):
        place(sfx, tick(), w(1, 6) + j * 0.09, db(-22))
    place(sfx, thunk(), w(2, 5), db(-11))                              # antifaz
    place(sfx, A.whoosh(0.6, seed=5), st(3) - 0.5, db(-12))             # entra a la nariz
    place(sfx, switch_click(), w(3, 6) + 0.3, db(-8))                  # apaga PERFUME
    for j in range(20):
        place(sfx, tick(), w(4, 9) - 0.3 + j * 0.1, db(-21))
    place(sfx, alarm(1.8), w(5, 13) - 0.1, db(-12))
    place(sfx, switch_click(), w(5, 13) - 0.1, db(-8))
    place(sfx, A.shimmer(0.8, seed=6), w(6, 8), db(-15))
    for j, wi in enumerate((6, 7, 9, 11)):
        place(sfx, A.spray(), w(7, wi), db(-12 + j))
    for j in range(4):
        place(sfx, cough(j), w(7, 9) + j * 0.35, db(-14))
    place(sfx, wah(), w(7, 4), db(-12))
    place(sfx, impact(), w(8, 6), db(-11))                             # MITO
    for wi in (4, 10, 15):
        place(sfx, AV.ding(), w(9, wi), db(-16))
    place(sfx, A.shimmer(1.0, seed=7), w(10, 5), db(-15))
    place(sfx, A.shimmer(1.2, seed=8), w(11, 3), db(-13))
    place(sfx, thunk(), w(11, 9), db(-13))
    place(sfx, thunk(), w(11, 11), db(-13))
    place(sfx, impact(), w(12, 5), db(-10))                            # BLACK FRIDAY
    place(sfx, AV.ding(), w(12, 7), db(-12))
    for j in range(2):
        place(sfx, thunk(), w(12, 11) + j * 0.25, db(-14))
    place(sfx, AV.ding(), w(12, 17) - 0.05, db(-11))
    place(sfx, A.shimmer(1.4, seed=9), w(12, 17), db(-12))
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
