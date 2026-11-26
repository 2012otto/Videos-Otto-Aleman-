"""Otto Aleman Perfumes — "El hermano más intenso del Mandarin Sky" (Mandarin Sky Elixir) + cómo se decanta
+ Black Friday (antes Q70, ahora Q60; llevá 6 y te regalamos 1).

Estilo de la referencia: fondos cálidos y oscuros con destellos, notas que se vuelven objetos grandes,
pedestales con precios; personaje A reaccionando; subtítulos arriba; cámara siempre en movimiento.
Uso:
  VIDEO_BUILD=$PWD/otto_serie/build_elixir VO_TRIM=0.15 VO_GAP=0.3 VO_TAIL=2.2 \
    python3 otto_serie/src/render_elixir.py --out otto_serie/build_elixir/video_mudo.mp4
"""
import math
import os
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "velto", "src"))
import render_decant_tarde as D  # noqa: E402
import render_mandarin as MS  # noqa: E402
from render_decant_tarde import (R, P, lin, rad, oval, rrect, clamp, lerp, smooth, ease_out, ease_in_out, back_out,  # noqa: E402
                                 prog, rng, glow, text_center, W, H, RECT, F, M, INK, GOLDD, OVER, sticker, hero,
                                 decant, Cam)

FEET = 1500


# ----------------------------------------------------------------------------
# fondos cálidos y oscuros con destellos (como la referencia)
# ----------------------------------------------------------------------------
MOODS = {"amber": ("#7a3a0a", "#1a0a04"), "orange": ("#c86a1a", "#2a1006"), "caramel": ("#6a3a16", "#140804"),
         "wood": ("#4a2a14", "#0e0604"), "red": ("#8a1020", "#1a0206"), "dark": ("#1a1a2a", "#040408"),
         "gold": ("#b8862a", "#2a1a06"), "black": ("#141414", "#000000")}


def warm_bg(c, t, mood="amber", seed=3):
    a, b = MOODS[mood]
    c.drawRect(RECT(-300, -300, W + 300, H + 300), P(a, shader=rad(540, 900, 1400, [a, b])))
    r = rng(seed)
    for i in range(36):  # bokeh y chispas doradas
        x = r.random() * 1300 - 100 + 30 * math.sin(t * 0.4 + i)
        y = (r.random() * 2200 - t * (10 + 20 * r.random())) % 2200 - 140
        rr = 6 + 40 * r.random() ** 2
        tw = 0.5 + 0.5 * math.sin(t * 2 + i)
        glow(c, R.RES.glow_warm, x, y, rr * 3, 0.25 * tw)
        oval(c, x, y, rr * 0.3, rr * 0.3, P("#ffe0a0", alpha=0.5 * tw))
    if mood == "red":  # cortinas de teatro
        for sd in (-1, 1):
            for i in range(5):
                x0 = 540 + sd * (380 + i * 40)
                c.drawRect(RECT(x0 - 22, -300, x0 + 22, H + 300), P("#6a0a16", shader=lin(x0 - 22, 0, x0 + 22, 0, ["#4a0610", "#a81828", "#4a0610"])))
        glow(c, R.RES.glow_warm, 540, 200, 700, 0.3)


def pedestal(c, x, y, w=260, h=520):
    c.drawRect(RECT(x - w / 2, y, x + w / 2, y + h), P("#d8d8e0", shader=lin(x - w / 2, 0, x + w / 2, 0, ["#9a9aa8", "#f4f4f8", "#b8b8c4", "#8a8a96"], [0, .35, .6, 1])))
    rrect(c, x - w / 2 - 20, y - 26, x + w / 2 + 20, y + 6, 8, P("#e8e8ee"))
    for i in range(1, 6):
        c.drawLine(x - w / 2 + i * w / 6, y + 10, x - w / 2 + i * w / 6, y + h, P("#ffffff", "stroke", 2, alpha=0.3))


# ----------------------------------------------------------------------------
# frascos
# ----------------------------------------------------------------------------


def elixir(c, x, y, s, t, cap=1.0, atom=1.0, glow_a=0.0, rot=0.0):
    """Odyssey Mandarin Sky Elixir: funda naranja de cuero con costuras y correa, tapa azul con asa.
    cap: 1 tapa puesta, 0 quitada. atom: 1 atomizador plateado, 0 solo el tubito blanco."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if glow_a > 0:
        glow(c, R.RES.glow_warm, 0, -220, 380, 0.7 * glow_a)
    oval(c, 0, 6, 170, 24, P("#000000", alpha=0.3))
    # cuello azul
    rrect(c, -100, -372, 100, -330, 18, P("#1f5ad8", shader=lin(-100, 0, 100, 0, ["#1440a8", "#2f6bf0", "#1440a8"])))
    if atom > 0.02:  # atomizador plateado
        ah = 70 * atom
        rrect(c, -44, -372 - ah, 44, -372, 10, P("#c8c8d0", shader=lin(-44, 0, 44, 0, ["#8a8a96", "#ffffff", "#a8a8b4", "#6a6a74"])))
        oval(c, 0, -372 - ah, 44, 8, P("#e8e8ee"))
    rrect(c, -16, -400, 16, -366, 6, P("#f4f4f4"))  # tubito blanco (queda al quitar el atomizador)
    rrect(c, -16, -400, 16, -366, 6, P("#9a9aa8", "stroke", 2))
    # funda de cuero naranja
    body = skia.Path()
    body.moveTo(-150, -340)
    body.quadTo(-158, -170, -150, -6)
    body.quadTo(0, 6, 150, -6)
    body.quadTo(158, -170, 150, -340)
    body.quadTo(0, -352, -150, -340)
    body.close()
    c.drawPath(body, P("#ff8a1a", shader=lin(-160, 0, 160, 0, ["#c85a0a", "#ff9a2a", "#ffb04a", "#e06a10"], [0, .3, .5, 1])))
    dash = P("#f4e8d8", "stroke", 3, alpha=0.8)
    dash.setPathEffect(skia.DashPathEffect.Make([12, 8], 0))
    inner = skia.Path()
    inner.moveTo(-138, -326)
    inner.quadTo(0, -338, 138, -326)
    inner.moveTo(-138, -22)
    inner.quadTo(0, -10, 138, -22)
    c.drawPath(inner, dash)
    c.drawRect(RECT(-156, -296, 156, -254), P("#f08a1a", shader=lin(0, -296, 0, -254, ["#ffa040", "#d86a10"])))  # correa
    rrect(c, -24, -304, 24, -246, 6, P("#e07a14"))
    for i, (txt, sz, col, yy) in enumerate((("ODYSSEY", 26, "#f4e8d8", -190), ("Mandarin Sky", 26, "#ffe0b0", -152),
                                             ("ELIXIR", 46, "#f4e8d8", -100), ("LIMITED EDITION", 18, "#f4e8d8", -46))):
        text_center(c, txt, 0, yy, F(R.RES.semi if i in (1, 3) else R.RES.bold, sz), P(col))
    rrect(c, -132, -320, -112, -30, 10, P("#ffffff", alpha=0.18))
    # tapa azul con asa
    if cap > 0.02:
        cy = -372 - (1 - cap) * 320
        c.save()
        c.translate((1 - cap) * 180, cy)
        c.rotate((1 - cap) * 25)
        rrect(c, -108, -60, 108, 0, 16, P("#1f5ad8", shader=lin(-108, 0, 108, 0, ["#1440a8", "#2f6bf0", "#1440a8"])))
        rrect(c, -82, -170, 82, -52, 18, P("#2a66e8", shader=lin(-82, 0, 82, 0, ["#1a4cc0", "#3a7af8", "#1a4cc0"])))
        handle = skia.Path()
        handle.moveTo(80, -150)
        handle.lineTo(150, -150)
        handle.lineTo(150, -40)
        handle.lineTo(100, -40)
        c.drawPath(handle, P("#2a66e8", "stroke", 18))
        c.restore()
    c.restore()


def scandal(c, x, y, s, t, glow_a=0.0):
    """Frasco tipo torso oscuro con corona dorada (referencia de comparación)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if glow_a > 0:
        glow(c, R.RES.glow_warm, 0, -200, 360, 0.5 * glow_a)
    body = skia.RRect.MakeRectXY(RECT(-130, -280, 130, 0), 40, 40)
    c.drawRRect(body, P("#1a1e2a", shader=lin(-130, 0, 130, 0, ["#0a0c14", "#2a3248", "#141824", "#05060a"], [0, .35, .6, 1])))
    c.drawRRect(body, P("#d8d8e0", "stroke", 10))
    rrect(c, -100, -190, 100, -130, 6, P("#c8a24a", shader=lin(0, -190, 0, -130, ["#f4d27a", "#a8782a"])))
    text_center(c, "SCANDAL", 0, -148, F(R.RES.xbold, 40), P("#1a1206"))
    rrect(c, -50, -320, 50, -280, 8, P("#d8b050"))
    crown = skia.Path()
    crown.moveTo(-80, -320)
    crown.lineTo(-95, -440)
    crown.lineTo(-45, -380)
    crown.lineTo(0, -470)
    crown.lineTo(45, -380)
    crown.lineTo(95, -440)
    crown.lineTo(80, -320)
    crown.close()
    c.drawPath(crown, P("#e0b84a", shader=lin(-95, 0, 95, 0, ["#a8782a", "#ffe08a", "#c8902a", "#ffe08a", "#a8782a"])))
    for px, py in ((-95, -440), (0, -470), (95, -440)):
        oval(c, px, py, 12, 12, P("#c8202a"))
    c.restore()


def price_tag(c, x, y, txt, k, col="#ffcf3a", rot=-10):
    if k <= 0:
        return
    s = back_out(clamp(k), 2)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    f = F(R.RES.xbold, 64)
    w = f.measureText(txt) + 70
    p = skia.Path()
    p.moveTo(-w / 2 - 30, 0)
    p.lineTo(-w / 2, -50)
    p.lineTo(w / 2, -50)
    p.lineTo(w / 2, 50)
    p.lineTo(-w / 2, 50)
    p.close()
    c.drawPath(p, P(col))
    oval(c, -w / 2 - 6, 0, 9, 9, P("#3a2a1a"))
    c.drawString(txt, -w / 2 + 30, 24, f, P("#3a1a06"))
    c.restore()


# ----------------------------------------------------------------------------
# notas animadas
# ----------------------------------------------------------------------------


def mandarin(c, x, y, r, burst=0.0, t=0.0):
    if burst < 0.05:
        oval(c, x, y, r, r, P("#ff8a1a", shader=rad(x - r * 0.3, y - r * 0.3, r * 1.4, ["#ffc070", "#ff7a0a", "#c84a00"])))
        leaf = skia.Path()
        leaf.moveTo(x, y - r)
        leaf.quadTo(x + r * 0.5, y - r * 1.5, x + r * 0.9, y - r * 1.1)
        leaf.quadTo(x + r * 0.4, y - r * 0.9, x, y - r)
        c.drawPath(leaf, P("#3a8a3a"))
        return
    for i in range(12):  # gajos que explotan
        a = i * math.pi / 6 + t * 0.6
        d = r * 2.4 * ease_out(burst)
        c.save()
        c.translate(x + math.cos(a) * d, y + math.sin(a) * d)
        c.rotate(math.degrees(a) + t * 80)
        wedge = skia.Path()
        wedge.moveTo(-r * 0.5, 0)
        wedge.quadTo(0, -r * 0.4, r * 0.5, 0)
        wedge.quadTo(0, r * 0.12, -r * 0.5, 0)
        c.drawPath(wedge, P("#ffa030"))
        c.drawPath(wedge, P("#ffe0a0", "stroke", 3, alpha=0.6))
        c.restore()
    glow(c, R.RES.glow_warm, x, y, r * 3 * (1 - burst * 0.5), 0.7 * (1 - burst))


def cardamom(c, x, y, s, rot):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    oval(c, 0, 0, 34, 20, P("#8ab85a", shader=rad(-10, -6, 40, ["#bfe08a", "#5a8a3a"])))
    for i in range(3):
        c.drawLine(-26 + i * 18, -14, -20 + i * 18, 14, P("#5a7a3a", "stroke", 2))
    c.restore()


def lavender(c, x, y, s, rot):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.drawLine(0, 80, 0, -80, P("#5a8a4a", "stroke", 5))
    for i in range(9):
        oval(c, (-1) ** i * 8, -80 + i * 12, 9, 7, P("#9a6ad8", shader=rad(0, -80 + i * 12, 12, ["#c8a0ff", "#7a4ab8"])))
    c.restore()


def tonka(c, x, y, s, rot):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    oval(c, 0, 0, 44, 16, P("#3a2014", shader=lin(0, -16, 0, 16, ["#6a4024", "#2a140a"])))
    for i in range(4):
        c.drawLine(-30 + i * 18, -10, -24 + i * 18, 10, P("#1a0a04", "stroke", 2))
    c.restore()


def incense(c, x, y, t, k):
    c.drawLine(x, y, x + 40, y - 300, P("#6a3a1a", "stroke", 8))
    oval(c, x + 40, y - 300, 8, 8, P("#ff6a1a"))
    for i in range(8):
        u = ((t * 0.3 + i / 8) % 1)
        px = x + 40 + math.sin(u * 9 + i) * 60 * u
        py = y - 300 - u * 500
        oval(c, px, py, 20 + 50 * u, 20 + 40 * u, P("#ffffff", alpha=0.25 * (1 - u) * k))


def patchouli(c, x, y, s, rot):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    lf = skia.Path()
    lf.moveTo(0, 60)
    lf.quadTo(-50, 0, 0, -70)
    lf.quadTo(50, 0, 0, 60)
    c.drawPath(lf, P("#3a7a3a", shader=lin(-40, 0, 40, 0, ["#2a5a2a", "#5a9a4a"])))
    c.drawLine(0, 60, 0, -60, P("#a8d080", "stroke", 2))
    c.restore()


def vanilla(c, x, y, s, rot):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.drawLine(-120, 0, 120, 10, P("#2a140a", "stroke", 14))
    for i in range(5):  # flor
        a = i * 2 * math.pi / 5
        oval(c, 150 + math.cos(a) * 26, -30 + math.sin(a) * 26, 22, 14, P("#fff4d0"))
    oval(c, 150, -30, 12, 12, P("#ffd04a"))
    c.restore()


def roots(c, x, y, t, k):
    for i in range(14):
        p = skia.Path()
        p.moveTo(x, y)
        ang = -1.2 + i * 0.18
        L = 260 * k
        p.cubicTo(x + math.cos(ang) * L * 0.3, y + 60, x + math.cos(ang) * L * 0.6, y + L * 0.5 + 10 * math.sin(t + i),
                  x + math.cos(ang) * L, y + L * 0.8)
        c.drawPath(p, P("#c8a26a", "stroke", 4, alpha=0.9))


def watch(c, x, y, r, hours):
    c.drawRect(RECT(x - 60, y - r - 120, x + 60, y + r + 120), P("#5a3a1a", shader=lin(x - 60, 0, x + 60, 0, ["#3a2210", "#7a4a22", "#3a2210"])))
    oval(c, x, y, r + 16, r + 16, P("#e0b84a"))
    D.clock(c, x, y, r, hours)


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def s0(c, k):  # el hermano más intenso
    lt, T = k.lt, k.w
    warm_bg(c, k.t, "amber")
    pedestal(c, 300, 1150, 240, 600)
    pedestal(c, 760, 1100, 260, 700)
    MS.msky(c, 300, 1124, 0.62, k.t, 0.7, "#ffb04a")
    ek = prog(lt, T(16) - 0.3, T(16) + 0.2)
    if ek > 0:
        elixir(c, 760, 1074, 0.75 * (0.6 + 0.4 * back_out(ek, 1.6)), k.t, glow_a=ek)
    ent = ease_out(prog(lt, 0, 0.5))
    hero(c, k, lerp(-300, 520, ent), FEET + 60, 0.62, [(0, "neutral"), (T(13), "espera"), (T(17), "enamorado")])
    sticker(c, "SU HERMANO MÁS INTENSO", 540, 1520, prog(lt, T(13), T(13) + 0.3), bg_col=GOLDD, size=48, rot=-3)


def s1(c, k):  # salida: mandarina/naranja + cardamomo y lavanda
    lt, T = k.lt, k.w
    warm_bg(c, k.t, "orange")
    burst = prog(lt, T(3) - 0.1, T(3) + 0.6)
    mandarin(c, 560, 900, 170, burst, k.t)
    if lt > T(8):
        mandarin(c, 560, 900, 120, 0.0, k.t)
    ck = prog(lt, T(13) - 0.1, T(13) + 0.4)
    for i in range(6):
        a = i * 1.05 + k.t * 0.8
        if ck > 0:
            cardamom(c, 560 + math.cos(a) * 320 * ck, 900 + math.sin(a) * 240 * ck, 1.6, math.degrees(a))
    lk = prog(lt, T(15) - 0.1, T(15) + 0.4)
    for i in range(5):
        a = i * 1.25 + 0.6 - k.t * 0.6
        if lk > 0:
            lavender(c, 560 + math.cos(a) * 400 * lk, 900 + math.sin(a) * 300 * lk, 1.4, math.degrees(a) + 90)
    hero(c, k, 880, FEET, 0.55, [(0, "neutral"), (T(3), "espera"), (T(13), "enamorado")])
    sticker(c, "MANDARINA · NARANJA", 540, 1340, prog(lt, T(5), T(5) + 0.3), bg_col="#ff8a1a", size=46, rot=-3)
    sticker(c, "CARDAMOMO · LAVANDA", 540, 1450, prog(lt, T(13), T(13) + 0.3), bg_col="#7a4ab8", size=44, rot=3)


def s2(c, k):  # corazón: caramelo y tonka + pachulí e incienso
    lt, T = k.lt, k.w
    warm_bg(c, k.t, "caramel")
    c.drawRect(RECT(-300, 1180, W + 300, 1240), P("#6a3a1a", shader=lin(0, 1180, 0, 1240, ["#8a5a2a", "#4a2410"])))
    for i in range(9):  # habas tonka en la mesa
        tonka(c, 160 + i * 95, 1170 - (i % 2) * 18, 1.3, (i * 23) % 40 - 20)
    ck = prog(lt, T(4) - 0.3, T(4) + 1.4)
    if ck > 0:  # caramelo cayendo en cámara lenta
        c.drawLine(560, -100, 560, lerp(-100, 1160, ck), P("#d8862a", "stroke", 34))
        oval(c, 560, 1160, 160 * ck, 30 * ck, P("#c8701a"))
    pk = prog(lt, T(12) - 0.1, T(12) + 0.4)
    for i in range(6):
        if pk > 0:
            a = i * 1.05 + k.t * 0.5
            patchouli(c, 560 + math.cos(a) * 360 * pk, 760 + math.sin(a) * 200 * pk, 1.3, math.degrees(a))
    ik = prog(lt, T(14) - 0.1, T(14) + 0.4)
    if ik > 0:
        incense(c, 850, 1170, k.t, ik)
    hero(c, k, 230, FEET, 0.55, [(0, "neutral"), (T(4), "enamorado")])
    sticker(c, "CARAMELO · HABA TONKA", 600, 1350, prog(lt, T(4), T(4) + 0.3), bg_col="#c8701a", size=44, rot=-3)
    sticker(c, "PACHULÍ · INCIENSO", 600, 1460, prog(lt, T(12), T(12) + 0.3), bg_col="#3a2014", size=44, rot=3)


def s3(c, k):  # fondo: vainilla y vetiver, horas en la piel
    lt, T = k.lt, k.w
    warm_bg(c, k.t, "wood")
    vk = prog(lt, T(4) - 0.1, T(4) + 0.4)
    if vk > 0:
        for i in range(3):
            vanilla(c, 300 + i * 120, 700 + i * 90, 1.2 * back_out(vk, 1.4), -20 + i * 15)
    rk = prog(lt, T(6) - 0.1, T(6) + 0.8)
    if rk > 0:
        roots(c, 760, 760, k.t, rk)
    hk = prog(lt, T(10) - 0.2, T(12))
    if hk > 0:
        watch(c, 540, 1180, 110, lerp(9, 18, ease_in_out(prog(lt, T(10), k.D))))
    hero(c, k, 880, FEET, 0.55, [(0, "neutral"), (T(7), "pulgar")])
    sticker(c, "VAINILLA · VETIVER", 540, 1450, prog(lt, T(4), T(4) + 0.3), bg_col="#5a3a1a", size=46, rot=-3)
    sticker(c, "HORAS EN TU PIEL", 300, 1000, prog(lt, T(11), T(11) + 0.3), bg_col=GOLDD, size=40, rot=4)


def s4(c, k):  # lo comparan con el Scandal… que cuesta mucho más
    lt, T = k.lt, k.w
    warm_bg(c, k.t, "red")
    pedestal(c, 330, 1080, 260, 700)
    pedestal(c, 760, 1080, 260, 700)
    sk = prog(lt, T(7) - 0.3, T(7) + 0.2)
    if sk > 0:
        scandal(c, 330, 1054, 0.8 * back_out(sk, 1.4), k.t, 0.8)
    elixir(c, 760, 1054, 0.66, k.t, glow_a=0.6)
    price_tag(c, 330, 1180, "$$$$", prog(lt, T(13) - 0.1, T(13) + 0.2), rot=-8)
    price_tag(c, 760, 1180, "$", prog(lt, T(14), T(14) + 0.3), col="#ff9a2a", rot=8)
    hero(c, k, 545, FEET + 120, 0.45, [(0, "neutral"), (T(13), "pulgar")])
    OVER.append(lambda cc: text_center(cc, "=", 545, 900, F(R.RES.xbold, 140), P("#ffffff", alpha=prog(lt, T(5), T(6)))))


def s5(c, k):  # más accesible: pedilo en decant en Otto Aleman Perfumes
    lt, T = k.lt, k.w
    warm_bg(c, k.t, "gold")
    lk = prog(lt, T(15) - 0.2, T(15) + 0.2)
    if lk > 0:
        img = M.logo()
        s = back_out(lk, 1.6)
        w = 300 * s
        h = w * img.height() / img.width()
        glow(c, R.RES.glow_warm, 540, 640, 360, 0.6 * lk)
        c.drawImageRect(img, RECT(540 - w / 2, 640 - h / 2, 540 + w / 2, 640 + h / 2), R.SAMP, skia.Paint())
        text_center(c, "OTTO ALEMAN PERFUMES", 540, 840, F(R.RES.xbold, 52), P("#ffffff", alpha=lk))
    elixir(c, 330, 1400, 0.62, k.t, glow_a=0.5)
    dk = prog(lt, T(13) - 0.3, T(13))
    if dk > 0:
        decant(c, 600, lerp(1900, 1220, back_out(dk, 1.3)), 380, -6, k.t, 0.9)
    hero(c, k, 880, FEET, 0.55, [(0, "piensa"), (T(10), "señala")], talk=True)
    sticker(c, "MÁS ACCESIBLE", 540, 1000, prog(lt, T(10), T(10) + 0.3), bg_col="#2fbf71", size=56, rot=-4)


def s6(c, k):  # quitamos el atomizador: queda el tubito
    lt, T = k.lt, k.w
    warm_bg(c, k.t, "amber")
    capk = 1 - prog(lt, T(6) - 0.4, T(7) + 0.2)
    atk = 1 - prog(lt, T(9), T(11) + 0.3)
    elixir(c, 540, 1500, 1.9, k.t, cap=capk, atom=atk)
    if 0 < atk < 1:  # el atomizador sube y se va
        c.save()
        c.translate(540 + (1 - atk) * 260, 1500 - 1.9 * 410 - (1 - atk) * 300)
        rrect(c, -80, -130, 80, 0, 16, P("#c8c8d0", shader=lin(-80, 0, 80, 0, ["#8a8a96", "#ffffff", "#a8a8b4", "#6a6a74"])))
        c.restore()
    tk = prog(lt, T(15) - 0.1, T(15) + 0.3)
    if tk > 0:
        sticker(c, "TUBITO (MACHO)", 820, 640, tk, bg_col=INK, size=44, rot=6)
        c.drawLine(700, 680, 580, 740, P("#ffffff", "stroke", 6, alpha=tk))
    hero(c, k, 170, FEET + 200, 0.5, [(0, "piensa"), (T(15), "señala")])
    qk = prog(lt, T(0), T(0) + 0.3)
    OVER.append(lambda cc: sticker(cc, "¿CÓMO SE DECANTA?", 540, 620, qk, bg_col=GOLDD, size=56, rot=-3))


def s7(c, k):  # el decant se coloca sobre el tubito y se presiona
    lt, T = k.lt, k.w
    warm_bg(c, k.t, "amber")
    tube_y = 1500 - 1.9 * 400
    elixir(c, 540, 1500, 1.9, k.t, cap=0.0, atom=0.0)
    seat = prog(lt, T(7) - 0.2, T(10))
    presses = prog(lt, T(13), k.D)
    n = int(presses * 24)
    bob = 30 * abs(math.sin(presses * 24 * math.pi)) if presses > 0 else 0
    dy = lerp(tube_y - 400, tube_y - 230, ease_in_out(seat)) + bob
    lvl = 0.08 + 0.8 * presses
    sys.modules["render_ep4"].decant_vec(c, 540, dy, 560, 0, k.t, lvl, 0.0)
    if prog(lt, T(4), T(5)) > 0 and seat < 0.4:  # entrada (hembra) abajo del decant
        c.save()
        c.translate(820, 980)
        s = back_out(prog(lt, T(4), T(5) + 0.2), 1.6)
        c.scale(s, s)
        oval(c, 0, 0, 130, 130, P("#ffffff"))
        oval(c, 0, 0, 130, 130, P(INK, "stroke", 6))
        oval(c, 0, 0, 90, 90, P("#14141a"))
        oval(c, 0, 0, 26, 26, P("#8a8a96"))
        oval(c, 0, 0, 12, 12, P("#000000"))
        c.restore()
        sticker(c, "ENTRADA (HEMBRA)", 740, 1170, prog(lt, T(4), T(5) + 0.2), bg_col=INK, size=40, rot=-4)
    if n > 0:
        OVER.append(lambda cc: sticker(cc, f"x{n}", 860, 700, 1.0, bg_col=GOLDD, size=70, rot=6))
        if bob > 20:
            for i in range(6):
                oval(c, 540 + (i - 2.5) * 30, tube_y - 40, 8, 8, P("#ffffff", alpha=0.5))
    hero(c, k, 170, FEET + 200, 0.5, [(0, "neutral"), (T(13), "pulgar")])


def s8(c, k):  # se llena: mismo perfume original
    lt, T = k.lt, k.w
    warm_bg(c, k.t, "gold")
    hero(c, k, 540, FEET, 0.92, [(0, "sostiene"), (T(4), "pulgar")], talk=True,
         hold_fn=lambda cc, x, y: decant(cc, x, y - 80, 220, -8, k.t, 0.9))
    R.RES.glow_gold = R.RES.glow_warm
    R.burst(c, 700, 800, lt - T(3), dur=1.0, n=40, radius=300, seed=5, intensity=0.8)
    sticker(c, "MISMO PERFUME ORIGINAL", 540, 1420, prog(lt, T(10), T(10) + 0.3), bg_col="#2fbf71", size=48, rot=-3)


def s9(c, k):  # Black Friday
    lt, T = k.lt, k.w
    warm_bg(c, k.t, "black")
    bk = prog(lt, T(9) - 0.2, T(9) + 0.2)
    intro = 1 - prog(lt, T(9) - 0.4, T(9))
    if intro > 0:  # "pedí el tuyo ya": el Elixir y el decant al centro
        c.saveLayerAlpha(None, int(255 * intro))
        elixir(c, 400, 1300, 0.9, k.t, glow_a=0.8)
        decant(c, 720, 1120, 420, 8, k.t, 1.0)
        c.restore()
        OVER.append(lambda cc: sticker(cc, "¡PEDÍ EL TUYO YA!", 540, 620, prog(lt, T(0), T(0) + 0.3) * intro, bg_col=GOLDD, size=60, rot=-3))

    def bf(cc):
        if bk <= 0:
            return
        s = back_out(bk, 1.8)
        cc.save()
        cc.translate(540, 620)
        cc.scale(s, s)
        cc.rotate(-4)
        rrect(cc, -400, -90, 400, 90, 20, P("#000000"))
        rrect(cc, -400, -90, 400, 90, 20, P("#e0203a", "stroke", 8))
        f = F(R.RES.xbold, 110)
        txt = "BLACK FRIDAY"
        w = f.measureText(txt)
        cc.drawString(txt, -w / 2, 38, f, P("#ffffff", shader=lin(0, -40, 0, 40, ["#ffffff", "#ffd04a"])))
        cc.restore()
    OVER.append(bf)
    ak = prog(lt, T(11) - 0.1, T(11) + 0.2)
    if ak > 0:
        price_tag(c, 300, 900, "Q70", ak, col="#d8d8e0", rot=-8)
        xk = prog(lt, T(13) + 0.1, T(14))
        if xk > 0:
            c.drawLine(200, 920, lerp(200, 420, xk), lerp(920, 870, xk), P("#e0203a", "stroke", 14))
        text_center(c, "ANTES", 300, 820, F(R.RES.bold, 40), P("#d8d8e0", alpha=ak))
    nk = prog(lt, T(14) - 0.1, T(16) + 0.2)
    if nk > 0:
        price_tag(c, 760, 920, "Q60", nk, col="#ffcf3a", rot=6)
        text_center(c, "AHORA", 760, 820, F(R.RES.xbold, 48), P("#ffcf3a", alpha=nk))
        glow(c, R.RES.glow_warm, 760, 920, 260, 0.5 * nk)
    gk = prog(lt, T(17) - 0.1, T(20))
    for i in range(6):
        if gk > i / 7:
            decant(c, 170 + i * 120, 1230, 220, (-6, 0, 6)[i % 3], k.t, 0.0)
    fk = prog(lt, T(22) - 0.2, T(24))
    if fk > 0:
        decant(c, 920, lerp(1900, 1230, back_out(fk, 1.3)), 260, 10, k.t, 1.0)
        c.drawString("+", 845, 1250, F(R.RES.xbold, 90), P("#2fbf71", alpha=fk))
        OVER.append(lambda cc: sticker(cc, "LLEVÁ 6 Y TE REGALAMOS 1", 540, 1430, fk, bg_col="#2fbf71", size=44, rot=-3))
        OVER.append(lambda cc: sticker(cc, "¡GRATIS!", 540, 1540, prog(lt, T(24) - 0.1, T(24) + 0.2), bg_col="#e0203a", size=70, rot=3))
    hero(c, k, 920, FEET + 220, 0.38, [(0, "señala"), (T(24) - 0.1, "celebra")], talk=True)
    if lt > T(24):
        r = rng(3)
        for i in range(60):
            x = r.random() * W
            y = -50 + ((lt - T(24)) * (400 + 400 * r.random()) + r.random() * 200)
            if y > H:
                continue
            c.save()
            c.translate(x, y)
            c.rotate(k.t * 200 + i * 30)
            c.drawRect(RECT(-11, -6, 11, 6), P(["#d6a24a", "#e0203a", "#2fbf71", "#ffffff"][i % 4]))
            c.restore()


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]
CAMS = [
    Cam(1.12, 1.0, punches=(5, 16, 19), focus=((16, 99, 1.3, 700, 900, 0),)),
    Cam(1.0, 1.1, punches=(3, 5, 8, 13, 15), focus=((1, 6, 1.35, 560, 900, 0),)),
    Cam(1.05, 1.15, punches=(4, 7, 12, 14), focus=((15, 99, 1.2, 700, 900, 0),)),
    Cam(1.0, 1.12, punches=(4, 6, 12), focus=((10, 99, 1.35, 540, 1100, 1),)),
    Cam(1.0, 1.08, punches=(7, 13, 14), focus=((12, 99, 1.25, 545, 1100, 0),)),
    Cam(1.1, 1.0, punches=(10, 13, 15)),
    Cam(1.0, 1.0, drift=15, punches=(9, 15), focus=((6, 99, 1.45, 540, 820, 0),)),
    Cam(1.12, 1.18, drift=10, punches=(1, 7, 14), focus=((0, 99, 1.15, 540, 800, 0),)),
    Cam(1.0, 1.15, punches=(3, 10)),
    Cam(1.0, 1.05, punches=(9, 13, 16, 22, 24), rot=1.0),
]


def render_frame(c, t, vo, phr, total):
    MS.VO = vo
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(R.hexc("#000000"))
    k = R.Ctx(vo, si, t)
    lt = k.lt
    OVER.clear()
    z, fx, fy, rot = CAMS[si].get(k)
    if 0 < si and lt < 0.2:
        z *= 1 + 0.08 * (1 - ease_out(lt / 0.2))
    c.save()
    c.translate(540, 960)
    c.rotate(rot)
    c.scale(z, z)
    c.translate(-fx, -fy)
    SCENES[si](c, k)
    c.restore()
    for fn in OVER:
        fn(c)
    R.vignette(c, 0.35)
    fade = clamp(t / 0.2) * clamp((total - t) / 0.4)
    if fade < 1:
        c.drawRect(RECT(0, 0, W, H), P("#000000", alpha=1 - fade))
    R.draw_subs(c, t, phr)
    draw_watermark(c)


def draw_watermark(c):
    f = F(R.RES.semi, 28)
    txt = "@ottoaleman.perfumesgt"
    w = f.measureText(txt)
    c.drawString(txt, 540 - w / 2, 1770, f, P("#ffffff", alpha=0.7))


def install():
    import render_sueno as S
    R.SCENES = SCENES
    R.render_frame = render_frame
    R.draw_subs = S.draw_subs
    R.draw_watermark = draw_watermark


if __name__ == "__main__":
    install()
    R.main()
