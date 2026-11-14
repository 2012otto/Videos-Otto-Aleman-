"""Audio GTA 6 parte 2 (Velto): beat enérgico, efecto de disco rayado en el giro, dings de pedidos.

Uso: VIDEO_BUILD=$PWD/velto/build_gta2 VO_TRIM=0.12 VO_GAP=0.15 VO_TAIL=1.2 python3 velto/src/audio_gta2.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_gta as AG  # noqa: E402
import audio_velto as AV  # noqa: E402
from audio_velto import A, timeline, SR, db, place, lowpass  # noqa: E402
from audio_ep2 import impact  # noqa: E402


def scratch(dur=0.35, seed=4):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 300 + 900 * np.abs(np.sin(2 * np.pi * 6 * t))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    noise = lowpass(r.standard_normal(n), 3000) * 0.5
    return (tone * 0.5 + noise) * np.exp(-t * 4) * 0.6


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
    gate[(tt >= st(4) - 0.05) & (tt < st(4) + 0.9)] = 0.0  # silencio en el giro
    gate = np.convolve(gate, np.ones(int(0.02 * SR)) / int(0.02 * SR), mode="same")
    i0 = int((st(4) - 0.05) * SR)
    mus = beat * gate
    place(mus, AG.tape_stop(beat[i0:i0 + int(0.5 * SR)]), st(4) - 0.05)
    k = int(0.2 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.4 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus = mus * db(-16) * duck
    mus[: int(1.2 * SR)] *= np.linspace(0.35, 1, int(1.2 * SR))

    sfx = np.zeros(n)
    place(sfx, A.whoosh(1.6, seed=1), 0.0, db(-12))
    place(sfx, impact(), w(0, 0) - 0.05, db(-11))
    for i in (1, 2, 3):
        place(sfx, A.whoosh(0.4, seed=40 + i), st(i) - 0.1, db(-13))
    for j in range(18):
        place(sfx, AV.ping(1320 + 40 * (j % 4), 1760), w(0, 8) + j * 0.07, db(-26))  # dinero
    place(sfx, impact(), w(0, 11) - 0.05, db(-12))
    for j in range(20):
        place(sfx, AV.click(j), w(1, 1) + j * 0.18, db(-26))                         # compras en el globo
    place(sfx, impact(), w(2, 4) - 0.1, db(-9))                                      # trofeo
    place(sfx, A.shimmer(1.0, seed=3), w(2, 4), db(-14))
    for j in range(14):
        place(sfx, AV.pluck(1320, 0.2), st(3) + 0.3 + j * 0.3, db(-24))              # "compra realizada"
    place(sfx, scratch(), st(4) - 0.05, db(-8))                                      # disco rayado
    place(sfx, A.whoosh(0.5, seed=60), w(4, 8) - 0.3, db(-16))                       # saca el teléfono
    place(sfx, AG.riser(0.6), st(5) - 0.6, db(-13))
    place(sfx, A.whoosh(0.7, seed=61), st(5), db(-12))                               # entra a la pantalla
    for j in range(4):
        place(sfx, AV.ding(), w(5, 13) - 0.2 + j * 0.32, db(-18))                    # pedidos
    place(sfx, A.whoosh(0.6, seed=62), st(6), db(-14))
    for j in range(5):
        place(sfx, AV.click(80 + j), w(6, 1) - 0.25 + j * 0.06, db(-18))             # tecleo VENTA
    for j in range(14):
        place(sfx, AV.ping(1320 + 40 * (j % 4), 1760), w(6, 1) + j * 0.15, db(-28))
    place(sfx, AV.ding(), w(6, 12) - 0.05, db(-13))
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
