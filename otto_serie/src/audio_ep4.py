"""Audio de "El mensaje en la botella": música de documental orquestal (original, sintetizada),
efectos de tormenta/mar, corte + "ba-dum-tss" en el giro y marimba alegre al final.

Uso: VIDEO_BUILD=$PWD/otto_serie/build_ep4 VO_TRIM=0.3 python3 otto_serie/src/audio_ep4.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_ep1 import A, timeline, SR, db, place  # noqa: E402
midi = A.midi

RNG = np.random.default_rng(21)


# ---------------------------------------------------------------- orquesta

def saw(f, n, det=0.0):
    t = np.arange(n) / SR
    ph = (f * (1 + det) * t + RNG.random()) % 1.0
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5.2 * t + RNG.random() * 6)
    ph = np.cumsum(f * (1 + det) * vib / SR) % 1.0
    return 2 * ph - 1


def strings(freqs, dur, att=0.6, rel=0.8, bright=2200):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for d in (-0.006, -0.002, 0.003, 0.007):
            s += saw(f, n, d)
    s = A.lowpass(s / (len(freqs) * 4), bright)
    env = np.minimum(1, t / att) * np.clip((dur - t) / rel, 0, 1)
    return s * env


def contrabass(f, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = saw(f, n) * 0.6 + np.sin(2 * np.pi * f * t) * 0.8
    s = A.lowpass(s, 380)
    return s * np.minimum(1, t / 0.15) * np.clip((dur - t) / 0.4, 0, 1)


def timpani(f=55.0, dur=1.8):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = f * (1 + 0.25 * np.exp(-t * 10))
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 2.5)
    s += A.lowpass(RNG.standard_normal(n), 400) * np.exp(-t * 18) * 0.5
    return s


def thunder(dur=3.0, seed=1):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = A.lowpass(r.standard_normal(n), 180)
    env = (1 - np.exp(-t * 20)) * np.exp(-t * 1.2) * (1 + 0.5 * np.sin(2 * np.pi * 3 * t))
    return x * env * 3


def ocean(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = A.lowpass(RNG.standard_normal(n), 600)
    return x * (0.5 + 0.5 * np.sin(2 * np.pi * t / 5.5) ** 2) * 0.5


def whale_call(dur=2.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 180 + 120 * np.sin(np.pi * t / dur)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return s * np.sin(np.pi * t / dur) ** 2 * 0.3


def violin(f, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.8)
    ph = np.cumsum(f * vib / SR)
    s = sum(np.sin(2 * np.pi * k * ph) / k ** 1.3 for k in range(1, 7))
    return s * np.minimum(1, t / 0.9) * np.clip((dur - t) / 0.3, 0, 1) * 0.25


CH = {"Dm": [50, 57, 62, 65], "Bb": [46, 58, 62, 65], "F": [41, 57, 60, 65], "C": [48, 55, 60, 64],
      "Gm": [43, 58, 62, 67], "A": [45, 57, 61, 64]}


def documentary(end):
    """Orquesta: tormenta (épico) -> isla (emotivo) -> viaje (crescendo) -> playa (suspenso)."""
    n = int((end + 2) * SR)
    out = np.zeros(n)
    bar = 2.4
    prog = ["Dm", "Bb", "F", "C", "Dm", "Gm", "Bb", "A", "Dm", "Bb", "F", "C", "Gm", "A", "Dm", "Dm"]
    t0 = 0.0
    i = 0
    while t0 < end - 4.0:
        name = prog[i % len(prog)]
        notes = CH[name]
        inten = min(1.0, 0.55 + t0 / 30)
        place(out, strings([midi(x) for x in notes[1:]], bar + 0.8, att=0.5, bright=1600 + 1400 * inten), t0, 0.9 * inten)
        place(out, strings([midi(notes[3] + 12)], bar + 0.6, att=0.8, bright=3500), t0, 0.35 * inten)
        place(out, contrabass(midi(notes[0] - 12), bar + 0.3), t0, 0.8)
        if i % 2 == 0 or t0 > 12:
            place(out, timpani(midi(notes[0] - 24) * 2, 1.8), t0, 0.7 * inten)
        t0 += bar
        i += 1
    return out[: int(end * SR) + int(1.2 * SR)]


# ---------------------------------------------------------------- giro y marimba

def ba_dum_tss():
    out = np.zeros(int(1.4 * SR))
    for k, (f, st) in enumerate(((200, 0.0), (150, 0.16))):
        n = int(0.25 * SR)
        t = np.arange(n) / SR
        tom = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.5 * np.exp(-t * 30))) / SR) * np.exp(-t * 14)
        place(out, tom * 0.9, st)
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    cym = A.highpass(RNG.standard_normal(n), 5000) * np.exp(-t * 3.5) * 0.6
    place(out, cym, 0.36)
    kick = np.sin(2 * np.pi * np.cumsum(60 + 80 * np.exp(-t[: int(0.3 * SR)] * 30)) / SR) * np.exp(-t[: int(0.3 * SR)] * 10)
    place(out, kick, 0.36, 0.8)
    return out


def marimba(f, dur=0.8, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)
    s += 0.12 * np.sin(2 * np.pi * f * 9.9 * t) * np.exp(-t * 60)
    return s * np.minimum(1, t / 0.002) * vel * 0.5


def marimba_song(dur):
    bpm = 126
    eighth = 60 / bpm / 2
    n = int((dur + 1) * SR)
    out = np.zeros(n)
    chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]  # C G Am F
    melody = [72, 74, 76, 79, 76, 74, 72, 74, 71, 72, 74, 76, 74, 72, 71, 67,
              72, 74, 76, 77, 76, 74, 72, 69, 72, 71, 69, 67, 69, 72, 74, 72]
    t = 0.0
    step = 0
    while t < dur:
        ch = chords[(step // 8) % 4]
        place(out, marimba(midi(melody[step % len(melody)]), 0.5, 0.9 if step % 2 == 0 else 0.7), t)
        if step % 2 == 0:
            place(out, marimba(midi(ch[(step // 2) % 3]), 0.6, 0.45), t)
        if step % 4 == 0:
            place(out, marimba(midi(ch[0] - 24), 0.9, 0.9), t)
            k = int(0.25 * SR)
            tt = np.arange(k) / SR
            place(out, np.sin(2 * np.pi * np.cumsum(55 + 70 * np.exp(-tt * 30)) / SR) * np.exp(-tt * 12) * 0.6, t)
        if step % 2 == 1:
            k = int(0.05 * SR)
            place(out, A.highpass(RNG.standard_normal(k), 7000) * np.exp(-np.arange(k) / SR * 70) * 0.15, t)
        t += eighth
        step += 1
    tt = np.arange(n) / SR
    out *= np.minimum(1, tt / 0.15) * np.clip((dur - tt) / 1.2, 0, 1)
    return A.reverb(out[: int(dur * SR)], 1.0, 0.15, seed=4)


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
    cut = vo[3]["vo_start"] + vo[3]["dur"] + 0.05  # la música se corta al terminar "cambió todo"

    # --- documental
    doc = documentary(cut)
    doc /= np.abs(doc).max() + 1e-9
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.4 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    bed = np.zeros(n)
    place(bed, A.reverb(doc, 2.6, 0.35, seed=2), 0.0, db(-15))
    # suspenso en la playa: la orquesta baja y queda un violín solo
    sus0 = st(3)
    tt = np.arange(n) / SR
    fade = np.where(tt < sus0, 1.0, np.clip(1 - (tt - sus0) / 2.0, 0.25, 1.0))
    bed *= fade
    place(bed, A.reverb(violin(midi(81), cut - sus0 + 0.2), 2.0, 0.4, seed=5), sus0 + 0.6, db(-14))
    bed[int(cut * SR):] = 0.0  # ¡corte seco!
    # --- ambiente y efectos del documental
    sfx = np.zeros(n)
    place(sfx, ocean(st(3)), 0.0, db(-24))
    for f, sd in zip((0.5, 2.6, 4.9, 6.4), (1, 2, 3, 4)):
        place(sfx, thunder(3.0, sd), f + 0.05, db(-14))
    rain = A.highpass(RNG.standard_normal(int(st(1) * SR)), 3000) * 0.08
    place(sfx, rain, 0.0, 1.0)
    place(sfx, A.whoosh(1.0, seed=9), w(1, 13), db(-18))       # lanza la botella
    place(sfx, A.pour(0.6), w(1, 13) + 0.6, db(-18))          # cae al agua
    place(sfx, whale_call(2.5), st(2) + 0.8, db(-16))
    place(sfx, thunder(2.0, 7), w(2, 4) - 0.1, db(-16))
    place(sfx, A.pop(), w(3, 11) + 0.2, db(-20))               # destapa la botella
    sfx[int(cut * SR):int(twist * SR) - int(0.4 * SR)] = 0.0
    # --- el giro
    gag = np.zeros(n)
    place(gag, ba_dum_tss(), twist - 0.36, db(-6))
    song = marimba_song(total - twist + 0.2)
    song /= np.abs(song).max() + 1e-9
    k2 = np.convolve(1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    place(gag, song * k2[int(twist * SR):][: len(song)] if len(song) <= n - int(twist * SR) else song, twist + 0.05, db(-15))
    place(gag, A.shimmer(1.2, n=40, seed=8), w(4, 8) - 0.1, db(-13))
    place(gag, A.shimmer(1.0, n=30, seed=9), w(5, 5) - 0.2, db(-11))   # ¡poof! era un decant
    place(gag, A.spray(), w(5, 6) + 0.3, db(-15))
    for j in range(7):
        t0 = w(6, 1) - 0.5 + j * 0.08
        kk = int(0.05 * SR)
        place(gag, np.sin(2 * np.pi * 2400 * np.arange(kk) / SR) * np.exp(-np.arange(kk) / SR * 120) * 0.4, t0, db(-20))
    place(gag, A.shimmer(1.4, n=50, seed=10), w(6, 6) - 0.1, db(-11))

    bedall = bed * duck + sfx + gag
    d = int(0.012 * SR)
    out = np.stack([voice + bedall, voice + np.concatenate([np.zeros(d), bedall[:-d]])], 1)
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
