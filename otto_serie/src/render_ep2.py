"""Serie Otto Aleman Perfumes — Ep. 2: "¿Perfume árabe = copia chafa?".

Escenarios fuera de la perfumería: desierto con caravana, mercado árabe, campo de ingredientes,
laboratorio molecular, pirata vs. original, el precio, y cierre en el mercado de noche.
Uso (desde la raíz del repo):
  VIDEO_BUILD=$PWD/otto_serie/build_ep2 VO_TRIM=0.3 python3 otto_serie/src/render_ep2.py --out otto_serie/build_ep2/video_mudo.mp4
"""
import math
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_ep1 as O1  # noqa: E402
from render_ep1 import (R, P, RECT, GOLD, back_out, clamp, ease_in_out, ease_out, font, glow, hexc, lerp, lin,  # noqa: E402
                        rad, oval, prog, rrect, smooth, text_center, draw_img, draw_kid, rng, W, H,
                        gold_text, pill_gold, mini_bottle, SHELF_COLS)

camera = R.camera
talk = O1.talk

EXPLORADOR = {"headwear": "safari"}
ARABE1 = {"robe": True, "shirt": ("#ffffff", "#f1eee8", "#d8d2c6"), "arm": "#f1eee8", "arm_hl": "#ffffff",
          "collar": "#e0dbd0", "hair": "none", "headwear": "ghutra", "ghutra": ("#ffffff", "#d22b3a"),
          "beard": "#2a1e1a", "skin": ("#f2d0ae", "#dba57a", "#c48a62")}
ARABE2 = {"robe": True, "shirt": ("#fbf8f0", "#ece6d8", "#cfc6b4"), "arm": "#ece6d8", "arm_hl": "#ffffff",
          "collar": "#dcd4c4", "hair": "none", "headwear": "ghutra", "ghutra": ("#ffffff", None),
          "beard": "#7a726c", "skin": ("#efc8a2", "#d29a6e", "#b97e56")}
URB1 = {"shirt": ("#5a6170", "#3a3f4a", "#262a33"), "hem": "#22252d", "collar": "#22252d", "arm": "#3a3f4a",
        "arm_hl": "#6a7180", "pants": ("#3a6ea8", "#24507e"), "headwear": "cap", "head_col": ("#ff8a3c", "#c85a10"),
        "glasses": True, "skin": ("#f5d3b5", "#e0aa82", "#c98f68")}
URB2 = {"shirt": ("#ffd060", "#f0b030", "#c88a10"), "hem": "#b07a10", "collar": "#b07a10", "arm": "#f0b030",
        "arm_hl": "#fff0b0", "pants": ("#2a2a3a", "#16161f"), "hair": "long", "hair_col": ("#5a3a24", "#2e1c10"),
        "lashes": True, "earrings": "#f4cf6a", "lips": "#b23a55", "glasses": True}


# ----------------------------------------------------------------------------
# frascos árabes (dibujados en el estilo del motor, con colores y formas de los originales)
# ----------------------------------------------------------------------------


def _dash(color, w, on=10, off=8, alpha=1.0):
    p = P(color, "stroke", w, alpha=alpha)
    p.setPathEffect(skia.DashPathEffect.Make([on, off], 0))
    return p


def odyssey(c, x, y, s, rot=0.0, glow_a=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if glow_a > 0:
        glow(c, R.RES.glow_warm, 0, -160, 300, 0.5 * glow_a)
    orange = lin(-95, 0, 95, 0, ["#d95e00", "#ffa040", "#ffc078", "#ff7a1a", "#c85000"], [0, .3, .45, .7, 1])
    handle = skia.Path()
    handle.moveTo(70, -335)
    handle.lineTo(128, -335)
    handle.lineTo(128, -268)
    handle.lineTo(70, -268)
    c.drawPath(handle, P("#ff7a1a", "stroke", 13))
    rrect(c, -95, -292, 95, -248, 12, P("#ff7a1a", shader=orange))
    rrect(c, -82, -350, 82, -288, 14, P("#ff7a1a", shader=orange))
    rrect(c, -70, -344, -56, -296, 6, P("#ffffff", alpha=0.35))
    body = lin(-112, 0, 112, 0, ["#137f9e", "#3cc4e4", "#7fe0f4", "#1fa8cc", "#0e6f8c"], [0, .28, .42, .72, 1])
    rrect(c, -112, -252, 112, 0, 28, P("#1fa8cc", shader=body))
    rrect(c, -100, -240, 100, -12, 22, _dash("#0b5a72", 2.5, alpha=0.8))
    c.drawRect(RECT(-114, -216, 114, -180), P("#18a0c4", shader=lin(0, -216, 0, -180, ["#4fd0ec", "#128aac"])))
    rrect(c, -14, -224, 14, -172, 4, P("#26b4d8"))
    rrect(c, -14, -224, 14, -172, 4, P("#0b5a72", "stroke", 2, alpha=0.6))
    text_center(c, "O D Y S S E Y", 0, -110, font(R.RES.semi, 24), P("#0b6e8c"))
    text_center(c, "Mandarin Sky", 0, -78, font(R.RES.bold, 22), P("#0b6e8c"))
    rrect(c, -98, -230, -84, -30, 6, P("#ffffff", alpha=0.18))
    c.restore()


def asad(c, x, y, s, rot=0.0, glow_a=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if glow_a > 0:
        glow(c, R.RES.glow_warm, 0, -170, 300, 0.5 * glow_a)
    bronze = lin(-80, 0, 80, 0, ["#7a4a1c", "#e8b878", "#fff0c8", "#c8904a", "#6a3e14"], [0, .3, .45, .7, 1])
    brown = lin(-74, 0, 74, 0, ["#4a2618", "#8a5638", "#a87050", "#7a4a30", "#3e2014"], [0, .3, .45, .7, 1])
    rrect(c, -72, -302, 72, 0, 34, P("#7a4a30", shader=brown))
    c.drawRect(RECT(-72, -304, 72, -286), P("#c8904a", shader=bronze))
    rrect(c, -70, -366, 70, -300, 22, P("#7a4a30", shader=brown))
    c.drawRect(RECT(-70, -334, 70, -320), P("#c8904a", shader=bronze))
    for sgn in (-1, 1):
        band = skia.Path()
        band.moveTo(-80, -205 if sgn > 0 else -105)
        band.cubicTo(-30, -190 if sgn > 0 else -120, 30, -120 if sgn > 0 else -190, 80, -105 if sgn > 0 else -205)
        c.drawPath(band, P("#c8904a", "stroke", 22, shader=bronze))
    oval(c, 0, -155, 30, 30, P("#c8904a", shader=bronze))
    oval(c, 0, -155, 20, 20, P("#6a3e14"))
    oval(c, 0, -155, 13, 13, P("#e8b878", "stroke", 3))
    text_center(c, "ASAD", 0, -232, font(R.RES.xbold, 30), P("#e8b878"))
    text_center(c, "BOURBON", 0, -58, font(R.RES.semi, 18), P("#e8b878"))
    rrect(c, -60, -280, -48, -30, 6, P("#ffffff", alpha=0.16))
    c.restore()


def hawas(c, x, y, s, rot=0.0, glow_a=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if glow_a > 0:
        glow(c, R.RES.glow_warm, 0, -160, 300, 0.5 * glow_a)
    rrect(c, -112, -262, 112, 0, 36, P("#13324a", shader=lin(0, -262, 0, 0, ["#06090f", "#0e1c2c", "#1d6c8a", "#5fd6ec"],
                                                             [0, .35, .7, 1])))
    rrect(c, -100, -250, -84, -24, 8, P("#ffffff", alpha=0.2))
    rrect(c, -112, -262, 112, 0, 36, P("#ffffff", "stroke", 2, alpha=0.25))
    rrect(c, -30, -292, 30, -258, 6, P("#0a0a0a"))
    rrect(c, -46, -354, 46, -288, 16, P("#151515"))
    for i in range(7):
        yy = -346 + i * 9
        c.drawLine(-44, yy, 44, yy + 6, P("#3a3a3a", "stroke", 3))
    oval(c, 54, -318, 16, 24, P("#151515", "stroke", 8))
    text_center(c, "HAWAS", 0, -170, font(R.RES.xbold, 40), P("#e8c47a"))
    text_center(c, "For Him", 0, -140, font(R.RES.medium, 18), P("#e8c47a"))
    text_center(c, "MALIBU", 0, -96, font(R.RES.semi, 26), P("#f4e2b8"))
    c.restore()


ARAB_BOTTLES = [odyssey, asad, hawas]


# ----------------------------------------------------------------------------
# escenarios nuevos
# ----------------------------------------------------------------------------


def desert(c, t, night=False, sun=True):
    if night:
        c.drawRect(RECT(-500, -500, W + 500, 1500), P("#0c1030", shader=lin(0, -300, 0, 1300, ["#070a1e", "#1a1440", "#3a2050"])))
        r = rng(3)
        for i in range(90):
            oval(c, -300 + r.random() * 1700, -300 + r.random() ** 1.3 * 1300, 2, 2,
                 P("#ffffff", alpha=0.5 + 0.4 * math.sin(t * 2 + i)))
        R.moon(c, 860, 520, 46)
        cols = ["#3a2a4a", "#4a3254", "#5a3a5a"]
    else:
        c.drawRect(RECT(-500, -500, W + 500, 1500), P("#f3a86a", shader=lin(0, -300, 0, 1300, ["#3a2050", "#a8486a", "#f08a5a", "#ffc878"], [0, .4, .7, 1])))
        if sun:
            glow(c, R.RES.glow_warm, 760, 1000, 600, 0.6)
            oval(c, 760, 1000, 130, 130, P("#ffe2a0", shader=rad(760, 1000, 130, ["#fff6d6", "#ffd27a"])))
        cols = ["#c98a4a", "#e0a35c", "#f0b76a"]
    for i, (base, amp, ph) in enumerate(((1120, 60, 0.3), (1260, 80, 1.7), (1420, 70, 3.1))):
        d = skia.Path()
        d.moveTo(-500, H + 400)
        d.lineTo(-500, base)
        for k in range(0, 21):
            xx = -500 + k * 105
            yy = base - amp * math.sin(xx / 330 + ph) - 20 * math.sin(xx / 120 + ph * 2)
            d.lineTo(xx, yy)
        d.lineTo(W + 500, H + 400)
        d.close()
        c.drawPath(d, P(cols[i], shader=lin(0, base - amp, 0, base + 300, [cols[i], R.mix_col(cols[i], "#2a1408", 0.25)])))


def camel(c, x, y, s, t, walk=1.0, face=1, blanket="#c22b3a"):
    """Camello caricatura. (x, y) = patas; face=1 mira a la derecha."""
    c.save()
    c.translate(x, y)
    c.scale(s * face, s)
    body_c = P("#d9a066", shader=lin(0, -300, 0, -100, ["#e8b47a", "#c98a4a"]))
    sw = math.sin(t * 6) * 18 * walk
    for i, (lx, ph) in enumerate(((-90, 0), (-55, math.pi), (60, math.pi), (95, 0))):
        a = math.sin(t * 6 + ph) * 18 * walk
        c.save()
        c.translate(lx, -150)
        c.rotate(a)
        rrect(c, -11, 0, 11, 150, 10, P("#c98a4a" if i % 2 else "#b8783e"))
        oval(c, 0, 150, 16, 8, P("#7a5230"))
        c.restore()
    oval(c, 0, -190, 135, 72, body_c)
    hump = skia.Path()
    hump.moveTo(-80, -230)
    hump.quadTo(-10, -340, 60, -230)
    hump.close()
    c.drawPath(hump, body_c)
    c.drawPath(hump, P(blanket, alpha=0.0))
    bl = skia.Path()
    bl.moveTo(-70, -238)
    bl.quadTo(-10, -320, 50, -238)
    bl.lineTo(60, -170)
    bl.lineTo(-80, -170)
    bl.close()
    c.drawPath(bl, P(blanket))
    for i in range(6):
        c.drawLine(-76 + i * 26, -172, -76 + i * 26, -160, P("#f4cf6a", "stroke", 5))
    c.drawLine(-76, -176, 58, -176, P("#f4cf6a", "stroke", 5))
    neck = skia.Path()
    neck.moveTo(100, -230)
    neck.quadTo(150, -280, 150, -360)
    neck.lineTo(185, -360)
    neck.quadTo(185, -260, 130, -170)
    neck.close()
    c.drawPath(neck, body_c)
    oval(c, 185, -372, 48, 26, P("#d9a066"))
    oval(c, 158, -394, 9, 14, P("#c98a4a"))
    oval(c, 190, -378, 6, 6, P("#1a1a24"))
    oval(c, 226, -366, 4, 3, P("#7a5230"))
    c.drawLine(-130, -200, -150 + sw * 0.3, -120, P("#b8783e", "stroke", 6))
    c.restore()


def lantern(c, x, y, s, t, col="#ff9a3c"):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawLine(0, -200, 0, -40, P("#5a3a20", "stroke", 3))
    glow(c, R.RES.glow_warm, 0, 0, 120, 0.6 + 0.1 * math.sin(t * 5 + x))
    p = skia.Path()
    p.moveTo(0, -42)
    p.lineTo(26, -10)
    p.lineTo(20, 34)
    p.lineTo(-20, 34)
    p.lineTo(-26, -10)
    p.close()
    c.drawPath(p, P(col, shader=lin(-26, 0, 26, 0, ["#c85a10", "#ffd27a", "#c85a10"])))
    c.drawPath(p, P("#5a3a20", "stroke", 3))
    rrect(c, -16, 34, 16, 44, 4, P("#5a3a20"))
    c.restore()


def awning(c, x0, x1, y, cols=("#c22b3a", "#f4e2b8")):
    n = int((x1 - x0) / 60)
    for i in range(n):
        xx = x0 + i * 60
        col = cols[i % 2]
        c.drawRect(RECT(xx, y, xx + 60, y + 70), P(col))
        oval(c, xx + 30, y + 70, 30, 18, P(col))


def souk(c, t, night=False):
    sky = ["#0c1030", "#2a1a4a"] if night else ["#f08a5a", "#ffd090"]
    c.drawRect(RECT(-500, -500, W + 500, 900), P(sky[0], shader=lin(0, -300, 0, 900, sky)))
    if night:
        R.moon(c, 880, 420, 40)
    wall = "#c8a070" if not night else "#5a4058"
    c.drawRect(RECT(-500, 560, W + 500, 1440), P(wall, shader=lin(0, 560, 0, 1440, [wall, R.mix_col(wall, "#2a1408", 0.4)])))
    for i in range(6):
        ax = -60 + i * 230
        arch = skia.Path()
        arch.moveTo(ax, 1440)
        arch.lineTo(ax, 860)
        arch.quadTo(ax + 80, 720, ax + 160, 860)
        arch.lineTo(ax + 160, 1440)
        arch.close()
        c.drawPath(arch, P("#3a2418" if not night else "#1e1428", alpha=0.85))
        c.drawPath(arch, P("#e8c896" if not night else "#8a6a7a", "stroke", 6))
    awning(c, -40, W + 60, 600, ("#c22b3a", "#f4e2b8") if not night else ("#7a1a2a", "#b8a080"))
    for i, lx in enumerate((120, 380, 700, 960)):
        lantern(c, lx, 830 + 30 * (i % 2), 1.0, t, ["#ff9a3c", "#3cc4e4", "#e0558a", "#ffd27a"][i])
    c.drawRect(RECT(-500, 1440, W + 500, H + 500), P("#8a6a4a", shader=lin(0, 1440, 0, H, ["#a07a52", "#3a2414"])))


def alembic(c, x, y, s, t, lt):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glow(c, R.RES.glow_warm, 0, 120, 140, 0.6 + 0.2 * math.sin(t * 9))
    for i in range(5):
        fx = -40 + i * 20
        fl = skia.Path()
        h = 40 + 15 * math.sin(t * 12 + i)
        fl.moveTo(fx - 12, 150)
        fl.quadTo(fx, 150 - h * 2, fx + 12, 150)
        c.drawPath(fl, P("#ff9a3c", alpha=0.8))
    oval(c, 0, 60, 110, 100, P("#c87a40", shader=lin(-110, 0, 110, 0, ["#7a3a14", "#f0a060", "#ffd0a0", "#a85a24"], [0, .4, .5, 1])))
    for i in range(6):
        oval(c, -50 + i * 20, 0 + 8 * math.sin(i), 18, 12, P("#ff6f91"))
    tube = skia.Path()
    tube.moveTo(0, -30)
    tube.quadTo(10, -160, 150, -150)
    tube.quadTo(260, -140, 300, 40)
    c.drawPath(tube, P("#c87a40", "stroke", 18, shader=lin(0, -150, 300, 40, ["#a85a24", "#f0a060"])))
    oval(c, 300, 150, 60, 70, P("#ffffff", alpha=0.15))
    oval(c, 300, 150, 60, 70, P("#e9d8b8", "stroke", 4))
    lvl = clamp(lt / 6)
    c.save()
    c.clipPath(skia.Path().addOval(RECT(240, 80, 360, 220)), True)
    c.drawRect(RECT(240, 220 - 120 * lvl, 360, 220), P("#ffc0d0", alpha=0.85))
    c.restore()
    for i in range(3):
        u = (t * 1.5 + i / 3) % 1
        oval(c, 300, 50 + u * 120, 6, 9, P("#ffd0e0", alpha=1 - u * 0.5))
    c.restore()


def field(c, t):
    c.drawRect(RECT(-500, -500, W + 500, 1100), P("#7ec8ff", shader=lin(0, -300, 0, 1100, ["#4aa8f0", "#a8dcff", "#e8f6ff"])))
    glow(c, R.RES.glow_white, 880, 300, 260, 0.7)
    oval(c, 880, 300, 70, 70, P("#fff6c8"))
    for (cx, cy, k) in ((200, 360, 1.0), (620, 260, 0.8), (980, 470, 0.7)):
        xx = cx + (t * 12 * k) % 300
        for (dx, dy, r) in ((0, 0, 50), (45, -18, 58), (95, 0, 48), (45, 14, 52)):
            oval(c, xx + dx, cy + dy, r * k * 1.2, r * k, P("#ffffff", alpha=0.9))
    for i, (base, col, amp, ph) in enumerate(((1000, "#7bc96f", 60, 0.5), (1130, "#5db55a", 70, 2.0), (1300, "#46a04a", 50, 3.3))):
        h = skia.Path()
        h.moveTo(-500, H + 400)
        h.lineTo(-500, base)
        for k in range(21):
            xx = -500 + k * 105
            h.lineTo(xx, base - amp * math.sin(xx / 300 + ph))
        h.lineTo(W + 500, H + 400)
        h.close()
        c.drawPath(h, P(col, shader=lin(0, base - amp, 0, base + 400, [col, R.mix_col(col, "#1e4a1e", 0.4)])))
    r = rng(8)
    for i in range(70):
        fx, fy = r.random() * W, 1150 + r.random() ** 0.8 * 650
        oval(c, fx, fy, 6, 6, P(["#ffffff", "#ffd23f", "#ff9fc0", "#c9a0ff"][i % 4], alpha=0.9))


def rose(c, x, y, r, col="#ff4f7a"):
    oval(c, x, y, r, r, P(col, shader=rad(x - r * .3, y - r * .3, r * 1.3, ["#ff9fb8", col, "#b8204a"])))
    for k in range(3):
        rr = r * (0.75 - k * 0.22)
        c.drawArc(RECT(x - rr, y - rr, x + rr, y + rr), 20 + k * 70, 220, False, P("#8a1438", "stroke", 3, alpha=0.6))


def rose_bush(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for (dx, dy, r) in ((-120, 40, 110), (0, -20, 130), (120, 40, 110), (0, 90, 120)):
        oval(c, dx, dy, r, r * 0.85, P("#3a8a3a", shader=rad(dx - 30, dy - 40, r * 1.4, ["#5cc05c", "#2a6a2a"])))
    for i, (dx, dy) in enumerate(((-130, -10), (-40, -80), (60, -60), (140, 10), (-70, 70), (40, 40), (110, 100))):
        rose(c, dx, dy + 4 * math.sin(t * 2 + i), 38)
    c.restore()


def saffron(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for i, dx in enumerate((-90, -30, 30, 90)):
        sway = 6 * math.sin(t * 2 + i)
        c.drawLine(dx, 0, dx + sway, -140, P("#3a8a3a", "stroke", 8))
        c.save()
        c.translate(dx + sway, -150)
        for k in range(6):
            c.save()
            c.rotate(k * 60)
            oval(c, 0, -32, 16, 34, P("#a86ae0", shader=lin(0, -66, 0, 0, ["#d8b0ff", "#7a3ac0"])))
            c.restore()
        for k in range(3):
            c.drawLine(0, 0, (k - 1) * 14, -40, P("#e02a1a", "stroke", 5))
        c.restore()
    c.restore()


def oud_tree(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    trunk = skia.Path()
    trunk.moveTo(-50, 0)
    trunk.quadTo(-30, -250, -60, -480)
    trunk.lineTo(60, -480)
    trunk.quadTo(30, -250, 50, 0)
    trunk.close()
    c.drawPath(trunk, P("#6a4a30", shader=lin(-60, 0, 60, 0, ["#4a3020", "#8a6440", "#4a3020"])))
    for (dx, dy) in ((-10, -120), (15, -240), (-15, -360)):
        oval(c, dx, dy, 22, 34, P("#2a1608"))
        glow(c, R.RES.glow_warm, dx, dy, 60, 0.6 + 0.3 * math.sin(t * 3 + dy))
        oval(c, dx + 4, dy + 30, 7, 10, P("#ffb84a"))
    for (dx, dy, r) in ((-150, -520, 150), (0, -620, 180), (150, -520, 150), (-80, -440, 120), (90, -440, 120)):
        oval(c, dx, dy, r, r * 0.8, P("#2f7a3a", shader=rad(dx - 40, dy - 50, r * 1.4, ["#4ea85a", "#1f5a28"])))
    c.restore()


def molecule(c, x, y, s, t, atoms, bonds, spin=0.6, alpha=1.0, glow_a=0.6):
    ang = t * spin
    ca, sa = math.cos(ang), math.sin(ang)
    proj = []
    for (ax, ay, az, kind) in atoms:
        rx = ax * ca + az * sa
        rz = -ax * sa + az * ca
        k = 1 / (1 + rz * 0.0015)
        proj.append((x + rx * s * k, y + ay * s * k, rz, kind, k))
    for i, j in bonds:
        a, b = proj[i], proj[j]
        c.drawLine(a[0], a[1], b[0], b[1], P("#e9d8b8", "stroke", 8 * s * (a[4] + b[4]) / 2, alpha=0.8 * alpha))
    for (px, py, pz, kind, k) in sorted(proj, key=lambda p: -p[2]):
        col = {"C": ["#fff1c4", "#d9a441", "#8a5a17"], "O": ["#ffb0b0", "#e04a4a", "#8a1a1a"],
               "H": ["#ffffff", "#e9e4f0", "#a8a0b8"]}[kind]
        r = {"C": 26, "O": 28, "H": 14}[kind] * s * k
        if glow_a > 0:
            glow(c, R.RES.glow_warm if kind != "H" else R.RES.glow_white, px, py, r * 2.2, 0.25 * glow_a * alpha)
        oval(c, px, py, r, r, P(col[1], shader=rad(px - r * .35, py - r * .35, r * 1.3, col), alpha=alpha))


def ring_mol(n_rings=3):
    """Esqueleto estilizado de anillos (decorativo)."""
    atoms, bonds = [], []
    for rI in range(n_rings):
        cx = rI * 104 - (n_rings - 1) * 52
        cy = (rI % 2) * 30
        base = len(atoms)
        for k in range(6):
            a = math.pi / 6 + k * math.pi / 3
            atoms.append((cx + math.cos(a) * 60, cy + math.sin(a) * 60, (k % 2) * 30 - 15, "C"))
            bonds.append((base + k, base + (k + 1) % 6))
        if rI > 0:
            bonds.append((base + 3, base - 6 + 0))
    atoms.append((atoms[-1][0] + 70, atoms[-1][1] - 40, 0, "O"))
    bonds.append((len(atoms) - 2, len(atoms) - 1))
    for k in (0, 4, 8, 12):
        if k < len(atoms) - 1:
            ax, ay, az, _ = atoms[k]
            atoms.append((ax + 30, ay - 50, az + 20, "H"))
            bonds.append((k, len(atoms) - 1))
    return atoms, bonds


MOL_A = ring_mol(3)
MOL_B = ring_mol(2)


def whale(c, x, y, s, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    w = skia.Path()
    w.moveTo(-200, 0)
    w.cubicTo(-200, -110, 60, -130, 160, -40)
    w.quadTo(230, -10, 260, -70)
    w.quadTo(280, -20, 300, -90)
    w.quadTo(280, 10, 230, 20)
    w.cubicTo(140, 90, -150, 90, -200, 0)
    w.close()
    c.drawPath(w, P("#5ab0ff", alpha=0.18 * a))
    c.drawPath(w, P("#7ac8ff", "stroke", 6, alpha=a))
    oval(c, -140, -20, 8, 8, P("#7ac8ff", alpha=a))
    c.drawLine(-170, 30, -60, 34, P("#7ac8ff", "stroke", 4, alpha=a))
    c.restore()


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def hook_plate(c, lines, y, size, k=1.0):
    c.save()
    c.translate(540, y)
    hgt = len(lines) * size * 1.08
    rrect(c, -500, -size * 1.2, 500, hgt - size * 0.6, 40, P("#0c0818", alpha=0.8 * k))
    rrect(c, -500, -size * 1.2, 500, hgt - size * 0.6, 40, P("#d9a441", "stroke", 3, alpha=0.7 * k))
    for i, (txt, white) in enumerate(lines):
        gold_text(c, txt, 0, i * size * 1.08, size, white=white, a=k)
    c.restore()


def stamp(c, x, y, text, k, col="#d62a3a", rot=-12, size=110):
    if k <= 0:
        return
    s = lerp(2.2, 1.0, ease_out(k))
    a = clamp(k * 3)
    f = font(R.RES.xbold, size)
    w = f.measureText(text) + 60
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    rrect(c, -w / 2, -size * 0.75, w / 2, size * 0.55, 20, P(col, "stroke", 12, alpha=a))
    rrect(c, -w / 2 + 14, -size * 0.75 + 14, w / 2 - 14, size * 0.55 - 14, 12, P(col, "stroke", 4, alpha=a))
    text_center(c, text, 0, size * 0.28, f, P(col, alpha=a))
    c.restore()


def scene1(c, k):  # GANCHO en el desierto
    lt = k.lt
    T = k.w
    camera(c, 1.0 + 0.03 * ease_out(prog(lt, 0, k.D)), 540, 960, k.t)
    desert(c, k.t)
    for i in range(3):
        cx = -150 + lt * 70 + i * 190
        camel(c, cx, 1190 - 20 * math.sin(cx / 330 + 0.3), 0.42, k.t + i * 0.7, walk=1.0,
              blanket=["#c22b3a", "#2a7ac2", "#e0a020"][i])
    draw_kid(c, -150 + lt * 70 + 3 * 190 + 40, 1170, 0.36, k.t, "happy", look=(1, 0), style=ARABE1,
             legs=(math.sin(lt * 6) * 14, -math.sin(lt * 6) * 14), hands={"L": (-120, -330), "R": (110, -200)})
    hook_plate(c, [("¿PERFUME ÁRABE", True), ("= COPIA CHAFA?", False)], 560, 104)
    stamp(c, 720, 860, "MITO", prog(lt, T(6) - 0.15, T(6) + 0.15))
    happy = lt > T(7) - 0.1
    draw_kid(c, 230, 1680, 0.72, k.t, "happy" if happy else "surprised", look=(0.6, -0.5), style=EXPLORADOR,
             hands={"R": (170, -480) if happy else (130, -260), "L": (-120, -230)}, talk=talk(k.t))


def scene2(c, k):  # historia: mercado y destilación de rosas
    lt = k.lt
    T = k.w
    camera(c, lerp(1.06, 1.0, ease_out(prog(lt, 0, 1.5))), 540, 980, k.t)
    souk(c, k.t)
    camel(c, 1010, 1470, 0.55, k.t, walk=0.0, face=-1, blanket="#2a7ac2")
    rrect(c, 140, 1330, 960, 1360, 8, P("#7a4a2e"))
    c.drawRect(RECT(160, 1360, 940, 1500), P("#5a341f"))
    r = rng(5)
    for i in range(6):
        mini_bottle(c, 200 + i * 40, 1330, 0.55, i % 3, SHELF_COLS[i])
    draw_kid(c, 250, 1520, 0.78, k.t, "happy", look=(0.6, -0.2), style=ARABE1,
             hands={"R": (150, -330), "L": (-110, -220)})
    alembic(c, 560, 1180, 0.8, k.t, lt)
    draw_kid(c, 860, 1540, 0.74, k.t, "happy", look=(-0.6, -0.2), style=ARABE2,
             hands={"L": (-150, -360), "R": (110, -220)},
             front_props=lambda cc, out: rose(cc, out["L"][0], out["L"][1] - 20, 30))
    pill_gold(c, 540, 690, "+1000 AÑOS DE HISTORIA", prog(lt, T(4) - 0.2, T(4) + 0.2), size=40, bg="#d9a441")
    pill_gold(c, 540, 790, "Avicena · siglo XI", prog(lt, T(9) - 0.2, T(9) + 0.2), size=36)
    pill_gold(c, 560, 1000, "Agua de rosas", prog(lt, T(17) - 0.2, T(17) + 0.2), size=32, fg="#ffb0c8")


def scene3(c, k):  # campo de ingredientes con gente urbana
    lt = k.lt
    T = k.w
    camera(c, 1.0, lerp(500, 580, ease_in_out(prog(lt, 0, k.D))), 980, k.t)
    field(c, k.t)
    oud_tree(c, 560, 1120, 0.95, k.t)
    rose_bush(c, 190, 1180, 1.0, k.t)
    saffron(c, 880, 1300, 1.0, k.t)
    walk = ease_in_out(prog(lt, 0.2, k.D))
    sw = math.sin(lt * 6) * 16
    draw_kid(c, lerp(300, 380, walk), 1640, 0.62, k.t, "bliss" if lt > T(4) else "happy", look=(-0.6, -0.3),
             style=URB2, legs=(sw, -sw), hands={"L": (-150, -380), "R": (110, -220)})
    draw_kid(c, lerp(560, 640, walk), 1660, 0.66, k.t, "happy", look=(0.5, -0.4), style=EXPLORADOR,
             legs=(-sw, sw), hands={"R": (160, -460), "L": (-110, -220)}, talk=talk(k.t))
    draw_kid(c, lerp(800, 870, walk), 1650, 0.64, k.t, "joy" if lt > T(7) else "happy", look=(0.4, -0.5),
             style=URB1, legs=(sw, -sw), hands={"R": (140, -380), "L": (-110, -220)})
    pill_gold(c, 190, 980, "Rosa de Taif", prog(lt, T(4) - 0.2, T(4) + 0.2), size=34)
    pill_gold(c, 880, 1080, "Azafrán", prog(lt, T(7) - 0.2, T(7) + 0.2), size=34)
    pill_gold(c, 560, 540, "Oud", prog(lt, T(9) - 0.2, T(9) + 0.2), size=40, bg="#d9a441")
    ok = prog(lt, T(17) - 0.2, T(17) + 0.2)
    if ok > 0:
        s = back_out(ok, 2.2)
        c.save()
        c.translate(560, 780)
        c.scale(s, s)
        glow(c, R.RES.glow_warm, 0, -30, 420, 0.6)
        rrect(c, -380, -100, 380, 40, 36, P("#1a1008", alpha=0.75))
        gold_text(c, "ORO LÍQUIDO", 0, 0, 100)
        c.restore()


def lab_bg(c, t):
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#0a1630", shader=rad(540, 900, 1200, ["#14285a", "#0a1630", "#050a18"], [0, .5, 1])))
    for j in range(-2, 18):
        for i in range(-2, 10):
            hx = i * 130 + (65 if j % 2 else 0)
            hy = j * 112
            hexa = skia.Path()
            for q in range(6):
                a = math.pi / 6 + q * math.pi / 3
                (hexa.moveTo if q == 0 else hexa.lineTo)(hx + math.cos(a) * 64, hy + math.sin(a) * 64)
            hexa.close()
            c.drawPath(hexa, P("#d9a441", "stroke", 1.5, alpha=0.08))
    R.dust(c, t, n=30, seed=17, alpha=0.4, col=R.RES.glow_white)


def scene4(c, k):  # laboratorio molecular
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 980, k.t)
    lab_bg(c, k.t)
    for i, (mx, my, sc) in enumerate(((200, 700, 0.6), (900, 760, 0.55), (850, 1330, 0.5))):
        molecule(c, mx, my + 20 * math.sin(k.t + i), sc, k.t + i, *MOL_B, spin=0.8, alpha=0.5)
    pk = prog(lt, T(3) - 0.2, T(3) + 0.2)
    bottle_a = 1 - prog(lt, T(15) - 0.3, T(15))
    if bottle_a > 0:
        c.saveLayerAlpha(None, int(255 * bottle_a))
        R.draw_bottle(c, 300, 1330, 0.9, glow_a=0.6)
        R.orbit_sparkles(c, 300, 1150, k.t, 180, 60, n=16, seed=3, intensity=0.6)
        c.restore()
        pill_gold(c, 300, 960, "Diseñador: también los usa", pk * bottle_a, size=32)
    mk = back_out(prog(lt, T(12) - 0.2, T(12) + 0.3))
    if mk > 0:
        molecule(c, 720, 900, 1.15 * mk, k.t, *MOL_A, spin=0.7, alpha=1.0, glow_a=1.0)
        pill_gold(c, 720, 1110, "Ambroxan", prog(lt, T(12), T(12) + 0.3), size=40, bg="#d9a441")
    wk = prog(lt, T(17) - 0.3, T(17) + 0.2)
    if wk > 0:
        whale(c, 300, 1330, 0.9, a=wk)
        pill_gold(c, 300, 1460, "Ámbar gris (ballenas)", wk, size=30, fg="#9ad4ff")
        ar = ease_out(prog(lt, T(18), T(20)))
        if ar > 0:
            x0, y0, x1, y1 = 470, 1250, 650, 1060
            c.drawLine(x0, y0, lerp(x0, x1, ar), lerp(y0, y1, ar), P("#f7d27a", "stroke", 10))
            if ar > 0.9:
                hd = skia.Path()
                hd.moveTo(x1, y1)
                hd.lineTo(x1 - 40, y1 + 6)
                hd.lineTo(x1 - 12, y1 + 40)
                hd.close()
                c.drawPath(hd, P("#f7d27a"))
    draw_kid(c, 930, 1690, 0.58, k.t, "happy", look=(-0.7, -0.5), style=EXPLORADOR,
             hands={"L": (-160, -440), "R": (110, -220)}, talk=talk(k.t))


def scene5(c, k):  # copia pirata vs. perfume árabe original
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 980, k.t)
    c.drawRect(RECT(-500, -500, 540, H + 500), P("#3a0c14", shader=lin(0, 0, 0, H, ["#2a0810", "#4a1018", "#1a0408"])))
    c.drawRect(RECT(540, -500, W + 500, H + 500), P("#1a1430", shader=lin(0, 0, 0, H, ["#120f26", "#2e2248", "#120f26"])))
    glow(c, R.RES.glow_warm, 800, 1050, 520, 0.35)
    c.drawLine(540, 480, 540, 1500, P("#d9a441", "stroke", 4, alpha=0.8))
    # pirata
    pa = ease_out(prog(lt, 0.0, 0.4))
    c.save()
    c.translate(270, 1250)
    c.rotate(-4 + 2 * math.sin(k.t * 2))
    rrect(c, -80, -260, 80, 0, 26, P("#6a6a72", shader=lin(-80, 0, 80, 0, ["#4a4a52", "#9a9aa4", "#4a4a52"]), alpha=pa))
    rrect(c, -34, -330, 34, -258, 10, P("#8a8a92", alpha=pa))
    rrect(c, -70, -180, 70, -100, 8, P("#e9e4f0", alpha=pa))
    text_center(c, "NOMBRE", 0, -150, font(R.RES.xbold, 26), P("#4a4a52", alpha=pa))
    text_center(c, "FALSO", 0, -116, font(R.RES.xbold, 26), P("#4a4a52", alpha=pa))
    xk = ease_out(prog(lt, T(5) - 0.1, T(5) + 0.2))
    if xk > 0:
        c.drawLine(-80, -190, -80 + 160 * xk, -90, P("#ff3b5c", "stroke", 12))
    c.restore()
    stamp(c, 270, 780, "COPIA PIRATA", prog(lt, T(1) - 0.1, T(1) + 0.2), size=56, rot=-8)
    # originales
    for i, fn in enumerate(ARAB_BOTTLES):
        bk = back_out(prog(lt, T(9) - 0.2 + i * 0.2, T(9) + 0.1 + i * 0.2))
        if bk > 0:
            fn(c, 660 + i * 135 - (0 if i != 1 else 0), 1300 - (40 if i == 1 else 0), 0.58 * bk,
               rot=3 * math.sin(k.t * 1.5 + i), glow_a=0.6)
    stamp(c, 800, 780, "ORIGINAL", prog(lt, T(11) - 0.1, T(11) + 0.2), col="#3aa86a", size=64, rot=6)
    pill_gold(c, 800, 1400, "Marca propia", prog(lt, T(15) - 0.2, T(15) + 0.15), size=30, bg="#d9a441")
    pill_gold(c, 800, 1470, "Fórmula propia", prog(lt, T(19) - 0.2, T(19) + 0.15), size=30, bg="#d9a441")


def balloon(c, x, y, label, col, a=1.0):
    c.drawLine(x, y + 70, x + 10 * math.sin(y / 50), y + 190, P("#e9d8b8", "stroke", 2, alpha=a))
    oval(c, x, y, 70, 80, P(col, shader=rad(x - 25, y - 30, 100, [R.mix_col(col, "#ffffff", 0.5), col]), alpha=a))
    tri = skia.Path()
    tri.moveTo(x - 10, y + 82)
    tri.lineTo(x + 10, y + 82)
    tri.lineTo(x, y + 70)
    tri.close()
    c.drawPath(tri, P(col, alpha=a))
    f = font(R.RES.xbold, 22)
    w = f.measureText(label) + 24
    rrect(c, x - w / 2, y + 190, x + w / 2, y + 230, 12, P("#fff8ea", alpha=a))
    text_center(c, label, x, y + 218, f, P("#2a1608", alpha=a))


def scene6(c, k):  # el precio: lo que no pagas
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 980, k.t)
    desert(c, k.t, night=True)
    for (tx, col) in ((140, "#c22b3a"), (980, "#2a7ac2")):
        tent = skia.Path()
        tent.moveTo(tx - 170, 1300)
        tent.lineTo(tx, 1060)
        tent.lineTo(tx + 170, 1300)
        tent.close()
        c.drawPath(tent, P(col, alpha=0.85))
        c.drawPath(tent, P("#f4cf6a", "stroke", 4, alpha=0.6))
        lantern(c, tx, 1120, 0.7, k.t)
    asad(c, 540, 1330, 1.15, rot=2 * math.sin(k.t * 1.3), glow_a=0.8)
    fly = ease_in_out(prog(lt, T(6) - 0.1, T(10) + 0.6))
    for i, (lab, col) in enumerate((("PUBLICIDAD", "#e0558a"), ("CELEBRIDADES", "#8a5aff"), ("CAMPAÑAS", "#2a9d8f"))):
        bx = 230 + i * 310
        by = lerp(780, -400, fly) + 20 * math.sin(k.t * 2 + i) - (i % 2) * 60
        balloon(c, bx, by, lab, col, a=ease_out(prog(lt, 0.1 + i * 0.2, 0.4 + i * 0.2)))
    expensive = lt < T(6)
    tag = "Q$$$" if expensive else "Q$"
    pill_gold(c, 540, 860, tag, 1.0 if lt > 0.3 else prog(lt, 0, 0.3), size=60, bg=None if expensive else "#d9a441",
              fg="#ff6f7a" if expensive else "#2a1608")
    draw_kid(c, 230, 1700, 0.6, k.t, "happy", look=(0.6, -0.4), style=ARABE2, hands={"R": (160, -440), "L": (-110, -220)})
    draw_kid(c, 860, 1700, 0.6, k.t, "happy", look=(-0.6, -0.4), style=EXPLORADOR,
             hands={"L": (-160, -440), "R": (110, -220)}, talk=talk(k.t))


def scene7(c, k):  # cierre: mercado de noche, comenta ÁRABE
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 960, k.t)
    souk(c, k.t, night=True)
    c.drawRect(RECT(0, 0, W, H), P("#0a0612", alpha=0.45))
    word = "ÁRABE"
    r = rng(31)
    for i in range(22):
        side = -1 if i % 2 == 0 else 1
        x = 540 + side * (405 + r.random() * 70)
        u = (lt - (T(11) + i * 0.15)) / 2.6
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
    lg = ease_out(prog(lt, T(1) - 0.3, T(1) + 0.2))
    glow(c, R.RES.glow_warm, 540, 600, 300, 0.4 * lg)
    draw_img(c, R.RES.logo_gold, 540, 590, 190 * (0.9 + 0.1 * lg), alpha=lg)
    text_center(c, "Quetzaltenango, Guatemala", 540, 730, font(R.RES.medium, 32), P("#e2b45e", alpha=lg))
    # podio con los perfumes
    rrect(c, 180, 1010, 900, 1050, 14, P("#d9a441", shader=lin(0, 1010, 0, 1050, GOLD)))
    c.drawRect(RECT(200, 1050, 880, 1080), P("#8a5a17"))
    for i, fn in enumerate(ARAB_BOTTLES):
        bk = back_out(prog(lt, T(5) - 0.2 + i * 0.15, T(5) + 0.1 + i * 0.15))
        if bk > 0:
            fn(c, 300 + i * 220, 1012, 0.6 * bk, rot=2 * math.sin(k.t * 1.4 + i), glow_a=0.5)
    dk = back_out(prog(lt, T(9) - 0.2, T(9) + 0.15))
    if dk > 0:
        R.draw_decant(c, 840, 930, 170 * dk, rot=8, glow_a=0.8, shadow=False)
    bk = ease_out(prog(lt, T(10) - 0.3, T(10)))
    if bk > 0:
        c.save()
        c.translate(540, 1170)
        rrect(c, -380, -56, 380, 56, 56, P("#fff8ea", alpha=bk))
        oval(c, -320, 0, 34, 34, P("#d9a441", alpha=bk))
        typed = word[: int(len(word) * prog(lt, T(11) - 0.45, T(11) + 0.15))]
        if typed:
            c.drawString(typed, -265, 18, font(R.RES.xbold, 50), P("#2a1608", alpha=bk))
        else:
            c.drawString("Agrega un comentario...", -265, 14, font(R.RES.semi, 34), P("#9a8a70", alpha=bk))
        oval(c, 320, 0, 38, 38, P("#d9a441" if lt > T(11) + 0.2 else "#e0d6c0", alpha=bk))
        ar = skia.Path()
        ar.moveTo(305, -16)
        ar.lineTo(338, 0)
        ar.lineTo(305, 16)
        ar.close()
        c.drawPath(ar, P("#2a1608", alpha=bk))
        c.restore()
    gk = prog(lt, T(16) - 0.2, T(16) + 0.25)
    if gk > 0:
        s = back_out(gk)
        c.save()
        c.translate(540, 1340)
        c.scale(s, s)
        glow(c, R.RES.glow_warm, 0, 0, 440, 0.55)
        rrect(c, -380, -100, 380, 100, 46, P("#d9a441", shader=lin(-380, -100, 380, 100, GOLD)))
        text_center(c, "20%", -190, 46, font(R.RES.xbold, 124), P("#2a1608"))
        c.drawString("DE", 0, -12, font(R.RES.xbold, 50), P("#2a1608"))
        c.drawString("DESCUENTO", -10, 46, font(R.RES.xbold, 54), P("#2a1608"))
        c.restore()
        R.burst(c, 540, 1340, lt - T(16) + 0.1, dur=1.1, n=50, radius=420, seed=7, intensity=0.8)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7]


def install():
    R.Res = O1.OttoRes
    R.SCENES = SCENES
    R.SCENE_GRADE = {}
    R.FADE_IN = 0.0
    R.SUB_PLATE = True
    O1.ENV = O1.build_env()


if __name__ == "__main__":
    install()
    R.main()
