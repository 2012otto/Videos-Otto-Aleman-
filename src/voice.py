"""Genera la voz en off por escena con edge-tts y guarda los tiempos reales de cada palabra.

Salida: build/vo_XX.mp3 y build/voice.json
"""
import asyncio
import json
import os
import subprocess

import edge_tts

VOICE = "es-GT-AndresNeural"
RATE = os.environ.get("VO_RATE", "-6%")
PITCH = os.environ.get("VO_PITCH", "+30Hz")  # +30Hz: base para clonar la voz de referencia (140 Hz)

SCENES = [
    "Siempre soñé con tener ese perfume... pero el frasco completo costaba demasiado.",
    "Y además pensaba: ¿y si lo compro... y no me queda bien?",
    "Entonces descubrí los decants.",
    "Un decant es el mismo perfume original, auténtico... solo que fraccionado en un frasquito pequeño.",
    "Así lo podés probar varios días, a un precio accesible, antes de comprar el frasco grande.",
    "Y hasta conseguir esa fragancia que no encontrabas en ningún lado.",
    "Yo los encontré en Otto Aleman Perfumes, aquí en Quetzaltenango.",
    "Tu perfume favorito, en tamaño pequeño. Escribinos y encontrá el tuyo.",
]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.environ.get("VIDEO_BUILD", os.path.join(ROOT, "build"))

# un guion alternativo (otro proyecto) puede venir en un JSON: {"voice", "rate", "pitch", "scenes": [...]}
if os.environ.get("VIDEO_SCRIPT"):
    with open(os.environ["VIDEO_SCRIPT"]) as _f:
        _cfg = json.load(_f)
    VOICE = _cfg.get("voice", VOICE)
    RATE = _cfg.get("rate", RATE)
    PITCH = _cfg.get("pitch", PITCH)
    SCENES = _cfg["scenes"]


async def synth(i, text):
    proxy = os.environ.get("HTTPS_PROXY")
    com = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH,
                               boundary="WordBoundary", proxy=proxy)
    path = os.path.join(BUILD, f"vo_{i:02d}.mp3")
    words = []
    with open(path, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7
                words.append({"w": ch["text"], "s": s, "e": s + ch["duration"] / 1e7})
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))
    return {"text": text, "file": path, "dur": dur, "words": words}


async def main():
    os.makedirs(BUILD, exist_ok=True)
    out = [await synth(i, t) for i, t in enumerate(SCENES)]
    with open(os.path.join(BUILD, "voice.json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    for s in out:
        print(f"{s['dur']:.2f}s  {len(s['words'])} palabras  {s['text'][:50]}")
    print("total", sum(s["dur"] for s in out))


if __name__ == "__main__":
    asyncio.run(main())
