"""Audio del Mandarin Sky Elixir: marimba alegre (original), explosión de mandarina, caramelo, reloj,
'pss' del decantado (presiones), caja registradora en el Black Friday, confeti y la voz de David.

Uso: VIDEO_BUILD=$PWD/otto_serie/build_elixir VO_TRIM=0.15 VO_GAP=0.3 VO_TAIL=2.2 python3 otto_serie/src/audio_elixir.py
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
from audio_decant_tarde import thunk, tick  # noqa: E402


def impact():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    k = np.zeros(n)
    place(k, AV.kick(), 0, 1.0)
    return k + np.sin(2 * np.pi * 45 * t) * np.exp(-t * 3) * 0.5


def pss():
    r = np.random.default_rng(4)
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    return A.highpass(r.standard_normal(n), 3000) * np.exp(-t * 18) * 0.3


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

    sfx = np.zeros(n)
    for i in range(1, len(vo)):
        place(sfx, A.whoosh(0.4, seed=10 + i), st(i) - 0.1, db(-17))
    place(sfx, A.shimmer(1.2, seed=1), w(0, 16), db(-14))            # aparece el Elixir
    place(sfx, A.spray(), w(1, 1), db(-12))
    place(sfx, impact(), w(1, 3) - 0.05, db(-12))                    # explota la mandarina
    place(sfx, A.shimmer(0.8, seed=2), w(1, 13), db(-17))
    place(sfx, A.pour(2.0, seed=3), w(2, 4) - 0.3, db(-16))         # caramelo
    place(sfx, A.swell(1.4), w(2, 14) - 0.3, db(-17))               # incienso
    for j in range(20):
        place(sfx, tick(), w(3, 10) + j * 0.09, db(-22))             # reloj
    place(sfx, impact(), w(4, 7) - 0.1, db(-13))                     # Scandal
    place(sfx, AV.ding(), w(4, 13), db(-16))
    place(sfx, A.shimmer(1.2, seed=4), w(5, 15), db(-13))            # logo
    place(sfx, thunk(), w(6, 7), db(-12))                            # quitar la tapa
    place(sfx, AV.click(3), w(6, 11), db(-10))                       # quitar el atomizador
    place(sfx, thunk(), w(7, 9), db(-12))                            # encajar el decant
    for j in range(24):
        place(sfx, pss(), w(7, 13) + j * ((st(8) - w(7, 13) - 0.3) / 24), db(-15))
    place(sfx, AV.ding(), w(8, 3), db(-13))
    place(sfx, A.shimmer(1.0, seed=6), w(8, 3), db(-15))
    place(sfx, impact(), w(9, 9) - 0.1, db(-9))                      # BLACK FRIDAY
    place(sfx, AV.buzz(0.3), w(9, 13), db(-17))
    place(sfx, AV.ding(), w(9, 14), db(-12))
    for j in range(6):
        place(sfx, AV.pluck(880 + 110 * j, 0.25), w(9, 17) + j * 0.15, db(-15))
    place(sfx, AV.ding(), w(9, 24) - 0.05, db(-11))
    place(sfx, A.shimmer(1.4, seed=8), w(9, 24), db(-12))
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
