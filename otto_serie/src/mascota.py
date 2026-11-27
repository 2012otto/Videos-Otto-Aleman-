"""Personaje de la serie Otto Aleman Perfumes: joven en traje (estilo "bitmoji", diseño original).

Esqueleto articulado con extremidades de verdad: brazo, codo, antebrazo con puño de camisa, muñeca y mano
(5 tipos); muslo, rodilla, pierna y zapato. Cabeza con inclinación y giro, cejas, 7 tipos de ojos,
6 bocas que además se mueven al hablar. Logo "OA" pequeño en el bolsillo del pecho.
Origen = entre los pies; mide ~1000 px a escala 1.

    from mascota import draw, POSES, STYLES
    draw(c, x, y, s, t, POSES["saludo"], style=STYLES["A"], talk=0.0)
"""
import math
import os

import numpy as np
import skia
from PIL import Image

import render as R
from render import P, lin, rad, oval, rrect, clamp, lerp

OUT = "#2a1a1a"  # contorno suave
_LOGO = None


def logo():
    global _LOGO
    if _LOGO is None:
        arr = np.asarray(Image.open(os.path.join(R.A, "logo_gold.png")).convert("RGBA")).copy()
        _LOGO = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType,
                                     alphaType=skia.kUnpremul_AlphaType).withDefaultMipmaps()
    return _LOGO


def mix(a, b, t):
    c = R.mix_col(a, b, clamp(t))
    return "#%02x%02x%02x" % (skia.ColorGetR(c), skia.ColorGetG(c), skia.ColorGetB(c))


STYLES = {
    # traje negro, camisa blanca, corbata delgada dorada, copete
    "A": dict(jacket="#17171d", shirt="#ffffff", tie="#d6a24a", pants="#17171d", shoes="#2a1a12",
              hair="#2a1a12", hair_style="copete", beard=0.0, skin=("#f1c3a0", "#d99a74")),
    # traje crema, camiseta negra, sin corbata, pelo corto degradado, barba corta
    "B": dict(jacket="#e9dcc4", shirt="#16161c", tie=None, pants="#e9dcc4", shoes="#f4f1ea",
              hair="#1a120a", hair_style="fade", beard=0.45, skin=("#d9a07a", "#b97a56")),
    # traje azul marino, camisa blanca sin corbata, pelo ondulado
    "C": dict(jacket="#1c2a4a", shirt="#ffffff", tie=None, pants="#1c2a4a", shoes="#3a2214",
              hair="#3a2418", hair_style="ondulado", beard=0.0, skin=("#f4cdb0", "#dba684")),
    # traje negro, camisa negra, corbata dorada, barba
    # Chepe (el cliente): camiseta naranja, jeans, tenis, pelo rizado, piel morena, sin barba
    "CHEPE": dict(jacket="#ff8a1a", shirt="#ff8a1a", tie=None, pants="#2f5aa8", shoes="#f4f1ea", print="#ffd04a",
                  hair="#1a0e08", hair_style="rizado", beard=0.0, skin=("#c98a5e", "#a86a40"), casual=True),
    # gente normal (ropa casual) para los videos
    "P1": dict(jacket="#f4f4f4", shirt="#f4f4f4", tie=None, pants="#3a5a9a", shoes="#2a2a2a", print=None,
               hair="#3a2414", hair_style="fade", beard=0.0, skin=("#f4cdb0", "#dba684"), casual=True),
    "P2": dict(jacket="#2fbf71", shirt="#2fbf71", tie=None, pants="#2a2a34", shoes="#f4f1ea", print=None,
               hair="#120a06", hair_style="ondulado", beard=0.3, skin=("#c98a5e", "#a86a40"), casual=True),
    "P3": dict(jacket="#e0405a", shirt="#e0405a", tie=None, pants="#d8c8a8", shoes="#ffffff", print="#ffffff",
               hair="#5a3a1a", hair_style="rizado", beard=0.0, skin=("#e8b78c", "#c8946a"), casual=True),
    "P4": dict(jacket="#5a7ad8", shirt="#5a7ad8", tie=None, pants="#1a1a22", shoes="#f4f1ea", print=None,
               hair="#1a0e08", hair_style="fade", beard=0.5, skin=("#8a5a3a", "#6a4024"), casual=True),
    "D": dict(jacket="#101014", shirt="#2c2c36", tie="#e0b050", pants="#101014", shoes="#101014",
              hair="#120a06", hair_style="copete", beard=0.55, skin=("#c98a62", "#a86a44")),
}

BASE = dict(lean=0.0, bob=0.0, head_tilt=0.0, head_turn=0.0,
            arm_l=(8, 12, "open"), arm_r=(8, 12, "open"),   # (hombro°, codo°, mano); 0 = colgando
            leg_l=(0, 0), leg_r=(0, 0),                      # (cadera°, rodilla°)
            eyes="open", brows=0.0, brow_up=0.0, mouth="smile", blush=0.0, sweat=0.0, look=(0.0, 0.0))


def pose(**kw):
    p = dict(BASE)
    p.update(kw)
    return p


POSES = {
    "neutral": pose(),
    "saludo": pose(arm_r=(140, 35, "open"), mouth="open", head_tilt=4),
    "espera": pose(arm_l=(150, 25, "open"), arm_r=(150, 25, "open"), mouth="O", eyes="wide", brow_up=1.0),
    "señala": pose(arm_r=(95, -5, "point"), mouth="smile", head_turn=0.3, look=(0.6, 0)),
    "pulgar": pose(arm_r=(55, 95, "thumb"), mouth="open", eyes="happy", blush=0.5),
    "encoge": pose(arm_l=(55, -80, "open"), arm_r=(55, -80, "open"), mouth="wavy", brows=-0.5, head_tilt=-6),
    "piensa": pose(arm_r=(20, 150, "fist"), arm_l=(30, 95, "open"), mouth="flat", look=(0.5, -0.6), head_tilt=5),
    "enamorado": pose(arm_l=(135, 25, "open"), arm_r=(135, 25, "open"), eyes="hearts", mouth="open", blush=1.0),
    "mareado": pose(lean=-6, eyes="spiral", mouth="wavy", sweat=1.0, arm_l=(30, 30, "open"), arm_r=(45, 60, "open")),
    "asco": pose(eyes="squint", mouth="yuck", brows=0.7, arm_r=(65, 115, "open"), head_tilt=-8, lean=-4),
    "triste": pose(eyes="teary", mouth="sad", brows=-0.9, head_tilt=-6, arm_l=(4, 6, "open"), arm_r=(4, 6, "open")),
    "sostiene": pose(arm_r=(18, 125, "hold"), mouth="smile", look=(0.3, 0.2)),
    "celebra": pose(arm_l=(160, 15, "fist"), arm_r=(160, 15, "fist"), eyes="happy", mouth="open", blush=0.6),
}


def blend(a, b, u):
    """Interpola dos poses; los valores discretos cambian a la mitad."""
    out = {}
    for k in a:
        va, vb = a[k], b.get(k, a[k])
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            out[k] = lerp(va, vb, u)
        elif isinstance(va, tuple) and isinstance(vb, tuple) and len(va) == len(vb):
            out[k] = tuple(lerp(x, y, u) if isinstance(x, (int, float)) else (x if u < 0.5 else y) for x, y in zip(va, vb))
        else:
            out[k] = va if u < 0.5 else vb
    return out


def walk(p, t, speed=1.0, amp=1.0):
    q = dict(p)
    ph = t * 6.0 * speed
    q["leg_l"] = (22 * math.sin(ph) * amp, max(0, -30 * math.sin(ph)) * amp)
    q["leg_r"] = (-22 * math.sin(ph) * amp, max(0, 30 * math.sin(ph)) * amp)
    q["bob"] = abs(math.sin(ph)) * 10 * amp
    if p["arm_l"][0] < 40:
        q["arm_l"] = (8 - 20 * math.sin(ph) * amp, 18, p["arm_l"][2])
    if p["arm_r"][0] < 40:
        q["arm_r"] = (8 + 20 * math.sin(ph) * amp, 18, p["arm_r"][2])
    return q


# ----------------------------------------------------------------------------
# geometría
# ----------------------------------------------------------------------------


def seg(c, a, b, w0, w1, col, outline=True, shade=True):
    """Segmento que se adelgaza de a a b, con sombreado y contorno."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    p = skia.Path()
    p.moveTo(a[0] + nx * w0 / 2, a[1] + ny * w0 / 2)
    p.lineTo(b[0] + nx * w1 / 2, b[1] + ny * w1 / 2)
    p.lineTo(b[0] - nx * w1 / 2, b[1] - ny * w1 / 2)
    p.lineTo(a[0] - nx * w0 / 2, a[1] - ny * w0 / 2)
    p.close()
    sh = lin(a[0] + nx * w0 / 2, a[1] + ny * w0 / 2, a[0] - nx * w0 / 2, a[1] - ny * w0 / 2,
             [mix(col, "#ffffff", 0.12), col, mix(col, "#000000", 0.28)]) if shade else None
    c.drawPath(p, P(col, shader=sh))
    if outline:
        c.drawPath(p, P(OUT, "stroke", 3, alpha=0.5))
    return p


def limb_path(c, pts, w, col, outline=True):
    """Extremidad continua (con codo/rodilla redondeados) con volumen: base oscura + luz."""
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if outline:
        c.drawPath(p, P(OUT, "stroke", w + 6, cap=skia.Paint.kRound_Cap, alpha=0.55))
    c.drawPath(p, P(mix(col, "#000000", 0.25), "stroke", w, cap=skia.Paint.kRound_Cap))
    c.save()
    c.translate(-w * 0.12, -w * 0.05)
    c.drawPath(p, P(col, "stroke", w * 0.72, cap=skia.Paint.kRound_Cap))
    c.restore()
    c.save()
    c.translate(-w * 0.22, -w * 0.08)
    c.drawPath(p, P(mix(col, "#ffffff", 0.14), "stroke", w * 0.22, cap=skia.Paint.kRound_Cap, alpha=0.8))
    c.restore()


def joint(a1, a2, l1, l2, x0, y0, side):
    r1 = math.radians(a1) * side
    x1, y1 = x0 + math.sin(r1) * l1, y0 + math.cos(r1) * l1
    r2 = r1 + math.radians(a2) * side
    x2, y2 = x1 + math.sin(r2) * l2, y1 + math.cos(r2) * l2
    return (x1, y1), (x2, y2), math.degrees(r2)


def hand(c, x, y, ang, kind, side, skin):
    c.save()
    c.translate(x, y)
    c.rotate(-ang)
    sk = P(skin[0], shader=lin(-34, 0, 34, 0, [skin[0], skin[1]]))
    ol = P(OUT, "stroke", 3, alpha=0.5)
    if kind == "fist":
        rrect(c, -32, 4, 32, 60, 22, sk)
        rrect(c, -32, 4, 32, 60, 22, ol)
        for i in range(3):
            c.drawLine(-14 + i * 14, 40, -14 + i * 14, 56, P(skin[1], "stroke", 3))
    elif kind == "point":
        rrect(c, -9, 40, 9, 110, 9, sk)
        rrect(c, -9, 40, 9, 110, 9, ol)
        rrect(c, -30, 4, 30, 56, 20, sk)
        rrect(c, -30, 4, 30, 56, 20, ol)
    elif kind == "thumb":
        rrect(c, -30, 4, 30, 60, 20, sk)
        rrect(c, -30, 4, 30, 60, 20, ol)
        rrect(c, side * 22 - 10, -48, side * 22 + 10, 20, 10, sk)
        rrect(c, side * 22 - 10, -48, side * 22 + 10, 20, 10, ol)
    elif kind == "hold":
        rrect(c, -32, 4, 32, 58, 20, sk)
        rrect(c, -32, 4, 32, 58, 20, ol)
        rrect(c, -30, 26, 30, 46, 10, P(skin[1]))
    else:  # abierta, con dedos
        for i in range(4):
            a = math.radians(-24 + i * 16)
            fx, fy = math.sin(a) * 26, 46
            c.drawLine(fx, fy, fx + math.sin(a) * 30, fy + math.cos(a) * 34, P(skin[0], "stroke", 15))
        c.drawLine(side * 26, 24, side * 54, 8, P(skin[0], "stroke", 15))
        rrect(c, -32, 4, 32, 60, 22, sk)
        rrect(c, -32, 4, 32, 60, 22, ol)
    c.restore()


def arm(c, sh, a1, a2, kind, side, st):
    """Brazo (manga del saco) → codo → antebrazo → puño de camisa → mano."""
    el, wr, ang = joint(a1, a2, 165, 155, sh[0], sh[1], side)
    r = math.radians(ang)
    ux, uy = math.sin(r), math.cos(r)
    cuff_a = (wr[0] - ux * 34, wr[1] - uy * 34)
    cuff_b = (wr[0] - ux * 12, wr[1] - uy * 12)
    if st.get("casual"):  # manga corta de camiseta + brazo de piel
        mid = (sh[0] + (el[0] - sh[0]) * 0.55, sh[1] + (el[1] - sh[1]) * 0.55)
        limb_path(c, [mid, el, cuff_b], 52, st["skin"][0])
        limb_path(c, [sh, mid], 78, st["jacket"])
    else:
        limb_path(c, [sh, el, cuff_a], 72, st["jacket"])
        limb_path(c, [cuff_a, cuff_b], 46, "#ffffff")
    hand(c, wr[0] - ux * 4, wr[1] - uy * 4, ang, kind, side, st["skin"])
    return wr


def leg(c, hip, a1, a2, side, st):
    kn, an, ang = joint(a1 * side, -a2 * side, 205, 195, hip[0], hip[1], side)
    limb_path(c, [hip, kn, (an[0], an[1] - 10)], 86, st["pants"])
    c.save()
    c.translate(*an)
    c.rotate(-ang * 0.3)
    shoe = skia.Path()
    shoe.moveTo(-40 + side * 8, -6)
    shoe.quadTo(-44 + side * 8, 30, -30 + side * 8, 32)
    shoe.lineTo(60 + side * 8, 32)
    shoe.quadTo(70 + side * 8, 10, 40 + side * 8, -4)
    shoe.close()
    c.drawPath(shoe, P(st["shoes"], shader=lin(0, -6, 0, 32, [mix(st["shoes"], "#ffffff", 0.25), st["shoes"]])))
    c.drawPath(shoe, P(OUT, "stroke", 3, alpha=0.5))
    c.drawLine(-36 + side * 8, 30, 58 + side * 8, 30, P(mix(st["shoes"], "#000000", 0.4), "stroke", 6))
    c.restore()


# ----------------------------------------------------------------------------
# cara
# ----------------------------------------------------------------------------


def eye(c, x, y, kind, look, t, side):
    lx, ly = look[0] * 9, look[1] * 7
    if kind in ("happy", "closed"):
        p = skia.Path()
        if kind == "happy":
            p.moveTo(x - 22, y + 6)
            p.quadTo(x, y - 22, x + 22, y + 6)
        else:
            p.moveTo(x - 22, y)
            p.quadTo(x, y + 12, x + 22, y)
        c.drawPath(p, P("#1a1010", "stroke", 7))
        return
    if kind == "hearts":
        s = 1 + 0.12 * math.sin(t * 10)
        hp = skia.Path()
        hp.moveTo(x, y + 20 * s)
        hp.cubicTo(x - 34 * s, y - 2 * s, x - 18 * s, y - 30 * s, x, y - 12 * s)
        hp.cubicTo(x + 18 * s, y - 30 * s, x + 34 * s, y - 2 * s, x, y + 20 * s)
        c.drawPath(hp, P("#ff3d6a"))
        return
    w, h = (30, 34) if kind == "wide" else (26, 30)
    if kind == "squint":
        h = 12
    oval(c, x, y, w, h, P("#ffffff"))
    oval(c, x, y, w, h, P("#1a1010", "stroke", 3))
    if kind == "spiral":
        p = skia.Path()
        for i in range(40):
            a = i * 0.45 + t * 8 * side
            r = i * 0.6
            (p.moveTo if i == 0 else p.lineTo)(x + math.cos(a) * r, y + math.sin(a) * r)
        c.drawPath(p, P("#4a3a2a", "stroke", 3))
        return
    pr = 15 if kind != "squint" else 9
    oval(c, x + lx, y + ly + 2, pr, pr, P("#5a3a20"))
    oval(c, x + lx, y + ly + 2, pr * 0.55, pr * 0.55, P("#0a0604"))
    oval(c, x + lx + 5, y + ly - 4, 5, 5, P("#ffffff"))
    if kind == "teary":
        oval(c, x, y + h + 4, 22, 8, P("#7fd6ff", alpha=0.8))
        drop = (t * 0.8 + side * 0.3) % 1
        oval(c, x + side * 10, y + h + 10 + drop * 80, 6, 9, P("#7fd6ff", alpha=1 - drop))


def mouth(c, kind, talk, t):
    o = talk
    if kind == "smile" and o < 0.2:
        p = skia.Path()
        p.moveTo(-40, 58)
        p.quadTo(0, 92, 40, 58)
        c.drawPath(p, P("#5a1a1a", "stroke", 7))
        return
    if kind in ("open", "smile"):
        h = 26 + 24 * o if kind == "open" else 14 + 26 * o
        p = skia.Path()
        p.moveTo(-42, 56)
        p.quadTo(0, 60, 42, 56)
        p.quadTo(30, 56 + h * 1.6, 0, 56 + h * 1.7)
        p.quadTo(-30, 56 + h * 1.6, -42, 56)
        p.close()
        c.drawPath(p, P("#6a1a20"))
        c.drawRect(R.R(-30, 57, 30, 66), P("#ffffff"))
        oval(c, 0, 56 + h * 1.4, 18, 8, P("#ff7a8a"))
        return
    if kind == "O":
        oval(c, 0, 76, 20 + 6 * o, 26 + 10 * o, P("#6a1a20"))
        return
    if kind == "sad":
        p = skia.Path()
        p.moveTo(-34, 84)
        p.quadTo(0, 56 - 8 * o, 34, 84)
        c.drawPath(p, P("#5a1a1a", "stroke", 7))
        return
    if kind == "wavy":
        p = skia.Path()
        p.moveTo(-40, 72)
        for i in range(4):
            p.quadTo(-30 + i * 20, 60 + 24 * (i % 2), -20 + i * 20, 72)
        c.drawPath(p, P("#5a1a1a", "stroke", 6))
        return
    if kind == "yuck":
        p = skia.Path()
        p.moveTo(-40, 74)
        p.quadTo(-10, 60, 10, 76)
        p.quadTo(26, 88, 40, 70)
        c.drawPath(p, P("#5a1a1a", "stroke", 7))
        oval(c, 14, 84, 12, 12 + 6 * math.sin(t * 6), P("#ff7a8a"))
        return
    c.drawLine(-30, 72 - 4 * o, 30, 72 - 4 * o, P("#5a1a1a", "stroke", 7))


def hair(c, st):
    hs, col = st["hair_style"], st["hair"]
    hp = skia.Path()
    if hs == "fade":
        hp.moveTo(-132, -30)
        hp.cubicTo(-150, -150, -80, -190, 0, -188)
        hp.cubicTo(80, -190, 150, -150, 132, -30)
        hp.quadTo(124, -96, 80, -104)
        hp.quadTo(0, -96, -80, -104)
        hp.quadTo(-124, -96, -132, -30)
        hp.close()
        c.drawPath(hp, P(col, shader=lin(0, -175, 0, -20, [mix(col, "#ffffff", 0.12), col])))
    elif hs == "rizado":
        r = [(-110, -110, 44), (-60, -160, 48), (0, -175, 50), (60, -160, 48), (110, -110, 44), (-130, -50, 34), (130, -50, 34),
             (-30, -130, 40), (35, -130, 40)]
        for (x, y, rr) in r:
            oval(c, x, y, rr, rr, P(col, shader=rad(x - rr * 0.3, y - rr * 0.3, rr * 1.3, [mix(col, "#ffffff", 0.18), col])))
        return
    elif hs == "ondulado":
        hp.moveTo(-134, -10)
        for i in range(7):
            x0 = -134 + i * 38
            hp.quadTo(x0 + 19, -196, x0 + 38, -184 + 4 * (i % 2))
        hp.lineTo(134, -10)
        hp.quadTo(110, -100, 0, -110)
        hp.quadTo(-110, -100, -134, -10)
        hp.close()
        c.drawPath(hp, P(col, shader=lin(0, -210, 0, -10, [mix(col, "#ffffff", 0.18), col])))
    else:  # copete
        hp.moveTo(-134, -10)
        hp.cubicTo(-150, -150, -60, -210, 20, -200)
        hp.cubicTo(100, -215, 160, -150, 134, -10)
        hp.quadTo(120, -90, 70, -110)
        hp.quadTo(-10, -80, -60, -120)
        hp.quadTo(-110, -100, -134, -10)
        hp.close()
        c.drawPath(hp, P(col, shader=lin(0, -215, 0, -10, [mix(col, "#ffffff", 0.18), col])))
        c.drawLine(-40, -170, 40, -185, P(mix(col, "#ffffff", 0.35), "stroke", 6, alpha=0.6))
    c.drawPath(hp, P(OUT, "stroke", 3, alpha=0.4))


def head(c, x, y, p, t, talk, st):
    skin = st["skin"]
    c.save()
    c.translate(x, y)
    c.rotate(p["head_tilt"])
    turn = p["head_turn"]
    for sd in (-1, 1):
        oval(c, sd * 124 - turn * 30, 10, 22 * (1 - 0.3 * turn * sd), 34, P(skin[1]))
    face = skia.Path()
    face.moveTo(0, -150)
    face.cubicTo(80, -150, 130, -90, 128, -10)
    face.cubicTo(126, 80, 80, 145, 0, 150)
    face.cubicTo(-80, 145, -126, 80, -128, -10)
    face.cubicTo(-130, -90, -80, -150, 0, -150)
    face.close()
    c.drawPath(face, P(skin[0], shader=rad(-30 + turn * 30, -40, 260, [mix(skin[0], "#ffffff", 0.15), skin[0], skin[1]], [0, .6, 1])))
    c.drawPath(face, P(OUT, "stroke", 3, alpha=0.4))
    fx = turn * 34
    if st["beard"] > 0:
        c.save()
        c.clipPath(face, True)
        bd = skia.Path()
        bd.moveTo(-130, 10)
        bd.cubicTo(-110, 160, 110, 160, 130, 10)
        bd.lineTo(100, 40)
        bd.quadTo(0, 110, -100, 40)
        bd.close()
        c.drawPath(bd, P(st["hair"], alpha=st["beard"]))
        c.restore()
    if p["blush"] > 0:
        for sd in (-1, 1):
            oval(c, fx + sd * 70, 40, 26, 14, P("#ff7a8a", alpha=0.45 * p["blush"]))
    for sd in (-1, 1):
        eye(c, fx + sd * 50, -10, p["eyes"], p["look"], t, sd)
        b, up = p["brows"], p["brow_up"]
        base = -58 - 14 * up
        bp = skia.Path()
        bp.moveTo(fx + sd * 24, base + b * 10)          # extremo interior (b>0 enojo, b<0 preocupación)
        bp.quadTo(fx + sd * 50, base - 12, fx + sd * 76, base - b * 6)
        c.drawPath(bp, P(st["hair"], "stroke", 10))
    nose = skia.Path()
    nose.moveTo(fx + 2, 6)
    nose.quadTo(fx - 12, 34, fx + 4, 38)
    c.drawPath(nose, P(skin[1], "stroke", 5))
    c.save()
    c.translate(fx, 0)
    mouth(c, p["mouth"], talk, t)
    c.restore()
    c.save()
    c.translate(turn * 12, 0)
    hair(c, st)
    c.restore()
    if p["sweat"] > 0:
        oval(c, 120, -60 + 10 * math.sin(t * 4), 10, 16, P("#7fd6ff", alpha=p["sweat"]))
    c.restore()


# ----------------------------------------------------------------------------
# cuerpo completo
# ----------------------------------------------------------------------------


def torso_casual(c, st):
    J = st["jacket"]
    tee = skia.Path()
    tee.moveTo(-60, -716)
    tee.lineTo(-150, -706)
    tee.quadTo(-192, -690, -182, -610)
    tee.lineTo(-150, -380)
    tee.quadTo(0, -362, 150, -380)
    tee.lineTo(182, -610)
    tee.quadTo(192, -690, 150, -706)
    tee.lineTo(60, -716)
    tee.quadTo(0, -660, -60, -716)
    tee.close()
    c.drawPath(tee, P(J, shader=lin(-192, 0, 192, 0, [mix(J, "#000000", 0.25), mix(J, "#ffffff", 0.1), J, mix(J, "#000000", 0.3)], [0, .35, .6, 1])))
    c.drawPath(tee, P(OUT, "stroke", 3, alpha=0.5))
    neck = skia.Path()
    neck.moveTo(-60, -716)
    neck.quadTo(0, -660, 60, -716)
    c.drawPath(neck, P(mix(J, "#000000", 0.35), "stroke", 10))
    if st.get("print"):  # estampado sencillo (franja)
        oval(c, 0, -560, 60, 60, P(st["print"], alpha=0.9))
        c.drawPath(skia.Path().addCircle(0, -560, 40), P("#ffffff", "stroke", 6, alpha=0.8))


def torso(c, st):
    if st.get("casual"):
        return torso_casual(c, st)
    J, S = st["jacket"], st["shirt"]
    shirt = skia.Path()
    shirt.moveTo(-64, -714)
    shirt.lineTo(64, -714)
    shirt.lineTo(40, -430)
    shirt.lineTo(-40, -430)
    shirt.close()
    c.drawPath(shirt, P(S))
    col = skia.Path()  # cuello de la camisa
    for sd in (-1, 1):
        col.moveTo(0, -690)
        col.lineTo(sd * 46, -720)
        col.lineTo(sd * 40, -676)
        col.close()
    c.drawPath(col, P(mix(S, "#000000", 0.08)))
    if st["tie"]:
        t1 = skia.Path()
        t1.moveTo(-14, -684)
        t1.lineTo(14, -684)
        t1.lineTo(20, -500)
        t1.lineTo(0, -470)
        t1.lineTo(-20, -500)
        t1.close()
        c.drawPath(t1, P(st["tie"], shader=lin(-20, 0, 20, 0, [mix(st["tie"], "#ffffff", 0.2), st["tie"], mix(st["tie"], "#000000", 0.25)])))
        rrect(c, -16, -704, 16, -680, 6, P(mix(st["tie"], "#000000", 0.15)))
    for sd in (-1, 1):  # saco
        jk = skia.Path()
        jk.moveTo(sd * 62, -718)
        jk.lineTo(sd * 150, -706)
        jk.quadTo(sd * 192, -690, sd * 182, -610)
        jk.lineTo(sd * 150, -380)
        jk.quadTo(sd * 70, -362, sd * 6, -380)
        jk.lineTo(sd * 6, -470)
        jk.lineTo(sd * 52, -600)
        jk.close()
        c.drawPath(jk, P(J, shader=lin(sd * 6, 0, sd * 192, 0, [mix(J, "#ffffff", 0.08), J, mix(J, "#000000", 0.3)])))
        c.drawPath(jk, P(OUT, "stroke", 3, alpha=0.5))
        lp = skia.Path()  # solapa
        lp.moveTo(sd * 62, -718)
        lp.lineTo(sd * 96, -640)
        lp.lineTo(sd * 74, -622)
        lp.lineTo(sd * 52, -600)
        lp.close()
        c.drawPath(lp, P(mix(J, "#ffffff", 0.14)))
        c.drawPath(lp, P(OUT, "stroke", 2, alpha=0.5))
    for i in range(2):
        oval(c, 14, -462 + i * 46, 8, 8, P(mix(J, "#000000", 0.5)))
    # bolsillo del pecho con el logo (lado del corazón)
    px, py = 112, -596
    c.drawLine(px - 36, py, px + 36, py, P(mix(J, "#000000", 0.45), "stroke", 5))
    img = logo()
    w = 60
    h = w * img.height() / img.width()
    c.drawImageRect(img, R.R(px - w / 2, py - h - 6, px + w / 2, py - 6), R.SAMP, skia.Paint())


def draw(c, x, y, s, t, p, style=None, talk=0.0, hold_fn=None, breathe=True):
    """Dibuja al personaje. hold_fn(c, x, y) dibuja un objeto en la mano derecha (mano 'hold')."""
    st = style or STYLES["A"]
    br = 4 * math.sin(t * 2.2) if breathe else 0
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, 6, 160, 24, P("#000000", alpha=0.15))
    c.translate(0, -p["bob"])
    c.rotate(p["lean"])
    for sd, (a1, a2) in ((-1, p["leg_l"]), (1, p["leg_r"])):
        leg(c, (sd * 54, -400), a1, a2, sd, st)
    c.drawRect(R.R(-128, -440, 128, -398), P(st["pants"]))
    a1, a2, hk = p["arm_l"]
    arm(c, (-160, -682), a1, a2, hk, -1, st)
    c.save()
    c.translate(0, br * 0.3)
    c.drawRect(R.R(-34, -752, 34, -700), P(st["skin"][1]))
    torso(c, st)
    c.restore()
    a1, a2, hk = p["arm_r"]
    if hk == "hold" and hold_fn:
        _, wr, _ = joint(a1, a2, 165, 155, 160, -682, 1)
        hold_fn(c, wr[0], wr[1] + 10)
    arm(c, (160, -682), a1, a2, hk, 1, st)
    head(c, 0, -874 + br * 0.5, p, t, talk, st)
    c.restore()


def talk_amount(t, words):
    for w in words:
        if w["s"] - 0.02 <= t <= w["e"]:
            return 0.5 + 0.5 * abs(math.sin((t - w["s"]) * 22))
    return 0.0
