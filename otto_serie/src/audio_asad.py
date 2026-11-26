"""Audio del Asad Bourbon original vs falso: beat nocturno suave (audio_gta) bajito, coro celestial en el
foco de luz, 'ding' de cada paso, chiste de la aureola, monedas, sellos y las dos voces.

Uso: VIDEO_BUILD=$PWD/otto_serie/build_asad VO_TRIM=0.15 VO_GAP=0.25 VO_TAIL=0.8 python3 otto_serie/src/audio_asad.py
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
import audio_gta as AG  # noqa: E402
from audio_ep1 import A, timeline, SR, db, place  # noqa: E402
midi = A.midi
import audio_velto as AV  # noqa: E402
from audio_decant_tarde import thunk, tick  # noqa: E402
from audio_elixir import impact, pss  # noqa: E402


def choir(dur=2.2):
    out = np.zeros(int(dur * SR))
    t = np.arange(len(out)) / SR
    for f in (midi(72), midi(76), midi(79), midi(84)):
        out += np.sin(2 * np.pi * f * t) * (1 + 0.3 * np.sin(2 * np.pi * 5 * t))
    return out * np.sin(np.pi * t / dur) * 0.08


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

    tt = np.arange(n) / SR
    beat = AG.music(total + 1)[:n]
    beat /= np.abs(beat).max() + 1e-9
    mar = marimba_song(total)[:n]
    mar /= np.abs(mar).max() + 1e-9
    gold = ((tt >= st(17)) & (tt < st(19))).astype(float)
    gold = np.convolve(gold, np.ones(int(0.3 * SR)) / int(0.3 * SR), mode="same")
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus = (beat * (1 - gold) * db(-22) + mar * gold * db(-19)) * duck
    sil = (tt >= st(4)) & (tt < st(9))
    mus[sil] *= 0.25                                            # el chiste: casi sin música
    # bucle: inicio y final con el mismo nivel para que el corte no se note
    f = int(0.25 * SR)
    mus[:f] *= np.linspace(0, 1, f)
    mus[-f:] *= np.linspace(1, 0, f)

    sfx = np.zeros(n)
    place(sfx, A.shimmer(1.0, seed=1), 0.05, db(-16))
    place(sfx, impact(), w(0, 7) + 0.2, db(-13))                   # sello ¿ORIGINAL?
    for i in range(1, len(vo)):
        place(sfx, A.pop(), st(i) + 0.02, db(-22))
    place(sfx, AV.buzz(0.3), w(1, 6), db(-18))                      # -50%
    for j in range(3):
        place(sfx, A.spray(), w(1, 9) + j * 0.25, db(-15))
    for j in range(16):
        place(sfx, tick(), st(2) + 0.1 + j * 0.1, db(-22))
    place(sfx, choir(2.6), st(4) - 0.1, db(-6))                     # foco de luz
    place(sfx, A.whoosh(0.6, seed=4), st(4), db(-14))
    place(sfx, A.shimmer(1.2, seed=5), w(5, 2), db(-11))            # aureola
    place(sfx, A.whoosh(0.4, seed=6), w(6, 1), db(-12))             # manotazo a la aureola
    place(sfx, A.shimmer(0.6, seed=7), st(8) + 0.5, db(-15))        # la aureola vuelve
    for j in range(6):
        place(sfx, AV.click(10 + j), st(9) + 0.3 + j * 0.3, db(-22))
    for i in (10, 11, 12, 13, 15):
        place(sfx, AV.ding(), w(i, 0), db(-16))                     # cada paso
    place(sfx, AV.ding(), w(10, 19), db(-13))
    place(sfx, AV.ping(), w(12, 12), db(-14))                       # QR oficial
    place(sfx, thunk(), w(13, 6), db(-10))
    for j in range(3):
        place(sfx, AV.click(30 + j), st(14) + 0.3 + j * 0.4, db(-18))  # monedas
    for j in range(5):
        place(sfx, AV.buzz(0.15), st(16) + 0.9 + j * 0.12, db(-22))   # X rojas
    place(sfx, impact(), w(17, 1), db(-12))
    place(sfx, A.shimmer(1.2, seed=8), w(17, 1), db(-13))
    for j in range(6):
        place(sfx, thunk(), w(18, 6) - 0.6 + j * 0.16, db(-15))
    place(sfx, AV.ding(), w(18, 12), db(-12))
    place(sfx, A.whoosh(0.5, seed=9), vo[-1]["tokens"][-1]["e"] - 0.4, db(-13))   # entra al frasco (bucle)
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
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                           "-ar", str(SR), dst])
    print(dst, f"{total:.2f}s")


if __name__ == "__main__":
    main()
