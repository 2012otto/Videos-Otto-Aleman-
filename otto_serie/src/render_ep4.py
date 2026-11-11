"""Otto Aleman Perfumes — "El mensaje en la botella" (anuncio inesperado estilo documental).

Primera parte: documental serio (franjas de cine, subtítulos sobrios, sin marca de agua).
Giro: corte seco a color, estilo de la marca, decant animado en vectores.
Uso (desde la raíz del repo):
  VIDEO_BUILD=$PWD/otto_serie/build_ep4 VO_TRIM=0.3 python3 otto_serie/src/render_ep4.py --out otto_serie/build_ep4/video_mudo.mp4
"""
import math
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_ep1 as O1  # noqa: E402
import render_ep2 as O2  # noqa: E402
from render_ep1 import (R, P, RECT, GOLD, back_out, clamp, ease_in_out, ease_out, font, glow, hexc, lerp, lin,  # noqa: E402
                        rad, oval, prog, rrect, smooth, text_center, draw_img, draw_kid, rng, W, H, gold_text, pill_gold)

camera = R.camera
talk = O1.talk
TWIST = 4  # índice de la escena del giro
CUR = {"t": 0.0, "twist_t": 1e9}
NAUFRAGO = {"shirt": ("#efe4c8", "#d2bf98", "#a8946a"), "hem": "#8a7650", "collar": "#8a7650", "arm": "#d2bf98",
            "arm_hl": "#fff4dc", "pants": ("#5a6a8a", "#3a4660"), "hair": "long", "hair_col": ("#5a3e28", "#2e1e12"),
            "beard": "#5a3e28", "skin": ("#f2cfa8", "#dca478", "#c48a5e")}


# ----------------------------------------------------------------------------
# objetos
# ----------------------------------------------------------------------------


def decant_vec(c, x, y, h, rot=0.0, t=0.0, level=0.62, glow_a=0.0, paper=False):
    """Decant dibujado: cápsula negra brillante, aro plateado y ventanita con perfume dorado."""
    w = h * 0.25
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    if glow_a > 0:
        glow(c, R.RES.glow_warm, 0, 0, h * 0.8, 0.5 * glow_a)
    top, ring_y, bot = -h / 2, -h / 2 + h * 0.4, h / 2
    gl = lin(-w / 2, 0, w / 2, 0, ["#3a3a44", "#0a0a0e", "#1c1c24", "#000000"], [0, .35, .7, 1])
    cap = skia.Path()
    cap.addRRect(skia.RRect.MakeRectXY(RECT(-w / 2, top, w / 2, ring_y + 4), w / 2, w / 2))
    c.drawPath(cap, P("#111111", shader=gl))
    body = skia.Path()
    body.addRRect(skia.RRect.MakeRectXY(RECT(-w / 2, ring_y - 4, w / 2, bot), w / 2, w / 2))
    c.drawPath(body, P("#111111", shader=gl))
    c.drawRect(RECT(-w / 2, ring_y - 4, w / 2, ring_y + 10), P("#111111", shader=gl))
    rrect(c, -w / 2 - 2, ring_y - h * 0.02, w / 2 + 2, ring_y + h * 0.025, 3,
          P("#cccccc", shader=lin(-w / 2, 0, w / 2, 0, ["#7a7a86", "#ffffff", "#b8b8c4", "#ffffff", "#6a6a74"])))
    # ventanita con perfume
    wx0, wx1 = -w * 0.2, w * 0.2
    wy0, wy1 = ring_y + h * 0.12, bot - h * 0.1
    rrect(c, wx0, wy0, wx1, wy1, w * 0.2, P("#2a2a32"))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(RECT(wx0, wy0, wx1, wy1), w * 0.2, w * 0.2), True)
    lvl = wy1 - (wy1 - wy0) * level
    surf = skia.Path()
    surf.moveTo(wx0, wy1)
    surf.lineTo(wx0, lvl + 3 * math.sin(t * 4))
    surf.quadTo(0, lvl - 4 * math.sin(t * 4 + 1), wx1, lvl + 3 * math.sin(t * 4 + 2))
    surf.lineTo(wx1, wy1)
    surf.close()
    c.drawPath(surf, P("#f2b544", shader=lin(0, lvl, 0, wy1, ["#ffe08a", "#d98a1c"])))
    if paper:
        rrect(c, -w * 0.12, wy0 + 4, w * 0.12, wy1 - 6, w * 0.1, P("#f4ead2", alpha=0.85))
    c.restore()
    rrect(c, wx0, wy0, wx1, wy1, w * 0.2, P("#9a9aa8", "stroke", 2, alpha=0.7))
    rrect(c, -w * 0.36, top + h * 0.06, -w * 0.24, bot - h * 0.06, w * 0.06, P("#ffffff", alpha=0.22))
    oval(c, -w * 0.14, top + h * 0.06, w * 0.12, w * 0.06, P("#ffffff", alpha=0.55))
    c.restore()


def glass_bottle(c, x, y, h, rot=0.0, t=0.0, a=1.0):
    """Botella de vidrio verde con corcho y un mensaje enrollado."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    w = h * 0.36
    b = skia.Path()
    b.moveTo(-w * 0.18, -h / 2 + h * 0.1)
    b.lineTo(-w * 0.18, -h / 2 + h * 0.3)
    b.quadTo(-w / 2, -h / 2 + h * 0.36, -w / 2, -h / 2 + h * 0.5)
    b.lineTo(-w / 2, h / 2 - w * 0.2)
    b.quadTo(-w / 2, h / 2, -w * 0.3, h / 2)
    b.lineTo(w * 0.3, h / 2)
    b.quadTo(w / 2, h / 2, w / 2, h / 2 - w * 0.2)
    b.lineTo(w / 2, -h / 2 + h * 0.5)
    b.quadTo(w / 2, -h / 2 + h * 0.36, w * 0.18, -h / 2 + h * 0.3)
    b.lineTo(w * 0.18, -h / 2 + h * 0.1)
    b.close()
    c.drawPath(b, P("#3a8a5a", shader=lin(-w / 2, 0, w / 2, 0, [hexc("#1e5a3a", .9 * a), hexc("#6ac08a", .75 * a), hexc("#1e5a3a", .9 * a)])))
    rrect(c, -w * 0.22, -h * 0.05, w * 0.22, h * 0.36, w * 0.08, P("#f4ead2", alpha=0.9 * a))
    for i in range(4):
        c.drawLine(-w * 0.15, h * 0.02 + i * h * 0.08, w * 0.15, h * 0.02 + i * h * 0.08, P("#a8946a", "stroke", 2, alpha=a))
    rrect(c, -w * 0.2, -h / 2, w * 0.2, -h / 2 + h * 0.13, 4, P("#b8865a", shader=lin(-w * .2, 0, w * .2, 0, ["#8a5a30", "#d8a878", "#8a5a30"]), alpha=a))
    rrect(c, -w * 0.38, -h / 2 + h * 0.48, -w * 0.28, h / 2 - h * 0.08, 4, P("#ffffff", alpha=0.3 * a))
    c.drawPath(b, P("#a8f0c8", "stroke", 2, alpha=0.5 * a))
    c.restore()


def ship(c, x, y, s, t, tilt=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s, s)
    hull = skia.Path()
    hull.moveTo(-260, -40)
    hull.lineTo(260, -60)
    hull.quadTo(230, 60, 140, 80)
    hull.lineTo(-170, 80)
    hull.quadTo(-240, 50, -260, -40)
    hull.close()
    c.drawPath(hull, P("#5a3a22", shader=lin(0, -60, 0, 80, ["#7a5232", "#3a2414"])))
    for i in range(4):
        c.drawLine(-240 + i * 6, -20 + i * 24, 240 - i * 20, -40 + i * 24, P("#2a180c", "stroke", 3, alpha=0.7))
    for (mx, mh) in ((-90, 380), (90, 440)):
        c.drawLine(mx, -50, mx, -50 - mh, P("#4a2e18", "stroke", 12))
        c.drawLine(mx - 110, -50 - mh * 0.7, mx + 110, -50 - mh * 0.7, P("#4a2e18", "stroke", 7))
        sail = skia.Path()
        sail.moveTo(mx - 100, -50 - mh * 0.68)
        sail.quadTo(mx + 30 * math.sin(t * 3), -50 - mh * 0.45, mx - 90, -70)
        sail.lineTo(mx - 60, -90)
        sail.lineTo(mx - 20, -75)
        sail.lineTo(mx + 30, -95)
        sail.lineTo(mx + 90, -70)
        sail.quadTo(mx + 60 + 30 * math.sin(t * 3 + 1), -50 - mh * 0.45, mx + 100, -50 - mh * 0.68)
        sail.close()
        c.drawPath(sail, P("#d8d0c0", shader=lin(mx - 100, 0, mx + 100, 0, ["#b8b0a0", "#efe8d8", "#a8a090"])))
        for k in range(3):
            c.drawLine(mx, -50 - mh, mx - 200 + k * 200, -50, P("#2a1c10", "stroke", 2, alpha=0.6))
    glow(c, R.RES.glow_warm, 180, -90, 70, 0.7 + 0.2 * math.sin(t * 9))
    oval(c, 180, -90, 9, 12, P("#ffd27a"))
    c.restore()


def sea(c, t, y0, cols, amp=40, speed=1.0, foam=True, k=1.0, seed=0, a=1.0):
    p = skia.Path()
    p.moveTo(-500, H + 400)
    pts = []
    for i in range(0, 44):
        x = -500 + i * 50
        y = (y0 + amp * math.sin(x / (130 * k) + t * speed + seed) + amp * 0.4 * math.sin(x / (55 * k) - t * speed * 1.7 + seed * 2))
        pts.append((x, y))
        p.lineTo(x, y)
    p.lineTo(W + 500, H + 400)
    p.close()
    c.drawPath(p, P(cols[0], shader=lin(0, y0 - amp, 0, y0 + 600, list(cols)), alpha=a))
    if foam:
        f = skia.Path()
        for i, (x, y) in enumerate(pts):
            (f.moveTo if i == 0 else f.lineTo)(x, y)
        c.drawPath(f, P("#ffffff", "stroke", 5, alpha=0.55 * a))
        r = rng(seed + 3)
        for i in range(0, len(pts), 2):
            x, y = pts[i]
            oval(c, x + r.random() * 20, y + 4, 8 + r.random() * 10, 4, P("#ffffff", alpha=0.5 * a))
    return pts


def rain(c, t, n=180, a=0.5, slant=0.35):
    r = rng(12)
    for i in range(n):
        x0, ph, sp = r.random() * 1400 - 160, r.random(), 1.6 + r.random()
        y = ((ph + t * sp) % 1) * 2100 - 100
        x = x0 - y * slant
        c.drawLine(x, y, x - 22 * slant * 2, y + 46, P("#cfe0ff", "stroke", 2, alpha=a))


def storm_clouds(c, t, y=300, dark="#1a1e2e"):
    r = rng(4)
    for i in range(16):
        cx = ((r.random() * 1600 + t * (20 + 15 * r.random())) % 1800) - 360
        cy = y + r.random() * 260
        rr = 120 + r.random() * 140
        oval(c, cx, cy, rr * 1.6, rr * 0.7, P(dark, shader=rad(cx, cy - rr * .3, rr * 1.6, ["#3a3f56", dark]), alpha=0.9))


def bolt(c, x, y0, y1, seed, a):
    if a <= 0:
        return
    r = rng(seed)
    p = skia.Path()
    p.moveTo(x, y0)
    yy, xx = y0, x
    while yy < y1:
        yy += 40 + r.random() * 50
        xx += (r.random() - 0.5) * 90
        p.lineTo(xx, yy)
    c.drawPath(p, P("#e6f0ff", "stroke", 14, blur=10, alpha=0.7 * a))
    c.drawPath(p, P("#ffffff", "stroke", 5, alpha=a))


def palm(c, x, y, s, t, marks=0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    trunk = skia.Path()
    trunk.moveTo(-26, 0)
    trunk.quadTo(-10, -260, 50, -520)
    trunk.lineTo(80, -515)
    trunk.quadTo(30, -250, 26, 0)
    trunk.close()
    c.drawPath(trunk, P("#8a6440", shader=lin(-26, 0, 30, 0, ["#6a4a2c", "#a87e54", "#6a4a2c"])))
    for i in range(12):
        yy = -i * 42
        xx = -5 + i * i * 0.35
        c.drawLine(xx - 22, yy, xx + 24, yy - 6, P("#5a3e22", "stroke", 3, alpha=0.6))
    for i in range(marks):  # rayitas de los días contados
        c.drawLine(-16 + (i % 5) * 7 + (i // 5) * 0, -90 - (i // 5) * 26, -16 + (i % 5) * 7, -70 - (i // 5) * 26,
                   P("#2a1808", "stroke", 3))
        if i % 5 == 4:
            c.drawLine(-20, -76 - (i // 5) * 26, 16, -86 - (i // 5) * 26, P("#2a1808", "stroke", 3))
    for k in range(7):
        ang = -160 + k * 26 + 6 * math.sin(t * 1.5 + k)
        c.save()
        c.translate(65, -520)
        c.rotate(ang)
        fr = skia.Path()
        fr.moveTo(0, 0)
        fr.quadTo(120, -60, 250, 30)
        fr.quadTo(120, -10, 0, 0)
        c.drawPath(fr, P("#3a9a4a", shader=lin(0, 0, 250, 0, ["#2a7a3a", "#5cc06a"])))
        c.restore()
    for (cx, cy) in ((50, -505), (80, -500), (64, -490)):
        oval(c, cx, cy, 16, 16, P("#6a4a24"))
    c.restore()


def gull(c, x, y, s, t):
    flap = 14 * math.sin(t * 8 + x)
    g = skia.Path()
    g.moveTo(x - 30 * s, y - flap * s * 0.5)
    g.quadTo(x - 14 * s, y - 14 * s - flap * s * 0.3, x, y)
    g.quadTo(x + 14 * s, y - 14 * s - flap * s * 0.3, x + 30 * s, y - flap * s * 0.5)
    c.drawPath(g, P("#ffffff", "stroke", 4 * s))


def crab(c, x, y, s, t):
    c.save()
    c.translate(x + 30 * math.sin(t * 1.2), y)
    c.scale(s, s)
    for side in (-1, 1):
        for k in range(3):
            c.drawLine(side * 14, 0, side * (30 + k * 4), 14 + k * 3 + 3 * math.sin(t * 12 + k), P("#c0392b", "stroke", 4))
        oval(c, side * 34, -18, 10, 8, P("#e74c3c"))
    oval(c, 0, 0, 26, 16, P("#e74c3c"))
    for side in (-1, 1):
        c.drawLine(side * 8, -12, side * 10, -24, P("#c0392b", "stroke", 3))
        oval(c, side * 10, -26, 4, 4, P("#1a1a24"))
    c.restore()


def doc_caption(c, text, k, x=90, y=250):
    if k <= 0:
        return
    f = font(R.RES.semi, 34)
    n = int(len(text) * clamp(k * 1.4))
    c.drawLine(x, y + 18, x + f.measureText(text) * clamp(k * 1.2), y + 18, P("#ffffff", "stroke", 2, alpha=0.8))
    c.drawString(text[:n], x, y, f, P("#ffffff", alpha=0.9))


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def scene1(c, k):  # tormenta y naufragio
    lt = k.lt
    T = k.w
    camera(c, lerp(1.12, 1.0, ease_out(prog(lt, 0, 3))), 540, 960, k.t)
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#0c1020", shader=lin(0, -200, 0, 1300, ["#05070f", "#141a2e", "#262c40"])))
    flashes = [0.5, 2.6, 4.9, 6.4]
    fl = max(max(0, 1 - (lt - f) / 0.35) if lt >= f else 0 for f in flashes)
    storm_clouds(c, k.t, 260)
    for i, f in enumerate(flashes):
        bolt(c, 260 + i * 190, 150, 1000, seed=i + 2, a=max(0, 1 - (lt - f) / 0.25) if lt >= f else 0)
    sea(c, k.t, 1120, ("#1a2a44", "#0a1220"), amp=50, speed=1.2, seed=1)
    sink = smooth(prog(lt, T(9), T(15)))
    ship(c, 560, 1120 + 380 * sink, 0.85, k.t, tilt=8 * math.sin(k.t * 1.6) + 30 * sink)
    sea(c, k.t, 1230, ("#20345a", "#08101c"), amp=70, speed=1.5, seed=2)
    sea(c, k.t, 1420, ("#2a4470", "#060c16"), amp=90, speed=1.9, seed=3)
    rain(c, k.t, n=200, a=0.45)
    if fl > 0:
        c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#dfe8ff", alpha=0.45 * fl))
    doc_caption(c, "OCÉANO PACÍFICO", prog(lt, 0.4, 1.6))


def scene2(c, k):  # la isla: escribe, guarda y lanza la botella
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 980, k.t)
    days = prog(lt, 0.0, T(5))  # "durante meses": el sol cruza el cielo varias veces
    sun_ph = (days * 2.2) % 1.0
    sky_day = math.sin(math.pi * sun_ph)
    c.drawRect(RECT(-500, -500, W + 500, 1200),
               P("#7ab8e8", shader=lin(0, -200, 0, 1200, [R.mix_col("#1a2448", "#5aa8e8", sky_day),
                                                         R.mix_col("#4a3a6a", "#ffd8a8", sky_day)])))
    sx = lerp(-80, 1160, sun_ph)
    sy = 900 - 600 * math.sin(math.pi * sun_ph)
    glow(c, R.RES.glow_warm, sx, sy, 300, 0.6 * sky_day)
    oval(c, sx, sy, 60, 60, P("#fff2c0", alpha=sky_day))
    if sky_day < 0.5:
        R.moon(c, 1080 - sx, 300, 34)
    for i in range(3):
        gull(c, (200 + i * 120 + lt * 60) % 1300 - 100, 420 + i * 40, 1.0, k.t + i)
    sea(c, k.t, 1040, (R.mix_col("#1a3050", "#2a8ac0", sky_day), "#0a2a44"), amp=16, speed=0.7, seed=4, foam=False)
    r = rng(2)
    for i in range(30):
        sxx = r.random() * W
        syy = 1060 + r.random() * 200
        oval(c, sxx, syy, 10, 2, P("#ffffff", alpha=0.4 * sky_day * (0.5 + 0.5 * math.sin(k.t * 3 + i))))
    isl = skia.Path()
    isl.moveTo(-200, 1500)
    isl.quadTo(200, 1140, 600, 1180)
    isl.quadTo(1000, 1220, 1300, 1500)
    isl.close()
    c.drawPath(isl, P("#e8cf9a", shader=lin(0, 1140, 0, 1500, ["#f4dcaa", "#c8a870"])))
    c.drawRect(RECT(-500, 1440, W + 500, H + 500), P("#c8a870", shader=lin(0, 1440, 0, H, ["#d8b880", "#8a6a40"])))
    palm(c, 150, 1300, 1.0, k.t, marks=int(lerp(0, 24, days)))
    palm(c, 950, 1260, 0.8, k.t + 1)
    rrect(c, 760, 1350, 980, 1380, 6, P("#6a4a2c"))  # tabla del naufragio
    oval(c, 820, 1330, 46, 30, P("#7a5232"))  # barril
    crab(c, 420, 1480, 0.8, k.t)
    throw = prog(lt, T(13) - 0.2, T(13) + 0.6)
    holding = lt < T(13) - 0.2
    writing = lt < T(7) - 0.1
    hands = {"R": (110, -330), "L": (-60, -330)} if writing else ({"R": (150, -420), "L": (-110, -230)}
                                                                if holding else {"R": (200, -560), "L": (-110, -230)})

    def props(cc, out):
        hx, hy = out["R"]
        if writing:
            rrect(cc, hx - 140, hy - 40, hx - 20, hy + 40, 6, P("#f4ead2"))
            for i in range(4):
                cc.drawLine(hx - 125, hy - 22 + i * 16, hx - 40 - (i == 3) * 30 * (1 - prog(lt, T(2), T(5))),
                            hy - 22 + i * 16, P("#5a4a3a", "stroke", 2))
            cc.drawLine(hx, hy, hx + 30, hy - 70, P("#ffffff", "stroke", 5))
            oval(cc, hx + 32, hy - 76, 8, 16, P("#f4f0e8"))
        elif holding:
            glass_bottle(cc, hx + 10, hy - 50, 120, rot=-15, t=k.t)
    draw_kid(c, 470, 1500, 0.95, k.t, "sad" if writing else "neutral", look=(0.4, 0.4 if writing else -0.3),
             style=NAUFRAGO, hands=hands, front_props=props)
    if throw > 0:
        bx = lerp(640, 820, throw)
        by = lerp(940, 1060, throw) - 380 * math.sin(math.pi * throw)
        if throw < 1:
            glass_bottle(c, bx, by, 110, rot=throw * 720, t=k.t)
        else:
            glass_bottle(c, 820 + 4 * math.sin(k.t * 2), 1055 + 6 * math.sin(k.t * 2.2), 90, rot=70 + 8 * math.sin(k.t * 1.5), t=k.t)
        R.burst(c, 820, 1060, lt - T(13) - 0.5, dur=0.8, n=24, radius=120, seed=5, intensity=0.5)


def scene3(c, k):  # el viaje de la botella y el mapa
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 980, k.t)
    split = T(5) - 0.1
    if lt < split:
        u = lt / max(split, 0.1)
        sky = [("#2a3040", "#5a6070"), ("#3a8ad0", "#c8e8ff"), ("#0a1028", "#2a2a50")][int(u * 3) % 3]
        c.drawRect(RECT(-500, -500, W + 500, H + 500), P(sky[0], shader=lin(0, 0, 0, 1100, list(sky))))
        if int(u * 3) % 3 == 0:
            storm_clouds(c, k.t, 200)
            rain(c, k.t, n=120, a=0.35)
            bolt(c, 760, 120, 900, 9, max(0, 1 - abs(lt - T(4)) / 0.2))
        elif int(u * 3) % 3 == 2:
            R.night_sky(c, -500, -500, W + 500, 1000, k.t)
            R.moon(c, 820, 360, 40)
        else:
            glow(c, R.RES.glow_warm, 820, 330, 300, 0.6)
            oval(c, 820, 330, 64, 64, P("#fff2c0"))
            for i in range(3):
                gull(c, (300 + i * 140 + lt * 90) % 1300 - 100, 520 + i * 30, 1.1, k.t + i)
        wb = prog(lt, split * 0.3, split * 0.9)
        if 0 < wb < 1:  # la ballena
            wx = lerp(-260, 1300, wb)
            wy = 1160 - 120 * math.sin(math.pi * wb)
            O2.whale(c, wx, wy, 1.1, a=1.0)
            c.drawPath(skia.Path().addOval(RECT(wx - 210, wy - 70, wx + 80, wy + 60)), P("#2a4a70", alpha=0.0))
        sea(c, k.t, 1060, ("#1e4a7a", "#0a1a30"), amp=40, speed=1.3, seed=6)
        glass_bottle(c, 540 + 30 * math.sin(k.t), 1100 + 24 * math.sin(k.t * 1.8), 230, rot=70 + 14 * math.sin(k.t * 1.4), t=k.t)
        sea(c, k.t, 1180, ("#235690", "#06101e"), amp=50, speed=1.6, seed=7)
    else:
        mk = prog(lt, split, split + 0.4)
        c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#e8d5a8", shader=rad(540, 960, 1100, ["#f4e4bc", "#d8bf88", "#a8864e"], [0, .6, 1])))
        r = rng(9)
        for i in range(14):
            oval(c, r.random() * W, r.random() * H, 40 + r.random() * 80, 30 + r.random() * 60, P("#a8864e", alpha=0.12))
        for i in range(26):  # olitas dibujadas del mapa antiguo
            wx, wy = r.random() * W, 620 + r.random() * 900
            wv = skia.Path()
            wv.moveTo(wx, wy)
            wv.quadTo(wx + 12, wy - 10, wx + 24, wy)
            wv.quadTo(wx + 36, wy + 10, wx + 48, wy)
            c.drawPath(wv, P("#8a6a3a", "stroke", 3, alpha=0.5))
        lands = (([(40, 760), (180, 640), (360, 660), (440, 780), (400, 900), (300, 1000), (160, 960), (60, 880)], "#c9a46a"),
                 ([(690, 640), (860, 580), (1030, 640), (1050, 760), (960, 860), (820, 860), (720, 780)], "#c9a46a"),
                 ([(540, 1090), (620, 1040), (720, 1060), (770, 1150), (720, 1240), (640, 1270), (570, 1210)], "#b89458"))
        for pts, col in lands:
            p = skia.Path()
            n = len(pts)
            mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)  # noqa: E731
            p.moveTo(*mid(pts[-1], pts[0]))
            for q in range(n):
                p.quadTo(pts[q][0], pts[q][1], *mid(pts[q], pts[(q + 1) % n]))
            p.close()
            c.drawPath(p, P(col, shader=rad(pts[0][0] + 100, pts[0][1], 300, ["#dcbf88", col])))
            c.drawPath(p, P("#6a4a24", "stroke", 4))
            for k2 in range(3):
                tx = pts[k2 * 2 % n][0] * 0.6 + pts[(k2 * 2 + 3) % n][0] * 0.4
                ty = pts[k2 * 2 % n][1] * 0.6 + pts[(k2 * 2 + 3) % n][1] * 0.4
                tri = skia.Path()
                tri.moveTo(tx - 14, ty + 10)
                tri.lineTo(tx, ty - 14)
                tri.lineTo(tx + 14, ty + 10)
                c.drawPath(tri, P("#6a4a24", "stroke", 3, alpha=0.7))
        text_center(c, "GUATEMALA", 660, 1300, font(R.RES.xbold, 30), P("#5a3a18"))
        route = skia.Path()
        route.moveTo(150, 1400)
        route.cubicTo(400, 1500, 300, 1100, 520, 1150)
        route.cubicTo(580, 1165, 610, 1150, 640, 1150)
        meas = skia.PathMeasure(route, False)
        L = meas.getLength()
        u = ease_in_out(prog(lt, split + 0.2, k.D - 0.2))
        seg = skia.Path()
        meas.getSegment(0, L * u, seg, True)
        dashp = P("#8a1a1a", "stroke", 6)
        dashp.setPathEffect(skia.DashPathEffect.Make([16, 12], 0))
        c.drawPath(seg, dashp)
        pos = meas.getPosTan(L * u)[0]
        glass_bottle(c, pos.x(), pos.y() - 30, 80, rot=20, t=k.t)
        # rosa de los vientos
        cx, cy = 880, 1420
        for i in range(8):
            a = i * math.pi / 4
            rr = 110 if i % 2 == 0 else 60
            p = skia.Path()
            p.moveTo(cx, cy)
            p.lineTo(cx + math.cos(a - 0.15) * 26, cy + math.sin(a - 0.15) * 26)
            p.lineTo(cx + math.cos(a) * rr, cy + math.sin(a) * rr)
            p.close()
            c.drawPath(p, P("#6a4a24" if i % 2 == 0 else "#a8864e"))
        year = int(lerp(1920, 2026, u))
        c.save()
        c.translate(540, 520)
        rrect(c, -230, -80, 230, 40, 20, P("#5a3a18", alpha=0.85 * mk))
        text_center(c, str(year), 0, 20, font(R.RES.xbold, 100), P("#f4e4bc", alpha=mk))
        c.restore()


def volcano(c, x, base, w, h, col):
    p = skia.Path()
    p.moveTo(x - w, base)
    p.lineTo(x - w * 0.12, base - h)
    p.quadTo(x, base - h - 12, x + w * 0.12, base - h)
    p.lineTo(x + w, base)
    p.close()
    c.drawPath(p, P(col))


def beach(c, t, warm=1.0):
    c.drawRect(RECT(-500, -500, W + 500, 1200), P("#f08a5a", shader=lin(0, -200, 0, 1150, ["#2a2050", "#8a3a6a", "#f07a50", "#ffc070"], [0, .35, .7, 1])))
    glow(c, R.RES.glow_warm, 760, 1000, 420, 0.7)
    oval(c, 760, 1010, 110, 110, P("#ffd88a"))
    volcano(c, 180, 1060, 260, 300, "#4a2a4a")
    volcano(c, 470, 1060, 220, 240, "#5a3050")
    volcano(c, 980, 1060, 240, 260, "#4a2a4a")
    sea(c, t, 1040, ("#e08a6a", "#5a3a6a"), amp=10, speed=0.6, seed=8, foam=False)
    r = rng(3)
    for i in range(24):
        oval(c, 600 + r.random() * 400, 1060 + r.random() * 60, 18, 2, P("#fff0c0", alpha=0.6))
    sand = skia.Path()
    sand.moveTo(-500, 1240)
    for i in range(22):
        x = -500 + i * 100
        sand.lineTo(x, 1240 + 18 * math.sin(x / 200 + t * 0.8))
    sand.lineTo(W + 500, H + 400)
    sand.lineTo(-500, H + 400)
    sand.close()
    c.drawPath(sand, P("#2a2228", shader=lin(0, 1240, 0, H, ["#3a3038", "#141016"])))
    for i in range(3):  # espuma que llega a la arena negra
        u = (t * 0.25 + i / 3) % 1
        y = 1230 + u * 90
        fp = skia.Path()
        fp.moveTo(-500, y)
        for q in range(22):
            x = -500 + q * 100
            fp.lineTo(x, y + 10 * math.sin(x / 90 + i))
        c.drawPath(fp, P("#ffffff", "stroke", 6, alpha=0.6 * (1 - u)))
    for i in range(80):
        oval(c, r.random() * W, 1300 + r.random() * 600, 2, 2, P("#d8c8e8", alpha=0.5))


def scene4(c, k):  # la playa de Guatemala: alguien la encuentra
    lt = k.lt
    T = k.w
    zoom = ease_in_out(prog(lt, T(13), T(17) + 0.6))
    camera(c, lerp(1.0, 1.9, zoom), lerp(540, 610, zoom), lerp(980, 1010, zoom), k.t)
    beach(c, k.t)
    palm(c, 70, 1400, 0.9, k.t)
    crab(c, 900, 1560, 0.7, k.t + 2)
    for i in range(3):
        gull(c, (500 + i * 140 + lt * 50) % 1300 - 100, 520 + i * 40, 1.0, k.t + i)
    walk = ease_in_out(prog(lt, 0.0, T(9)))
    kx = lerp(160, 560, walk)
    moving = 1.0 if 0.02 < walk < 0.98 else 0.0
    sw = math.sin(lt * 9) * 20 * moving
    found = lt > T(10) - 0.1
    reading = lt > T(12) - 0.2
    if not found:
        glass_bottle(c, 690, 1500, 110, rot=80, t=k.t)
        for i in range(int(kx / 60)):
            oval(c, 120 + i * 60, 1640 + (i % 2) * 14, 12, 6, P("#141016"))
    if reading:
        hands = {"R": (85, -255), "L": (-85, -255)}
    elif found:
        hands = {"R": (160, -420), "L": (-110, -230)}
    else:
        hands = {"R": (110, -220), "L": (-110, -220)}

    def props(cc, out):
        if reading:
            hx, hy = out["R"]
            lx, ly = out["L"]
            rrect(cc, lx - 14, ly - 80, hx + 14, hy + 34, 8, P("#f4ead2"))
            for i in range(5):
                cc.drawLine(lx + 6, ly - 60 + i * 18, hx - 6, ly - 60 + i * 18, P("#a8946a", "stroke", 3))
        elif found:
            hx, hy = out["R"]
            glass_bottle(cc, hx + 6, hy - 50, 120, rot=-10, t=k.t)
    expr = "neutral" if lt < T(10) else ("happy" if lt < T(16) - 0.1 else "surprised")
    draw_kid(c, kx, 1640, 0.95, k.t, expr, look=(0.4, 0.4 if reading else -0.1), legs=(sw, -sw),
             hands=hands, front_props=props)
    if found and not reading:
        R.burst(c, kx + 160, 1240, lt - T(11) - 0.3, dur=0.6, n=14, radius=80, seed=3, intensity=0.6)
    doc_caption(c, "COSTA DEL PACÍFICO · GUATEMALA", prog(lt, 0.3, 1.6))


def sunburst(c, t, cols=("#ffd23f", "#ffb02e")):
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P(cols[0]))
    c.save()
    c.translate(540, 960)
    c.rotate(t * 20)
    for i in range(18):
        p = skia.Path()
        p.moveTo(0, 0)
        a0, a1 = math.radians(i * 20), math.radians(i * 20 + 10)
        p.lineTo(math.cos(a0) * 2000, math.sin(a0) * 2000)
        p.lineTo(math.cos(a1) * 2000, math.sin(a1) * 2000)
        p.close()
        c.drawPath(p, P(cols[1]))
    c.restore()


def confetti(c, t, n=70, seed=4):
    r = rng(seed)
    cols = ["#e8414f", "#2fbf71", "#3aa0ff", "#ffffff", "#8a5aff", "#ff7ab8"]
    for i in range(n):
        x = r.random() * W + 30 * math.sin(t * 2 + i)
        y = ((r.random() + t * (0.12 + r.random() * 0.1)) % 1) * 2000 - 80
        c.save()
        c.translate(x, y)
        c.rotate(t * 200 * (r.random() - 0.5) + i * 30)
        c.drawRect(RECT(-9, -5, 9, 5), P(cols[i % len(cols)]))
        c.restore()


def scene5(c, k):  # EL GIRO
    lt = k.lt
    T = k.w
    shake = 14 * max(0, 1 - lt / 0.3) * math.sin(lt * 80)
    camera(c, 1.0 + 0.08 * (1 - ease_out(prog(lt, 0, 0.4))), 540 + shake, 960, k.t)
    sunburst(c, k.t)
    confetti(c, k.t)
    bk = back_out(prog(lt, 0.0, 0.45))
    c.save()
    c.translate(540, 900)
    c.scale(bk, bk)
    c.rotate(-3 + 1.5 * math.sin(k.t * 2))
    for side in (-1, 1):
        oval(c, side * 430, -260, 40, 300, P("#d8c49a"))
    rrect(c, -430, -300, 430, 300, 20, P("#f4ead2", shader=lin(0, -300, 0, 300, ["#fbf3de", "#e8d8b0"])))
    rrect(c, -430, -300, 430, 300, 20, P("#a8864e", "stroke", 4))
    lines = [("¡YA LLEGARON", "#2a1608"), ("LOS NUEVOS", "#2a1608"), ("ÁRABES A", "#2a1608"), ("OTTO ALEMAN!", "#b8203a")]
    for i, (txt, col) in enumerate(lines):
        kk = ease_out(prog(lt, T(1 + i * 2) - 0.1, T(1 + i * 2) + 0.15)) if i < 3 else ease_out(prog(lt, T(8) - 0.1, T(8) + 0.2))
        text_center(c, txt, 0, -170 + i * 130, font(R.RES.xbold, 96), P(col, alpha=kk))
    c.restore()
    for i, fn in enumerate(O2.ARAB_BOTTLES):
        ak = back_out(prog(lt, T(6) - 0.2 + i * 0.15, T(6) + 0.1 + i * 0.15))
        if ak > 0:
            fn(c, 230 + i * 310, 1560, 0.6 * ak, rot=6 * math.sin(k.t * 3 + i), glow_a=0.6)


def scene6(c, k):  # la botella era un decant
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 980, k.t)
    beach(c, k.t)
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#ffb84a", alpha=0.18))
    confetti(c, k.t, n=30, seed=7)
    poof = prog(lt, T(5) - 0.25, T(5) + 0.05)
    hands = {"R": (150, -430), "L": (-110, -230)}
    spraying = lt > T(6) + 0.2

    def props(cc, out):
        hx, hy = out["R"]
        if poof < 1:
            jig = 10 * math.sin(lt * 40) * clamp(poof * 3)
            glass_bottle(cc, hx + 6 + jig, hy - 60, 150, rot=-10, t=k.t)
        else:
            decant_vec(cc, hx + 6, hy - 70, 190, rot=-12, t=k.t, glow_a=0.8)
    hp = draw_kid(c, 520, 1720, 1.15, k.t, "joy" if spraying else ("surprised" if poof > 0 else "happy"),
                  look=(0.5, -0.3), hands=hands, front_props=props, talk=0.0)
    hx, hy = hp["R"]
    if poof > 0:
        R.burst(c, hx, hy - 80 * 1.15, lt - T(5) + 0.1, dur=0.9, n=50, radius=260, seed=11, intensity=1.0)
    if spraying:
        R.aroma(c, hx - 30, hy - 200, k.t, n=40, height=500, spread=120, intensity=0.9, seed=6, size=1.2)
    pk = prog(lt, T(6) - 0.1, T(6) + 0.25)
    if pk > 0:
        s = back_out(pk)
        c.save()
        c.translate(540, 700)
        c.rotate(-4)
        c.scale(s, s)
        rrect(c, -330, -80, 330, 60, 30, P("#1a1430", alpha=0.92))
        rrect(c, -330, -80, 330, 60, 30, P("#d9a441", "stroke", 4))
        gold_text(c, "¡ERA UN DECANT!", 0, 12, 76)
        c.restore()


def scene7(c, k):  # CTA: comenta BOTELLA
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 960, k.t)
    beach(c, k.t)
    c.drawRect(RECT(0, 0, W, H), P("#0a0612", alpha=0.62))
    confetti(c, k.t, n=24, seed=9)
    word = "BOTELLA"
    r = rng(41)
    for i in range(22):
        side = -1 if i % 2 == 0 else 1
        x = 540 + side * (405 + r.random() * 70)
        u = (lt - (T(1) + i * 0.15)) / 2.6
        if u <= 0 or u >= 1:
            continue
        y = lerp(1500, 520, u)
        a = math.sin(math.pi * u)
        txt = [word, "¡" + word + "!", word + "!!", word][i % 4]
        f = font(R.RES.xbold, 22)
        w = f.measureText(txt) + 62
        c.save()
        c.translate(x + 20 * math.sin(lt * 2 + i), y)
        rrect(c, -w / 2, -26, w / 2, 26, 26, P("#1a1430", alpha=0.92 * a))
        rrect(c, -w / 2, -26, w / 2, 26, 26, P("#d9a441", "stroke", 2, alpha=a))
        oval(c, -w / 2 + 26, 0, 14, 14, P(["#e0558a", "#2a9d8f", "#d9a441", "#5ab0ff"][i % 4], alpha=a))
        c.drawString(txt, -w / 2 + 50, 10, f, P("#ffffff", alpha=a))
        c.restore()
    lg = ease_out(prog(lt, 0.0, 0.4))
    glow(c, R.RES.glow_warm, 540, 600, 300, 0.4 * lg)
    draw_img(c, R.RES.logo_gold, 540, 600, 200, alpha=lg)
    text_center(c, "Otto Aleman Perfumes", 540, 770, font(R.RES.semi, 48), P("#fff1c4", alpha=lg))
    decant_vec(c, 880, 1020, 230, rot=12, t=k.t, glow_a=0.7)
    glass_bottle(c, 200, 1030, 200, rot=-14, t=k.t)
    c.save()
    c.translate(540, 900)
    rrect(c, -330, -56, 330, 56, 56, P("#fff8ea"))
    oval(c, -270, 0, 34, 34, P("#d9a441"))
    typed = word[: int(len(word) * prog(lt, T(1) - 0.5, T(1) + 0.2))]
    if typed:
        c.drawString(typed, -215, 18, font(R.RES.xbold, 50), P("#2a1608"))
    else:
        c.drawString("Comenta...", -215, 14, font(R.RES.semi, 34), P("#9a8a70"))
    oval(c, 270, 0, 38, 38, P("#d9a441"))
    ar = skia.Path()
    ar.moveTo(255, -16)
    ar.lineTo(288, 0)
    ar.lineTo(255, 16)
    ar.close()
    c.drawPath(ar, P("#2a1608"))
    c.restore()
    gk = prog(lt, T(6) - 0.2, T(6) + 0.25)
    if gk > 0:
        s = back_out(gk)
        c.save()
        c.translate(540, 1250)
        c.scale(s, s)
        glow(c, R.RES.glow_warm, 0, 0, 440, 0.55)
        rrect(c, -380, -110, 380, 110, 46, P("#d9a441", shader=lin(-380, -110, 380, 110, GOLD)))
        text_center(c, "10%", -190, 50, font(R.RES.xbold, 130), P("#2a1608"))
        c.drawString("DE", 0, -12, font(R.RES.xbold, 50), P("#2a1608"))
        c.drawString("DESCUENTO", -10, 48, font(R.RES.xbold, 54), P("#2a1608"))
        c.restore()
        R.burst(c, 540, 1250, lt - T(6) + 0.1, dur=1.1, n=50, radius=420, seed=7, intensity=0.8)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7]


# ----------------------------------------------------------------------------
# documental vs. giro: franjas de cine, subtítulos sobrios y marca de agua solo después del giro
# ----------------------------------------------------------------------------
_orig_frame = R.render_frame
_orig_subs = R.draw_subs
_orig_wm = R.draw_watermark


def doc_subs(c, t, phr):
    f = font(R.RES.medium, 50)
    for p in phr:
        if not (p["s"] <= t < p["e"]):
            continue
        fade = clamp((p["e"] - t) / 0.15) * clamp((t - p["s"]) / 0.15)
        words = [w for w in p["words"] if t >= w["s"] - 0.04]
        if not words:
            continue
        full = " ".join(w["w"] for w in p["words"])
        # cortar en líneas usando todas las palabras (posiciones fijas)
        sp = f.measureText(" ")
        rows, cur, cw = [], [], 0
        for w in p["words"]:
            wd = f.measureText(w["w"])
            if cur and cw + sp + wd > 940:
                rows.append((cur, cw))
                cur, cw = [], 0
            cw = cw + (sp if cur else 0) + wd
            cur.append((w, wd))
        rows.append((cur, cw))
        y0 = 1690 - (len(rows) - 1) * 64
        for ri, (row, rw) in enumerate(rows):
            x = W / 2 - rw / 2
            for w, wd in row:
                if t >= w["s"] - 0.04:
                    c.drawString(w["w"], x + 2, y0 + ri * 64 + 3, f, P("#000000", alpha=0.7 * fade, blur=4))
                    c.drawString(w["w"], x, y0 + ri * 64, f, P("#ffffff", alpha=0.95 * fade))
                x += wd + sp


def render_frame(c, t, vo, phr, total):
    CUR["t"] = t
    _orig_frame(c, t, vo, phr, total)


def draw_subs(c, t, phr):
    if t < CUR["twist_t"]:
        # franjas de cine y subtítulos de documental
        c.drawRect(RECT(0, 0, W, 150), P("#000000"))
        c.drawRect(RECT(0, H - 150, W, H), P("#000000"))
        doc_subs(c, t, phr)
    else:
        _orig_subs(c, t, phr)


def draw_watermark(c):
    if CUR["t"] >= CUR["twist_t"]:
        _orig_wm(c)


def install():
    R.Res = O1.OttoRes
    R.SCENES = SCENES
    R.SCENE_GRADE = {}
    R.FADE_IN = 0.6
    R.SUB_PLATE = True
    R.HARD_CUTS = {TWIST}
    R.render_frame = render_frame
    R.draw_subs = draw_subs
    R.draw_watermark = draw_watermark
    vo, _ = R.timeline.load()
    CUR["twist_t"] = vo[TWIST]["start"]
    O1.ENV = O1.build_env()


if __name__ == "__main__":
    install()
    R.main()
