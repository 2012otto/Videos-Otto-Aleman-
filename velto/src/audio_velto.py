"""Audio del video Velto: música original (sintetizada, sin derechos), efectos y mezcla con la voz.

Uso: VIDEO_BUILD=velto/build VO_TRIM=0.3 python3 velto/src/audio_velto.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "src"))
import audio as A  # noqa: E402
import timeline  # noqa: E402
from audio import SR, db, place, midi, lowpass, highpass, reverb  # noqa: E402

RNG = np.random.default_rng(7)


def pluck(f, dur=0.6, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k in range(1, 6):
        s += np.sin(2 * np.pi * f * k * t) * (0.6 ** k) * np.exp(-t * (6 + 3 * k))
    return s * np.minimum(1, t / 0.003) * vel * 0.6


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.9


def hat(seed):
    r = np.random.default_rng(seed)
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    return highpass(r.standard_normal(n), 7000) * np.exp(-t * 60) * 0.25


def clap(seed):
    r = np.random.default_rng(seed)
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    x = lowpass(r.standard_normal(n), 3500) - lowpass(r.standard_normal(n), 900)
    env = np.exp(-t * 22) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0))
    return x * env * 0.35


CH = {"C": [48, 60, 64, 67], "G": [43, 59, 62, 67], "Am": [45, 60, 64, 69], "F": [41, 60, 65, 69],
      "Dm": [50, 62, 65, 69], "Em": [40, 59, 64, 67]}


def music(total, drop):
    bpm = 104
    beat = 60 / bpm
    bar = 4 * beat
    n = int((total + 3) * SR)
    syn, pd, bs, dr = (np.zeros(n) for _ in range(4))
    nbars = int(total / bar) + 2
    for b in range(nbars):
        t0 = b * bar
        on = t0 >= drop - 0.01
        name = (["Am", "F", "Dm", "Em"] if not on else ["C", "G", "Am", "F"])[b % 4]
        notes = CH[name]
        place(pd, A.pad([midi(x) for x in notes[1:]], bar + 0.8), t0, 0.8 if on else 1.0)
        for i in range(8 if on else 4):
            step = beat / 2 if on else beat
            nt = notes[1 + (i * 2) % 3] + (12 if on and i % 4 == 3 else 0)
            place(syn, pluck(midi(nt + 12), 0.5, 0.8 if i % 2 == 0 else 0.55), t0 + i * step)
        if on:
            for i in range(4):
                place(bs, pluck(midi(notes[0]), 0.45, 1.0), t0 + i * beat)
                place(dr, kick(), t0 + i * beat, 0.9)
                place(dr, hat(b * 8 + i), t0 + i * beat + beat / 2)
                if i in (1, 3):
                    place(dr, clap(b * 4 + i), t0 + i * beat, 0.8)
    t = np.arange(n) / SR
    # bombeo suave (sidechain) con el bombo después del drop
    pump = np.ones(n)
    k = (t >= drop)
    ph = ((t - drop) % beat) / beat
    pump[k] = 0.55 + 0.45 * np.minimum(1, ph[k] / 0.35)
    mix = (syn * 0.55 + pd * 0.7) * pump + lowpass(bs, 300) * 0.8 * pump + dr * 0.75
    mix = reverb(mix, 1.6, 0.22)
    # subida antes del drop
    riser_n = int(1.2 * SR)
    rt = np.arange(riser_n) / SR
    riser = highpass(RNG.standard_normal(riser_n), 2000) * (rt / 1.2) ** 2 * 0.25
    place(mix, riser, drop - 1.2)
    mix *= np.minimum(1, t / 1.0) * np.clip((total - t) / 1.4, 0, 1)
    return mix[: int(total * SR)]


def ping(f1=1320, f2=1760):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f1 * t) * (t < 0.08) + np.sin(2 * np.pi * f2 * t) * (t >= 0.08)
    return s * np.exp(-((t % 0.08) * 25)) * np.exp(-t * 6) * 0.35


def buzz(dur=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 170 * t)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * t)))
    return lowpass(s, 700) * 0.25 * np.minimum(1, (dur - t) / 0.05)


def click(seed):
    r = np.random.default_rng(seed)
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return highpass(r.standard_normal(n), 2500) * np.exp(-t * 200) * 0.4


def sad():
    out = np.zeros(int(2.5 * SR))
    place(out, A.piano(midi(64), 2.0, 0.7), 0.0)
    place(out, A.piano(midi(60), 2.0, 0.7), 0.35)
    place(out, A.piano(midi(57), 2.0, 0.7), 0.7)
    return out * 0.6


def ding():
    out = np.zeros(int(2.5 * SR))
    place(out, A.bell(1568.0), 0.0, 0.6)
    place(out, A.bell(2093.0), 0.12, 0.5)
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
    drop = st(3) + 0.55
    mus = music(total, drop)
    mus /= np.abs(mus).max() + 1e-9
    env = np.abs(voice)
    win = int(0.25 * SR)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    duck = 1 - 0.4 * np.clip(env / (env.max() * 0.35), 0, 1)
    duck = np.convolve(duck, np.ones(win) / win, mode="same")
    mus *= duck * db(-16)

    sfx = np.zeros(n)
    place(sfx, buzz(0.5), st(0) + 0.3, db(-20))
    t0 = w(0, 8) - 0.3
    for i in range(7):
        place(sfx, ping(1320 + 60 * (i % 3), 1760 + 60 * (i % 3)), t0 + i * 0.32 - st(0) + st(0), db(-19))
    place(sfx, buzz(0.8), w(0, 12), db(-18))
    for i in range(1, 8):
        place(sfx, A.whoosh(0.6, seed=20 + i), st(i) - 0.25, db(-22))
    for j in (0, 2, 4):  # fotos enviadas / precios
        place(sfx, ping(990, 1320), w(1, j), db(-21))
    for j in (1, 3, 5):
        place(sfx, ping(1320, 1760), w(1, j) + 0.3, db(-21))
    place(sfx, sad(), w(2, 6) - 0.1, db(-17))
    place(sfx, A.shimmer(1.4, n=50, seed=3, lo=2000, hi=7000), st(3) + 0.1, db(-12))
    place(sfx, A.swell(1.8), st(3) + 0.4, db(-15))
    for j in range(8):
        place(sfx, click(j), w(4, 8) + j * 0.06, db(-24))
    for j in range(4):
        place(sfx, A.pop(), w(4, 10) - 0.2 + j * 0.18, db(-22))
    place(sfx, A.pop(), w(4, 14), db(-20))
    place(sfx, click(99), w(5, 12), db(-16))
    place(sfx, A.whoosh(0.5, seed=77), w(5, 12) + 0.1, db(-20))
    place(sfx, ding(), w(5, 13) + 0.3, db(-15))
    for j in range(7):
        place(sfx, A.pop(), w(6, 2) - 0.2 + (0 if j == 0 else w(6, 5) - w(6, 2) + (j - 1) * 0.22), db(-24))
    place(sfx, A.shimmer(1.6, n=50, seed=8, lo=2000, hi=7000), st(7) + 0.1, db(-12))
    place(sfx, A.pop(), w(7, 6) - 0.15, db(-20))
    place(sfx, A.pop(), w(7, 8) - 0.15, db(-20))
    sfx = reverb(sfx, 1.4, 0.2, seed=9)

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
