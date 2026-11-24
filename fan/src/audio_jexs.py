"""Audio del video de fan de Jexs: beat alegre en el universo real, música chiptune "chafa" de 2016 en el
universo alterno, y efectos cómicos (glitch, rebobinar, ups, grillo, puerta, aureola, confeti).

Uso: VIDEO_BUILD=$PWD/fan/build_jexs VO_TRIM=0.15 VO_GAP=0.25 VO_TAIL=1.5 python3 fan/src/audio_jexs.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "velto", "src"))
import audio_gta as AG  # noqa: E402
import audio_velto as AV  # noqa: E402
from audio_velto import A, timeline, SR, db, place, midi, lowpass  # noqa: E402
from audio_ep2 import impact  # noqa: E402


def square(f, dur, vol=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * f * t)) * vol
    return s * np.minimum(1, t / 0.005) * np.clip((dur - t) / 0.02, 0, 1)


def chiptune(dur):
    bpm, n = 120, int((dur + 1) * SR)
    e = 60 / bpm / 2
    out = np.zeros(n)
    mel = [72, 76, 79, 76, 74, 71, 67, 71, 72, 76, 79, 84, 83, 79, 76, 74]
    bass = [48, 48, 43, 43, 45, 45, 41, 43]
    step, t = 0, 0.0
    while t < dur:
        place(out, square(midi(mel[step % 16]), e * 0.8, 0.12), t)
        if step % 2 == 0:
            place(out, square(midi(bass[(step // 2) % 8]), e * 1.6, 0.14), t)
        t += e
        step += 1
    return lowpass(out[: int(dur * SR)], 5000)


def noise(dur, seed=1, lo=None):
    r = np.random.default_rng(seed)
    x = r.standard_normal(int(dur * SR))
    return lowpass(x, lo) if lo else x


def rewind(dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 900 + 600 * np.sin(2 * np.pi * 7 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + noise(dur, 3, 3000) * 0.08


def ups():
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    f = 700 * np.exp(-t * 3)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * 0.4


def cricket(dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = ((t * 3) % 1 < 0.25) * (np.sin(2 * np.pi * 60 * t) > 0)
    return np.sin(2 * np.pi * 4500 * t) * env * 0.12


def creak(dur=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 180 + 120 * np.sin(2 * np.pi * 2 * t)
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * lowpass(np.ones(n), 50) * 0.08 * np.exp(-t * 2)


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
    alt0, alt1 = w(0, 5) - 0.05, st(5)

    real = AG.music(total + 1)[:n]
    real /= np.abs(real).max() + 1e-9
    chip = chiptune(total)[:n]
    chip /= np.abs(chip).max() + 1e-9
    tt = np.arange(n) / SR
    m_alt = ((tt >= alt0 + 1.6) & (tt < alt1)).astype(float)
    m_real = ((tt < alt0) | (tt >= alt1)).astype(float)
    sm = lambda x: np.convolve(x, np.ones(int(0.05 * SR)) / int(0.05 * SR), mode="same")  # noqa: E731
    k = int(0.2 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.4 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus = (real * sm(m_real) * db(-17) + chip * sm(m_alt) * db(-21)) * duck
    i_atol = (tt >= w(4, 16)) & (tt < st(5))
    mus[i_atol] *= 0.15                                                   # silencio incómodo

    sfx = np.zeros(n)
    place(sfx, noise(0.5, 5) * 0.3 * np.exp(-np.arange(int(0.5 * SR)) / SR * 5), alt0 - 0.3, db(-10))  # glitch
    place(sfx, rewind(1.6), alt0 + 0.05, db(-10))
    place(sfx, impact(), alt0 + 0.3, db(-14))
    place(sfx, AV.click(5), w(1, 19) - 0.15, db(-10))                     # clic en "JUEGOS ANDROID"
    place(sfx, ups(), w(1, 19) + 0.15, db(-10))
    for j in range(4):                                                    # miniaturas
        t0 = st(2) + w(2, 5) - st(2) + 0.15 + j * ((st(3) - (w(2, 5) + 0.15) - 0.2) / 4)
        place(sfx, A.whoosh(0.3, seed=20 + j), t0 - 0.05, db(-14))
        place(sfx, AV.pluck(660, 0.25), t0 + 0.4, db(-18))
    place(sfx, creak(), w(3, 18) - 0.2, db(-8))                           # la puerta
    place(sfx, impact(), w(3, 19), db(-14))
    place(sfx, AV.buzz(0.4), w(3, 24) - 0.1, db(-16))                     # "expresiones" (censura)
    place(sfx, A.shimmer(1.0, seed=4), w(3, 26), db(-12))                 # aureola
    place(sfx, cricket(1.8), w(4, 18) + 0.5, db(-8))
    place(sfx, AG.riser(0.6), st(5) - 0.6, db(-12))                       # portal
    place(sfx, impact(), st(5) + 0.05, db(-9))
    place(sfx, A.shimmer(1.2, seed=6), st(5) + 0.1, db(-12))
    for j in range(20):
        place(sfx, AV.click(60 + j), w(5, 4) + j * 0.08, db(-24))         # contador
    place(sfx, AV.ding(), w(5, 11), db(-12))                               # corona
    for j in range(12):
        place(sfx, AV.ping(1320 + 40 * (j % 4), 1760), w(6, 12) + j * 0.22, db(-28))
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
