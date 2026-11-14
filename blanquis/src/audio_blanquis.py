"""Audio Chocobananos Blanqui's: música tropical instrumental suave (marimba + guitarra + shaker, original),
olas en la playa, efectos de gotas/pops/selector y la voz.

Uso: VIDEO_BUILD=$PWD/blanquis/build VO_TRIM=0.2 VO_GAP=0.4 VO_TAIL=2.5 python3 blanquis/src/audio_blanquis.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "velto", "src"))
sys.path.insert(0, os.path.join(REPO, "otto_serie", "src"))
from audio_ep4 import marimba, ocean  # noqa: E402
from audio_ep1 import A, timeline, SR, db, place  # noqa: E402
import audio_velto as AV  # noqa: E402

midi = A.midi
RNG = np.random.default_rng(5)


def guitar(f, dur=0.6, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * k * t) * (0.55 ** k) * np.exp(-t * (4 + 2.5 * k)) for k in range(1, 7))
    return s * np.minimum(1, t / 0.004) * vel * 0.4


def shaker(seed):
    r = np.random.default_rng(seed)
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    return A.highpass(r.standard_normal(n), 6000) * np.sin(np.pi * t / 0.08) * 0.12


def tropical(dur):
    bpm = 104
    e = 60 / bpm / 2
    n = int((dur + 2) * SR)
    out = np.zeros(n)
    chords = [[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]]  # C F G C
    mel = [76, 79, 81, 79, 76, 74, 72, 74, 77, 81, 84, 81, 77, 76, 74, 72,
           79, 83, 86, 83, 79, 77, 74, 71, 76, 74, 72, 67, 72, 76, 79, 76]
    step, t = 0, 0.0
    while t < dur + 1:
        ch = chords[(step // 8) % 4]
        if step % 2 == 0 or step % 8 == 3:
            place(out, marimba(midi(mel[step % len(mel)]), 0.5, 0.55), t)
        if step % 8 in (0, 3, 6):  # guitarra con patrón tropical
            for j, nn in enumerate(ch):
                place(out, guitar(midi(nn - 12), 0.8, 0.5), t + j * 0.012)
        if step % 4 == 0:
            place(out, guitar(midi(ch[0] - 24), 1.0, 0.9), t)
        place(out, shaker(step), t, 1.0 if step % 2 else 0.6)
        if step % 8 == 4:
            place(out, AV.clap(step) * 0.4, t)
        t += e
        step += 1
    tt = np.arange(n) / SR
    out *= np.minimum(1, tt / 1.0) * np.clip((dur - tt) / 1.5, 0, 1)
    return A.reverb(out[: int(dur * SR)], 1.2, 0.18, seed=3)


def plop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 600 + 900 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * 0.4


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

    mus = tropical(total)
    mus /= np.abs(mus).max() + 1e-9
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus = mus[:n] * duck * db(-17)

    sfx = np.zeros(n)
    oc = ocean(st(1) + 0.5)
    oc *= np.clip((st(1) + 0.5 - np.arange(len(oc)) / SR) / 0.8, 0, 1)
    place(sfx, oc, 0.0, db(-16))
    place(sfx, A.whoosh(1.2, seed=1), 0.6, db(-20))
    place(sfx, A.shimmer(1.0, seed=2), 1.6, db(-18))
    for i in (1, 2, 4, 5):
        place(sfx, A.whoosh(0.45, seed=10 + i), st(i) - 0.1, db(-18))
    place(sfx, A.whoosh(0.8, seed=30), st(3) - 0.4, db(-15))           # chocosandía frente a la cámara
    place(sfx, A.whoosh(0.9, seed=31), st(4) - 0.8, db(-17))           # zoom al topogigio
    place(sfx, plop(), st(1) + 0.3, db(-16))
    place(sfx, plop(), w(1, 3) - 0.05, db(-14))
    for d in (0.0, 1.35, 2.7):
        place(sfx, plop(), st(2) + d, db(-14))
    for j in range(8):
        place(sfx, AV.click(j), w(1, 8) + j * 0.05, db(-24))            # caen los trocitos de manía
    sel = [6, 7, 10, 11, 12, 13, 15]
    for i, wi in enumerate(sel[1:]):
        place(sfx, AV.click(40 + i), w(4, wi) - 0.3, db(-14))           # tic del selector
        place(sfx, A.shimmer(0.4, n=12, seed=50 + i, lo=2500, hi=6000), w(4, wi) - 0.2, db(-22))
    place(sfx, A.shimmer(1.0, seed=60), w(4, 16), db(-16))
    for wi in (6, 7, 10):
        place(sfx, A.whoosh(0.3, seed=70 + wi), w(5, wi) - 0.4, db(-20))
        for j in range(10):
            place(sfx, AV.click(90 + j + wi), w(5, wi) + 0.1 + j * 0.06, db(-26))
    for j in range(8):
        place(sfx, plop(), st(6) + 0.4 + j * 0.15, db(-20))
    place(sfx, AV.ding(), st(6) + 0.6, db(-17))
    place(sfx, A.shimmer(1.4, seed=80), w(6, 12), db(-15))
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
