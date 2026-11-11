"""Audio de "La lámpara": orquesta de documental (más suave) con laúd árabe, corte más tardío,
"ba-dum-tss" en el giro y marimba alegre. Música original sintetizada.

Uso: VIDEO_BUILD=$PWD/otto_serie/build_ep5 VO_TRIM=0.3 python3 otto_serie/src/audio_ep5.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_ep4 as E4  # noqa: E402
from audio_ep4 import A, timeline, SR, db, place, midi  # noqa: E402

RNG = np.random.default_rng(33)


def oud(f, dur=1.2, vel=1.0):
    """Laúd (cuerda pulsada, Karplus-Strong)."""
    n = int(dur * SR)
    p = max(2, int(SR / f))
    buf = RNG.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    t = np.arange(n) / SR
    return A.lowpass(out, 3500) * np.minimum(1, t / 0.004) * vel * 0.6


def arabic_melody(start, end):
    """Melodía en Re frigio dominante (escala de sabor árabe)."""
    scale = [62, 63, 66, 67, 69, 70, 72, 74]
    phrase = [0, 1, 2, 1, 3, 2, 1, 0, 4, 5, 4, 3, 2, 1, 2, 0]
    out = np.zeros(int((end + 2) * SR))
    t = start
    i = 0
    while t < end - 1.0:
        note = scale[phrase[i % len(phrase)]]
        dur = 0.6 if i % 4 != 3 else 1.2
        place(out, oud(midi(note), 1.4, 0.8), t)
        t += dur
        i += 1
    return out


def documentary_soft(end):
    n = int((end + 2) * SR)
    out = np.zeros(n)
    bar = 2.6
    prog = ["Dm", "Bb", "Gm", "A", "Dm", "Bb", "F", "A"]
    t0 = 0.0
    i = 0
    while t0 < end - 3.0:
        notes = E4.CH[prog[i % len(prog)]]
        inten = min(0.8, 0.5 + t0 / 50)
        place(out, E4.strings([midi(x) for x in notes[1:]], bar + 0.9, att=0.9, bright=1400 + 900 * inten), t0, 0.8 * inten)
        place(out, E4.contrabass(midi(notes[0] - 12), bar + 0.3), t0, 0.55)
        if i % 4 == 0:
            place(out, E4.timpani(midi(notes[0] - 24) * 2, 2.0), t0, 0.35)
        t0 += bar
        i += 1
    place(out, arabic_melody(1.5, end), 0.0, 0.55)
    return out[: int(end * SR) + int(1.5 * SR)]


def magic_rise(dur=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 300 + 900 * (t / dur) ** 2
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + A.shimmer(dur, n=60, seed=6)[:n]
    return s * np.minimum(1, t / 0.5)


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
    twist = st(4)
    cut = vo[3]["vo_start"] + vo[3]["dur"] + 0.6  # corte un poco más tarde que en el video anterior

    doc = documentary_soft(cut)
    doc /= np.abs(doc).max() + 1e-9
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.4 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    bed = np.zeros(n)
    place(bed, A.reverb(doc, 2.8, 0.38, seed=2), 0.0, db(-17))
    tt = np.arange(n) / SR
    sus0 = st(3)
    bed *= np.where(tt < sus0, 1.0, np.clip(1 - (tt - sus0) / 2.0, 0.3, 1.0))
    place(bed, A.reverb(E4.violin(midi(81), cut - sus0), 2.0, 0.4, seed=5), sus0 + 0.4, db(-16))
    bed[int(cut * SR):] = 0.0

    sfx = np.zeros(n)
    wind = A.lowpass(RNG.standard_normal(int(st(4) * SR)), 400) * 0.25
    place(sfx, wind, 0.0, db(-12))
    place(sfx, A.shimmer(1.0, n=24, seed=3), w(0, 9) - 0.2, db(-18))      # lámpara brilla
    for j in range(6):
        place(sfx, A.whoosh(0.25, seed=40 + j), st(1) + 0.2 + j * 0.18, db(-26))  # frotar
    place(sfx, magic_rise(3.0), w(1, 2), db(-13))                         # humo dorado
    place(sfx, E4.timpani(55.0, 2.0), w(1, 9) - 0.1, db(-12))             # aparece el genio
    place(sfx, A.shimmer(1.6, n=60, seed=4), w(1, 9) - 0.1, db(-13))
    for j in range(14):
        place(sfx, A.bell(1800 + 300 * (j % 5), 0.6) * 0.5, w(2, 8) + j * 0.12, db(-24))  # monedas
    place(sfx, A.swell(2.0), w(2, 10) - 0.3, db(-16))                     # palacio
    place(sfx, A.shimmer(1.2, n=40, seed=5), w(2, 11) - 0.1, db(-15))
    sfx[int(cut * SR):int(twist * SR) - int(0.4 * SR)] = 0.0

    gag = np.zeros(n)
    place(gag, E4.ba_dum_tss(), twist - 0.36, db(-6))
    song = E4.marimba_song(total - twist + 0.2)
    song /= np.abs(song).max() + 1e-9
    seg = duck[int(twist * SR):][: len(song)]
    song[: len(seg)] *= seg
    place(gag, song, twist + 0.05, db(-15))
    place(gag, A.shimmer(1.2, n=45, seed=8), w(5, 9) - 0.2, db(-11))      # el genio saca el decant
    for j in range(5):
        place(gag, A.whoosh(0.5, seed=60 + j), st(6) + 0.3 + j * 0.3, db(-20))  # reparte al pueblo
        place(gag, A.pop(), st(6) + 0.9 + j * 0.3, db(-20))
    for j in range(5):
        kk = int(0.05 * SR)
        place(gag, np.sin(2 * np.pi * 2400 * np.arange(kk) / SR) * np.exp(-np.arange(kk) / SR * 120) * 0.4,
              w(7, 1) - 0.45 + j * 0.09, db(-20))
    place(gag, A.shimmer(1.4, n=50, seed=10), w(7, 7) - 0.1, db(-11))

    mix = bed * duck + sfx + gag
    d = int(0.012 * SR)
    out = np.stack([voice + mix, voice + np.concatenate([np.zeros(d), mix[:-d]])], 1)
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
