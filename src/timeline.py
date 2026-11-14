"""Línea de tiempo del video: inicio de cada escena, voz y frases de subtítulos.

Todo se calcula a partir de los tiempos reales de la voz (build/voice.json).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.environ.get("VIDEO_BUILD", os.path.join(ROOT, "build"))

LEAD = 0.35   # silencio antes de la primera frase
GAP = float(os.environ.get("VO_GAP", 0.30))    # pausa entre escenas
TAIL = float(os.environ.get("VO_TAIL", 1.60))   # cierre después de la última frase
PRE = 0.20    # la escena visual empieza un poco antes que su voz

PUNCT = ".,:;?!…"
DISPLAY = {"cincuenta": "50", "trescientos": "300", "diez": "10", "Diez": "10"}  # cómo se escribe en subtítulos lo que la voz dice en palabras


def load():
    with open(os.path.join(BUILD, "voice.json")) as f:
        vo = json.load(f)
    if os.environ.get("VO_TRIM"):  # recorta el silencio final de cada clip de voz
        for s in vo:
            s["dur"] = min(s["dur"], s["words"][-1]["e"] + float(os.environ["VO_TRIM"]))
    t = LEAD
    for s in vo:
        s["vo_start"] = t
        t += s["dur"] + GAP + s.get("pause", 0.0)
    for i, s in enumerate(vo):
        s["start"] = 0.0 if i == 0 else s["vo_start"] - PRE
    total = vo[-1]["vo_start"] + vo[-1]["dur"] + TAIL
    for i, s in enumerate(vo):
        s["end"] = vo[i + 1]["start"] if i + 1 < len(vo) else total
        # palabras con la puntuación del guion
        toks = s["text"].split()
        ws = s["words"]
        if len(toks) != len(ws):
            toks = [w["w"] for w in ws]
        toks = [DISPLAY.get(tok, tok) for tok in toks]
        s["tokens"] = [{"w": tok, "s": s["vo_start"] + w["s"], "e": s["vo_start"] + w["e"]}
                       for tok, w in zip(toks, ws)]
    return vo, total


def phrases(vo, max_words=6):
    out = []
    for si, s in enumerate(vo):
        cur = []
        toks = s["tokens"]
        for k, tok in enumerate(toks):
            cur.append(tok)
            end_punct = tok["w"][-1] in PUNCT or tok["w"].endswith("...")
            left = len(toks) - k - 1
            if left == 1 or tok["w"] in ("Otto", "Aleman"):  # sin huérfanas ni cortar la marca
                continue
            if left and toks[k + 1]["w"] == "Otto" and len(cur) >= 3:
                out.append({"scene": si, "words": cur})
                cur = []
                continue
            nxt_ends = left > 0 and toks[k + 1]["w"][-1] in ".?!"
            if len(cur) >= max_words and nxt_ends and len(cur) < max_words + 1 and not end_punct:
                continue  # deja que la oración termine en la misma frase
            if (end_punct and len(cur) >= 2) or len(cur) >= max_words or left == 0:
                out.append({"scene": si, "words": cur})
                cur = []
        if cur:
            out[-1]["words"] += cur
    for p in out:
        p["s"] = p["words"][0]["s"] - 0.05
    for i, p in enumerate(out):
        last_e = p["words"][-1]["e"]
        nxt = out[i + 1]["s"] if i + 1 < len(out) else last_e + 1.0
        p["e"] = min(nxt, last_e + 0.6) if out[i + 1:] and out[i + 1]["scene"] == p["scene"] else min(nxt, last_e + 0.45)
    return out


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(path, phr, t0=0.0, t1=1e9):
    n = 0
    lines = []
    for p in phr:
        if p["e"] <= t0 or p["s"] >= t1:
            continue
        n += 1
        text = " ".join(w["w"] for w in p["words"])
        lines += [str(n), f"{srt_time(max(p['s'], t0) - t0)} --> {srt_time(min(p['e'], t1) - t0)}", text, ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    vo, total = load()
    for i, s in enumerate(vo):
        print(f"escena {i+1}: {s['start']:.2f}-{s['end']:.2f}  voz {s['vo_start']:.2f}")
    print("total", round(total, 2))
    for p in phrases(vo):
        print(f"{p['s']:.2f}-{p['e']:.2f}", " ".join(w["w"] for w in p["words"]))
