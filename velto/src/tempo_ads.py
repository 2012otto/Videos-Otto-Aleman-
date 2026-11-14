"""Acelera un poco la voz de los anuncios (escenas 3 y 8) para que cada anuncio dure máx. 3 s. Idempotente."""
import json, os, subprocess
B = os.environ["VIDEO_BUILD"]
p = os.path.join(B, "voice.json")
vo = json.load(open(p))
K = 1.15
for i in (3, 8):
    s = vo[i]
    if s.get("tempo"):
        continue
    src = s["file"]
    dst = src.replace(".mp3", "_fast.mp3")
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"atempo={K}", dst])
    s["file"], s["tempo"] = dst, K
    s["dur"] = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst]))
    for w in s["words"]:
        w["s"] /= K
        w["e"] /= K
json.dump(vo, open(p, "w"), ensure_ascii=False, indent=1)
