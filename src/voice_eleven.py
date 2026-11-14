"""Voz en off con ElevenLabs (texto a voz con tiempos por carácter -> tiempos por palabra).

La clave de la API la inyecta el proxy del entorno (no se guarda en el código).
Usa el mismo formato de salida que src/voice.py (build/vo_XX.mp3 + build/voice.json).

Guion JSON: {"eleven_voice": "<voice_id>", "model": "eleven_multilingual_v2",
             "settings": {...}, "say": {"PALABRA": "pronunciación"}, "scenes": [...], "pauses": [...]}
Uso: VIDEO_BUILD=... VIDEO_SCRIPT=... python3 src/voice_eleven.py
"""
import base64
import json
import os
import subprocess
import time

BUILD = os.environ["VIDEO_BUILD"]
CFG = json.load(open(os.environ["VIDEO_SCRIPT"]))
API = "https://api.elevenlabs.io/v1/text-to-speech/{}/with-timestamps?output_format=mp3_44100_128"


def synth(i, text):
    say = text
    for k, v in CFG.get("say", {}).items():  # cómo se pronuncia vs. cómo se escribe en subtítulos
        say = say.replace(k, v)
    body = json.dumps({"text": say, "model_id": CFG.get("model", "eleven_multilingual_v2"),
                       "voice_settings": CFG.get("settings", {"stability": 0.45, "similarity_boost": 0.8, "style": 0.25})})
    for intento in range(4):
        r = subprocess.run(["curl", "-sS", "-m", "120", "-X", "POST", API.format(CFG["eleven_voice"]),
                            "-H", "xi-api-key: proxy-injected", "-H", "Content-Type: application/json", "-d", body],
                           capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            audio = base64.b64decode(d["audio_base64"])
            al = d["alignment"]
            break
        except Exception:
            if intento == 3:
                raise RuntimeError(r.stdout[:300])
            time.sleep(3)
    path = os.path.join(BUILD, f"vo_{i:02d}.mp3")
    open(path, "wb").write(audio)
    chars, cs, ce = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    words, cur, ws, we = [], "", None, None
    for ch, s, e in zip(chars, cs, ce):
        if ch.isspace():
            if cur:
                words.append({"w": cur, "s": ws, "e": we})
            cur, ws = "", None
            continue
        if ws is None:
            ws = s
        cur += ch
        we = e
    if cur:
        words.append({"w": cur, "s": ws, "e": we})
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", path]))
    return {"text": text, "file": path, "dur": dur, "words": words}


def main():
    os.makedirs(BUILD, exist_ok=True)
    out = [synth(i, t) for i, t in enumerate(CFG["scenes"])]
    for i, r in enumerate(out):
        p = CFG.get("pauses", [])
        if i < len(p) and p[i]:
            r["pause"] = p[i]
    json.dump(out, open(os.path.join(BUILD, "voice.json"), "w"), ensure_ascii=False, indent=1)
    for s in out:
        print(f"{s['dur']:.2f}s  {len(s['words'])}/{len(s['text'].split())} palabras  {s['text'][:50]}")
    print("total", round(sum(s["dur"] for s in out), 2))


if __name__ == "__main__":
    main()
