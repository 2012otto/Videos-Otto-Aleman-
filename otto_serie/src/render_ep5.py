"""Otto Aleman Perfumes — "La lámpara de las mil y una noches" (anuncio inesperado estilo documental).

Documental (sin @, subtítulos sobrios) -> giro con corte seco -> el genio con un decant reparte
perfumes y decants a todo el pueblo -> "Comenta GENIO, visita nuestra página".
Uso:
  VIDEO_BUILD=$PWD/otto_serie/build_ep5 VO_TRIM=0.3 python3 otto_serie/src/render_ep5.py --out otto_serie/build_ep5/video_mudo.mp4
"""
import math
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_ep1 as O1  # noqa: E402
import render_ep2 as O2  # noqa: E402
import render_ep4 as O4  # noqa: E402
from render_ep1 import (R, P, RECT, GOLD, back_out, clamp, ease_in_out, ease_out, font, glow, hexc, lerp, lin,  # noqa: E402
                        rad, oval, prog, rrect, smooth, text_center, draw_img, draw_kid, rng, W, H, gold_text, pill_gold,
                        CLIENTA, SENOR)

camera = R.camera
TWIST = 4
MERCADER = {"robe": True, "shirt": ("#c8a070", "#a8804e", "#7a5a30"), "arm": "#a8804e", "arm_hl": "#e0c090",
            "collar": "#7a5a30", "hair": "none", "headwear": "ghutra", "ghutra": ("#efe4cc", None), "agal": False,
            "beard": "#3a2a1e", "skin": ("#f0cba4", "#d69e72", "#bd8458")}
ALDEANA = {"robe": True, "shirt": ("#e07a9a", "#c0507a", "#8a2a50"), "arm": "#c0507a", "arm_hl": "#ffc0d8",
           "collar": "#8a2a50", "hair": "none", "headwear": "ghutra", "ghutra": ("#f4cf6a", None), "agal": False,
           "lashes": True, "earrings": "#f4cf6a", "skin": ("#f5d2b0", "#dca67c", "#c48c62")}
ALDEANO = {"robe": True, "shirt": ("#7ac0e0", "#3a8ab8", "#1e5a80"), "arm": "#3a8ab8", "arm_hl": "#c0e8ff",
           "collar": "#1e5a80", "hair": "none", "headwear": "ghutra", "ghutra": ("#ffffff", "#2a6ab8"), "agal": True,
           "beard": "#2a1e16", "skin": ("#efc8a2", "#d29a6e", "#b97e56")}
NINO = {"shirt": ("#ffd060", "#f0b030", "#c88a10"), "hem": "#b07a10", "collar": "#b07a10", "arm": "#f0b030",
        "arm_hl": "#fff0b0", "pants": ("#7a5a30", "#5a3e20"), "hair_col": ("#2a1e16", "#140e0a"),
        "skin": ("#efc8a2", "#d29a6e", "#b97e56")}


# ----------------------------------------------------------------------------
# lámpara y genio
# ----------------------------------------------------------------------------


def lamp(c, x, y, s, rot=0.0, glow_a=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if glow_a > 0:
        glow(c, R.RES.glow_warm, 0, -30, 220, 0.6 * glow_a)
    gold = lin(-120, 0, 120, 0, ["#8a5a17", "#f7d27a", "#fff1c4", "#d9a441", "#7a4a12"], [0, .3, .45, .7, 1])
    handle = skia.Path()
    handle.addArc(RECT(-150, -70, -60, 20), 90, 220)
    c.drawPath(handle, P("#d9a441", "stroke", 14, shader=gold))
    spout = skia.Path()
    spout.moveTo(60, -30)
    spout.quadTo(150, -40, 190, -90)
    spout.lineTo(200, -78)
    spout.quadTo(160, 0, 60, 10)
    spout.close()
    c.drawPath(spout, P("#d9a441", shader=gold))
    oval(c, 0, -10, 110, 46, P("#d9a441", shader=gold))
    oval(c, 0, 36, 50, 14, P("#b8842e", shader=gold))
    oval(c, 0, -52, 54, 18, P("#e8b860", shader=gold))
    oval(c, 0, -76, 20, 22, P("#f7d27a", shader=gold))
    oval(c, 0, -102, 8, 8, P("#fff1c4"))
    oval(c, -40, -26, 30, 8, P("#ffffff", alpha=0.45))
    c.restore()


def genie(c, x, y, s, t, expr="happy", pose="cross", hold=None, appear=1.0):
    """Genio azul con cola de humo. (x, y) = punta de la cola (la lámpara)."""
    if appear <= 0:
        return {}
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    a = clamp(appear)
    skin = P("#3ab0d8", shader=lin(-160, -900, 160, -400, ["#6ad8f4", "#2a98c8", "#1a6a9a"]), alpha=a)
    # cola de humo
    tail = skia.Path()
    tail.moveTo(0, 0)
    sw = 30 * math.sin(t * 2)
    tail.cubicTo(-60 + sw, -120, 90 - sw, -220, -40, -330)
    tail.cubicTo(-120, -400, -150, -470, -130, -520)
    tail.lineTo(130, -520)
    tail.cubicTo(140, -440, 90, -380, 40, -330)
    tail.cubicTo(150 - sw, -200, 30 + sw, -110, 0, 0)
    tail.close()
    c.drawPath(tail, P("#2a98c8", shader=lin(0, 0, 0, -520, [hexc("#7ad8f0", 0.2 * a), hexc("#2a98c8", 0.95 * a)])))
    for i in range(8):
        u = (t * 0.6 + i / 8) % 1
        oval(c, 30 * math.sin(i * 2 + t), -u * 500, 20 + 20 * u, 14 + 12 * u, P("#9ae4f8", alpha=0.3 * a * (1 - u)))
    # cinturón y torso
    rrect(c, -150, -560, 150, -505, 22, P("#d9a441", shader=lin(-150, 0, 150, 0, GOLD), alpha=a))
    chest = skia.Path()
    chest.moveTo(-150, -520)
    chest.quadTo(-190, -700, -170, -820)
    chest.quadTo(0, -880, 170, -820)
    chest.quadTo(190, -700, 150, -520)
    chest.close()
    c.drawPath(chest, skin)
    for side in (-1, 1):  # chaleco morado abierto
        v = skia.Path()
        v.moveTo(side * 170, -820)
        v.quadTo(side * 190, -700, side * 150, -560)
        v.lineTo(side * 70, -560)
        v.quadTo(side * 60, -700, side * 90, -836)
        v.close()
        c.drawPath(v, P("#7a2ab8", shader=lin(0, -840, 0, -560, ["#a050e0", "#5a1a90"]), alpha=a))
        c.drawPath(v, P("#d9a441", "stroke", 5, alpha=a))
    c.drawLine(-40, -760, -10, -700, P("#1a6a9a", "stroke", 5, alpha=0.5 * a))
    c.drawLine(40, -760, 10, -700, P("#1a6a9a", "stroke", 5, alpha=0.5 * a))
    # brazos
    targets = {"cross": ((-120, -640), (120, -640)), "open": ((-330, -860), (330, -860)),
               "hold": ((-150, -560), (250, -830)), "give": ((-330, -700), (330, -700)),
               "shrug": ((-260, -760), (260, -760))}[pose]
    hands = {}
    for side, (tx, ty) in zip((-1, 1), targets):
        sx, sy = side * 160, -800
        l1, l2 = 170, 170
        dx, dy = tx - sx, ty - sy
        d = clamp(math.hypot(dx, dy), 30, l1 + l2 - 1)
        ang0 = math.atan2(dy, dx)
        b = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1))
        ang = ang0 - b * side
        ex, ey = sx + math.cos(ang) * l1, sy + math.sin(ang) * l1
        hx, hy = sx + math.cos(ang0) * d, sy + math.sin(ang0) * d
        arm = skia.Path()
        arm.moveTo(sx, sy)
        arm.lineTo(ex, ey)
        arm.lineTo(hx, hy)
        c.drawPath(arm, P("#2a98c8", "stroke", 64, alpha=a))
        c.drawPath(arm, P("#7ad8f0", "stroke", 18, alpha=0.3 * a))
        bx, by = lerp(ex, hx, 0.75), lerp(ey, hy, 0.75)
        oval(c, bx, by, 38, 38, P("#d9a441", "stroke", 12, alpha=a))
        oval(c, hx, hy, 42, 42, P("#3ab0d8", shader=rad(hx - 12, hy - 12, 50, ["#6ad8f4", "#2a98c8"]), alpha=a))
        hands[side] = (hx, hy)
    # cabeza
    c.save()
    c.translate(0, -960)
    c.rotate(4 * math.sin(t * 1.3))
    for side in (-1, 1):
        ear = skia.Path()
        ear.moveTo(side * 100, -20)
        ear.lineTo(side * 170, -60)
        ear.lineTo(side * 110, 30)
        ear.close()
        c.drawPath(ear, P("#2a98c8", alpha=a))
        oval(c, side * 120, 50, 18, 18, P("#f7d27a", "stroke", 7, alpha=a))
    oval(c, 0, 0, 125, 120, P("#3ab0d8", shader=rad(-40, -50, 190, ["#7ae0f8", "#3ab0d8", "#1e78a8"]), alpha=a))
    knot = skia.Path()  # coleta
    knot.moveTo(-14, -118)
    knot.cubicTo(-30, -230, 90, -260, 120, -190 + 10 * math.sin(t * 3))
    knot.cubicTo(70, -220, 20, -190, 14, -118)
    knot.close()
    c.drawPath(knot, P("#141420", alpha=a))
    rrect(c, -22, -132, 22, -110, 8, P("#d9a441", alpha=a))
    eyes = {"happy": "open", "surprised": "wide", "laugh": "closed", "wink": "open"}[expr]
    for side in (-1, 1):
        ex, ey = side * 46, -6
        if eyes == "closed" or (expr == "wink" and side > 0):
            pth = skia.Path()
            pth.moveTo(ex - 22, ey + 6)
            pth.quadTo(ex, ey - 16, ex + 22, ey + 6)
            c.drawPath(pth, P("#141420", "stroke", 8, alpha=a))
        else:
            r = 26 if eyes == "wide" else 22
            oval(c, ex, ey, r, r * 1.15, P("#ffffff", alpha=a))
            oval(c, ex + 4, ey + 4, r * 0.5, r * 0.55, P("#141420", alpha=a))
            oval(c, ex + 8, ey - 4, 5, 5, P("#ffffff", alpha=a))
        br = skia.Path()
        lift = -18 if expr == "surprised" else 0
        br.moveTo(ex - 28, ey - 40 + lift + side * 4)
        br.lineTo(ex + 28, ey - 40 + lift - side * 4)
        c.drawPath(br, P("#141420", "stroke", 12, alpha=a))
    beard = skia.Path()
    beard.moveTo(-30, 80)
    beard.quadTo(0, 200, 30, 80)
    beard.close()
    c.drawPath(beard, P("#141420", alpha=a))
    m = skia.Path()
    if expr in ("laugh", "happy", "wink"):
        m.moveTo(-50, 44)
        m.quadTo(0, 110, 50, 44)
        m.close()
        c.drawPath(m, P("#5a1a2a", alpha=a))
        c.drawRect(RECT(-36, 46, 36, 58), P("#ffffff", alpha=a))
    else:
        oval(c, 0, 60, 22, 28, P("#5a1a2a", alpha=a))
    c.drawPath(skia.Path(), P("#000000"))
    c.restore()
    out = {}
    if hold:
        hx, hy = hands[1]
        hold(c, hx, hy)
    c.restore()
    return {k: (x + v[0] * s, y + v[1] * s) for k, v in hands.items()}


def gold_smoke(c, x, y, t, k, h=900):
    if k <= 0:
        return
    for i in range(16):
        u = (t * 0.35 + i / 16) % 1
        yy = y - u * h * k
        xx = x + math.sin(u * 7 + i) * 120 * u
        r = 40 + 120 * u
        oval(c, xx, yy, r, r * 0.7, P("#ffd88a", alpha=0.25 * k * (1 - u)))
    R.aroma(c, x, y, t, n=40, height=h * k, spread=150, intensity=k, seed=3, size=1.3)


def city(c, base, col="#2a1e3e", t=0.0):
    r = rng(2)
    x = -200
    while x < W + 200:
        w = 80 + r.random() * 120
        h = 80 + r.random() * 160
        c.drawRect(RECT(x, base - h, x + w, base), P(col))
        if r.random() > 0.4:
            oval(c, x + w / 2, base - h, w * 0.38, w * 0.38, P(col))
            c.drawLine(x + w / 2, base - h - w * 0.38, x + w / 2, base - h - w * 0.38 - 30, P(col, "stroke", 4))
        if r.random() > 0.7:
            c.drawRect(RECT(x + w * 0.8, base - h - 140, x + w * 0.8 + 18, base - h), P(col))
            oval(c, x + w * 0.8 + 9, base - h - 140, 14, 14, P(col))
        for k in range(int(w / 40)):
            if r.random() > 0.5:
                glow(c, R.RES.glow_warm, x + 20 + k * 40, base - h * 0.5, 16, 0.6)
        x += w + 10


def coin_rain(c, t, k, seed=5):
    r = rng(seed)
    for i in range(40):
        x = r.random() * W
        y = ((r.random() + t * (0.4 + r.random() * 0.3)) % 1) * 1500 + 300
        rr = 18 + r.random() * 10
        sq = abs(math.cos(t * 6 + i))
        oval(c, x, y, rr * sq + 3, rr, P("#f4cf6a", shader=lin(x - rr, 0, x + rr, 0, GOLD), alpha=k))


def palace(c, x, y, s, k):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s * back_out(k), s * back_out(k))
    glow(c, R.RES.glow_warm, 0, -200, 420, 0.5)
    body = P("#f4ead2", shader=lin(0, -400, 0, 0, ["#fff8e8", "#e8d4a8"]))
    c.drawRect(RECT(-260, -220, 260, 0), body)
    oval(c, 0, -250, 130, 120, P("#f4cf6a", shader=lin(-130, 0, 130, 0, GOLD)))
    c.drawLine(0, -370, 0, -420, P("#d9a441", "stroke", 8))
    for side in (-1, 1):
        c.drawRect(RECT(side * 230 - 30, -420, side * 230 + 30, 0), body)
        oval(c, side * 230, -430, 42, 40, P("#f4cf6a", shader=lin(-42, 0, 42, 0, GOLD)))
    for i in range(5):
        ax = -180 + i * 90
        arch = skia.Path()
        arch.moveTo(ax - 26, 0)
        arch.lineTo(ax - 26, -90)
        arch.quadTo(ax, -130, ax + 26, -90)
        arch.lineTo(ax + 26, 0)
        arch.close()
        c.drawPath(arch, P("#7a4a2e"))
    c.restore()


def speech(c, x, y, lines, k, w=760):
    if k <= 0:
        return
    s = back_out(k)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    h = 70 + 74 * len(lines)
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, 40, P("#ffffff"))
    tail = skia.Path()
    tail.moveTo(-60, h / 2 - 4)
    tail.lineTo(-130, h / 2 + 70)
    tail.lineTo(10, h / 2 - 4)
    tail.close()
    c.drawPath(tail, P("#ffffff"))
    for i, (txt, col) in enumerate(lines):
        text_center(c, txt, 0, -h / 2 + 90 + i * 74, font(R.RES.xbold, 60), P(col))
    c.restore()


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def desert_night(c, t):
    O2.desert(c, t, night=True)
    city(c, 1130, "#251a38", t)


def scene1(c, k):  # el mercader encuentra la lámpara
    lt = k.lt
    T = k.w
    camera(c, lerp(1.08, 1.0, ease_out(prog(lt, 0, 4))), 540, 980, k.t)
    desert_night(c, k.t)
    walk = ease_in_out(prog(lt, 0.0, T(7)))
    mx = lerp(120, 470, walk)
    moving = 1.0 if 0.02 < walk < 0.98 else 0.0
    O2.camel(c, mx - 230, 1530, 0.6, k.t, walk=moving, blanket="#c22b3a")
    found = lt > T(9) - 0.1
    if not found:
        glow(c, R.RES.glow_warm, 650, 1520, 90, 0.5 + 0.4 * math.sin(k.t * 6))
        lamp(c, 650, 1525, 0.45, rot=-14)
    sw = math.sin(lt * 7) * 18 * moving
    hands = {"R": (150, -420), "L": (-110, -230)} if found else {"R": (110, -220), "L": (-110, -220)}

    def props(cc, out):
        if found:
            hx, hy = out["R"]
            lamp(cc, hx + 40, hy - 30, 0.5, rot=-8, glow_a=0.6)
    draw_kid(c, mx, 1560, 0.9, k.t, "surprised" if found else "neutral", look=(0.6, 0.3 if not found else -0.3),
             legs=(sw, -sw), style=MERCADER, hands=hands, front_props=props)
    O4.doc_caption(c, "ARABIA · HACE MIL AÑOS", prog(lt, 0.4, 1.8))


def scene2(c, k):  # frota la lámpara y aparece el genio
    lt = k.lt
    T = k.w
    camera(c, lerp(1.0, 1.0, 1), 540, 960, k.t)
    desert_night(c, k.t)
    smoke = smooth(prog(lt, T(2) - 0.2, T(7)))
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#ffb84a", alpha=0.22 * smoke))
    rub = 18 * math.sin(lt * 18) * (lt < T(2))
    gold_smoke(c, 360, 1240, k.t, smoke)
    ap = smooth(prog(lt, T(9) - 0.4, T(9) + 0.6))
    genie(c, 400, 1260, 0.82, k.t, expr="laugh" if ap > 0.6 else "happy", pose="open", appear=ap)
    hands = {"R": (120 + rub, -330), "L": (-40 - rub, -330)}

    def props(cc, out):
        hx, hy = out["R"]
        lamp(cc, hx - 40, hy - 10, 0.55, rot=4, glow_a=0.6 + 0.4 * smoke)
    draw_kid(c, 760, 1620, 0.8, k.t, "surprised" if lt > T(2) else "neutral", look=(-0.7, -0.6 if lt > T(9) else 0.2),
             style=MERCADER, hands=hands, front_props=props)


def scene3(c, k):  # los dos primeros deseos: oro y palacio
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 960, k.t)
    desert_night(c, k.t)
    gold_k = smooth(prog(lt, T(7) - 0.2, T(8) + 0.2)) * (1 - smooth(prog(lt, T(9) + 0.6, T(10))))
    pal_k = prog(lt, T(10) - 0.2, T(11) + 0.2)
    palace(c, 700, 1180, 1.0, pal_k)
    genie(c, 330, 1260, 0.75, k.t, expr="happy", pose="give" if gold_k > 0 or pal_k > 0 else "cross")
    if gold_k > 0:
        coin_rain(c, k.t, gold_k)
        for i in range(12):
            x = 640 + (i % 6) * 34
            y = 1560 - (i // 6) * 18
            oval(c, x, y, 26, 10, P("#f4cf6a", shader=lin(x - 26, 0, x + 26, 0, GOLD), alpha=min(1, gold_k * 2)))
    draw_kid(c, 820, 1600, 0.75, k.t, "happy", look=(-0.6, -0.4), style=MERCADER,
             hands={"R": (160, -470), "L": (-160, -470)} if gold_k > 0.5 else {"R": (110, -220), "L": (-110, -220)})
    for i, (lab, tm) in enumerate((("DESEO 1 · ORO", T(6)), ("DESEO 2 · PALACIO", T(9)))):
        pk = prog(lt, tm - 0.2, tm + 0.15)
        if pk > 0:
            O4.doc_caption(c, lab, pk, x=90, y=250 + 0 * i) if (i == 0 and lt < T(9)) or i == 1 else None


def scene4(c, k):  # el último deseo: suspenso
    lt = k.lt
    T = k.w
    zoom = ease_in_out(prog(lt, T(5), T(11) + 0.8))
    camera(c, lerp(1.0, 1.7, zoom), lerp(540, 810, zoom), lerp(960, 1100, zoom), k.t)
    desert_night(c, k.t)
    palace(c, 760, 1150, 0.7, 1.0)
    genie(c, 330, 1260, 0.75, k.t, expr="surprised" if lt > T(8) else "happy", pose="cross")
    draw_kid(c, 780, 1600, 0.8, k.t, "neutral", look=(-0.4, -0.2), style=MERCADER,
             hands={"R": (40, -460), "L": (-110, -220)})
    O4.doc_caption(c, "DESEO 3 · ???", prog(lt, 0.3, 1.2))


def scene5(c, k):  # EL GIRO: el deseo
    lt = k.lt
    T = k.w
    shake = 14 * max(0, 1 - lt / 0.3) * math.sin(lt * 80)
    camera(c, 1.0 + 0.08 * (1 - ease_out(prog(lt, 0, 0.4))), 540 + shake, 960, k.t)
    O4.sunburst(c, k.t, ("#8a3ae0", "#b06aff"))
    O4.confetti(c, k.t)
    speech(c, 540, 760, [("¡Quiero oler", "#2a1608"), ("increíble... sin", "#2a1608"), ("gastar una fortuna!", "#b8203a")],
           prog(lt, T(0) - 0.1, T(0) + 0.3))
    draw_kid(c, 330, 1780, 1.05, k.t, "happy", look=(0.4, -0.3), style=MERCADER,
             hands={"R": (170, -470), "L": (-110, -230)})
    genie(c, 860, 1640, 0.55, k.t, expr="surprised", pose="shrug")


def scene6(c, k):  # el genio con un decant
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 960, k.t)
    O2.souk(c, k.t, night=False)
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#ffb84a", alpha=0.12))
    has = lt > T(9) - 0.2
    expr = "wink" if has else ("laugh" if lt > T(2) else "happy")

    def hold(cc, hx, hy):
        if has:
            O4.decant_vec(cc, hx + 20, hy - 260, 560, rot=8, t=k.t, glow_a=1.0)
    genie(c, 560, 1500, 0.7, k.t, expr=expr, pose="hold" if has else "shrug", hold=hold)
    if has:
        R.burst(c, 700, 830, lt - T(9) + 0.2, dur=1.0, n=40, radius=300, seed=4, intensity=0.9)
    pk = prog(lt, T(13) - 0.2, T(13) + 0.2)
    if pk > 0:
        s = back_out(pk)
        c.save()
        c.translate(540, 1360)
        c.scale(s, s)
        rrect(c, -330, -64, 330, 64, 32, P("#1a1430", alpha=0.92))
        rrect(c, -330, -64, 330, 64, 32, P("#d9a441", "stroke", 4))
        gold_text(c, "Otto Aleman Perfumes", 0, 20, 52)
        c.restore()


def scene7(c, k):  # reparte perfumes y decants a todo el pueblo
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 960, k.t)
    O2.souk(c, k.t, night=False)
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#ffb84a", alpha=0.12))
    genie(c, 540, 1180, 0.48, k.t, expr="laugh", pose="give")
    people = [(130, ALDEANA, 1.0), (330, ALDEANO, 0.95), (560, NINO, 0.7), (760, CLIENTA, 0.95), (960, SENOR, 0.92)]
    items = [O2.odyssey, None, O2.asad, None, O2.hawas]
    for i, (px, st, sc) in enumerate(people):
        got = prog(lt, 0.3 + i * 0.3, 0.9 + i * 0.3)
        u = ease_in_out(got)
        sx, sy = 540, 760
        tx, ty = px + 60, 1640 - 470 * sc
        if 0 < got < 1:
            fx, fy = lerp(sx, tx, u), lerp(sy, ty, u) - 260 * math.sin(math.pi * u)
            if items[i]:
                items[i](c, fx, fy + 60, 0.28, rot=u * 360)
            else:
                O4.decant_vec(c, fx, fy, 110, rot=u * 540, t=k.t)
        happy = got >= 1

        def props(cc, out, i=i, happy=happy):
            if happy:
                hx, hy = out["R"]
                if items[i]:
                    items[i](cc, hx + 4, hy + 30, 0.26, rot=-6)
                else:
                    O4.decant_vec(cc, hx + 4, hy - 40, 110, rot=-10, t=k.t)
        draw_kid(c, px, 1640, sc * 0.82, k.t, "bliss" if happy else "surprised", look=(0, -0.6), style=st,
                 hands={"R": (130, -430), "L": (-110, -220)} if happy else {"R": (150, -480), "L": (-150, -480)},
                 front_props=props)
        if happy:
            R.aroma(c, px + 60, 1640 - 470 * sc * 0.82, k.t, n=14, height=280, spread=40, intensity=0.8, seed=20 + i)


def scene8(c, k):  # CTA: comenta GENIO, visita nuestra página
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 960, k.t)
    O2.souk(c, k.t, night=True)
    c.drawRect(RECT(0, 0, W, H), P("#0a0612", alpha=0.55))
    O4.confetti(c, k.t, n=24, seed=9)
    word = "GENIO"
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
        f = font(R.RES.xbold, 24)
        w = f.measureText(txt) + 64
        c.save()
        c.translate(x + 20 * math.sin(lt * 2 + i), y)
        rrect(c, -w / 2, -27, w / 2, 27, 27, P("#1a1430", alpha=0.92 * a))
        rrect(c, -w / 2, -27, w / 2, 27, 27, P("#d9a441", "stroke", 2, alpha=a))
        oval(c, -w / 2 + 27, 0, 15, 15, P(["#e0558a", "#2a9d8f", "#d9a441", "#5ab0ff"][i % 4], alpha=a))
        c.drawString(txt, -w / 2 + 52, 11, f, P("#ffffff", alpha=a))
        c.restore()
    lg = ease_out(prog(lt, 0.0, 0.4))
    glow(c, R.RES.glow_warm, 540, 600, 300, 0.4 * lg)
    draw_img(c, R.RES.logo_gold, 540, 600, 200, alpha=lg)
    text_center(c, "Otto Aleman Perfumes", 540, 770, font(R.RES.semi, 48), P("#fff1c4", alpha=lg))
    c.save()
    c.translate(540, 900)
    rrect(c, -330, -56, 330, 56, 56, P("#fff8ea"))
    oval(c, -270, 0, 34, 34, P("#d9a441"))
    typed = word[: int(len(word) * prog(lt, T(1) - 0.45, T(1) + 0.15))]
    if typed:
        c.drawString(typed, -215, 18, font(R.RES.xbold, 52), P("#2a1608"))
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
    vk = prog(lt, T(2) - 0.2, T(2) + 0.25)
    if vk > 0:
        s = back_out(vk)
        c.save()
        c.translate(540, 1070)
        c.scale(s, s)
        rrect(c, -360, -60, 360, 60, 60, P("#1a1430", alpha=0.95))
        rrect(c, -360, -60, 360, 60, 60, P("#d9a441", "stroke", 4))
        text_center(c, "Visita nuestra página", 0, -6, font(R.RES.bold, 34), P("#e9d8b8"))
        text_center(c, "@ottoaleman.perfumesgt", 0, 38, font(R.RES.xbold, 38), P("#f7d27a"))
        c.restore()
    dk = prog(lt, T(7) - 0.2, T(7) + 0.25)
    if dk > 0:
        s = back_out(dk)
        c.save()
        c.translate(540, 1260)
        c.scale(s, s)
        glow(c, R.RES.glow_warm, 0, 0, 440, 0.55)
        rrect(c, -390, -90, 390, 90, 46, P("#d9a441", shader=lin(-390, -90, 390, 90, GOLD)))
        text_center(c, "¡LOS MEJORES", 0, -12, font(R.RES.xbold, 58), P("#2a1608"))
        text_center(c, "DESCUENTOS!", 0, 56, font(R.RES.xbold, 62), P("#2a1608"))
        c.restore()
        R.burst(c, 540, 1260, lt - T(7) + 0.1, dur=1.1, n=50, radius=420, seed=7, intensity=0.8)
    genie(c, 940, 1640, 0.32, k.t, expr="wink", pose="open")


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8]


def draw_subs(c, t, phr):
    if t < O4.CUR["twist_t"]:
        O4.doc_subs(c, t, phr)  # subtítulos sobrios, sin franjas negras
    else:
        O4._orig_subs(c, t, phr)


def install():
    O4.install()
    R.SCENES = SCENES
    R.HARD_CUTS = {TWIST}
    R.draw_subs = draw_subs
    vo, _ = R.timeline.load()
    O4.CUR["twist_t"] = vo[TWIST]["start"]


if __name__ == "__main__":
    install()
    R.main()
