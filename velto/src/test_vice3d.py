"""Prueba de estilo (8 s): Vice City 2.5D/3D con cámara en perspectiva real.

- Vuelo desde el cielo bajando por "Ocean Drive" (hoteles art déco con neón, palmeras, playa, mar) al atardecer.
- Un superdeportivo (sin marca) rebasa a la cámara a nivel de calle.
- Corte a una pareja original (inspirada en el ambiente, no copia de personajes) junto a un deportivo,
  con iluminación de volumen (luz cálida + borde rosado) y fondo bokeh; ella saca el teléfono.
Uso: python3 velto/src/test_vice3d.py out.mp4 [--still t ...]
"""
import math
import os
import subprocess
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_velto as V  # noqa: E402
import render_gta as G  # noqa: E402
from render_velto import (R, P, RECT, LIME, F, back_out, clamp, ease_in_out, ease_out, glow, lerp,  # noqa: E402
                          lin, rad, oval, prog, rrect, smooth, text_center, rng, W, H)

FPS = 30
DUR = 8.0
FOC = 950.0
HAZE = "#ff9ab0"


def hx(col):
    if isinstance(col, int):
        return "#%02x%02x%02x" % (skia.ColorGetR(col), skia.ColorGetG(col), skia.ColorGetB(col))
    return col


def mixc(a, b, t):
    return hx(R.mix_col(hx(a), hx(b), clamp(t)))


class Cam:
    def __init__(self, x, y, z, yaw=0.0, pitch=0.0, roll=0.0):
        self.x, self.y, self.z = x, y, z
        self.cy, self.sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        self.cp, self.sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
        self.roll = roll
        self.pitch = pitch

    def view(self, p):
        dx, dy, dz = p[0] - self.x, p[1] - self.y, p[2] - self.z
        x1 = dx * self.cy - dz * self.sy
        z1 = dx * self.sy + dz * self.cy
        y2 = dy * self.cp - z1 * self.sp
        z2 = dy * self.sp + z1 * self.cp
        return x1, y2, z2

    def proj(self, p):
        x, y, z = self.view(p)
        if z < 0.2:
            return None
        return W / 2 + FOC * x / z, H / 2 - FOC * y / z, z

    def horizon(self):
        return H / 2 - FOC * math.tan(math.radians(-self.pitch)) * -1


def poly(c, cam, pts, paint):
    """Polígono 3D recortado contra el plano cercano."""
    vs = [cam.view(p) for p in pts]
    near = 0.25
    out = []
    for i in range(len(vs)):
        a, b = vs[i], vs[(i + 1) % len(vs)]
        if a[2] >= near:
            out.append(a)
        if (a[2] >= near) != (b[2] >= near):
            t = (near - a[2]) / (b[2] - a[2])
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, near))
    if len(out) < 3:
        return False
    path = skia.Path()
    for i, (x, y, z) in enumerate(out):
        sx, sy = W / 2 + FOC * x / z, H / 2 - FOC * y / z
        (path.moveTo if i == 0 else path.lineTo)(sx, sy)
    path.close()
    c.drawPath(path, paint)
    return True


# ----------------------------------------------------------------------------
# mundo: Ocean Drive
# ----------------------------------------------------------------------------
PASTEL = ["#ffb3c9", "#bdf2dc", "#ffe28a", "#c9d6ff", "#ff9ac0", "#ffd0a8", "#a8f0e8"]
NEON = ["#ff3d9a", "#2ff0ff", "#ffe04a", "#b46bff"]
SIGNS = ["HOTEL", "OCEAN", "BAR", "CAFÉ", "CLUB", "NEON", "TIDES", "PALMS"]


def buildings():
    r = rng(11)
    out = []
    z = -60
    i = 0
    while z < 700:
        w = 18 + r.random() * 16
        h = 14 + r.random() * 22
        d = 16 + r.random() * 10
        out.append(dict(z0=z, z1=z + w, h=h, d=d, col=PASTEL[i % len(PASTEL)], neon=NEON[i % 4], sign=SIGNS[i % 8], i=i))
        z += w + 2 + r.random() * 4
        i += 1
    return out


BLD = buildings()
for _b in buildings()[::1]:  # segunda fila de edificios, más altos y detrás
    _b = dict(_b)
    _b.update(off=34.0, h=_b["h"] * 1.8 + 10, z0=_b["z0"] + 9, z1=_b["z1"] + 9, sign="", i=_b["i"] + 50)
    BLD.append(_b)
PALMS = [(8.5, z) for z in range(-60, 700, 14)] + [(-7.6, z + 7) for z in range(-60, 700, 28)]


def sky(c, cam, t):
    hy = H / 2 + FOC * math.tan(math.radians(cam.pitch))
    c.drawRect(RECT(-400, -400, W + 400, H + 400), P("#2a0f4a", shader=lin(0, hy - 1500, 0, hy + 40,
                                                                          ["#1a0a3a", "#5a1a7a", "#c8407a", "#ff7a6a", "#ffc27a"],
                                                                          [0, .3, .6, .85, 1])))
    sx = W / 2 + 220
    glow(c, R.RES.g_mag, sx, hy - 120, 700, 0.55, skia.BlendMode.kScreen)
    glow(c, R.RES.glow_warm, sx, hy - 90, 380, 0.6, skia.BlendMode.kScreen)
    oval(c, sx, hy - 90, 120, 120, P("#ffe9b0"))
    for k in range(5):  # franjas del sol
        c.drawRect(RECT(sx - 130, hy - 60 + k * 14, sx + 130, hy - 54 + k * 14), P("#ff7a6a", alpha=0.8))
    r = rng(2)
    for i in range(8):  # nubes rosadas
        x = (r.random() * 1600 - 260 + t * 12) % 1700 - 300
        y = hy - 300 - r.random() * 900
        glow(c, R.RES.g_mag, x, y, 260, 0.25, skia.BlendMode.kScreen)
        oval(c, x, y, 220, 40, P("#ff9ac0", alpha=0.35, blur=20))
    return hy


def fogc(col, z, k=1.0):
    return mixc(col, HAZE, (max(z, 0) / 520) ** 0.8 * k)


def draw_building(c, cam, b, t):
    x0 = -10.0 - b.get("off", 0.0)
    x1 = x0 - b["d"]
    z0, z1, h = b["z0"], b["z1"], b["h"]
    zm = (z0 + z1) / 2 - cam.z
    if zm < -40:
        return
    col = b["col"]
    # cara lateral (mirando a la cámara)
    poly(c, cam, [(x0, 0, z0), (x1, 0, z0), (x1, h, z0), (x0, h, z0)], P(fogc(mixc(col, "#5a2a6a", 0.45), zm)))
    # fachada a la calle con luz del atardecer
    fac = P(col, shader=None)
    fac.setColor(R.hexc(fogc(mixc(col, "#ff9a6a", 0.15), zm)))
    poly(c, cam, [(x0, 0, z0), (x0, 0, z1), (x0, h, z1), (x0, h, z0)], fac)
    # cornisa
    poly(c, cam, [(x0 + 0.3, h - 0.8, z0), (x0 + 0.3, h - 0.8, z1), (x0 + 0.3, h, z1), (x0 + 0.3, h, z0)],
         P(fogc("#ffffff", zm, 0.7), alpha=0.85))
    if zm < 260:  # ventanas
        rows = int((h - 3) / 3.2)
        cols_ = int((z1 - z0 - 2) / 3.0)
        wc = fogc("#7fd6ff", zm)
        for rr in range(rows):
            for cc in range(cols_):
                y0 = 2.0 + rr * 3.2
                za = z0 + 1.5 + cc * 3.0
                lit = (rr * 7 + cc * 3 + b["i"]) % 5 == 0
                poly(c, cam, [(x0 + 0.05, y0, za), (x0 + 0.05, y0, za + 1.6), (x0 + 0.05, y0 + 2.0, za + 1.6), (x0 + 0.05, y0 + 2.0, za)],
                     P(fogc("#ffd88a", zm) if lit else wc))
    # letrero de neón vertical
    sp = cam.proj((x0 + 0.6, h * 0.8, z0 + 3))
    sp2 = cam.proj((x0 + 0.6, h * 0.8 - 1.0, z0 + 3))
    if sp and sp2 and zm < 400 and b["sign"]:
        size = abs(sp2[1] - sp[1]) * 1.4
        if size > 3:
            f = F(R.RES.mx, size)
            tw = f.measureText(b["sign"])
            flick = 0.85 + 0.15 * math.sin(t * 9 + b["i"] * 3)
            glow(c, R.RES.g_mag if b["neon"] in ("#ff3d9a", "#b46bff") else R.RES.g_lime, sp[0], sp[1], tw * 0.9, 0.35 * flick)
            c.save()
            c.translate(sp[0], sp[1])
            c.drawString(b["sign"], -tw / 2, 0, f, P(b["neon"], "stroke", max(1, size * 0.06), alpha=flick))
            c.drawString(b["sign"], -tw / 2, 0, f, P("#ffffff", alpha=0.85 * flick))
            c.restore()


def draw_palm(c, cam, x, z, t):
    p = cam.proj((x, 0, z))
    if not p:
        return
    hp = FOC * 11.0 / p[2]
    if hp < 3 or p[0] < -400 or p[0] > W + 400:
        return
    col = fogc("#5a2a3a", p[2], 0.9)
    G.palm(c, p[0], p[1], hp, t, lean=0.1 if x > 0 else -0.1, col_trunk=hx(col), col_leaf=hx(mixc("#1f4a3a", HAZE, max(p[2], 0) / 600)))


def car_rear(c, x, y, s, col="#e8202a", glow_a=1.0):
    """Superdeportivo (vista trasera, sin marca)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, 4, 230, 26, P("#000000", alpha=0.45, blur=8))
    for sd in (-1, 1):
        rrect(c, sd * 190 - 34, -60, sd * 190 + 34, 10, 14, P("#111111"))
    body = skia.Path()
    body.moveTo(-235, -20)
    body.lineTo(-225, -95)
    body.quadTo(-120, -150, 0, -155)
    body.quadTo(120, -150, 225, -95)
    body.lineTo(235, -20)
    body.quadTo(0, 0, -235, -20)
    body.close()
    c.drawPath(body, P(col, shader=lin(0, -155, 0, 0, [mixc(col, "#ffffff", 0.35), col, mixc(col, "#000000", 0.4)])))
    glass = skia.Path()
    glass.moveTo(-120, -150)
    glass.quadTo(0, -205, 120, -150)
    glass.close()
    c.drawPath(glass, P("#1a1030", shader=lin(0, -205, 0, -150, ["#ff9ac0", "#1a1030"])))
    rrect(c, -210, -105, 210, -88, 8, P("#ff2030"))
    glow(c, R.RES.g_mag, -150, -96, 120, 0.8 * glow_a)
    glow(c, R.RES.g_mag, 150, -96, 120, 0.8 * glow_a)
    rrect(c, -90, -60, 90, -30, 8, P("#1a1a1a"))
    for dx in (-30, 30):
        oval(c, dx, -24, 14, 9, P("#c8c8d0"))
    c.restore()


def car_side(c, x, y, s, col="#e8202a", t=0.0):
    """Superdeportivo de perfil (forma genérica de cuña, sin marca)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, 8, 520, 30, P("#000000", alpha=0.5, blur=10))
    body = skia.Path()
    body.moveTo(-520, -40)
    body.lineTo(-500, -120)
    body.quadTo(-420, -150, -300, -160)
    body.quadTo(-120, -280, 60, -270)
    body.quadTo(250, -250, 420, -170)
    body.lineTo(520, -140)
    body.lineTo(530, -50)
    body.quadTo(500, -20, 450, -20)
    body.lineTo(-480, -20)
    body.close()
    c.drawPath(body, P(col, shader=lin(0, -280, 0, -20, [mixc(col, "#ffd0e0", 0.55), col, mixc(col, "#000000", 0.45)], [0, .45, 1])))
    glass = skia.Path()
    glass.moveTo(-250, -170)
    glass.quadTo(-110, -262, 60, -258)
    glass.quadTo(200, -240, 300, -175)
    glass.close()
    c.drawPath(glass, P("#1a1030", shader=lin(-250, 0, 300, 0, ["#2a1040", "#ff9ac0", "#2a1040"], [0, .4, 1])))
    c.drawLine(-470, -130, 480, -150, P("#ffffff", "stroke", 5, alpha=0.6))  # reflejo
    intake = skia.Path()
    intake.moveTo(90, -110)
    intake.lineTo(230, -130)
    intake.lineTo(210, -70)
    intake.lineTo(110, -70)
    intake.close()
    c.drawPath(intake, P("#140a14"))
    for wx in (-330, 330):
        oval(c, wx, -30, 96, 96, P("#0a0a0e"))
        oval(c, wx, -30, 64, 64, P("#c8c8d0", shader=rad(wx - 20, -50, 80, ["#ffffff", "#8a8a96"])))
        for k in range(5):
            a = k * 1.2566 + t * 0.0
            c.drawLine(wx, -30, wx + math.cos(a) * 58, -30 + math.sin(a) * 58, P("#3a3a44", "stroke", 9))
        oval(c, wx, -30, 16, 16, P("#2a2a30"))
    rrect(c, 470, -140, 525, -125, 6, P("#fff4d0"))
    glow(c, R.RES.glow_white, 515, -132, 60, 0.7)
    rrect(c, -515, -125, -490, -100, 6, P("#ff2030"))
    c.restore()


def world(c, cam, t, car=None):
    hy = sky(c, cam, t)
    # mar y playa
    poly(c, cam, [(9, 0, -400), (2000, 0, -400), (2000, 0, 3000), (9, 0, 3000)], P("#1aa0c0"))
    poly(c, cam, [(26, 0.02, -400), (2000, 0.02, -400), (2000, 0.02, 3000), (26, 0.02, 3000)],
         P("#2a6aa8", shader=lin(0, hy, 0, H, ["#ff9ab0", "#c85a9a", "#2a5aa8"], [0, .1, 1])))
    poly(c, cam, [(9, 0.01, -400), (26, 0.01, -400), (26, 0.01, 3000), (9, 0.01, 3000)], P("#f3d8b0"))
    poly(c, cam, [(-3000, 0.0, -400), (-10, 0.0, -400), (-10, 0.0, 3000), (-3000, 0.0, 3000)], P("#b86a8a"))
    # calle y aceras
    poly(c, cam, [(-6, 0.03, -400), (6, 0.03, -400), (6, 0.03, 3000), (-6, 0.03, 3000)], P("#4a3a5a"))
    poly(c, cam, [(6, 0.04, -400), (9, 0.04, -400), (9, 0.04, 3000), (6, 0.04, 3000)], P("#e8c8d8"))
    poly(c, cam, [(-10, 0.04, -400), (-6, 0.04, -400), (-6, 0.04, 3000), (-10, 0.04, 3000)], P("#e8c8d8"))
    for z in range(-60, 900, 10):
        if z + 4 > cam.z - 2:
            poly(c, cam, [(-0.15, 0.05, z), (0.15, 0.05, z), (0.15, 0.05, z + 4), (-0.15, 0.05, z + 4)], P("#ffe9a0"))
    # reflejos del sol en el agua
    for i in range(30):
        zz = cam.z + 80 + i * 25
        p = cam.proj((120 + (i % 5) * 30, 0.05, zz))
        if p:
            w = FOC * 6 / p[2]
            c.drawLine(p[0] - w, p[1], p[0] + w, p[1], P("#ffe9b0", "stroke", max(1, FOC * 0.3 / p[2]), alpha=0.6))
    # objetos ordenados por profundidad (de lejos a cerca)
    items = []
    for b in BLD:
        items.append(((b["z0"] + b["z1"]) / 2 - cam.z, "b", b))
    for x, z in PALMS:
        items.append((z - cam.z, "p", (x, z)))
    if car is not None:
        items.append((car[2] - cam.z, "c", car))
    items.sort(key=lambda q: -q[0])
    for d, kind, obj in items:
        if d < -30:
            continue
        if kind == "b":
            draw_building(c, cam, obj, t)
        elif kind == "p":
            draw_palm(c, cam, obj[0], obj[1], t)
        else:
            p = cam.proj(obj)
            if p:
                car_rear(c, p[0], p[1], FOC * 2.2 / p[2] / 470, glow_a=1.0)
    return hy


# ----------------------------------------------------------------------------
# la pareja (original), con iluminación de volumen
# ----------------------------------------------------------------------------


def shade(base, k):
    return mixc(base, "#2a0a3a", k)


def light(base, k):
    return mixc(base, "#ffd0a0", k)


def head(c, x, y, s, skin, t, female, look=0.0, smile=0.6, phone_glow=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    # cuello
    neck = skia.Path()
    neck.moveTo(-34, 60)
    neck.lineTo(-30, 150)
    neck.lineTo(30, 150)
    neck.lineTo(34, 60)
    neck.close()
    c.drawPath(neck, P(skin, shader=lin(-34, 0, 34, 0, [shade(skin, 0.35), skin, light(skin, 0.2)])))
    face = skia.Path()
    if female:
        face.moveTo(0, -120)
        face.cubicTo(70, -120, 92, -60, 88, 0)
        face.cubicTo(84, 60, 50, 110, 0, 118)
        face.cubicTo(-50, 110, -84, 60, -88, 0)
        face.cubicTo(-92, -60, -70, -120, 0, -120)
    else:
        face.moveTo(0, -125)
        face.cubicTo(76, -125, 96, -60, 94, 0)
        face.cubicTo(92, 60, 70, 112, 0, 124)
        face.cubicTo(-70, 112, -92, 60, -94, 0)
        face.cubicTo(-96, -60, -76, -125, 0, -125)
    face.close()
    c.drawPath(face, P(skin, shader=rad(30 + look * 10, -30, 210, [light(skin, 0.25), skin, shade(skin, 0.35)], [0, .55, 1])))
    if phone_glow > 0:
        c.save()
        c.clipPath(face, True)
        glow(c, R.RES.g_vio, 30, 40, 160, 0.35 * phone_glow, skia.BlendMode.kScreen)
        c.restore()
    # borde rosado (luz del neón)
    c.save()
    c.clipPath(face, True)
    c.drawPath(face, P("#ff5aa8", "stroke", 18, alpha=0.45, blur=6))
    c.restore()
    for sd in (-1, 1):  # orejas
        oval(c, sd * 92, 6, 16, 26, P(shade(skin, 0.15)))
    if not female:  # barba corta
        c.save()
        c.clipPath(face, True)
        beard = skia.Path()
        beard.moveTo(-96, -10)
        beard.cubicTo(-80, 90, -40, 130, 0, 130)
        beard.cubicTo(40, 130, 80, 90, 96, -10)
        beard.lineTo(70, 20)
        beard.quadTo(0, 50, -70, 20)
        beard.close()
        c.drawPath(beard, P("#2a1a12", alpha=0.5))
        r = rng(4)
        for i in range(60):
            oval(c, -80 + r.random() * 160, 10 + r.random() * 110, 1.5, 1.5, P("#140a06", alpha=0.6))
        c.restore()
    # ojos
    for sd in (-1, 1):
        ex, ey = sd * 36, -12
        oval(c, ex, ey, 19, 10, P("#ffffff"))
        oval(c, ex + look * 5, ey, 9, 9, P("#4a2a14"))
        oval(c, ex + look * 5, ey, 4.5, 4.5, P("#0a0604"))
        oval(c, ex + look * 5 + 3, ey - 3, 2.5, 2.5, P("#ffffff"))
        lid = skia.Path()
        lid.moveTo(ex - 22, ey - 1)
        lid.quadTo(ex, ey - 16, ex + 22, ey - 1)
        c.drawPath(lid, P("#1a0a06", "stroke", 4 if female else 3))
        if female:
            for j in range(3):
                c.drawLine(ex + sd * (14 + j * 4), ey - 9 + j * 2, ex + sd * (20 + j * 5), ey - 15 + j * 2, P("#1a0a06", "stroke", 2))
        brow = skia.Path()
        brow.moveTo(ex - 22, ey - 26 - (0 if female else 2))
        brow.quadTo(ex, ey - 36, ex + 24, ey - 28)
        c.drawPath(brow, P("#2a1a10", "stroke", 5 if female else 8))
    nose = skia.Path()
    nose.moveTo(4, -5)
    nose.quadTo(-6, 34, -14, 42)
    nose.quadTo(0, 50, 14, 42)
    c.drawPath(nose, P(shade(skin, 0.4), "stroke", 3.5))
    m = skia.Path()
    m.moveTo(-30, 70)
    m.quadTo(0, 70 + 22 * smile, 30, 70)
    if female:
        lips = skia.Path()
        lips.moveTo(-28, 70)
        lips.quadTo(-10, 60, 0, 66)
        lips.quadTo(10, 60, 28, 70)
        lips.quadTo(0, 88 + 6 * smile, -28, 70)
        lips.close()
        c.drawPath(lips, P("#b8405a", shader=lin(0, 60, 0, 90, ["#c85a6a", "#8a2a3a"])))
        c.drawLine(-26, 70, 26, 70, P("#5a1a24", "stroke", 2))
    else:
        c.drawPath(m, P("#5a2a24", "stroke", 4))
    # cabello
    if female:
        hair = skia.Path()
        hair.moveTo(-96, 10)
        hair.cubicTo(-120, -150, 120, -160, 98, 0)
        hair.quadTo(60, -90, -10, -96)
        hair.quadTo(-70, -80, -96, 10)
        hair.close()
        c.drawPath(hair, P("#1a0e0a", shader=lin(-100, -150, 100, 0, ["#3a2014", "#120806"])))
        for i in range(6):
            c.drawLine(-60 + i * 22, -110, -70 + i * 26, -40, P("#5a3420", "stroke", 3, alpha=0.5))
        for sd in (-1, 1):  # aretes de aro
            c.drawPath(skia.Path().addCircle(sd * 92, 48, 18), P("#f5c84a", "stroke", 4))
    else:
        hair = skia.Path()
        hair.moveTo(-94, -20)
        hair.cubicTo(-104, -150, 104, -155, 94, -20)
        hair.quadTo(80, -96, 20, -100)
        hair.quadTo(-60, -98, -94, -20)
        hair.close()
        c.drawPath(hair, P("#1a100a", shader=lin(0, -150, 0, -20, ["#3a2414", "#140a06"])))
    c.restore()


def long_hair_back(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    hp = skia.Path()
    hp.moveTo(-110, -60)
    sw = 8 * math.sin(t * 1.5)
    hp.cubicTo(-150, 80, -150, 260, -110 + sw, 340)
    hp.quadTo(-40, 300, 0, 260)
    hp.quadTo(40, 300, 110 + sw, 340)
    hp.cubicTo(150, 260, 150, 80, 110, -60)
    hp.close()
    c.drawPath(hp, P("#1a0e0a", shader=lin(-150, 0, 150, 0, ["#120806", "#3a2014", "#120806"])))
    c.restore()


def torso(c, x, y, s, skin, top, shirt=None, female=False):
    """Medio cuerpo con volumen: hombros redondeados, brazos separados, cintura."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    sw, ww, hw = (125, 88, 112) if female else (165, 120, 128)
    # brazos (detrás del torso)
    for sd in (-1, 1):
        arm = skia.Path()
        arm.moveTo(sd * (sw - 30), 0)
        arm.cubicTo(sd * (sw + 40), 20, sd * (sw + 40), 200, sd * (sw + 24), 330)
        arm.lineTo(sd * (sw + 30), 640)
        arm.lineTo(sd * (sw - 30), 640)
        arm.lineTo(sd * (sw - 22), 330)
        arm.cubicTo(sd * (sw - 30), 200, sd * (sw - 60), 60, sd * (sw - 70), 30)
        arm.close()
        c.drawPath(arm, P(skin, shader=lin(sd * (sw - 60), 0, sd * (sw + 40), 0,
                                           [light(skin, 0.15), skin, shade(skin, 0.45)] if sd > 0 else [shade(skin, 0.45), skin, light(skin, 0.1)][::-1])))
        c.drawPath(arm, P("#ff5aa8", "stroke", 6, alpha=0.35 if sd > 0 else 0.0, blur=3))
    body = skia.Path()
    body.moveTo(-sw + 40, -14)
    body.quadTo(-sw - 10, 0, -sw + 6, 70)
    body.cubicTo(-sw + 10, 200, -ww - 10, 330, -ww, 420)
    body.cubicTo(-ww + 4, 500, -hw, 560, -hw, 700)
    body.lineTo(hw, 700)
    body.cubicTo(hw, 560, ww - 4, 500, ww, 420)
    body.cubicTo(ww + 10, 330, sw - 10, 200, sw - 6, 70)
    body.quadTo(sw + 10, 0, sw - 40, -14)
    body.close()
    c.drawPath(body, P(skin, shader=lin(-sw, 0, sw, 0, [shade(skin, 0.4), skin, light(skin, 0.18), shade(skin, 0.3)], [0, .35, .6, 1])))
    # camiseta sin mangas
    tk = skia.Path()
    strap = 46 if female else 60
    tk.moveTo(-sw + 70, -12)
    tk.lineTo(-sw + 70 + strap, -12)
    tk.quadTo(0, 120 if female else 90, sw - 70 - strap, -12)
    tk.lineTo(sw - 70, -12)
    tk.cubicTo(sw - 30, 120, ww + 6, 300, ww + 2, 420)
    tk.cubicTo(ww + 6, 500, hw + 4, 560, hw + 4, 702)
    tk.lineTo(-hw - 4, 702)
    tk.cubicTo(-hw - 4, 560, -ww - 6, 500, -ww - 2, 420)
    tk.cubicTo(-ww - 6, 300, -sw + 30, 120, -sw + 70, -12)
    tk.close()
    if female:  # top corto: se ve la cintura
        c.save()
        c.clipRect(RECT(-400, -100, 400, 380))
    c.drawPath(tk, P(top, shader=lin(-sw, 0, sw, 0, [shade(top, 0.4), top, light(top, 0.05), shade(top, 0.35)], [0, .35, .6, 1])))
    for i in range(4):  # pliegues
        c.drawLine(-ww + 20 + i * 50, 300, -ww + 40 + i * 50, 380, P(shade(top, 0.3), "stroke", 3, alpha=0.4))
    if female:
        c.restore()
        jeans = skia.Path()
        jeans.moveTo(-ww - 4, 470)
        jeans.cubicTo(-ww, 520, -hw - 4, 560, -hw - 4, 702)
        jeans.lineTo(hw + 4, 702)
        jeans.cubicTo(hw + 4, 560, ww, 520, ww + 4, 470)
        jeans.close()
        c.drawPath(jeans, P("#3a5a9a", shader=lin(-hw, 0, hw, 0, ["#1a2a5a", "#4a6aaa", "#2a3a7a"])))
        c.drawLine(-ww, 478, ww, 478, P("#2a2a40", "stroke", 10))
        oval(c, 0, 470 - 20, 4, 6, P(shade(skin, 0.5)))
        c.drawPath(skia.Path().addCircle(0, 30, 10), P("#f5c84a", "stroke", 3))  # collar
    if shirt:  # camisa abierta con estampado tropical
        for sd in (-1, 1):
            sp = skia.Path()
            sp.moveTo(sd * 60, -20)
            sp.cubicTo(sd * (sw + 30), -20, sd * (sw + 60), 60, sd * (sw + 56), 200)
            sp.lineTo(sd * (sw + 10), 230)
            sp.lineTo(sd * (sw + 6), 700)
            sp.lineTo(sd * (ww - 10), 700)
            sp.lineTo(sd * 70, 160)
            sp.close()
            c.drawPath(sp, P(shirt, shader=lin(sd * 60, 0, sd * (sw + 60), 0, [light(shirt, 0.1), shade(shirt, 0.4)])))
            c.save()
            c.clipPath(sp, True)
            r = rng(7 + sd)
            for i in range(18):
                lx, ly = sd * (70 + r.random() * 140), r.random() * 680
                lf = skia.Path()
                lf.moveTo(lx, ly)
                lf.quadTo(lx + 22, ly - 34, lx + 44, ly)
                lf.quadTo(lx + 22, ly + 12, lx, ly)
                c.drawPath(lf, P("#1f7a5a", alpha=0.85))
                oval(c, lx - 20, ly + 30, 9, 9, P("#ffe04a", alpha=0.8))
            c.restore()
            c.drawPath(sp, P(shade(shirt, 0.5), "stroke", 3, alpha=0.6))
    c.restore()



def phone_hand(c, x, y, s, skin, k, t):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rotate(lerp(30, -8, ease_out(k)))
    rrect(c, -48, -95, 48, 95, 16, P("#121018"))
    rrect(c, -42, -88, 42, 88, 12, P("#7a3ae0", shader=lin(0, -88, 0, 88, ["#c08aff", "#7a3ae0", "#2a0f4a"])))
    glow(c, R.RES.g_vio, 0, 0, 140, 0.5 * k, skia.BlendMode.kScreen)
    oval(c, 0, 0, 22, 22, P("#ffffff", alpha=0.9))
    tri = skia.Path()
    tri.moveTo(-6, -11)
    tri.lineTo(12, 0)
    tri.lineTo(-6, 11)
    tri.close()
    c.drawPath(tri, P("#7a3ae0"))
    for i in range(4):  # dedos
        rrect(c, -62, -50 + i * 26, -30, -28 + i * 26, 11, P(skin, shader=lin(-62, 0, -30, 0, [shade(skin, 0.3), skin])))
    rrect(c, 30, -10, 60, 30, 13, P(skin))
    c.restore()


def couple_shot(c, t, lt, cam_bg):
    # fondo: la misma calle en 3D, desenfocada (bokeh) y con paralaje
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(14, 14, skia.TileMode.kClamp))
    c.saveLayer(None, p)
    world(c, cam_bg, t)
    c.restore()
    r = rng(9)
    for i in range(26):  # bokeh de neón
        x = r.random() * 1300 - 110 - lt * 40
        y = 300 + r.random() * 1000
        rr_ = 30 + r.random() * 70
        col = NEON[i % 4]
        oval(c, x, y, rr_, rr_, P(col, alpha=0.18))
        c.drawPath(skia.Path().addCircle(x, y, rr_), P(col, "stroke", 3, alpha=0.25))
    c.drawRect(RECT(0, 0, W, H), P("#2a0a3a", alpha=0.18))
    u = ease_in_out(prog(lt, 0, 3.2))
    z = lerp(1.0, 1.12, u)
    c.save()
    c.translate(540, 1250)
    c.scale(z, z)
    c.translate(-540 + lerp(-50, 40, u), -1250)
    car_side(c, lerp(560, 520, u), 1500, 1.05, "#e8202a", t)
    # él (izquierda), apoyado
    skin_m, skin_f = "#c98a62", "#d9a07a"
    torso(c, 270, 1150, 1.0, skin_m, "#f4f1ea", shirt="#ff8aa8")
    head(c, 270, 960, 1.05, skin_m, t, False, look=0.6, smile=0.4)
    # ella (derecha)
    long_hair_back(c, 780, 900, 1.0, t)
    torso(c, 780, 1100, 0.92, skin_f, "#ffffff", female=True)
    phk = prog(lt, 1.2, 1.8)
    head(c, 780, 920, 1.0, skin_f, t, True, look=-0.6 if phk < 0.5 else -0.2, smile=0.7, phone_glow=phk)
    phone_hand(c, 660, lerp(1500, 1190, ease_out(phk)), 1.2, skin_f, phk, t)
    c.restore()
    # luz cálida + borde neón general
    c.drawRect(RECT(0, 0, W, H), P("#ff9a5a", blend=skia.BlendMode.kSoftLight, alpha=0.35))
    G.pop_text(c, "GTA 6", 540, 560, 170, prog(lt, 1.8, 2.2), rot=-4, shader=G.sunset_text_shader(430, 560))


# ----------------------------------------------------------------------------
# guion de cámara de la prueba
# ----------------------------------------------------------------------------


def frame(c, t):
    c.clear(R.hexc("#000000"))
    if t < 3.2:  # vuelo bajando sobre Ocean Drive
        u = ease_in_out(t / 3.2)
        cam = Cam(lerp(30, 1.5, u), lerp(90, 4.0, u), lerp(-120, 60, u), yaw=lerp(-6, 4, u) + 2 * math.sin(t),
                  pitch=lerp(-38, -4, u))
        world(c, cam, t)
    elif t < 4.9:  # a ras de calle: el deportivo rebasa
        lt = t - 3.2
        cz = 60 + lt * 22
        cam = Cam(1.5 + 0.3 * math.sin(lt * 3), 1.4, cz, yaw=lerp(4, -3, lt / 1.7), pitch=-2)
        car_z = cz + lerp(2.0, 140, ease_in_out(prog(lt, 0.0, 1.7)) ** 1.6)
        hyy = world(c, cam, t, car=(2.8, 0.0, car_z))
        for i in range(24):  # líneas de velocidad
            y = (i * 97) % 1900
            x = (lt * 3000 + i * 300) % 1500 - 200
            c.drawLine(x, y, x + 220, y, P("#ffffff", "stroke", 2, alpha=0.18))
        del hyy
        if lt < 0.25:
            c.drawRect(RECT(0, 0, W, H), P("#ffffff", alpha=0.3 * (1 - lt / 0.25)))
    else:  # la pareja
        lt = t - 4.9
        cam_bg = Cam(-2 + lt * 0.8, 1.6, 140 + lt * 2, yaw=-38 + lt * 3, pitch=2)
        wh = 1 - ease_out(clamp(lt / 0.25))
        if wh > 0.02:
            p = skia.Paint()
            p.setImageFilter(skia.ImageFilters.Blur(60 * wh, 2, skia.TileMode.kClamp))
            c.saveLayer(None, p)
        couple_shot(c, t, lt, cam_bg)
        if wh > 0.02:
            c.restore()
    R.vignette(c, 0.45)
    c.drawRect(RECT(0, 0, W, H), P("#000000", alpha=1 - clamp(t / 0.3) * clamp((DUR - t) / 0.3)))


def main():
    R.Res = V.VeltoRes
    R.RES = R.Res()
    out = sys.argv[1]
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    if "--still" in sys.argv:
        for ts in sys.argv[sys.argv.index("--still") + 1:]:
            frame(c, float(ts))
            surf.makeImageSnapshot().save(f"{out}_{float(ts):05.2f}.png", skia.kPNG)
        return
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out],
                          stdin=subprocess.PIPE)
    for fi in range(int(DUR * FPS)):
        frame(c, fi / FPS)
        ff.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    main()
