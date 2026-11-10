"""Hace que la mezcla use la voz clonada (build/clon/vo_XX.wav) en lugar de la voz TTS base."""
import json
import os
import subprocess

B = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build")
p = os.path.join(B, "voice.json")
vo = json.load(open(p))
for i, s in enumerate(vo):
    f = os.path.join(B, "clon", f"vo_{i:02d}.wav")
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
    print(f"escena {i+1}: base {s['dur']:.2f}s  clonada {d:.2f}s")
    s["file"] = f
json.dump(vo, open(p, "w"), ensure_ascii=False, indent=1)
