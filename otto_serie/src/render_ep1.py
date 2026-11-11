"""Serie Otto Aleman Perfumes — Ep. 1: "3 datos que no sabías de tu perfume".

Set fijo de la serie: la perfumería de noche (estantes dorados, luna, mostrador, partículas doradas).
Uso (desde la raíz del repo):
  VIDEO_BUILD=$PWD/otto_serie/build_ep1 VO_TRIM=0.3 python3 otto_serie/src/render_ep1.py --out otto_serie/build_ep1/video_mudo.mp4
"""
import math
import os
import subprocess
import sys

import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "src"))
import render as R  # noqa: E402
import timeline  # noqa: E402
from render import (P, R as RECT, back_out, clamp, ease_in_out, ease_out, font, glow, hexc, lerp, lin, rad,  # noqa: E402
                    oval, prog, rrect, smooth, text_center, draw_img, draw_kid, rng, W, H)

GOLD = ["#8a5a17", "#f7d27a", "#fff1c4", "#d9a441"]
CLIENTA = {"shirt": ("#ff9fc0", "#e0558a", "#a8285e"), "hem": "#9a2456", "collar": "#9a2456", "arm": "#d84a82",
           "arm_hl": "#ffc2d8", "pants": ("#3a2a4a", "#22182e"), "hair": "long", "hair_col": ("#2a2030", "#120c16"),
           "lashes": True, "earrings": "#f4cf6a", "lips": "#b23a55"}
SENOR = {"shirt": ("#6fd6c8", "#2a9d8f", "#1d6f66"), "hem": "#1a6058", "collar": "#1a6058", "arm": "#2a9d8f",
         "arm_hl": "#a8f0e6", "pants": ("#3a3a4a", "#22222e"), "hair_col": ("#6a5a4a", "#3a2e24")}

camera = R.camera
ENV = None


# ----------------------------------------------------------------------------
# voz -> boca
# ----------------------------------------------------------------------------


def build_env():
    vo, total = timeline.load()
    fps = 60
    env = np.zeros(int(total * fps) + 2)
    for s in vo:
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", s["file"], "-ac", "1", "-ar", "8000", "-f", "s16le", "-"])
        x = np.frombuffer(raw, np.int16).astype(float) / 32768
        hop = 8000 // fps
        n = len(x) // hop
        r = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1))
        i0 = int(s["vo_start"] * fps)
        m = min(n, len(env) - i0)
        env[i0:i0 + m] = np.maximum(env[i0:i0 + m], r[:m])
    env /= np.percentile(env[env > 0], 95) + 1e-9
    return np.clip(env, 0, 1)


def talk(t):
    if ENV is None:
        return 0.0
    i = int(t * 60)
    return clamp((ENV[i] - 0.12) * 1.5) if 0 <= i < len(ENV) else 0.0


# ----------------------------------------------------------------------------
# set fijo: la perfumería de noche
# ----------------------------------------------------------------------------


def mini_bottle(c, x, y, s, kind, col):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glass = P(col, shader=lin(-30, 0, 30, 0, [hexc(col, 0.55), hexc(col, 0.95), hexc(col, 0.6)]))
    if kind == 0:
        rrect(c, -26, -70, 26, 0, 10, glass)
        rrect(c, -9, -84, 9, -70, 3, P("#c9902f"))
        rrect(c, -14, -104, 14, -84, 5, P("#d9a441", shader=lin(-14, 0, 14, 0, GOLD)))
    elif kind == 1:
        oval(c, 0, -34, 30, 34, glass)
        rrect(c, -7, -80, 7, -64, 3, P("#c9902f"))
        oval(c, 0, -88, 12, 12, P("#d9a441", shader=lin(-12, 0, 12, 0, GOLD)))
    else:
        p = skia.Path()
        p.moveTo(-30, 0)
        p.lineTo(30, 0)
        p.lineTo(20, -76)
        p.lineTo(-20, -76)
        p.close()
        c.drawPath(p, glass)
        rrect(c, -10, -104, 10, -76, 4, P("#d9a441", shader=lin(-10, 0, 10, 0, GOLD)))
    rrect(c, -18, -60, -11, -10, 3, P("#ffffff", alpha=0.35))
    c.restore()


SHELF_COLS = ["#d9a441", "#e0558a", "#8a5aff", "#2a9d8f", "#f39c4a", "#c9902f", "#ff7a9a", "#5ab0ff"]


def perfumery(c, t, floor_y=1430, moon=True, shelves=True, lamp=True):
    c.drawRect(RECT(-500, -500, W + 500, floor_y), P("#1c1836", shader=lin(0, -200, 0, floor_y, ["#120f26", "#221a3e", "#2e2248"])))
    if moon:
        R.window(c, 90, 600, 390, 960, t, moon_pos=(300, 700, 38))
    if shelves:
        r = rng(11)
        for row, y in enumerate((640, 860, 1080)):
            c.drawRect(RECT(470, y, 1100, y + 16), P("#c9902f", shader=lin(0, y, 0, y + 16, ["#f7d27a", "#8a5a17"])))
            glow(c, R.RES.glow_warm, 780, y - 40, 340, 0.12)
            for i in range(7):
                mini_bottle(c, 515 + i * 88, y, 0.8 + 0.25 * r.random(), int(r.random() * 3),
                            SHELF_COLS[int(r.random() * len(SHELF_COLS))])
    if lamp:
        c.drawLine(780, -100, 780, 430, P("#3a2e24", "stroke", 4))
        dome = skia.Path()
        dome.moveTo(720, 490)
        dome.quadTo(780, 400, 840, 490)
        dome.close()
        c.drawPath(dome, P("#c9902f", shader=lin(720, 0, 840, 0, GOLD)))
        glow(c, R.RES.glow_warm, 780, 520, 300, 0.4 + 0.05 * math.sin(t * 3))
    c.drawRect(RECT(-500, floor_y, W + 500, H + 500), P("#3d2618", shader=lin(0, floor_y, 0, H, ["#4a2e1c", "#1a0f09"])))
    for i in range(7):
        yy = floor_y + 30 + i * i * 14
        c.drawLine(-500, yy, W + 500, yy, P("#000000", "stroke", 2, alpha=0.18))


def counter(c, y=1330):
    rrect(c, -100, y, W + 100, y + 30, 8, P("#c9902f", shader=lin(0, y, 0, y + 30, ["#f7d27a", "#8a5a17"])))
    c.drawRect(RECT(-100, y + 30, W + 100, H + 300), P("#5a3420", shader=lin(0, y + 30, 0, H, ["#6e4128", "#2a170d"])))
    for i in range(7):
        x = i * 180
        c.drawRect(RECT(x + 20, y + 70, x + 160, y + 250), P("#000000", alpha=0.12))
        c.drawRect(RECT(x + 20, y + 70, x + 160, y + 250), P("#f7d27a", "stroke", 2, alpha=0.25))


def gold_text(c, txt, x, y, size, tf=None, white=False, a=1.0):
    f = font(tf or R.RES.xbold, size)
    w = f.measureText(txt)
    c.drawString(txt, x - w / 2 + 4, y + 6, f, P("#000000", alpha=0.5 * a, blur=6))
    sh = None if white else lin(0, y - size, 0, y, ["#fff1c4", "#f7d27a", "#c9902f"])
    c.drawString(txt, x - w / 2, y, f, P("#ffffff", shader=sh, alpha=a))
    return w


def dato_tag(c, num, title, k, y=600):
    if k <= 0:
        return
    s = back_out(k)
    c.save()
    c.translate(540, y)
    c.scale(s, s)
    f1, f2 = font(R.RES.xbold, 40), font(R.RES.bold, 40)
    w1 = f1.measureText(f"DATO {num}") + 50
    w2 = f2.measureText(title) + 56
    x0 = -(w1 + w2) / 2
    glow(c, R.RES.glow_warm, 0, 0, (w1 + w2) * 0.6, 0.3)
    rrect(c, x0, -40, x0 + w1, 40, 20, P("#d9a441", shader=lin(x0, 0, x0 + w1, 0, GOLD)))
    c.drawString(f"DATO {num}", x0 + 25, 14, f1, P("#2a1608"))
    rrect(c, x0 + w1 - 10, -40, x0 + w1 + w2, 40, 20, P("#fff8ea"))
    c.drawRect(RECT(x0 + w1 - 10, -40, x0 + w1 + 10, 40), P("#d9a441"))
    c.drawString(title, x0 + w1 + 28, 14, f2, P("#2a1608"))
    c.restore()


def tint_aroma(c, x, y, t, sprite, n=26, height=380, seed=1, intensity=1.0, spread=50):
    old = R.RES.glow_gold
    R.RES.glow_gold = sprite
    R.aroma(c, x, y, t, n=n, height=height, spread=spread, intensity=intensity, seed=seed, speed=0.45)
    R.RES.glow_gold = old


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def scene1(c, k):  # GANCHO
    lt = k.lt
    T = k.w
    camera(c, 1.0 + 0.03 * ease_out(prog(lt, 0, k.D)), 540, 960, k.t)
    perfumery(c, k.t)
    R.dust(c, k.t, n=30, seed=3, alpha=0.6)
    swap = smooth(prog(lt, T(13) - 0.2, T(13) + 0.15))
    punch = 1 + 0.07 * (1 - ease_out(prog(lt, 0, 0.35)))
    c.save()
    c.translate(540, 620)
    c.scale(punch, punch)
    rrect(c, -500, -175, 500, 205, 40, P("#0c0818", alpha=0.82))
    rrect(c, -500, -175, 500, 205, 40, P("#d9a441", "stroke", 3, alpha=0.7))
    if swap < 1:
        for i, txt in enumerate(("¿POR QUÉ YA NO", "TE HUELE TU", "PERFUME?")):
            gold_text(c, txt, 0, -60 + i * 108, 100, white=(i < 2), a=1 - swap)
    if swap > 0:
        s = back_out(swap)
        c.save()
        c.scale(s, s)
        gold_text(c, "3 DATOS", 0, 0, 150, a=swap)
        gold_text(c, "QUE NO SABÍAS", 0, 110, 80, white=True, a=swap)
        c.restore()
    c.restore()
    # chico confundido oliendo su muñeca / clienta encantada
    sniff = 0.5 + 0.5 * math.sin(lt * 4)
    draw_kid(c, 330, 1500, 0.95, k.t, "worried", look=(0.2, 0.5), tilt=-6,
             hands={"L": (-30, -470 + 10 * sniff), "R": (110, -200)}, talk=talk(k.t))
    tint_aroma(c, 360, 1000, k.t, R.RES.glow_gold, n=18, height=260, seed=4, intensity=0.6, spread=70)
    draw_kid(c, 790, 1500, 0.95, k.t, "bliss", look=(-0.4, -0.2), tilt=8, style=CLIENTA,
             hands={"L": (-110, -330), "R": (110, -200)})
    mk = prog(lt, 1.6, 1.9)
    if mk > 0:
        s = back_out(mk)
        c.save()
        c.translate(900, 880)
        c.scale(s, s)
        rrect(c, -80, -36, 80, 36, 30, P("#fff8ea"))
        text_center(c, "mmm...", 0, 12, font(R.RES.xbold, 34), P("#a8285e"))
        c.restore()
    counter(c, 1330)


def nose(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    p = skia.Path()
    p.moveTo(-30, -150)
    p.cubicTo(-20, -60, 40, 20, 60, 60)
    p.cubicTo(70, 90, 30, 110, 0, 100)
    p.cubicTo(-30, 96, -50, 80, -60, 70)
    p.cubicTo(-70, 40, -40, -60, -30, -150)
    p.close()
    c.drawPath(p, P("#f7d27a", shader=lin(-60, -150, 70, 110, ["#fff1c4", "#f7d27a", "#c9902f"])))
    oval(c, 10, 80, 18, 10, P("#8a5a17"))
    c.restore()


def scene2(c, k):  # DATO 1: la nariz se acostumbra
    lt = k.lt
    T = k.w
    camera(c, lerp(1.05, 1.0, ease_out(prog(lt, 0, 1.0))), 540, 980, k.t)
    perfumery(c, k.t, moon=False)
    # espejo dorado
    oval(c, 300, 960, 230, 290, P("#1a1430"))
    oval(c, 300, 960, 230, 290, P("#d9a441", "stroke", 18, shader=lin(70, 0, 530, 0, GOLD)))
    oval(c, 260, 900, 120, 170, P("#ffffff", alpha=0.05))
    R.dust(c, k.t, n=22, seed=5, alpha=0.5)
    dato_tag(c, 1, "Tu nariz se acostumbra", prog(lt, 0, 0.35))
    # medidor de olor
    lvl = 1 - ease_in_out(prog(lt, T(4), T(9) + 0.3))
    mx, my = 820, 1010
    nose(c, mx, my - 250, 0.6)
    rrect(c, mx - 60, my - 170, mx + 60, my + 230, 30, P("#1a1430", alpha=0.9))
    rrect(c, mx - 60, my - 170, mx + 60, my + 230, 30, P("#d9a441", "stroke", 5))
    hh = 380 * lvl
    rrect(c, mx - 46, my + 216 - hh, mx + 46, my + 216, 22, P("#f7d27a", shader=lin(0, my - 160, 0, my + 216, ["#fff1c4", "#d9a441", "#8a5a17"])))
    text_center(c, f"{int(round(100 * lvl))}%", mx, my + 300, font(R.RES.xbold, 64), P("#fff1c4"))
    text_center(c, "lo que TÚ hueles", mx, my + 350, font(R.RES.semi, 30), P("#e9d8b8"))
    stop = prog(lt, T(17) - 0.2, T(17) + 0.2)
    holding = stop < 0.5
    draw_kid(c, 300, 1920, 1.35, k.t, "happy" if lt < T(10) else "surprised", look=(0.4, 0.0), tilt=3 * math.sin(k.t),
             hands={"R": (190, -560) if holding else (140, -260), "L": (-130, -240)}, talk=talk(k.t),
             front_props=(lambda cc, out: R.draw_decant(cc, out["R"][0], out["R"][1] - 70, 170, rot=-10, glow_a=0.4,
                                                         shadow=False)) if holding else None)
    if stop > 0:
        s = back_out(stop)
        c.save()
        c.translate(780, 1450)
        c.scale(s, s)
        glow(c, R.RES.glow_warm, 0, 0, 240, 0.4)
        rrect(c, -210, -50, 210, 50, 50, P("#d9a441", shader=lin(-210, 0, 210, 0, GOLD)))
        text_center(c, "¡NO TE ECHES MÁS!", 0, 16, font(R.RES.xbold, 40), P("#2a1608"))
        c.restore()


def scene3(c, k):  # DATO 2: distinto en cada piel
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 980, k.t)
    perfumery(c, k.t)
    dato_tag(c, 2, "Huele distinto en cada piel", prog(lt, 0, 0.35))
    people = [(200, CLIENTA, R.RES.glow_gold), (540, None, R.RES.glow_rose), (880, SENOR, R.RES.glow_cyan)]
    bx = lerp(200, 880, ease_in_out(prog(lt, 0.2, T(5))))
    for i, (x, st, spr) in enumerate(people):
        on = prog(lt, T(5) - 0.3 + i * 0.12, T(5) + i * 0.12)
        if on > 0:
            tint_aroma(c, x + 70, 1150, k.t, spr, n=26, height=430, seed=10 + i, intensity=on, spread=60)
        draw_kid(c, x, 1500, 0.78, k.t, "bliss" if on > 0.5 else "neutral", look=(0, -0.3), style=st,
                 hands={"R": (100, -330), "L": (-110, -220)}, talk=talk(k.t) if st is None else 0.0)
    R.draw_bottle(c, bx, 880 + 12 * math.sin(k.t * 3), 0.55, rot=8 * math.sin(k.t * 2), glow_a=0.6)
    counter(c, 1380)
    for i, (lab, col) in enumerate((("Ámbar", "#f7d27a"), ("Floral", "#ff9fc0"), ("Fresco", "#7ae0ff"))):
        kk = prog(lt, T(7) - 0.2 + i * 0.12, T(7) + i * 0.12)
        if kk > 0:
            pill_gold(c, people[i][0], 1450, lab, kk, fg=col)


def pill_gold(c, x, y, text, k, size=34, fg="#2a1608", bg=None):
    if k <= 0:
        return
    s = back_out(k)
    f = font(R.RES.xbold, size)
    w = f.measureText(text) + size * 1.2
    h = size * 1.8
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if bg is None:
        rrect(c, -w / 2, -h / 2, w / 2, h / 2, h / 2, P("#1a1430", alpha=0.9))
        rrect(c, -w / 2, -h / 2, w / 2, h / 2, h / 2, P("#d9a441", "stroke", 3))
    else:
        rrect(c, -w / 2, -h / 2, w / 2, h / 2, h / 2, P(bg, shader=lin(-w / 2, 0, w / 2, 0, GOLD)))
    text_center(c, text, 0, size * 0.36, f, P(fg))
    c.restore()


def scene4(c, k):  # DATO 3: pirámide olfativa
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 980, k.t)
    perfumery(c, k.t, shelves=False)
    R.dust(c, k.t, n=26, seed=7, alpha=0.6)
    dato_tag(c, 3, "Las notas cambian", prog(lt, 0, 0.35))
    px, top, base_y, half = 430, 720, 1340, 330
    bands = [("SALIDA", 0.0, 0.33, "#fff1c4", T(6) - 0.2), ("CORAZÓN", 0.33, 0.66, "#ffb3c8", T(12) - 0.2),
             ("FONDO", 0.66, 1.0, "#d9a441", T(14) - 0.2)]
    for name, a0, a1, col, tm in bands:
        on = smooth(prog(lt, tm, tm + 0.3))
        y0, y1 = lerp(top, base_y, a0), lerp(top, base_y, a1)
        w0, w1 = half * a0, half * a1
        p = skia.Path()
        p.moveTo(px - w0, y0 + 6)
        p.lineTo(px + w0, y0 + 6)
        p.lineTo(px + w1, y1)
        p.lineTo(px - w1, y1)
        p.close()
        c.drawPath(p, P(col, alpha=0.25 + 0.75 * on))
        if on > 0:
            glow(c, R.RES.glow_warm, px, (y0 + y1) / 2, 200, 0.25 * on)
        text_center(c, name, px, (y0 + y1) / 2 + 18 + (20 if a0 == 0 else 0), font(R.RES.xbold, 40 if a0 else 30),
                    P("#2a1608", alpha=0.4 + 0.6 * on))
    # reloj de arena
    hx, hy = 860, 1030
    sand = prog(lt, T(9), T(19))
    frame = P("#d9a441", "stroke", 10, shader=lin(hx - 100, 0, hx + 100, 0, GOLD))
    c.drawLine(hx - 100, hy - 230, hx + 100, hy - 230, frame)
    c.drawLine(hx - 100, hy + 230, hx + 100, hy + 230, frame)
    glass = skia.Path()
    glass.moveTo(hx - 80, hy - 220)
    glass.lineTo(hx + 80, hy - 220)
    glass.lineTo(hx + 10, hy)
    glass.lineTo(hx + 80, hy + 220)
    glass.lineTo(hx - 80, hy + 220)
    glass.lineTo(hx - 10, hy)
    glass.close()
    c.drawPath(glass, P("#ffffff", alpha=0.08))
    c.drawPath(glass, P("#e9d8b8", "stroke", 3))
    c.save()
    c.clipPath(glass, True)
    c.drawRect(RECT(hx - 90, lerp(hy - 180, hy - 10, sand), hx + 90, hy), P("#f7d27a"))
    c.drawRect(RECT(hx - 90, lerp(hy + 220, hy + 60, sand), hx + 90, hy + 230), P("#f7d27a"))
    c.drawLine(hx, hy, hx, hy + 220, P("#f7d27a", "stroke", 4, alpha=0.9 * (0 < sand < 1)))
    c.restore()
    if lt > T(10) - 0.2:
        pill_gold(c, hx, hy - 290, "minutos", prog(lt, T(10) - 0.2, T(10) + 0.1))
    if lt > T(19) - 0.3:
        pill_gold(c, hx, hy + 300, "horas", prog(lt, T(19) - 0.3, T(19)), bg="#d9a441")


def chip(c, x, y, r, rot):
    c.save()
    c.translate(x, y)
    c.scale(abs(math.cos(rot)) * 0.9 + 0.1, 1)
    oval(c, 0, 0, r, r, P("#b8232f"))
    for i in range(8):
        a = i * math.pi / 4
        c.save()
        c.rotate(math.degrees(a))
        rrect(c, r * 0.72, -r * 0.1, r * 0.98, r * 0.1, 3, P("#fff8ea"))
        c.restore()
    oval(c, 0, 0, r * 0.62, r * 0.62, P("#d9a441", shader=lin(-r, 0, r, 0, GOLD)))
    text_center(c, "Q", 0, r * 0.22, font(R.RES.xbold, r * 0.6), P("#2a1608"))
    c.restore()


def scene5(c, k):  # el giro: ¿una apuesta?
    lt = k.lt
    T = k.w
    camera(c, lerp(1.0, 1.08, ease_in_out(prog(lt, 0, k.D))), 600, 1000, k.t)
    perfumery(c, k.t, shelves=False, moon=False, lamp=False)
    cone = skia.Path()
    cone.moveTo(620, -200)
    cone.lineTo(760, -200)
    cone.lineTo(980, 1300)
    cone.lineTo(400, 1300)
    cone.close()
    c.drawPath(cone, P("#ffffff", shader=lin(0, -200, 0, 1300, [hexc("#fff3d6", .14), hexc("#fff3d6", .03)])))
    rrect(c, 540, 1180, 860, 1300, 10, P("#7a4a2e", shader=lin(0, 1180, 0, 1300, ["#9b6440", "#5a341f"])))
    R.draw_bottle(c, 700, 1185, 1.25, glow_a=0.8)
    R.price_tag(c, 900, 900, 8 * math.sin(k.t * 1.6), "Q1,500")
    R.burst(c, 700, 790, lt - T(8) + 0.1, dur=1.0, n=40, radius=220, seed=5, intensity=0.8)
    ak = prog(lt, T(12) - 0.2, T(12) + 0.2)
    if ak > 0:
        s = back_out(ak, 2.2)
        c.save()
        c.translate(600, 640)
        c.scale(s, s)
        gold_text(c, "¿APUESTA?", 0, 40, 120)
        c.restore()
        chip(c, 300, 600, 60, lt * 5)
        chip(c, 900, 560, 50, lt * 4 + 1)
    counter(c, 1340)
    draw_kid(c, 230, 1560, 0.85, k.t, "worried", look=(1, -0.5), tilt=-5,
             hands={"R": (130, -330), "L": (-60, -420)}, talk=talk(k.t))


def scene6(c, k):  # la solución: el decant, varios días
    lt = k.lt
    T = k.w
    warm = smooth(prog(lt, T(6) - 0.2, T(8) + 0.5))
    camera(c, lerp(1.0, 1.05, ease_in_out(prog(lt, 0, k.D))), 540, 1000, k.t)
    R.wall_and_floor(c, k.t, 1500, (R.mix_col("#232846", "#4a2f4c", warm), R.mix_col("#33335a", "#5a3a50", warm)))
    R.window(c, 640, 560, 1000, 940, k.t, moon_pos=(900, 650, 36) if warm < 0.5 else None)
    if warm >= 0.5:
        glow(c, R.RES.glow_warm, 820, 700, 300, 0.7 * warm)
        oval(c, 870, 660, 46, 46, P("#ffd27a", alpha=warm))
    R.dust(c, k.t, n=22, seed=14, alpha=0.4, big=True, col=R.RES.glow_warm)
    # calendario
    days = ["LUN", "MAR", "MIÉ"]
    di = 0 if lt < T(7) - 0.1 else (1 if lt < T(8) - 0.1 else 2)
    ck = prog(lt, T(5) - 0.3, T(5))
    if ck > 0:
        s = back_out(ck)
        c.save()
        c.translate(220, 700)
        c.scale(s, s)
        rrect(c, -120, -110, 120, 120, 20, P("#fff8ea"))
        rrect(c, -120, -110, 120, -40, 20, P("#b8232f"))
        c.drawRect(RECT(-120, -60, 120, -40), P("#b8232f"))
        text_center(c, "DÍA", 0, -62, font(R.RES.xbold, 34), P("#ffffff"))
        text_center(c, days[di], 0, 70, font(R.RES.xbold, 78), P("#2a1608"))
        c.restore()
    spray_t = [T(6), T(7), T(8)]
    hands = {"R": (175, -470), "L": (20, -290)}

    def decant_in_hand(cc, out):
        hx, hy = out["R"]
        R.draw_decant(cc, hx + 4, hy - 60, 190, rot=-18, glow_a=0.5, shadow=False)
    happy = lt > T(8)
    hp = draw_kid(c, 540, 1960, 1.55, k.t, "happy" if happy else "neutral", look=(-0.2, 0.3), tilt=-4 * warm,
                  hands=hands, front_props=decant_in_hand, talk=talk(k.t))
    for st in spray_t:
        R.burst(c, hp["R"][0] - 80, hp["R"][1] - 200, lt - st + 0.05, dur=0.9, n=30, radius=180, seed=int(st * 10),
                intensity=0.6)
    lx, ly = hp["L"]
    R.aroma(c, lx - 40, ly - 60, k.t, n=50, height=800, spread=110, intensity=warm, seed=6, size=1.2)
    pk = prog(lt, T(18) - 0.2, T(18) + 0.2)
    pill_gold(c, 540, 965, "Perfume original · tamaño pequeño", pk, size=34, bg="#d9a441")
    k.grade = (warm * 0.5, (1 - warm) * 0.45)


def scene7(c, k):  # cierre en Xela: comenta AROMA
    lt = k.lt
    T = k.w
    # fondo: la tienda en Quetzaltenango (del primer video), atenuada
    c.save()
    R.scene7(c, k)
    c.restore()
    c.drawRect(RECT(0, 0, W, H), P("#0a0612", alpha=0.78))
    k.grade = (0.25, 0)
    word = "AROMA"
    r = rng(29)
    for i in range(22):
        side = -1 if i % 2 == 0 else 1
        x = 540 + side * (405 + r.random() * 70)
        u = (lt - (T(4) + i * 0.15)) / 2.6
        if u <= 0 or u >= 1:
            continue
        y = lerp(1500, 520, u)
        a = math.sin(math.pi * u)
        txt = [word, "¡" + word + "!", word + "!!", word][i % 4]
        f = font(R.RES.xbold, 24)
        w = f.measureText(txt) + 66
        c.save()
        c.translate(x + 20 * math.sin(lt * 2 + i), y)
        rrect(c, -w / 2, -28, w / 2, 28, 28, P("#1a1430", alpha=0.92 * a))
        rrect(c, -w / 2, -28, w / 2, 28, 28, P("#d9a441", "stroke", 2, alpha=a))
        oval(c, -w / 2 + 28, 0, 16, 16, P(["#e0558a", "#2a9d8f", "#d9a441", "#5ab0ff"][i % 4], alpha=a))
        c.drawString(txt, -w / 2 + 54, 11, f, P("#ffffff", alpha=a))
        c.restore()
    lg = ease_out(prog(lt, 0.1, 0.6))
    glow(c, R.RES.glow_warm, 540, 650, 360, 0.4 * lg)
    draw_img(c, R.RES.logo_gold, 540, 640, 240 * (0.9 + 0.1 * lg), alpha=lg)
    gold_text(c, "Otto Aleman Perfumes", 540, 830, 56, tf=R.RES.semi, white=True, a=lg)
    text_center(c, "Quetzaltenango, Guatemala", 540, 880, font(R.RES.medium, 34), P("#e2b45e", alpha=lg))
    bk = ease_out(prog(lt, T(3) - 0.3, T(3)))
    if bk > 0:
        c.save()
        c.translate(540, 990)
        rrect(c, -380, -56, 380, 56, 56, P("#fff8ea", alpha=bk))
        oval(c, -320, 0, 34, 34, P("#d9a441", alpha=bk))
        typed = word[: int(len(word) * prog(lt, T(4) - 0.4, T(4) + 0.15))]
        if typed:
            c.drawString(typed, -265, 18, font(R.RES.xbold, 50), P("#2a1608", alpha=bk))
        else:
            c.drawString("Agrega un comentario...", -265, 14, font(R.RES.semi, 34), P("#9a8a70", alpha=bk))
        oval(c, 320, 0, 38, 38, P("#d9a441" if lt > T(4) + 0.2 else "#e0d6c0", alpha=bk))
        ar = skia.Path()
        ar.moveTo(305, -16)
        ar.lineTo(338, 0)
        ar.lineTo(305, 16)
        ar.close()
        c.drawPath(ar, P("#2a1608", alpha=bk))
        c.restore()
    dk = prog(lt, T(9) - 0.2, T(9) + 0.25)
    if dk > 0:
        s = back_out(dk)
        c.save()
        c.translate(540, 1220)
        c.scale(s, s)
        glow(c, R.RES.glow_warm, 0, 0, 440, 0.55)
        rrect(c, -380, -110, 380, 110, 46, P("#d9a441", shader=lin(-380, -110, 380, 110, GOLD)))
        text_center(c, "10%", -190, 50, font(R.RES.xbold, 130), P("#2a1608"))
        c.drawString("DE", 0, -12, font(R.RES.xbold, 50), P("#2a1608"))
        c.drawString("DESCUENTO", -10, 48, font(R.RES.xbold, 54), P("#2a1608"))
        c.restore()
        R.burst(c, 540, 1220, lt - T(9) + 0.1, dur=1.1, n=50, radius=420, seed=7, intensity=0.8)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7]


class OttoRes(R.Res):
    def __init__(self):
        super().__init__()
        self.glow_rose = R.sprite(255, 130, 180, power=1.8)
        self.glow_cyan = R.sprite(110, 220, 255, power=1.8)


def install():
    global ENV
    R.Res = OttoRes
    R.SCENES = SCENES
    R.SCENE_GRADE = {}
    R.FADE_IN = 0.0
    ENV = build_env()


if __name__ == "__main__":
    install()
    R.main()
