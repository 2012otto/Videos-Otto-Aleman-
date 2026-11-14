"""Audio del video GTA 6 (Velto Studio): beat enérgico original a 128 BPM que se frena ("tape stop")
cuando el video se pausa para el anuncio, y vuelve con golpe al reanudar.

Uso: VIDEO_BUILD=$PWD/velto/build_gta VO_TRIM=0.12 VO_GAP=0.12 VO_TAIL=0.4 python3 velto/src/audio_gta.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_velto as AV  # noqa: E402
from audio_velto import A, timeline, SR, db, place, midi, lowpass, highpass  # noqa: E402
from audio_ep2 import impact  # noqa: E402

BPM = 128


def saw(f, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9))
    return s * np.minimum(1, t / 0.005) * np.minimum(1, (dur - t) / 0.02)


def music(total):
    beat = 60 / BPM
    n = int((total + 3) * SR)
    kk, hh, cl, bs, ar, ld = (np.zeros(n) for _ in range(6))
    prog_ = [("Am", 45), ("F", 41), ("C", 48), ("G", 43)]
    notes = {"Am": [69, 72, 76], "F": [65, 69, 72], "C": [64, 67, 72], "G": [62, 67, 71]}
    nb = int(total / beat) + 4
    for b in range(nb):
        t0 = b * beat
        place(kk, AV.kick(), t0, 1.0)
        place(hh, AV.hat(b), t0 + beat / 2, 1.0)
        place(hh, AV.hat(b + 999), t0 + beat * 0.75, 0.5)
        if b % 2 == 1:
            place(cl, AV.clap(b), t0, 1.0)
        name, root = prog_[(b // 4) % 4]
        for j in range(2):  # bajo en corcheas
            place(bs, lowpass(saw(midi(root - 12 + (12 if j else 0)), beat / 2 * 0.9), 600), t0 + j * beat / 2, 0.5)
        for j in range(4):  # arpegio en semicorcheas
            f = midi(notes[name][(b * 4 + j) % 3] + (12 if (b // 8) % 2 else 0))
            place(ar, AV.pluck(f, 0.25, 0.9), t0 + j * beat / 4, 1.0)
        if b % 8 == 0:
            place(ld, lowpass(saw(midi(notes[name][0] + 12), beat * 3.5), 2500) * np.exp(-np.arange(int(beat * 3.5 * SR)) / SR * 1.2), t0, 0.12)
    # bombeo tipo "sidechain" con el bombo
    tt = np.arange(n) / SR
    side = 0.45 + 0.55 * np.minimum(1, ((tt % beat) / (beat * 0.45)) ** 1.5)
    mix = kk * 0.9 + hh * 0.8 + cl * 0.8 + (bs * 0.9 + ar * 0.55 + ld) * side
    return mix[:n]


def tape_stop(seg, dur=0.45):
    """Frena la música como cinta: la velocidad cae a cero."""
    m = int(dur * SR)
    speed = np.linspace(1, 0, m) ** 1.3
    pos = np.cumsum(speed)
    pos = pos[pos < len(seg) - 1]
    i = pos.astype(int)
    fr = pos - i
    out = seg[i] * (1 - fr) + seg[i + 1] * fr
    return out * np.linspace(1, 0.3, len(out))


def riser(dur=0.8, seed=5):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = highpass(r.standard_normal(n), 1500) * (t / dur) ** 2 * 0.3
    return x + np.sin(2 * np.pi * (200 + 900 * (t / dur) ** 2) * t) * (t / dur) ** 2 * 0.15


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
    ads = [(st(3), st(4)), (st(8), total)]

    beat = music(total + 1)
    beat /= np.abs(beat).max() + 1e-9
    tt = np.arange(n) / SR
    gate = np.ones(n)
    for a0, a1 in ads:
        gate[(tt >= a0) & (tt < a1)] = 0.0
    gate = np.convolve(gate, np.ones(int(0.02 * SR)) / int(0.02 * SR), mode="same")
    mus = beat[:n] * gate
    # durante el anuncio: el mismo beat, apagado (filtro) y bajito, como "en pausa"
    muffled = lowpass(beat[:n], 350) * (1 - gate) * 0.55
    for a0, _ in ads:
        i0 = int(a0 * SR)
        place(mus, tape_stop(beat[i0:i0 + int(0.5 * SR)]), a0)
    k = int(0.2 * SR)
    env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
    duck = np.convolve(1 - 0.4 * np.clip(env / (env.max() * 0.35), 0, 1), np.ones(k) / k, mode="same")
    music_bus = (mus * db(-16) + muffled * db(-17)) * duck
    music_bus[: int(1.2 * SR)] *= np.linspace(0.35, 1, int(1.2 * SR))  # entra tras las nubes

    sfx = np.zeros(n)
    place(sfx, A.whoosh(1.6, seed=1), 0.0, db(-12))                       # caída entre nubes
    place(sfx, A.whoosh(0.9, seed=2), 1.2, db(-14))
    place(sfx, impact(), w(0, 1) - 0.05, db(-12))                         # 5
    place(sfx, impact(), w(0, 4) - 0.05, db(-11))                         # GTA 6
    for i in (2, 5, 6, 7):
        place(sfx, A.whoosh(0.4, seed=40 + i), st(i) - 0.1, db(-13))      # barridos
    for j in (5, 8, 14, 16, 21):
        place(sfx, impact(), w(1, j) - 0.02, db(-17))                     # caen los mapas
    place(sfx, A.shimmer(0.8, seed=3), w(1, 22), db(-15))
    for j in range(10):
        place(sfx, AV.click(j), w(2, 3) + j * 0.05, db(-20))              # contador 170
    place(sfx, A.swell(1.6), w(2, 10) - 0.8, db(-12))                     # legendario
    place(sfx, impact(), w(2, 12) - 0.05, db(-14))                        # SECRETO
    for a0, _ in ads:
        place(sfx, AV.click(77), a0 + 0.01, db(-8))                       # clic de pausa
        place(sfx, A.whoosh(0.5, seed=60), a0 + 0.25, db(-15))            # entra el teléfono
    place(sfx, AV.ding(), w(3, 8) - 0.05, db(-12))
    place(sfx, A.shimmer(0.9, n=30, seed=7, lo=2000, hi=7000), w(3, 8), db(-14))
    place(sfx, riser(0.6), st(4) - 0.6, db(-12))
    place(sfx, AV.click(78), st(4), db(-8))                               # play
    place(sfx, impact(), st(4) + 0.02, db(-11))
    r = np.random.default_rng(3)
    wind = lowpass(r.standard_normal(int(1.6 * SR)), 500) * np.sin(np.linspace(0, np.pi, int(1.6 * SR))) * 0.5
    place(sfx, wind, st(4), db(-12))                                      # huracán
    place(sfx, impact(), w(6, 8) - 0.1, db(-9))                           # $79.99
    place(sfx, AV.ding(), w(6, 8), db(-15))
    place(sfx, AV.pluck(1320, 0.3), w(6, 10), db(-14))
    for j in range(16):
        place(sfx, AV.ping(1320 + 40 * (j % 4), 1760), w(7, 5) + j * 0.06, db(-26))  # dinero
    place(sfx, impact(), w(7, 5) - 0.05, db(-13))
    place(sfx, A.shimmer(1.2, seed=9), w(7, 14), db(-14))
    for j in range(5):
        place(sfx, AV.click(80 + j), w(8, 1) - 0.25 + j * 0.06, db(-18))  # tecleo VIDEO
    place(sfx, AV.ding(), w(8, 9) - 0.05, db(-12))
    place(sfx, A.shimmer(0.9, n=30, seed=8, lo=2000, hi=7000), w(8, 9), db(-14))
    sfx = A.reverb(sfx, 1.0, 0.15, seed=9)

    bed = music_bus + sfx
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
