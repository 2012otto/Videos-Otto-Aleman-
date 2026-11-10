"""Música original (piano + pad sintetizados, sin derechos de autor), efectos y mezcla con la voz.

Salida: build/audio.wav (48 kHz estéreo)
"""
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline  # noqa: E402

SR = 48000
RNG = np.random.default_rng(1234)


def db(x):
    return 10 ** (x / 20)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def place(buf, sig, t, gain=1.0):
    i = int(t * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def lowpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def highpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def reverb(x, secs=2.8, wet=0.35, seed=0):
    r = np.random.default_rng(seed)
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t * 6.9 / secs)
    ir = lowpass(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    L = len(x) + n
    nfft = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
    return x * (1 - wet) + y * wet * 2.2


# ---------------------------------------------------------------- instrumentos

def piano(f, dur=2.5, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k in range(1, 8):
        inh = f * k * (1 + 0.0004 * k * k)
        s += np.sin(2 * np.pi * inh * t) * (1 / k ** 1.6) * np.exp(-t * (1.1 + 0.9 * k))
    att = np.minimum(1, t / 0.004)
    return s * att * vel * 0.5


def pad(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ph = RNG.random() * 6.28
            s += np.sin(2 * np.pi * f * (1 + det / 100 * 3) * t + ph) * 0.6
            s += np.sin(2 * np.pi * 2 * f * t + ph) * 0.12
    env = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.0)
    return s * np.clip(env, 0, 1) / len(freqs) * 0.35


def bell(f, dur=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3)
         + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6))
    return s * np.exp(-t * 1.6) * np.minimum(1, t / 0.002) * 0.4


# ---------------------------------------------------------------- efectos

def shimmer(dur=1.4, n=34, seed=1, lo=2200, hi=7500):
    r = np.random.default_rng(seed)
    out = np.zeros(int((dur + 0.6) * SR))
    for i in range(n):
        f = r.uniform(lo, hi)
        st = r.random() ** 1.5 * dur
        ln = int(0.5 * SR)
        t = np.arange(ln) / SR
        ping = np.sin(2 * np.pi * f * t) * np.exp(-t * r.uniform(8, 16)) * np.minimum(1, t / 0.002)
        place(out, ping, st, r.uniform(0.25, 0.6) * (1 - st / dur * 0.5))
    return out * 0.35


def whoosh(dur=0.7, seed=2):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = r.standard_normal(n)
    x = lowpass(x, 1800) - lowpass(x, 250)
    env = np.sin(np.pi * t / dur) ** 2
    return x * env * 0.35


def clink():
    out = np.zeros(int(0.8 * SR))
    for st, g in ((0.0, 1.0), (0.09, 0.6), (0.16, 0.35)):
        t = np.arange(int(0.5 * SR)) / SR
        s = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((3150, 1), (4720, .6), (6230, .35), (2100, .3)))
        place(out, s * np.exp(-t * 18) * 0.25, st, g)
    return out


def pour(dur=3.5, seed=3):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = r.standard_normal(n)
    x = lowpass(x, 1400) - lowpass(x, 300)
    x *= np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.5) * 0.12
    for _ in range(45):
        st = r.random() * (dur - 0.2)
        ln = int(0.06 * SR)
        tt = np.arange(ln) / SR
        f0 = r.uniform(500, 1100)
        b = np.sin(2 * np.pi * (f0 * tt + 2500 * tt * tt)) * np.exp(-tt * 60)
        place(x, b, st, r.uniform(0.05, 0.12))
    return x


def spray(dur=0.45, seed=4):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = highpass(r.standard_normal(n), 4000)
    return x * np.minimum(1, t / 0.01) * np.exp(-t * 6) * 0.25


def pop():
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * (500 * t + 2200 * t * t)) * np.exp(-t * 28) * 0.35


def chime():
    out = np.zeros(int(3.5 * SR))
    place(out, bell(1318.5), 0.0, 0.5)
    place(out, bell(1760.0), 0.18, 0.4)
    return out


def swell(dur=2.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t)
    return s * np.sin(np.pi * t / dur) ** 2 * 0.3


# ---------------------------------------------------------------- música

CHORDS = {  # (bajo, notas del acorde)
    "Am": (45, [57, 60, 64, 69]),
    "F": (41, [53, 57, 60, 65]),
    "C": (48, [55, 60, 64, 67]),
    "G": (43, [55, 59, 62, 67]),
    "Em": (40, [55, 59, 64, 67]),
    "Fmaj7": (41, [53, 57, 60, 64]),
}


def music(total, bright_at):
    bpm = 72
    beat = 60 / bpm
    bar = beat * 4
    prog = ["Am", "F", "C", "G", "Am", "F", "C", "G", "F", "G", "Em", "Am", "Fmaj7", "G", "C", "C"]
    n = int((total + 3) * SR)
    pno = np.zeros(n)
    pd = np.zeros(n)
    bs = np.zeros(n)
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]  # arpegio en corcheas
    for b, name in enumerate(prog):
        t0 = b * bar
        if t0 > total:
            break
        root, notes = CHORDS[name]
        place(pd, pad([midi(x) for x in notes[:3]], bar + 1.0), t0)
        place(bs, piano(midi(root), 3.5, 0.7), t0)
        bright = t0 >= bright_at
        for i, idx in enumerate(pattern):
            note = notes[idx] + (12 if bright and i in (3, 6) else 0)
            vel = (0.55 if i % 2 else 0.75) * (0.85 + 0.3 * RNG.random())
            place(pno, piano(midi(note), 2.4, vel), t0 + i * beat / 2 + RNG.normal(0, 0.006))
    t = np.arange(n) / SR
    mix = pno * 0.9 + pd * 0.8 + lowpass(bs, 400) * 0.7
    mix = reverb(mix, 3.0, 0.38)
    # entrada suave y final con fade
    mix *= np.minimum(1, t / 1.5) * np.clip((total - t) / 1.6, 0, 1)
    return mix[: int(total * SR)]


# ---------------------------------------------------------------- mezcla

def load_mp3(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.float32).astype(np.float64)


def main():
    vo, total = timeline.load()
    n = int(total * SR)
    voice = np.zeros(n)
    for s in vo:
        place(voice, load_mp3(s["file"]), s["vo_start"])
    voice /= np.abs(voice).max() + 1e-9
    voice *= db(-3)

    mus = music(total, bright_at=vo[2]["start"])
    mus /= np.abs(mus).max() + 1e-9

    # ducking: la música baja mientras habla la voz
    env = np.abs(voice)
    win = int(0.25 * SR)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    duck = 1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1)
    duck = np.convolve(duck, np.ones(win) / win, mode="same")
    mus *= duck * db(-17)

    st = lambda i: vo[i]["start"]  # noqa: E731
    w = lambda i, j: vo[i]["tokens"][j]["s"]  # noqa: E731
    sfx = np.zeros(n)
    place(sfx, shimmer(1.2, seed=1), 0.05, db(-14))           # destello inicial del frasco
    for i in range(1, 8):
        place(sfx, whoosh(0.7, seed=10 + i), st(i) - 0.25, db(-20))  # transiciones
    place(sfx, clink(), st(1) + 0.15, db(-16))                # moneda
    place(sfx, pop(), w(1, 3) - 0.2, db(-22))                 # nube de pensamiento
    place(sfx, shimmer(1.6, n=50, seed=3), st(2) + 0.1, db(-11))  # aparece el decant
    place(sfx, swell(2.2), st(2), db(-16))
    place(sfx, pour(4.0), st(3) + 1.3, db(-12))               # vertido
    place(sfx, pop(), w(3, 6) - 0.15, db(-20))                # "100% original"
    place(sfx, pop(), w(3, 13) - 0.15, db(-20))               # "5 ml · 10 ml"
    place(sfx, spray(), st(4) + 0.9, db(-14))                 # spray
    place(sfx, shimmer(2.0, n=40, seed=5, lo=1800, hi=6000), st(4) + 1.2, db(-17))
    for j in range(6):
        place(sfx, pop(), st(5) + 0.15 + j * 0.22, db(-26))   # decants aparecen
    place(sfx, shimmer(1.2, seed=6), w(5, 4) - 0.2, db(-14))  # fragancia especial
    place(sfx, chime(), st(6) + 0.3, db(-17))                 # campanita de la tienda
    place(sfx, shimmer(1.6, n=50, seed=8), st(7) + 0.2, db(-11))  # logo
    place(sfx, swell(2.4), st(7) + 0.1, db(-15))
    sfx = reverb(sfx, 1.8, 0.25, seed=9)

    mono_bed = mus + sfx
    # estéreo: voz al centro, música/efectos con un poco de amplitud
    d = int(0.012 * SR)
    left = voice + mono_bed
    right = voice + np.concatenate([np.zeros(d), mono_bed[:-d]])
    out = np.stack([left, right], 1)
    out /= max(1.0, np.abs(out).max() / db(-1))
    pcm = (np.clip(out, -1, 1) * 32767).astype("<i2")
    raw = os.path.join(timeline.BUILD, "audio_raw.wav")
    import wave
    with wave.open(raw, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(pcm.tobytes())
    dst = os.path.join(timeline.BUILD, "audio.wav")
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                           "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), dst])
    print(dst, f"{total:.2f}s")


if __name__ == "__main__":
    main()
