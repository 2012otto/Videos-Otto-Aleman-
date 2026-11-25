"""Personaje de la serie Otto Aleman Perfumes (estilo "bitmoji", original) con esqueleto articulado.

Partes móviles: inclinación del cuerpo, cabeza (inclinación y giro), cejas, ojos (abiertos, felices,
corazones, espiral, llorosos, cerrados), boca (sonrisa, abierta, "O", triste, ondulada, asco) que también
habla, hombros, codos, muñecas con varias manos (abierta, señalar, pulgar arriba, puño, sostener), cadera,
rodillas y pies (para caminar). Origen = entre los pies; mide ~1000 px a escala 1.

Uso:
    from mascota import draw, POSES
    draw(c, x, y, s, t, POSES["saludo"], talk=0.0)
"""
import math

import skia

import render as R
from render import P, lin, rad, oval, rrect, clamp, lerp

SKIN = ("#f1c3a0", "#d99a74")
HAIR = "#2a1a12"
SHIRT = "#16161c"       # camisa negra
TRIM = "#d6a24a"         # detalles dorados de la marca
PANTS = ("#e6d6b8", "#c8b48e")
SHOE = "#f4f1ea"


def mix(a, b, t):
    c = R.mix_col(a, b, clamp(t))
    return "#%02x%02x%02x" % (skia.ColorGetR(c), skia.ColorGetG(c), skia.ColorGetB(c))


BASE = dict(lean=0.0, bob=0.0, head_tilt=0.0, head_turn=0.0,
            arm_l=(10, 10, "open"), arm_r=(10, 10, "open"),   # (hombro°, codo°, mano)  0 = colgando
            leg_l=(0, 0), leg_r=(0, 0),                        # (cadera°, rodilla°)
            eyes="open", brows=0.0, mouth="smile", blush=0.0, sweat=0.0, look=(0.0, 0.0), hold=None)


def pose(**kw):
    p = dict(BASE)
    p.update(kw)
    return p


POSES = {
    "neutral": pose(),
    "saludo": pose(arm_r=(150, 30, "open"), mouth="open", head_tilt=4),
    "espera": pose(arm_l=(155, 25, "open"), arm_r=(155, 25, "open"), mouth="O", eyes="wide", brows=-0.35),
    "señala": pose(arm_r=(95, -5, "point"), mouth="smile", head_turn=0.3, look=(0.6, 0)),
    "pulgar": pose(arm_r=(60, 80, "thumb"), mouth="open", eyes="happy", blush=0.5),
    "encoge": pose(arm_l=(60, -70, "open"), arm_r=(60, -70, "open"), mouth="wavy", brows=-0.4, head_tilt=-6),
    "piensa": pose(arm_r=(25, 160, "fist"), arm_l=(20, 80, "open"), mouth="flat", look=(0.5, -0.6), head_tilt=5),
    "enamorado": pose(arm_l=(140, 20, "open"), arm_r=(140, 20, "open"), eyes="hearts", mouth="open", blush=1.0),
    "mareado": pose(lean=-6, eyes="spiral", mouth="wavy", sweat=1.0, arm_l=(30, 30, "open"), arm_r=(45, 60, "open")),
    "asco": pose(eyes="squint", mouth="yuck", brows=0.7, arm_r=(70, 110, "open"), head_tilt=-8, lean=-4),
    "triste": pose(eyes="teary", mouth="sad", brows=-0.9, head_tilt=-6, arm_l=(5, 5, "open"), arm_r=(5, 5, "open")),
    "sostiene": pose(arm_r=(35, 95, "hold"), mouth="smile"),
    "celebra": pose(arm_l=(165, 10, "fist"), arm_r=(165, 10, "fist"), eyes="happy", mouth="open", blush=0.6),
}


def blend(a, b, u):
    """Interpola dos poses (ángulos y valores); los elementos discretos cambian a la mitad."""
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
    """Ciclo de caminata encima de una pose."""
    q = dict(p)
    ph = t * 6.0 * speed
    q["leg_l"] = (22 * math.sin(ph) * amp, max(0, -30 * math.sin(ph)) * amp)
    q["leg_r"] = (-22 * math.sin(ph) * amp, max(0, 30 * math.sin(ph)) * amp)
    q["bob"] = abs(math.sin(ph)) * 10 * amp
    if p["arm_l"][0] < 40:
        q["arm_l"] = (10 - 20 * math.sin(ph) * amp, 15, p["arm_l"][2])
    if p["arm_r"][0] < 40:
        q["arm_r"] = (10 + 20 * math.sin(ph) * amp, 15, p["arm_r"][2])
    return q


# ----------------------------------------------------------------------------
# partes
# ----------------------------------------------------------------------------


def limb(c, x0, y0, a1, a2, l1, l2, w1, w2, col_shader, side):
    """Extremidad de dos segmentos. Ángulos en grados; 0 = hacia abajo; positivo = hacia afuera."""
    r1 = math.radians(a1) * side
    x1 = x0 + math.sin(r1) * l1
    y1 = y0 + math.cos(r1) * l1
    r2 = r1 + math.radians(a2) * side
    x2 = x1 + math.sin(r2) * l2
    y2 = y1 + math.cos(r2) * l2
    p = skia.Path()
    p.moveTo(x0, y0)
    p.lineTo(x1, y1)
    p.lineTo(x2, y2)
    c.drawPath(p, P(col_shader[0], "stroke", w1))
    c.drawLine(x1, y1, x2, y2, P(col_shader[1], "stroke", w2))
    return (x1, y1), (x2, y2), math.degrees(r2)


def hand(c, x, y, ang, kind, side):
    c.save()
    c.translate(x, y)
    c.rotate(-ang)
    sk = P(SKIN[0], shader=lin(-30, 0, 30, 0, [SKIN[0], SKIN[1]]))
    if kind == "fist":
        oval(c, 0, 18, 30, 30, sk)
        for i in range(3):
            c.drawLine(-14 + i * 14, 30, -14 + i * 14, 44, P(SKIN[1], "stroke", 3))
    elif kind == "point":
        oval(c, 0, 16, 28, 28, sk)
        rrect(c, -8, 30, 8, 92, 8, sk)
    elif kind == "thumb":
        oval(c, 0, 16, 30, 28, sk)
        rrect(c, side * 18 - 8, -40, side * 18 + 8, 14, 8, sk)
    elif kind == "hold":
        oval(c, 0, 16, 30, 30, sk)
        rrect(c, -26, 8, 26, 30, 10, P(SKIN[1]))
    else:  # abierta, dedos separados
        oval(c, 0, 18, 30, 30, sk)
        for i in range(4):
            a = math.radians(-30 + i * 20)
            c.drawLine(math.sin(a) * 22, 30, math.sin(a) * 40, 30 + math.cos(a) * 34, P(SKIN[0], "stroke", 13))
        c.drawLine(side * 24, 16, side * 50, 0, P(SKIN[0], "stroke", 13))
    c.restore()


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
    o = talk  # 0..1 apertura por el habla
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
    c.drawLine(-30, 72 - 4 * o, 30, 72 - 4 * o, P("#5a1a1a", "stroke", 7))   # flat


def head(c, x, y, p, t, talk):
    c.save()
    c.translate(x, y)
    c.rotate(p["head_tilt"])
    turn = p["head_turn"]
    # orejas
    for sd in (-1, 1):
        oval(c, sd * 124 - turn * 30, 10, 22 * (1 - 0.3 * turn * sd), 34, P(SKIN[1]))
    face = skia.Path()
    face.addOval(R.R(-128, -150, 128, 150))
    c.drawPath(face, P(SKIN[0], shader=rad(-30 + turn * 30, -40, 260, [mix(SKIN[0], "#ffffff", 0.15), SKIN[0], SKIN[1]], [0, .6, 1])))
    fx = turn * 34  # rasgos se desplazan al girar
    # barba corta
    c.save()
    c.clipPath(face, True)
    bd = skia.Path()
    bd.moveTo(-130, 20)
    bd.cubicTo(-110, 150, 110, 150, 130, 20)
    bd.lineTo(100, 50)
    bd.quadTo(0, 110, -100, 50)
    bd.close()
    c.drawPath(bd, P("#3a2418", alpha=0.35))
    c.restore()
    if p["blush"] > 0:
        for sd in (-1, 1):
            oval(c, fx + sd * 70, 40, 26, 14, P("#ff7a8a", alpha=0.45 * p["blush"]))
    for sd in (-1, 1):
        eye(c, fx + sd * 50, -10, p["eyes"], p["look"], t, sd)
        b = p["brows"]
        bp = skia.Path()
        bp.moveTo(fx + sd * 50 - 26, -58 - (b * 14 if sd < 0 else 0) + (b * 6 if sd > 0 else 0))
        bp.quadTo(fx + sd * 50, -70 - b * 8, fx + sd * 50 + 26, -58 - (b * 14 if sd > 0 else 0) + (b * 6 if sd < 0 else 0))
        c.drawPath(bp, P(HAIR, "stroke", 10))
    nose = skia.Path()
    nose.moveTo(fx + 2, 6)
    nose.quadTo(fx - 12, 34, fx + 4, 38)
    c.drawPath(nose, P(SKIN[1], "stroke", 5))
    c.save()
    c.translate(fx, 0)
    mouth(c, p["mouth"], talk, t)
    c.restore()
    # cabello con copete
    hp = skia.Path()
    hp.moveTo(-134, -10)
    hp.cubicTo(-150, -150, -60, -210, 20, -200)
    hp.cubicTo(100, -215, 160, -150, 134, -10)
    hp.quadTo(120, -90, 70, -110)
    hp.quadTo(-10, -80, -60, -120)
    hp.quadTo(-110, -100, -134, -10)
    hp.close()
    c.save()
    c.translate(turn * 12, 0)
    c.drawPath(hp, P(HAIR, shader=lin(0, -215, 0, -10, ["#4a3020", HAIR])))
    c.drawLine(-40, -170, 40, -185, P("#6a4a30", "stroke", 6, alpha=0.6))
    c.restore()
    if p["sweat"] > 0:
        oval(c, 120, -60 + 10 * math.sin(t * 4), 10, 16, P("#7fd6ff", alpha=p["sweat"]))
    c.restore()


def draw(c, x, y, s, t, p, talk=0.0, hold_fn=None, breathe=True):
    """Dibuja al personaje con pose `p`. talk 0..1 abre la boca al hablar. hold_fn(c, x, y) dibuja un objeto en la mano derecha."""
    br = 4 * math.sin(t * 2.2) if breathe else 0
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, 4, 150, 24, P("#000000", alpha=0.15))
    c.translate(0, -p["bob"])
    c.rotate(p["lean"])
    hip = (0, -400)
    # piernas
    for sd, (a1, a2) in ((-1, p["leg_l"]), (1, p["leg_r"])):
        _, ank, ang = limb(c, sd * 52, hip[1], a1 * sd, -a2 * sd, 200, 190, 86, 78, (PANTS[0], PANTS[0]), sd)
        c.save()
        c.translate(*ank)
        c.rotate(-ang * 0.3)
        rrect(c, -36 + sd * 10, -6, 50 + sd * 10, 30, 16, P(SHOE))
        c.drawRect(R.R(-36 + sd * 10, 22, 50 + sd * 10, 30), P("#b8b4a8"))
        c.restore()
    # torso
    c.save()
    c.translate(0, br * 0.3)
    torso = skia.Path()
    torso.moveTo(-150, -700)
    torso.quadTo(-185, -690, -175, -620)
    torso.lineTo(-135, -400)
    torso.lineTo(135, -400)
    torso.lineTo(175, -620)
    torso.quadTo(185, -690, 150, -700)
    torso.close()
    c.drawPath(torso, P(SHIRT, shader=lin(-185, 0, 185, 0, ["#0c0c10", "#2a2a34", "#16161c"])))
    c.drawRect(R.R(-137, -430, 137, -400), P("#6a5a40"))  # cinturón
    oval(c, 0, -415, 14, 10, P(TRIM))
    col = skia.Path()
    col.moveTo(-50, -708)
    col.lineTo(0, -660)
    col.lineTo(50, -708)
    c.drawPath(col, P("#3a3a44", "stroke", 10))
    oval(c, -80, -610, 14, 14, P(TRIM))  # emblema dorado
    # brazos
    for sd, (a1, a2, hk) in ((-1, p["arm_l"]), (1, p["arm_r"])):
        sh = (sd * 158, -672)
        oval(c, sh[0], sh[1] + 6, 40, 40, P("#22222a"))
        _, wr, ang = limb(c, sh[0], sh[1], a1, a2, 160, 150, 68, 56, (SHIRT, SKIN[0]), sd)
        if sd > 0 and hk == "hold" and hold_fn:
            hold_fn(c, wr[0], wr[1] + 20)
        hand(c, wr[0], wr[1], ang, hk, sd)
    c.restore()
    # cuello y cabeza
    c.drawRect(R.R(-34, -750, 34, -690), P(SKIN[1]))
    head(c, 0, -870 + br * 0.5, p, t, talk)
    c.restore()


def talk_amount(t, words):
    """Apertura de boca (0..1) según las palabras que se están diciendo en t."""
    for w in words:
        if w["s"] - 0.02 <= t <= w["e"]:
            return 0.5 + 0.5 * abs(math.sin((t - w["s"]) * 22))
    return 0.0
