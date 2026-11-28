"""Frascos nuevos para el video de Black Friday: Valentino Born in Roma (Intense / Yellow Dream) y Yara Candy.
(x, y) = base del frasco; s = escala (s=1 -> ~560 px de alto)."""
import math

import skia

import render as R
from render import P, lin, oval, rrect, glow, text_center, font

SERIF = skia.Typeface("Liberation Serif", skia.FontStyle.Normal())


def mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(int(ca[i] + (cb[i] - ca[i]) * t) for i in range(3))


def spaced(c, txt, x, y, f, paint, sp):
    ws = [f.measureText(ch) for ch in txt]
    tot = sum(ws) + sp * (len(txt) - 1)
    xx = x - tot / 2
    for ch, w in zip(txt, ws):
        c.drawString(ch, xx, y, f, paint)
        xx += w + sp


# ---------------------------------------------------------------- Valentino Born in Roma
VALENTINO = {
    # bandas de color de arriba (0) a abajo (1): (posición, color base)
    "intense": dict(bands=[(0.0, "#16161a"), (0.58, "#16161a"), (0.62, "#d01838"), (0.80, "#9a0c28"), (0.84, "#b8b8bc"), (1.0, "#d8d8dc")],
                    label="#0d0d0f", text="#ff6aa0", sub="INTENSE"),
    "yellow": dict(bands=[(0.0, "#f4d84a"), (0.55, "#f8e070"), (0.80, "#f4ecc0"), (1.0, "#e8e8e4")],
                   label="#0d0d0f", text="#f2e650", sub="YELLOW DREAM"),
}


def band_color(bands, u):
    for (p0, c0), (p1, c1) in zip(bands, bands[1:]):
        if u <= p1:
            return mix(c0, c1, (u - p0) / max(p1 - p0, 1e-6))
    return bands[-1][1]


def stud(c, x, y, r, col, clear=False):
    """Una tacha piramidal (rombo con 4 caras de luz distinta)."""
    lum = sum(int(col[i:i + 2], 16) for i in (1, 3, 5)) / 765
    lite = mix(col, "#ffffff", (0.55 if not clear else 0.7) * (0.45 + 0.55 * lum))
    mid = mix(col, "#ffffff", 0.18)
    dark = mix(col, "#000000", 0.45 if not clear else 0.25)
    darker = mix(col, "#000000", 0.65 if not clear else 0.35)
    pts = [(x, y - r), (x + r, y), (x, y + r), (x - r, y)]
    faces = [(pts[3], pts[0], lite), (pts[0], pts[1], mid), (pts[1], pts[2], darker), (pts[2], pts[3], dark)]
    for a, b, fc in faces:
        p = skia.Path()
        p.moveTo(x, y)
        p.lineTo(*a)
        p.lineTo(*b)
        p.close()
        c.drawPath(p, P(fc))


def valentino(c, x, y, s, t=0.0, kind="intense", glow_a=0.0, rot=0.0):
    V = VALENTINO[kind]
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if glow_a > 0:
        glow(c, R.RES.glow_warm, 0, -200, 340, 0.6 * glow_a)
    oval(c, 0, 6, 170, 22, P("#000000", alpha=0.3))
    top, bot = -380, 0
    body = skia.Path()
    body.moveTo(-95, top)
    body.lineTo(95, top)
    body.cubicTo(150, top + 10, 165, top + 50, 165, top + 110)
    body.lineTo(165, -40)
    body.quadTo(165, 0, 125, 0)
    body.lineTo(-125, 0)
    body.quadTo(-165, 0, -165, -40)
    body.lineTo(-165, top + 110)
    body.cubicTo(-165, top + 50, -150, top + 10, -95, top)
    body.close()
    c.drawPath(body, P(band_color(V["bands"], 0.5)))
    c.save()
    c.clipPath(body, True)
    r, step = 19, 38
    row = 0
    yy = top - 10
    while yy < 30:
        u = (yy - top) / (bot - top)
        col = band_color(V["bands"], max(0, min(1, u)))
        clear = u > 0.82 or kind == "yellow"
        off = (row % 2) * step / 2
        xx = -190 + off
        while xx < 200:
            stud(c, xx, yy, r, col, clear)
            xx += step
        yy += step / 2
        row += 1
    # sombreado cilíndrico + brillo
    c.drawPath(body, P("#000000", shader=lin(-165, 0, 165, 0, ["#000000", R.hexc("#000000", 0), R.hexc("#000000", 0), "#000000"], [0, .25, .7, 1]), alpha=0.45))
    c.drawRect(R.R(-120, top + 30, -100, -30), P("#ffffff", alpha=0.18))
    c.restore()
    c.drawPath(body, P("#000000", "stroke", 3, alpha=0.5))
    # etiqueta negra
    ly = -190
    rrect(c, -125, ly - 52, 125, ly + 40, 6, P(V["label"], shader=lin(0, ly - 52, 0, ly + 40, ["#1c1c20", "#0a0a0c"])))
    rrect(c, -125, ly - 52, 125, ly + 40, 6, P("#ffffff", "stroke", 2, alpha=0.12))
    spaced(c, "VALENTINO", 0, ly + 10, font(SERIF, 34), P(V["text"]), 0)
    spaced(c, V["sub"], 0, ly + 32, font(R.RES.semi, 13), P(V["text"], alpha=0.85), 3)
    # cuello con collar de tachas grandes + tapa negra
    rrect(c, -80, top - 30, 80, top + 4, 8, P("#111114"))
    collar = skia.Path()
    collar.moveTo(-90, top - 30)
    collar.lineTo(-118, top - 64)
    collar.lineTo(-90, top - 98)
    collar.lineTo(90, top - 98)
    collar.lineTo(118, top - 64)
    collar.lineTo(90, top - 30)
    collar.close()
    c.drawPath(collar, P("#1a1a1e"))
    for i, xx in enumerate((-66, 0, 66)):
        stud(c, xx, top - 64, 30, "#2a2a30")
    stud(c, -104, top - 64, 22, "#222226")
    stud(c, 104, top - 64, 22, "#222226")
    rrect(c, -62, top - 108, 62, top - 94, 4, P("#0c0c0e"))
    cap = R.R(-72, top - 220, 72, top - 104)
    c.drawRRect(skia.RRect.MakeRectXY(cap, 10, 10), P("#111111", shader=lin(-72, 0, 72, 0, ["#050506", "#2c2c32", "#141418", "#050506"], [0, .3, .6, 1])))
    c.drawRect(R.R(-52, top - 212, -40, top - 112), P("#ffffff", alpha=0.12))
    c.restore()


# ---------------------------------------------------------------- Yara Candy
GOLD = ["#8a5a24", "#f6dc9a", "#c89048", "#fff0c4", "#a8742e"]


def yara_candy(c, x, y, s, t=0.0, glow_a=0.0, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if glow_a > 0:
        glow(c, R.RES.glows["rose"], 0, -260, 360, 0.6 * glow_a)
    oval(c, 0, 6, 140, 20, P("#000000", alpha=0.3))
    pink = ["#c2185a", "#ff5a9a", "#ff86b6", "#f04a8a", "#a8124c"]
    pos = [0, .25, .42, .7, 1]
    body = skia.Path()
    body.moveTo(-118, -330)
    body.lineTo(118, -330)
    body.lineTo(118, -110)
    body.cubicTo(118, -40, 100, 0, 70, 0)
    body.lineTo(-70, 0)
    body.cubicTo(-100, 0, -118, -40, -118, -110)
    body.close()
    c.drawPath(body, P("#ff5a9a", shader=lin(-118, 0, 118, 0, pink, pos)))
    c.drawRect(R.R(-96, -320, -84, -40), P("#ffffff", alpha=0.25))
    rrect(c, -120, -346, 120, -326, 4, P("#d8a050", shader=lin(-120, 0, 120, 0, GOLD)))  # aro dorado
    rrect(c, -98, -384, 98, -346, 4, P("#d8a050", shader=lin(-98, 0, 98, 0, GOLD)))       # cuello dorado
    # tapa rosada con aros dorados
    rrect(c, -120, -400, 120, -384, 4, P("#d8a050", shader=lin(-120, 0, 120, 0, GOLD)))
    rrect(c, -118, -520, 118, -400, 6, P("#ff5a9a", shader=lin(-118, 0, 118, 0, pink, pos)))
    c.drawRect(R.R(-96, -510, -84, -408), P("#ffffff", alpha=0.25))
    rrect(c, -120, -534, 120, -516, 4, P("#d8a050", shader=lin(-120, 0, 120, 0, GOLD)))
    # cinta dorada en X
    cy = -190
    for sgn in (1, -1):
        b = skia.Path()
        b.moveTo(-132, cy - sgn * 70)
        b.cubicTo(-60, cy - sgn * 40, 60, cy + sgn * 40, 132, cy + sgn * 70)
        b.lineTo(132, cy + sgn * 70 + 46)
        b.cubicTo(60, cy + sgn * 40 + 46, -60, cy - sgn * 40 + 46, -132, cy - sgn * 70 + 46)
        b.close()
        c.drawPath(b, P("#e0a860", shader=lin(0, cy - 80, 0, cy + 100, ["#fff0c4", "#d8a050", "#8a5a24", "#f6dc9a"])))
        c.drawPath(b, P("#6a4018", "stroke", 2, alpha=0.4))
    # medallón
    oval(c, 0, cy + 10, 56, 56, P("#d8a050", shader=lin(-56, cy - 46, 56, cy + 66, GOLD)))
    oval(c, 0, cy + 10, 46, 46, P("#ff6aa4", shader=lin(0, cy - 36, 0, cy + 56, ["#ff8ab8", "#e83c80"])))
    oval(c, 0, cy + 10, 40, 40, P("#f6dc9a", "stroke", 2))
    text_center(c, "Candy", 0, cy + 20, font(SERIF, 26), P("#f6dc9a"))
    spaced(c, "YARA", 0, -44, font(SERIF, 36), P("#e8b860"), 4)
    c.restore()
