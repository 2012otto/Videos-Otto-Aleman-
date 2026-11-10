"""Clona el timbre de la voz de referencia (audio con derechos del cliente) sobre la voz TTS
usando el conversor de timbre de OpenVoice V2 (MIT). Los tiempos de las palabras no cambian.

Requiere:
  OPENVOICE_DIR = carpeta del repo github.com/myshell-ai/OpenVoice
  OPENVOICE_CKPT = carpeta con converter/config.json y converter/checkpoint.pth (HF myshell-ai/OpenVoiceV2)
Uso:
  python3 src/clone_voice.py REF.(mp4|wav) archivo1.mp3 [archivo2.mp3 ...] --out-dir DIR [--tau 0.3]
"""
import argparse
import os
import subprocess
import sys

import numpy as np
import torch

sys.path.insert(0, os.environ["OPENVOICE_DIR"])
from openvoice.api import OpenVoiceBaseClass, ToneColorConverter  # noqa: E402


def to_wav(src, dst, sr=22050):
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", str(sr), dst])
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--tau", type=float, default=0.3)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    ck = os.path.join(os.environ["OPENVOICE_CKPT"], "converter")
    # se construye sin la marca de agua de audio (wavmark), que el constructor original no deja desactivar
    conv = ToneColorConverter.__new__(ToneColorConverter)
    OpenVoiceBaseClass.__init__(conv, os.path.join(ck, "config.json"), device="cpu")
    conv.watermark_model = None
    conv.version = getattr(conv.hps, "_version_", "v1")
    conv.load_ckpt(os.path.join(ck, "checkpoint.pth"))

    ref = to_wav(a.ref, os.path.join(a.out_dir, "_ref.wav"))
    tgt = conv.extract_se([ref])
    wavs = [to_wav(s, os.path.join(a.out_dir, "_src_" + os.path.basename(s) + ".wav")) for s in a.sources]
    src = conv.extract_se(wavs)
    sim = torch.nn.functional.cosine_similarity(src.flatten(), tgt.flatten(), dim=0).item()
    print(f"similitud timbre base vs referencia: {sim:.3f}")
    for s, w in zip(a.sources, wavs):
        out = os.path.join(a.out_dir, os.path.splitext(os.path.basename(s))[0] + ".wav")
        conv.convert(audio_src_path=w, src_se=src, tgt_se=tgt, output_path=out, tau=a.tau)
        se_out = conv.extract_se([out])
        sim2 = torch.nn.functional.cosine_similarity(se_out.flatten(), tgt.flatten(), dim=0).item()
        print(f"{out}  similitud con referencia: {sim2:.3f}")
        os.remove(w)


if __name__ == "__main__":
    main()
