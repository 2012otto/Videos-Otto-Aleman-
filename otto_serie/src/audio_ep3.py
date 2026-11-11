"""Audio del quiz "¿Cuánto sabes de perfumes?" (Otto Aleman, Ep. 3): música de concurso + efectos + voz.

Uso: VIDEO_BUILD=$PWD/otto_serie/build_ep3 VO_TRIM=0.3 python3 otto_serie/src/audio_ep3.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "velto", "src"))
from audio_ep1 import A, timeline, SR, db, place, hit, tick  # noqa: E402
import audio_velto as AV  # noqa: E402  (música con batería, original)


def buzzer():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 220 * t)) * 0.5 + np.sign(np.sin(2 * np.pi * 227 * t)) * 0.5
    return A.lowpass(s, 1600) * np.minimum(1, (0.5 - t) / 0.05) * 0.3


def drumroll(dur=1.4):
    out = np.zeros(int((dur + 0.3) * SR))
    t = 0.0
    k = 0
    while t < dur:
        place(out, AV.clap(k) * 0.6, t)
        t += 0.09 - 0.05 * (t / dur)
        k += 1
    return out * np.linspace(0.4, 1.0, len(out))


def correct():
    out = np.zeros(int(1.5 * SR))
    for i, f in enumerate((1046.5, 1318.5, 1568.0)):
        place(out, A.bell(f, 1.2), i * 0.08, 0.5)
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

    mus = AV.music(total, drop=0.6)
    mus /= np.abs(mus).max() + 1e-9
    k = int(0.25 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.45 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    mus *= duck * db(-18)

    sfx = np.zeros(n)
    place(sfx, hit(), 0.0, db(-11))
    place(sfx, A.pop(), w(0, 4) - 0.1, db(-18))
    place(sfx, A.pop(), w(0, 7) - 0.1, db(-18))
    for i in range(1, 8):
        place(sfx, A.whoosh(0.6, seed=90 + i), st(i) - 0.25, db(-22))
    for q in (1, 2, 3):  # cuenta regresiva 3-2-1 + timbre
        q_end = vo[q]["vo_start"] + vo[q]["dur"]
        for j in range(3):
            place(sfx, tick(), q_end + j * 1.03, db(-13))
            place(sfx, tick(), q_end + j * 1.03 + 0.5, db(-22))
        place(sfx, buzzer(), q_end + 3.05, db(-17))
    for j in range(3):
        place(sfx, tick(), w(4, 4) - 0.4 + j * 0.1, db(-20))
        place(sfx, tick(), w(4, 6) - 0.4 + j * 0.1, db(-20))
    place(sfx, A.shimmer(1.2, n=40, seed=8), w(4, 11) - 0.1, db(-12))
    place(sfx, drumroll(1.3), w(4, 14) - 0.2, db(-14))
    for r in (5, 6, 7):
        place(sfx, correct(), w(r, 1) - 0.1, db(-13))
    place(sfx, hit(), w(7, 9) + 0.3, db(-12))
    sfx = A.reverb(sfx, 1.3, 0.18, seed=9)

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
