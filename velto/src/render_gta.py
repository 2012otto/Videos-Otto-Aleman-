"""Velto Studio — Dato curioso: GTA 6 (datos que casi nadie sabe) con anuncios de $5 que PAUSAN el video.

Cámara siempre en movimiento: caída desde el cielo entre nubes hasta el mapa, zoom out del mapa,
paneo por el pantano, huracán girando, travelling por el malecón, giro de la caja del juego y
subida por un rascacielos. En los anuncios el video se congela, se difumina y aparece el teléfono.
Uso:
  VIDEO_BUILD=$PWD/velto/build_gta VO_TRIM=0.12 VO_GAP=0.12 VO_TAIL=0.4 \
    python3 velto/src/render_gta.py --out velto/build_gta/video_mudo.mp4
"""
import math
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_velto as V  # noqa: E402
import render_sueno as S  # noqa: E402
from render_velto import (R, P, RECT, VIO, VIO2, LIME, F, back_out, clamp, ease_in_out, ease_out, glow, lerp,  # noqa: E402
                          lin, rad, oval, prog, rrect, smooth, text_center, rng, use, W, H, draw_img)

CLOUD = None
VO = None
AD_SCENES = (3, 8)


def cloud_img():
    global CLOUD
    if CLOUD is None:
        CLOUD = R.sprite(255, 252, 248, n=96, power=1.25)
    return CLOUD


def shake(t, amp, f=1.0):
    return (amp * (math.sin(t * 37 * f) + 0.6 * math.sin(t * 23 * f + 1)),
            amp * (math.cos(t * 31 * f) + 0.5 * math.sin(t * 19 * f + 2)))


def world_cam(c, cx, cy, z, rot=0.0, px=540, py=1060, sh=(0.0, 0.0)):
    c.translate(px + sh[0], py + sh[1])
    c.rotate(rot)
    c.scale(z, z)
    c.translate(-cx, -cy)


def smooth_path(pts):
    p = skia.Path()
    mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)  # noqa: E731
    p.moveTo(*mid(pts[-1], pts[0]))
    for i in range(len(pts)):
        m = mid(pts[i], pts[(i + 1) % len(pts)])
        p.quadTo(pts[i][0], pts[i][1], m[0], m[1])
    p.close()
    return p


def blob(seed, rx, ry, n=11, rough=0.28):
    r = rng(seed)
    pts = []
    for i in range(n):
        a = i / n * 6.283
        k = 1 + rough * (r.random() - 0.5) * 2
        pts.append((math.cos(a) * rx * k, math.sin(a) * ry * k))
    return smooth_path(pts)


def pop_text(c, txt, x, y, size, k, col="#ffffff", tf=None, rot=0.0, stroke="#14061f", shader=None):
    if k <= 0:
        return
    s = back_out(clamp(k), 2.4)
    f = F(tf or R.RES.mx, size)
    w = f.measureText(txt)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.drawString(txt, -w / 2 + 6, 8, f, P("#000000", alpha=0.45, blur=8))
    sp = P(stroke, "stroke", size * 0.14)
    sp.setStrokeJoin(skia.Paint.kRound_Join)
    c.drawString(txt, -w / 2, 0, f, sp)
    c.drawString(txt, -w / 2, 0, f, P(col, shader=shader))
    c.restore()


def tag(c, txt, x, y, k, bg="#ff3d7f", fg="#ffffff", size=42, rot=0.0):
    if k <= 0:
        return
    s = back_out(clamp(k), 2.2)
    f = F(R.RES.mx, size)
    w = f.measureText(txt) + size * 1.2
    h = size * 1.7
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    rrect(c, -w / 2 + 6, -h / 2 + 8, w / 2 + 6, h / 2 + 8, 16, P("#000000", alpha=0.35, blur=6))
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, 16, P(bg))
    c.drawString(txt, -f.measureText(txt) / 2, size * 0.36, f, P(fg))
    c.restore()


def sunset_text_shader(y0, y1):
    return lin(0, y0, 0, y1, ["#ffe27a", "#ff8a3d", "#ff3d7f"])


# ----------------------------------------------------------------------------
# el mapa de Leonida (estilizado, original)
# ----------------------------------------------------------------------------
LAND = [(-1100, -950), (-500, -1010), (200, -985), (520, -905), (565, -700), (625, -400), (700, -100),
        (765, 200), (785, 500), (725, 800), (620, 1000), (430, 1060), (255, 950), (120, 700), (40, 400),
        (-60, 150), (-150, -100), (-300, -350), (-430, -560), (-650, -640), (-900, -655), (-1110, -720)]
KEYS = [(470, 1130, 40), (380, 1190, 34), (280, 1240, 38), (170, 1275, 30), (60, 1300, 36), (-50, 1310, 28),
        (-150, 1305, 32)]
CITY = (640, 700)


def draw_map(c, t, labels=0.0):
    land = smooth_path(LAND)
    c.drawRect(RECT(-6000, -6000, 6000, 6000), P("#0b6fa8", shader=rad(150, 150, 2600, ["#1aa7c9", "#0b6fa8", "#073f70"], [0, .55, 1])))
    # olas brillantes en el mar
    r = rng(41)
    for i in range(90):
        x, y = r.random() * 4400 - 2200, r.random() * 4400 - 2000
        a = 0.5 + 0.5 * math.sin(t * 2 + i)
        c.drawLine(x, y, x + 40, y, P("#bff7ff", "stroke", 4, alpha=0.18 * a))
    c.drawPath(land, P("#3fe0d6", "stroke", 170, alpha=0.35, blur=40))
    c.drawPath(land, P("#7ff3e6", "stroke", 60, alpha=0.6))
    for x, y, s in KEYS:
        oval(c, x, y, s * 1.8, s * 1.8, P("#7ff3e6", alpha=0.6))
    bridge = skia.Path()
    bridge.moveTo(*KEYS[0][:2])
    for x, y, s in KEYS[1:]:
        bridge.lineTo(x, y)
    c.drawPath(bridge, P("#f4e9d0", "stroke", 5, alpha=0.8))
    for x, y, s in KEYS:
        oval(c, x, y, s * 1.1, s * 0.8, P("#f3dfa8"))
        oval(c, x, y, s * 0.8, s * 0.55, P("#6cbf55"))
    c.drawPath(land, P("#f3dfa8", "stroke", 22))
    c.drawPath(land, P("#6cb04f", shader=lin(0, -1000, 0, 1050, ["#3f8f45", "#69b350", "#8cc75a"])))
    c.save()
    c.clipPath(land, True)
    r = rng(7)
    for i in range(60):  # bosques
        x, y = r.random() * 1900 - 1150, r.random() * 2000 - 1000
        oval(c, x, y, 50 + 70 * r.random(), 40 + 50 * r.random(), P("#2f7a3c", alpha=0.45))
    oval(c, 330, 860, 330, 190, P("#7d9a4e", alpha=0.85))   # pantano
    r = rng(9)
    for i in range(40):
        oval(c, 160 + r.random() * 350, 760 + r.random() * 220, 14 + 20 * r.random(), 8 + 10 * r.random(), P("#3aa6b9", alpha=0.7))
    for i, (mx, my) in enumerate(((-420, -760), (-330, -720), (-250, -780), (-520, -720))):  # montaña
        tri = skia.Path()
        tri.moveTo(mx - 80, my + 50)
        tri.lineTo(mx, my - 80)
        tri.lineTo(mx + 80, my + 50)
        tri.close()
        c.drawPath(tri, P("#5c6b4a", shader=lin(mx - 80, 0, mx + 80, 0, ["#7b8a5e", "#4a5a3a"])))
        tri2 = skia.Path()
        tri2.moveTo(mx - 22, my - 46)
        tri2.lineTo(mx, my - 80)
        tri2.lineTo(mx + 22, my - 46)
        tri2.close()
        c.drawPath(tri2, P("#f4f4ee"))
    c.restore()
    oval(c, 360, 300, 120, 160, P("#2c9bd0"))
    oval(c, 360, 300, 120, 160, P("#bff7ff", "stroke", 6, alpha=0.6))
    road = P("#f6e7b8", "stroke", 9, alpha=0.85)
    for pts in (((-1000, -820), (-400, -860), (300, -800), (500, -500), (620, 0), (700, 400), CITY),
                ((-650, -700), (-200, -400), (100, 0), (250, 400), (450, 700), CITY),
                ((300, -800), (200, -300), (360, 140))):
        p = skia.Path()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        c.drawPath(p, road)
    # Vice City: cuadrícula de edificios de colores
    r = rng(17)
    cols = ["#ffffff", "#ffd1e6", "#bdf6ff", "#ffe8a8", "#ff8fc1", "#9fe6ff"]
    glow(c, R.RES.g_mag, CITY[0] + 20, CITY[1], 360, 0.5, skia.BlendMode.kScreen)
    for i in range(-5, 6):
        for j in range(-6, 7):
            if r.random() < 0.18 or abs(i) + abs(j) * 0.8 > 8:
                continue
            x, y = CITY[0] + i * 34, CITY[1] + j * 34
            hgt = 10 + 18 * r.random()
            c.drawRect(RECT(x - 13, y - 13 - hgt * 0.3, x + 13, y + 13), P(cols[int(r.random() * 6)]))
            c.drawRect(RECT(x - 13, y + 13 - 4, x + 13, y + 13), P("#5a3a6a", alpha=0.35))
    r = rng(23)
    for i in range(-2, 3):  # puerto del norte
        for j in range(-2, 2):
            x, y = 380 + i * 30, -820 + j * 30
            c.drawRect(RECT(x - 11, y - 11, x + 11, y + 11), P(cols[int(r.random() * 6)]))
    if labels > 0:
        f = F(R.RES.mx, 54)
        for txt, x, y in (("VICE CITY", CITY[0], CITY[1] - 230), ("LEONIDA KEYS", 160, 1420), ("GRASSRIVERS", 330, 640),
                          ("MOUNT KALAGA", -400, -900), ("PORT GELLHORN", 380, -960), ("AMBROSIA", -150, -200)):
            w = f.measureText(txt)
            c.drawString(txt, x - w / 2, y, f, P("#14061f", "stroke", 12, alpha=0.6 * labels))
            c.drawString(txt, x - w / 2, y, f, P("#ffffff", alpha=labels))


def clouds3d(c, alt, t, n=46, seed=3, tint="#ffffff"):
    """Nubes en 3D: alt = altura de la cámara. Cada nube vive a una altura; al bajar la cámara pasa a través."""
    img = cloud_img()
    r = rng(seed)
    items = []
    for i in range(n):
        a = 1.4 + r.random() * 7.0
        ox, oy = (r.random() - 0.5) * 2600, (r.random() - 0.5) * 3600
        rr = 260 + r.random() * 320
        items.append((a, ox, oy, rr, i))
    items.sort(key=lambda q: -q[0])
    for a, ox, oy, rr, i in items:
        d = alt - a
        if d <= 0.05:
            continue
        s = 1.1 / d
        al = clamp(s * 1.6) * clamp(1 - (s - 2.2) / 2.0)
        if al <= 0.01:
            continue
        x, y = 540 + ox * s * 0.45, 1000 + oy * s * 0.45
        rad_ = rr * s
        for j in range(5):
            dx = math.cos(j * 1.3 + i) * rad_ * 0.55
            dy = math.sin(j * 1.7 + i) * rad_ * 0.3
            glow(c, R.RES.soft_dark, x + dx + rad_ * 0.15, y + dy + rad_ * 0.2, rad_ * 0.75, 0.08 * al, skia.BlendMode.kSrcOver)
            glow(c, img, x + dx, y + dy, rad_ * 0.8, 0.95 * al, skia.BlendMode.kSrcOver)


# ----------------------------------------------------------------------------
# escena 1: caída desde el cielo
# ----------------------------------------------------------------------------


def scene1(c, k):
    lt, T = k.lt, k.w
    u = ease_in_out(prog(lt, 0.0, 2.5))
    if lt < 2.5:
        z = 0.5 * (0.11 / 0.5) ** (1 - u)
    else:
        z = 0.5 * (1.7 / 0.5) ** ease_in_out(prog(lt, 2.5, k.D + 0.2))
    w2 = ease_in_out(prog(lt, 0.6, k.D + 0.2))
    cx, cy = lerp(-100, CITY[0], w2), lerp(80, CITY[1], w2)
    rot = lerp(55, 0, u) - 6 * smooth(prog(lt, 2.5, k.D))
    c.save()
    world_cam(c, cx, cy, z, rot)
    draw_map(c, k.t)
    c.restore()
    alt = 1 / z
    # neblina rosada sobre las nubes al inicio
    haze = clamp(1 - prog(lt, 0.2, 1.5))
    if haze > 0:
        c.drawRect(RECT(0, 0, W, H), P("#ffe6ef", shader=lin(0, 0, 0, H, ["#ffd2a8", "#ffe6ef", "#c9b8ff"]), alpha=haze))
    clouds3d(c, alt + 0.3, k.t)
    glow(c, R.RES.glow_warm, 900, 200, 900, 0.35 * (1 - u) + 0.1, skia.BlendMode.kScreen)
    # textos
    d5 = prog(lt, T(1) - 0.1, T(1) + 0.15)
    out5 = prog(lt, T(4) - 0.15, T(4) + 0.05)
    if d5 > 0 and out5 < 1:
        c.save()
        c.translate(540, 1020)
        c.scale(1 + 0.6 * out5, 1 + 0.6 * out5)
        c.saveLayerAlpha(None, int(255 * (1 - out5)))
        pop_text(c, "5", 0, 120, 360, d5, shader=sunset_text_shader(-150, 120))
        pop_text(c, "DÍAS", 0, 250, 110, prog(lt, T(2) - 0.1, T(2) + 0.15))
        c.restore()
        c.restore()
    g = prog(lt, T(4) - 0.1, T(4) + 0.2)
    if g > 0:
        sh = shake(k.t, 8 * (1 - clamp((lt - T(4)) / 0.4)))
        pop_text(c, "GTA 6", 540 + sh[0], 1120 + sh[1], 190, g, rot=-4, shader=sunset_text_shader(980, 1120))
        q = prog(lt, T(8) - 0.1, T(8) + 0.2)
        tag(c, "CASI NADIE LO SABE", 540, 1260, q, bg=LIME, fg="#14061f", size=44, rot=3)


# ----------------------------------------------------------------------------
# escena 2: tamaño del mapa
# ----------------------------------------------------------------------------
SHAPES5 = [(-280, -380, 480, 560, 0), (330, 420, 440, 560, 1)]
SHAPES3 = [("GTA 4", "#4aa8ff", -760, -800, 330, 230, 5), ("GTA 5", "#ff3d7f", 120, -180, 430, 520, 6),
           ("RED DEAD 2", "#ff9a2e", 420, 720, 420, 420, 8)]


def drop_shape(c, x, y, rx, ry, col, label, k, seed, t):
    if k <= 0:
        return
    s = lerp(2.4, 1.0, ease_out(clamp(k * 1.4)))
    a = clamp(k * 3)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    p = blob(seed, rx, ry)
    c.drawPath(p, P(col, alpha=0.55 * a))
    pp = P("#ffffff", "stroke", 14, alpha=a)
    pp.setPathEffect(skia.DashPathEffect.Make([40, 24], -t * 120))
    c.drawPath(p, pp)
    f = F(R.RES.mx, 92)
    w = f.measureText(label)
    c.drawString(label, -w / 2, 30, f, P("#14061f", "stroke", 16, alpha=a))
    c.drawString(label, -w / 2, 30, f, P("#ffffff", alpha=a))
    c.restore()
    if 0 < k < 0.6:  # onda del impacto
        q = k / 0.6
        oval(c, x, y, rx * (1 + q), ry * (1 + q), P("#ffffff", "stroke", 18 * (1 - q), alpha=1 - q))


def scene2(c, k):
    lt, T = k.lt, k.w
    zo = ease_in_out(prog(lt, 0.0, 1.0))
    z = 1.7 * (0.40 / 1.7) ** zo
    bumps = [T(5), T(8), T(14), T(16), T(21), T(22)]
    bump = sum(max(0, 1 - abs(lt - b - 0.08) / 0.18) for b in bumps)
    z *= 1 + 0.06 * bump
    cx = lerp(CITY[0], -160, zo) + 40 * math.sin(lt * 0.7)
    cy = lerp(CITY[1], 150, zo)
    rot = 7 * math.sin(lt * 0.55) - 2
    sh = shake(k.t, 10 * bump)
    c.save()
    world_cam(c, cx, cy, z, rot, sh=sh)
    draw_map(c, k.t, labels=prog(lt, 0.8, 1.3) * (1 - prog(lt, T(4), T(5))))
    second = prog(lt, T(13) - 0.15, T(13) + 0.1)
    for i, (x, y, rx, ry, sd) in enumerate(SHAPES5):
        kk = prog(lt, T(5) + i * 0.45 - 0.1, T(5) + i * 0.45 + 0.4)
        if second < 1:
            c.saveLayerAlpha(None, int(255 * (1 - second)))
            drop_shape(c, x, y, rx, ry, "#ff3d7f", "GTA 5", kk, 30 + sd, k.t)
            c.restore()
    for i, (lab, col, x, y, rx, ry, sd) in enumerate(SHAPES3):
        wi = (14, 17, 20)[i]
        drop_shape(c, x, y, rx, ry, col, lab, prog(lt, T(wi) - 0.1, T(wi) + 0.35), sd, k.t)
    jn = prog(lt, T(22) - 0.1, T(22) + 0.3)
    if jn > 0:
        land = smooth_path(LAND)
        c.drawPath(land, P(LIME, "stroke", 26 * (1 + 0.3 * math.sin(lt * 10)), alpha=jn))
    c.restore()
    x2 = prog(lt, T(5) + 0.45, T(5) + 0.75) * (1 - second)
    pop_text(c, "x2", 830, 680, 200, x2, rot=10, shader=sunset_text_shader(530, 680))
    tag(c, "MAPA DE GTA 6", 300, 640, prog(lt, 0.9, 1.2) * (1 - prog(lt, T(4), T(5))), bg="#14061f", size=40, rot=-4)
    pop_text(c, "= JUNTOS", 540, 1620, 110, jn, col=LIME)


# ----------------------------------------------------------------------------
# escena 3: 170 especies y animales legendarios (paneo por el pantano)
# ----------------------------------------------------------------------------


def cypress(c, x, base, h, col, t, seed):
    c.drawRect(RECT(x - h * 0.03, base - h, x + h * 0.03, base), P(col))
    r = rng(seed)
    for i in range(7):
        yy = base - h + i * h * 0.1
        rw = h * (0.12 + 0.05 * i)
        oval(c, x + (r.random() - 0.5) * 30, yy, rw, h * 0.07, P(col))
        sw = 4 * math.sin(t * 1.5 + i)
        c.drawLine(x - rw * 0.6, yy, x - rw * 0.6 + sw, yy + h * 0.12, P(col, "stroke", 4))  # musgo


def flamingo(c, x, y, s, t, ph=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pk = P("#ff6fa8", shader=lin(-60, -80, 60, 40, ["#ff9cc6", "#ff4f8f"]))
    c.drawLine(0, 0, 0, 170, P("#e0507f", "stroke", 7))
    leg = skia.Path()
    leg.moveTo(8, 0)
    leg.lineTo(30, 70)
    leg.lineTo(8, 90)
    c.drawPath(leg, P("#e0507f", "stroke", 7))
    oval(c, 0, -20, 70, 42, pk)
    neck = skia.Path()
    bob = 6 * math.sin(t * 2 + ph)
    neck.moveTo(50, -40)
    neck.cubicTo(110, -90, 20, -150, 60, -210 + bob)
    c.drawPath(neck, P("#ff6fa8", "stroke", 16))
    oval(c, 66, -216 + bob, 20, 16, pk)
    bk = skia.Path()
    bk.moveTo(80, -222 + bob)
    bk.lineTo(112, -206 + bob)
    bk.lineTo(84, -204 + bob)
    bk.close()
    c.drawPath(bk, P("#1a1a1a"))
    oval(c, 70, -220 + bob, 4, 4, P("#1a1a1a"))
    c.restore()


def alligator(c, x, y, s, t):
    c.save()
    c.translate(x, y + 6 * math.sin(t * 1.3))
    c.scale(s, s)
    oval(c, 0, 20, 300, 26, P("#0d3a3a", alpha=0.5))
    body = skia.Path()
    body.moveTo(-320, 10)
    body.quadTo(-100, -40, 120, -20)
    body.lineTo(300, -16)
    body.quadTo(330, 0, 300, 12)
    body.lineTo(-320, 14)
    body.close()
    c.drawPath(body, P("#4c7a3a", shader=lin(0, -40, 0, 14, ["#6f9e4a", "#3a5e2c"])))
    for i in range(12):
        oval(c, -240 + i * 34, -22 + abs(i - 6) * 1.5, 9, 9, P("#3a5e2c"))
    for dx in (100, 140):
        oval(c, dx, -34, 14, 14, P("#6f9e4a"))
        oval(c, dx, -36, 7, 7, P("#ffd84a"))
        oval(c, dx, -36, 2.5, 6, P("#1a1a1a"))
    c.drawLine(180, 0, 300, 0, P("#2a3e1e", "stroke", 3))
    c.restore()


def pelican(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    fl = math.sin(t * 7)
    for side in (-1, 1):
        wing = skia.Path()
        wing.moveTo(0, 0)
        wing.quadTo(side * 80, -60 * fl - 20, side * 170, -10 - 70 * fl)
        wing.quadTo(side * 90, 10, 0, 14)
        c.drawPath(wing, P("#f4f1ea"))
        c.drawLine(side * 110, -20 - 50 * fl, side * 170, -10 - 70 * fl, P("#3a3a44", "stroke", 8))
    oval(c, 0, 4, 60, 24, P("#ffffff"))
    oval(c, 56, -6, 18, 16, P("#ffffff"))
    bk = skia.Path()
    bk.moveTo(68, -8)
    bk.lineTo(150, 4)
    bk.quadTo(100, 24, 68, 6)
    bk.close()
    c.drawPath(bk, P("#ffb02e"))
    c.restore()


def manatee(c, x, y, s, t):
    c.save()
    c.translate(x + 30 * math.sin(t * 0.6), y)
    c.scale(s, s)
    c.saveLayerAlpha(None, 170)
    oval(c, 0, 0, 170, 70, P("#8a9aa6", shader=lin(0, -70, 0, 70, ["#a9b8c2", "#6a7a86"])))
    tail = skia.Path()
    tail.moveTo(-150, 0)
    tail.quadTo(-250, -60, -260, 0)
    tail.quadTo(-250, 60, -150, 0)
    c.drawPath(tail, P("#7a8a96"))
    oval(c, 150, -6, 50, 44, P("#9aa9b4"))
    oval(c, 186, 6, 22, 18, P("#b8c4cc"))
    oval(c, 160, -20, 5, 5, P("#1a1a1a"))
    oval(c, 40, 50, 40, 14, P("#7a8a96"))
    c.restore()
    c.restore()


def monkey(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    tail = skia.Path()
    tail.moveTo(-20, 40)
    tail.cubicTo(-80, 120, 20, 160, -30, 220 + 10 * math.sin(t * 2))
    c.drawPath(tail, P("#8a5a32", "stroke", 10))
    oval(c, 0, 20, 46, 56, P("#a06a3a"))
    oval(c, 0, -50, 40, 38, P("#a06a3a"))
    for sd in (-1, 1):
        oval(c, sd * 40, -54, 14, 14, P("#d9a77a"))
    oval(c, 0, -42, 26, 24, P("#e8b78c"))
    for sd in (-1, 1):
        oval(c, sd * 10, -50, 5, 6, P("#1a1a1a"))
    c.drawLine(-36, 0, -70, -60, P("#a06a3a", "stroke", 14))
    c.restore()


def iguana(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    body = skia.Path()
    body.moveTo(-240, 0)
    body.quadTo(-80, -10, 0, -30)
    body.quadTo(80, -50, 120, -30)
    body.quadTo(80, 0, -240, 6)
    c.drawPath(body, P("#5fbf4a", shader=lin(0, -50, 0, 6, ["#8fe060", "#3f9a3a"])))
    for i in range(8):
        tri = skia.Path()
        bx = -20 + i * 14
        tri.moveTo(bx, -34 - i * 1.5)
        tri.lineTo(bx + 6, -54 - i * 1.5)
        tri.lineTo(bx + 12, -36 - i * 1.5)
        c.drawPath(tri, P("#3f9a3a"))
    oval(c, 96, -38, 5, 5, P("#1a1a1a"))
    oval(c, 70, -16, 14, 16, P("#ffb24a", alpha=0.8))
    c.restore()


def swamp(c, k, camx, z, dark):
    t = k.t
    c.drawRect(RECT(0, 0, W, H), P("#ff8a62", shader=lin(0, 0, 0, 1180, ["#3b2a7a", "#c45a8a", "#ff8a62", "#ffc27a"], [0, .35, .7, 1])))
    glow(c, R.RES.glow_warm, 760 - camx * 0.05, 1000, 520, 0.6, skia.BlendMode.kScreen)
    oval(c, 760 - camx * 0.05, 1060, 110, 110, P("#ffe9b0", alpha=0.95))
    c.save()
    c.translate(540, 1150)
    c.scale(z, z)
    c.translate(-540, -1150)

    def layer(p):
        c.save()
        c.translate(-camx * p, 0)

    layer(0.25)
    r = rng(5)
    path = skia.Path()
    path.moveTo(-200, 1180)
    for i in range(40):
        path.lineTo(-200 + i * 90, 1100 - r.random() * 90)
    path.lineTo(3400, 1180)
    path.close()
    c.drawPath(path, P("#4a2a5a"))
    c.restore()
    c.drawRect(RECT(-500, 1170, W + 500, H + 500), P("#2a6f7a", shader=lin(0, 1170, 0, H, ["#e0897a", "#3a7f8a", "#123a48"], [0, .2, 1])))
    layer(0.6)
    for i in range(14):
        cypress(c, -100 + i * 260, 1200, 360 + 120 * math.sin(i * 2.1), "#22383a", t, i)
    for i in range(30):
        c.drawLine(-200 + i * 120, 1230 + (i % 3) * 30, -140 + i * 120, 1230 + (i % 3) * 30, P("#ffd8a8", "stroke", 4, alpha=0.35))
    c.restore()
    layer(1.0)
    flamingo(c, 380, 1400, 1.1, t)
    flamingo(c, 560, 1440, 0.95, t, 1.3)
    flamingo(c, 230, 1460, 0.8, t, 2.1)
    pelican(c, 900 + 60 * k.lt, 800 + 20 * math.sin(t * 2), 0.9, t)
    alligator(c, 1150, 1540, 1.0, t)
    cypress(c, 1600, 1330, 640, "#2e4a3c", t, 99)
    c.drawLine(1600, 1000, 1760, 960, P("#2e4a3c", "stroke", 20))
    monkey(c, 1720, 900, 1.0, t)
    manatee(c, 1900, 1690, 1.0, t)
    rrect(c, 2180, 1420, 2560, 1470, 24, P("#6a4a2a"))
    iguana(c, 2380, 1418, 1.0, t)
    c.restore()
    if dark > 0:  # el legendario: silueta gigante entre la niebla
        c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#0c0820", alpha=0.62 * dark))
        layer(1.0)
        lx, ly = 2700, 1200
        c.save()
        c.translate(lx, ly)
        s = lerp(0.8, 1.0, dark)
        c.scale(s, s)
        head = skia.Path()
        head.moveTo(-260, 120)
        head.cubicTo(-300, -160, -150, -300, 0, -300)
        head.cubicTo(150, -300, 300, -160, 260, 120)
        head.close()
        c.drawPath(head, P("#05040c", alpha=dark))
        for sd in (-1, 1):
            ear = skia.Path()
            ear.moveTo(sd * 120, -270)
            ear.lineTo(sd * 200, -400)
            ear.lineTo(sd * 240, -200)
            ear.close()
            c.drawPath(ear, P("#05040c", alpha=dark))
            blink = 1 - max(0, 1 - abs(((k.lt * 0.7) % 1) - 0.5) * 30)
            glow(c, R.RES.glow_warm, sd * 90, -110, 120, 0.9 * dark)
            oval(c, sd * 90, -110, 34, 18 * blink, P("#ffe04a", alpha=dark))
            oval(c, sd * 90, -110, 6, 15 * blink, P("#14061f", alpha=dark))
        c.restore()
        c.restore()
        for i in range(8):  # niebla
            x = (i * 260 + k.t * 40) % 1600 - 260
            glow(c, cloud_img(), x, 1520 + 40 * math.sin(i), 380, 0.25 * dark, skia.BlendMode.kSrcOver)
    layer(1.5)
    for i in range(70):
        x = -200 + i * 60
        hgt = 140 + 80 * math.sin(i * 1.7)
        sw = 18 * math.sin(t * 1.8 + i * 0.4)
        bl = skia.Path()
        bl.moveTo(x, 1960)
        bl.quadTo(x + 6, 1960 - hgt / 2, x + sw, 1960 - hgt)
        c.drawPath(bl, P("#16301f", "stroke", 12))
    c.restore()
    c.restore()


def scene3(c, k):
    lt, T = k.lt, k.w
    leg = T(10) - 0.1
    camx = lerp(0, 1800, ease_in_out(prog(lt, 0, leg + 0.4))) + 260 * ease_in_out(prog(lt, leg, k.D))
    z = 1.0 + 0.35 * ease_in_out(prog(lt, leg, k.D)) + 0.03 * math.sin(lt * 2)
    dark = smooth(prog(lt, leg - 0.3, leg + 0.4))
    sh = shake(k.t, 5 * max(0, 1 - abs(lt - T(10)) / 0.3))
    c.save()
    c.translate(*sh)
    swamp(c, k, camx, z, dark)
    c.restore()
    ck = prog(lt, T(3) - 0.15, T(3) + 0.15)
    if ck > 0:
        n = int(170 * ease_out(prog(lt, T(3) - 0.1, T(3) + 0.6)))
        out = prog(lt, leg - 0.2, leg + 0.1)
        c.save()
        c.translate(lerp(0, -900, ease_in_out(out)), 0)
        pop_text(c, f"+{n}", 540, 760, 200, ck, shader=sunset_text_shader(610, 760))
        tag(c, "ESPECIES", 540, 850, prog(lt, T(4) - 0.1, T(4) + 0.2), bg=LIME, fg="#14061f", size=46, rot=-3)
        c.restore()
    lg = prog(lt, T(10) - 0.1, T(10) + 0.2)
    tag(c, "LEGENDARIO", 540, 1560, lg, bg="#ffcf3a", fg="#14061f", size=52, rot=-3)
    pop_text(c, "?", 860, 820, 220, prog(lt, T(10), T(10) + 0.3), col="#ffe04a", rot=12)
    st = prog(lt, T(12) - 0.1, T(12) + 0.15)
    if st > 0:
        s = lerp(2.2, 1.0, ease_out(st))
        c.save()
        c.translate(400, 760)
        c.rotate(-14)
        c.scale(s, s)
        a = clamp(st * 3)
        rrect(c, -260, -70, 260, 60, 14, P("#ff2a4a", "stroke", 12, alpha=a))
        text_center(c, "SECRETO", 0, 30, F(R.RES.mx, 92), P("#ff2a4a", alpha=a))
        c.restore()


# ----------------------------------------------------------------------------
# anuncio: el video se pausa, se difumina y aparece el teléfono
# ----------------------------------------------------------------------------


def frozen(c, idx, sigma, dim):
    """Dibuja el último instante de la escena idx difuminado."""
    s = VO[idx]
    t = s["end"] - 0.02
    k = R.Ctx(VO, idx, t)
    if sigma > 0.3:
        p = skia.Paint()
        p.setImageFilter(skia.ImageFilters.Blur(sigma, sigma, skia.TileMode.kClamp))
        c.saveLayer(None, p)
    c.save()
    SCENES[idx](c, k)
    c.restore()
    if sigma > 0.3:
        c.restore()
    if dim > 0:
        c.drawRect(RECT(0, 0, W, H), P("#0a0614", alpha=dim))


def pause_icon(c, k, x=540, y=1050):
    if k <= 0 or k >= 1:
        return
    a = math.sin(math.pi * k)
    s = lerp(0.7, 1.15, ease_out(k))
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, 0, 130, 130, P("#000000", alpha=0.45 * a))
    for dx in (-36, 36):
        rrect(c, dx - 18, -55, dx + 18, 55, 8, P("#ffffff", alpha=a))
    c.restore()


def ad_scene(prev, final=False):
    def scene(c, k):
        lt, T = k.lt, k.w
        bl = ease_out(prog(lt, 0.0, 0.3))
        frozen(c, prev, 22 * bl, 0.5 * bl)
        # barra de "pausa" de reproductor
        rrect(c, 60, 1740, W - 60, 1748, 4, P("#ffffff", alpha=0.3 * bl))
        rrect(c, 60, 1740, lerp(60, W - 60, 0.45 if not final else 0.92), 1748, 4, P("#ff2a4a", alpha=bl))
        oval(c, lerp(60, W - 60, 0.45 if not final else 0.92), 1744, 14, 14, P("#ff2a4a", alpha=bl))
        pause_icon(c, prog(lt, 0.0, 0.7))
        draw_img(c, R.RES.vlogo, 110, 150, 80, alpha=bl)
        ph = ease_out(prog(lt, 0.25, 0.65))
        fy = 1080 + 14 * math.sin(k.t * 1.8) + 900 * (1 - ph)

        def screen(c2, x0, y0, x1, y1):
            c2.drawRect(RECT(x0, y0, x1, y1), P("#1a1030", shader=lin(0, y0, 0, y1, ["#ff8a3d", "#c43a8a", "#3a1a6a"])))
            oval(c2, (x0 + x1) / 2, y0 + 260, 90, 90, P("#ffe9b0", alpha=0.8))
            for i in range(4):
                c2.drawRect(RECT(x0 + 20 + i * 95, y1 - 300 + (i % 2) * 60, x0 + 90 + i * 95, y1), P("#2a0f3a", alpha=0.85))
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            pulse = 1 + 0.07 * math.sin(k.t * 5)
            oval(c2, cx, cy, 85 * pulse, 85 * pulse, P("#ffffff", alpha=0.95))
            tri = skia.Path()
            tri.moveTo(cx - 24, cy - 38)
            tri.lineTo(cx + 42, cy)
            tri.lineTo(cx - 24, cy + 38)
            tri.close()
            c2.drawPath(tri, P(VIO))
            prg = (k.t * 0.3) % 1
            rrect(c2, x0 + 30, y1 - 60, x1 - 30, y1 - 50, 5, P("#ffffff", alpha=0.3))
            rrect(c2, x0 + 30, y1 - 60, lerp(x0 + 30, x1 - 30, prg), y1 - 50, 5, P(LIME))
        if ph > 0:
            V.phone(c, 540, fy, 420, 820, screen, rot=-5 + 2 * math.sin(k.t * 1.3), glow_a=0.9 * ph)
        pi = 9 if final else 8
        pk = prog(lt, T(pi) - 0.15, T(pi) + 0.15)
        if pk > 0:
            s = back_out(pk, 2.2)
            c.save()
            c.translate(770, fy - 300)
            c.rotate(14)
            c.scale(s, s)
            c.drawLine(-90, -20, -160, -70, P("#e9e4f0", "stroke", 4))
            tg = skia.Path()
            tg.moveTo(-110, 0)
            tg.lineTo(-70, -60)
            tg.lineTo(110, -60)
            tg.lineTo(110, 60)
            tg.lineTo(-70, 60)
            tg.close()
            glow(c, R.RES.g_lime, 0, 0, 220, 0.6)
            c.drawPath(tg, P(LIME))
            oval(c, -76, 0, 10, 10, P("#000000"))
            text_center(c, "$5", 20, 34, F(R.RES.mx, 96), P("#14061f"))
            c.restore()
            use("lime")
            R.burst(c, 770, fy - 300, lt - T(pi) + 0.1, dur=0.9, n=36, radius=300, seed=6, intensity=0.8)
        text_center(c, "VELTO STUDIO", 540, 1560, F(R.RES.mx, 40), P("#ffffff", alpha=0.9 * ph))
        if final:
            bk = ease_out(prog(lt, T(0), T(0) + 0.3))
            if bk > 0:
                c.save()
                c.translate(540, 560)
                c.scale(bk, bk)
                rrect(c, -290, -46, 290, 46, 46, P("#ffffff"))
                oval(c, -240, 0, 26, 26, P(VIO))
                typed = "VIDEO"[: int(5 * prog(lt, T(1) - 0.2, T(1) + 0.2))]
                if typed:
                    c.drawString(typed, -196, 16, F(R.RES.mx, 44), P("#14061f"))
                else:
                    c.drawString("Comenta...", -196, 12, F(R.RES.ms, 30), P("#8a7aa8"))
                c.restore()
            r = rng(29)
            for i in range(12):
                side = -1 if i % 2 == 0 else 1
                x = 540 + side * (400 + r.random() * 70)
                u = (lt - (T(1) + i * 0.12)) / 2.0
                if u <= 0 or u >= 1:
                    continue
                yy = lerp(1500, 620, u)
                a = math.sin(math.pi * u)
                tx = ["VIDEO", "¡VIDEO!", "VIDEO!!", "VIDEO"][i % 4]
                f = F(R.RES.mx, 24)
                w = f.measureText(tx) + 64
                c.save()
                c.translate(x + 16 * math.sin(lt * 2 + i), yy)
                rrect(c, -w / 2, -26, w / 2, 26, 26, P("#2c2540", alpha=0.9 * a))
                oval(c, -w / 2 + 26, 0, 14, 14, P([VIO2, LIME, "#ff6fb1", "#5ad1ff"][i % 4], alpha=a))
                c.drawString(tx, -w / 2 + 50, 9, f, P("#ffffff", alpha=a))
                c.restore()
    return scene


# ----------------------------------------------------------------------------
# escena 5: huracán (vista satélite girando) y después de la tormenta
# ----------------------------------------------------------------------------


def hurricane(c, x, y, t, s=1.0):
    img = cloud_img()
    c.save()
    c.translate(x, y)
    c.rotate(-t * 70)
    c.scale(s, s)
    glow(c, R.RES.soft_dark, 40, 60, 900, 0.35, skia.BlendMode.kSrcOver)
    for arm in range(4):
        for i in range(34):
            a = arm * 1.5708 + i * 0.16
            rr = 70 + i * 20
            px, py = math.cos(a) * rr, math.sin(a) * rr
            glow(c, img, px, py, 70 + i * 4, 0.8 * (1 - i / 40), skia.BlendMode.kSrcOver)
    oval(c, 0, 0, 46, 46, P("#1a5a7a", alpha=0.6))
    c.restore()


def palm(c, x, base, h, t, lean=0.0, col_trunk="#8a5a32", col_leaf="#2f8f4a", wind=0.0):
    top = (x + h * lean, base - h)
    tr = skia.Path()
    tr.moveTo(x, base)
    tr.quadTo(x + h * lean * 0.2, base - h * 0.5, *top)
    c.drawPath(tr, P(col_trunk, "stroke", h * 0.06))
    for i in range(7):
        a = -150 + i * 50 + 10 * math.sin(t * 2 + i) + wind
        rad_ = math.radians(a)
        L = h * 0.42
        lf = skia.Path()
        lf.moveTo(*top)
        ex, ey = top[0] + math.cos(rad_) * L, top[1] + math.sin(rad_) * L * 0.6 + L * 0.25
        lf.quadTo(top[0] + math.cos(rad_) * L * 0.5, top[1] - L * 0.25, ex, ey)
        c.drawPath(lf, P(col_leaf, "stroke", h * 0.05))


def after_storm(c, k, u):
    t = k.t
    c.drawRect(RECT(-500, -500, W + 500, 1250), P("#6fb0e0", shader=lin(0, 0, 0, 1250, ["#4a86c8", "#9cd0ee", "#ffe2b8"])))
    for i in range(6):
        glow(c, cloud_img(), (i * 300 + t * 30) % 1700 - 300, 700 + (i % 3) * 120, 260, 0.75, skia.BlendMode.kSrcOver)
        glow(c, R.RES.soft_dark, (i * 300 + t * 30) % 1700 - 280, 760 + (i % 3) * 120, 220, 0.12, skia.BlendMode.kSrcOver)
    c.drawRect(RECT(-500, 1180, W + 500, 1260), P("#2aa6c0"))
    cols = ["#ffb3c9", "#bdf2dc", "#ffe28a", "#c9d6ff"]
    for i, (x0, w, h) in enumerate(((-220, 300, 420), (90, 260, 300), (720, 300, 380), (1010, 300, 460))):
        c.drawRect(RECT(x0, 1300 - h, x0 + w, 1300), P(cols[i]))
        for r_ in range(int(h / 70)):
            for cc in range(3):
                broken = (i + r_ + cc) % 4 == 0
                c.drawRect(RECT(x0 + 30 + cc * 80, 1300 - h + 30 + r_ * 70, x0 + 80 + cc * 80, 1300 - h + 70 + r_ * 70),
                           P("#2a3a5a" if broken else "#7fd6ff"))
        c.drawRect(RECT(x0, 1300 - h, x0 + w, 1300 - h + 18), P("#ffffff", alpha=0.7))
    c.drawRect(RECT(-500, 1300, W + 500, H + 500), P("#55606e", shader=lin(0, 1300, 0, H, ["#6a7482", "#3a424e"])))
    for i in range(8):
        c.drawRect(RECT(-60 + i * 170, 1600, 30 + i * 170, 1615), P("#f2e9c8", alpha=0.6))
    for x, y, rx, ry in ((260, 1720, 200, 36), (820, 1500, 150, 26), (560, 1830, 240, 40)):  # charcos
        oval(c, x, y, rx, ry, P("#9cd0ee", alpha=0.75))
        oval(c, x - rx * 0.3, y - ry * 0.2, rx * 0.4, ry * 0.25, P("#ffffff", alpha=0.5))
    # palmera caída
    c.save()
    c.translate(140, 1460)
    c.rotate(-78)
    palm(c, 0, 0, 560, 0, lean=0.0, wind=0)
    c.restore()
    palm(c, 960, 1320, 520, t, lean=0.25)
    # auto volteado
    c.save()
    c.translate(640, 1450)
    c.rotate(180 + 8)
    rrect(c, -170, -50, 170, 50, 30, P("#ff3d7f"))
    rrect(c, -100, -110, 90, -40, 30, P("#ff3d7f"))
    rrect(c, -86, -98, 76, -52, 16, P("#9cd0ee"))
    for dx in (-110, 110):
        oval(c, dx, 50, 42, 42, P("#1a1a1a"))
        oval(c, dx, 50, 18, 18, P("#9aa0aa"))
    c.restore()
    # escombros
    r = rng(61)
    for i in range(10):
        c.save()
        c.translate(80 + r.random() * 900, 1380 + r.random() * 480)
        c.rotate(r.random() * 180)
        rrect(c, -50, -9, 50, 9, 3, P(["#8a5a32", "#c9b08a", "#7a7a86"][i % 3]))
        c.restore()
    c.save()  # señal doblada
    c.translate(330, 1310)
    c.rotate(-24)
    c.drawRect(RECT(-6, -300, 6, 0), P("#9aa0aa"))
    rrect(c, -70, -380, 70, -290, 10, P("#2a8a4a"))
    text_center(c, "OCEAN DR", 0, -322, F(R.RES.mx, 26), P("#ffffff"))
    c.restore()


def scene5(c, k):
    lt, T = k.lt, k.w
    sw = T(2) - 0.15
    if lt < sw:
        u = lt / sw
        z = lerp(0.55, 0.95, ease_in_out(u))
        rot = lt * 50
        sh = shake(k.t, 14)
        blur = 26 * (1 - ease_out(prog(lt, 0, 0.25)))
        if blur > 0.3:
            p = skia.Paint()
            p.setImageFilter(skia.ImageFilters.Blur(blur, blur, skia.TileMode.kClamp))
            c.saveLayer(None, p)
        c.save()
        world_cam(c, 560, 520, z, rot, sh=sh)
        draw_map(c, k.t)
        hurricane(c, 560, 520, k.t, 1.3)
        c.restore()
        c.drawRect(RECT(0, 0, W, H), P("#0a1a3a", alpha=0.25))
        for i in range(30):  # viento
            y = (i * 71) % 1900
            x = (k.t * 2600 + i * 337) % 1600 - 300
            c.drawLine(x, y, x + 180, y + 20, P("#ffffff", "stroke", 3, alpha=0.35))
        if blur > 0.3:
            c.restore()
        pop_text(c, "HURACANES", 540, 1250, 120, prog(lt, T(1) - 0.1, T(1) + 0.2), rot=-5, shader=lin(0, 1150, 0, 1250, ["#ffffff", "#9cd0ee"]))
        return
    u = lt - sw
    wh = 1 - ease_out(clamp(u / 0.22))
    p = None
    if wh > 0.02:
        p = skia.Paint()
        p.setImageFilter(skia.ImageFilters.Blur(60 * wh, 2, skia.TileMode.kClamp))
        c.saveLayer(None, p)
    c.save()
    z = lerp(1.0, 1.22, ease_in_out(prog(u, 0, k.D - sw)))
    c.translate(540 + 400 * wh, 1300)
    c.rotate(lerp(-5, 2, ease_in_out(prog(u, 0, 2.5))))
    c.scale(z, z)
    c.translate(-540, -1300)
    after_storm(c, k, u)
    c.restore()
    if p is not None:
        c.restore()
    tag(c, "LOS DESTROZOS SE QUEDAN", 540, 760, prog(lt, T(6) - 0.1, T(6) + 0.2), bg="#ff2a4a", size=44, rot=-3)


# ----------------------------------------------------------------------------
# escena 6: cada persona es distinta (travelling por el malecón)
# ----------------------------------------------------------------------------
PEOPLE = [  # (x, altura, ancho, panza, piel, camisa, pantalón, pelo)
    (120, 1.00, 1.00, 0.0, "#f2c9a0", "#ff6fa8", "#2a3a5a", "#2a1a10"),
    (330, 1.22, 0.85, 0.0, "#8a5a3a", "#4ad1c9", "#f4f1ea", "#120a06"),
    (520, 0.82, 1.10, 0.3, "#d9a77a", "#ffd84a", "#3a2a5a", "#5a3a20"),
    (720, 1.08, 1.45, 1.0, "#f2c9a0", "#ffffff", "#4a6aa8", "#8a8a8a"),
    (930, 0.92, 0.80, 0.0, "#5a3a24", "#a64dff", "#14141a", "#120a06"),
    (1130, 1.15, 1.05, 0.2, "#e8b78c", "#ff8a3d", "#2a2a3a", "#d9b04a"),
    (1330, 0.75, 0.95, 0.0, "#f2c9a0", "#5ab0ff", "#ff6fa8", "#5a3a20"),
    (1520, 1.05, 1.25, 0.6, "#a06a3a", "#2fbf6a", "#3a3a44", "#120a06"),
    (1720, 1.18, 0.90, 0.0, "#f8d6b8", "#ff3d7f", "#14141a", "#ff9a2e"),
]


def walker(c, x, base, hs, ws, belly, skin, shirt, pants, hair, t, ph, hl=0.0):
    H0 = 520 * hs
    sw = math.sin(t * 6 + ph)
    c.save()
    c.translate(x, base - abs(math.sin(t * 6 + ph)) * 8)
    oval(c, 0, 0, 90 * ws, 16, P("#000000", alpha=0.25))
    leg_top = -H0 * 0.47
    for sd in (-1, 1):
        c.drawLine(sd * 22 * ws, leg_top, sd * 22 * ws + sd * sw * 16, -6, P(pants, "stroke", 34 * ws))
        oval(c, sd * 22 * ws + sd * sw * 16, -6, 24 * ws, 12, P("#1a1a1a"))
    tw = 70 * ws
    torso = skia.Path()
    torso.moveTo(-tw, -H0 * 0.8)
    torso.lineTo(tw, -H0 * 0.8)
    torso.quadTo(tw + belly * 50, -H0 * 0.6, tw * 0.9 + belly * 30, leg_top)
    torso.lineTo(-tw * 0.9 - belly * 30, leg_top)
    torso.quadTo(-tw - belly * 50, -H0 * 0.6, -tw, -H0 * 0.8)
    torso.close()
    c.drawPath(torso, P(shirt))
    if hl > 0:
        oval(c, 0, -H0 * 0.6, tw + belly * 60 + 30, H0 * 0.18, P(LIME, "stroke", 8, alpha=hl))
    for sd in (-1, 1):
        c.drawLine(sd * (tw + 4), -H0 * 0.78, sd * (tw + 20 + belly * 30), -H0 * 0.5 - sd * sw * 20, P(shirt, "stroke", 26 * ws))
        oval(c, sd * (tw + 20 + belly * 30), -H0 * 0.5 - sd * sw * 20, 16, 16, P(skin))
    c.drawRect(RECT(-14, -H0 * 0.86, 14, -H0 * 0.78), P(skin))
    oval(c, 0, -H0 * 0.92, 52, 58, P(skin))
    hp = skia.Path()
    hp.addArc(RECT(-54, -H0 * 0.92 - 62, 54, -H0 * 0.92 + 30), 180, 180)
    c.drawPath(hp, P(hair))
    for sd in (-1, 1):
        oval(c, sd * 18, -H0 * 0.91, 5, 6, P("#1a1a1a"))
    c.drawLine(-12, -H0 * 0.875, 12, -H0 * 0.875, P("#8a3a3a", "stroke", 4))
    c.restore()
    return H0


def scene6(c, k):
    lt, T = k.lt, k.w
    camx = lerp(-40, 860, ease_in_out(prog(lt, 0, k.D)))
    z = 1.05 + 0.1 * math.sin(lt * 0.9)
    c.drawRect(RECT(0, 0, W, H), P("#ff8a62", shader=lin(0, 0, 0, 1100, ["#5a2a8a", "#ff5a8a", "#ffb36a"])))
    glow(c, R.RES.glow_warm, 300, 1000, 500, 0.7, skia.BlendMode.kScreen)
    oval(c, 300 - camx * 0.05, 1030, 120, 120, P("#ffe9b0"))
    c.drawRect(RECT(0, 1080, W, 1260), P("#2a6aa0", shader=lin(0, 1080, 0, 1260, ["#ff9a8a", "#2a6aa0"])))
    c.save()
    c.translate(540, 1500)
    c.scale(z, z)
    c.translate(-540 - camx * 0.5, -1500)
    for i in range(10):
        palm(c, -200 + i * 330, 1260, 420, k.t, lean=0.12, col_trunk="#3a1a3a", col_leaf="#3a1a3a")
    c.restore()
    c.save()
    c.translate(540, 1500)
    c.scale(z, z)
    c.translate(-540 - camx, -1500)
    c.drawRect(RECT(-600, 1260, 3000, 2400), P("#e8c9a0", shader=lin(0, 1260, 0, 1920, ["#f4d9b0", "#c99a70"])))
    for i in range(40):
        c.drawLine(-600 + i * 90, 1260, -800 + i * 110, 2400, P("#b98a60", "stroke", 3, alpha=0.4))
    hl_grasa = prog(lt, T(11) - 0.1, T(11) + 0.2)
    tops = []
    for i, (x, hs, ws, bel, sk, sh_, pa, hr) in enumerate(PEOPLE):
        xx = x + 30 * math.sin(k.t * 0.8 + i)
        H0 = walker(c, xx, 1700, hs, ws, bel, sk, sh_, pa, hr, k.t, i * 1.3, hl=hl_grasa if bel > 0.5 else 0)
        tops.append((xx, 1700 - H0 * 1.04))
    ak = prog(lt, T(4) - 0.1, T(4) + 0.2)
    if ak > 0:  # medidor de altura
        for i in (1, 6):
            x, top = tops[i]
            c.drawLine(x + 120, 1700, x + 120, lerp(1700, top, ease_out(ak)), P(LIME, "stroke", 8))
            c.drawLine(x + 100, top, x + 140, top, P(LIME, "stroke", 8, alpha=ak))
    bk = prog(lt, T(5) - 0.1, T(5) + 0.2)
    if bk > 0:
        for i in (4, 3):
            x, ws = PEOPLE[i][0], PEOPLE[i][2]
            w = 90 * ws + PEOPLE[i][3] * 50
            c.drawLine(x - w, 1760, x + w, 1760, P("#5ad1ff", "stroke", 8, alpha=bk))
            for sd in (-1, 1):
                c.drawLine(x + sd * w, 1740, x + sd * w, 1780, P("#5ad1ff", "stroke", 8, alpha=bk))
    c.restore()
    tag(c, "ALTURA", 260, 700, ak, bg=LIME, fg="#14061f", size=44, rot=-4)
    tag(c, "CUERPO", 540, 820, bk, bg="#5ad1ff", fg="#14061f", size=44, rot=3)
    tag(c, "¡HASTA LA GRASA!", 700, 940, hl_grasa, bg="#ff3d7f", size=46, rot=-3)


# ----------------------------------------------------------------------------
# escena 7: el precio (caja del juego girando y etiqueta que golpea)
# ----------------------------------------------------------------------------


def game_box(c, x, y, s, spin, t):
    c.save()
    c.translate(x, y)
    c.scale(s * max(0.04, math.cos(math.radians(spin))), s)
    w, h = 300, 400
    glow(c, R.RES.g_mag, 0, 0, 600, 0.5, skia.BlendMode.kScreen)
    rrect(c, -w + 16, -h + 24, w + 16, h + 24, 24, P("#000000", alpha=0.4, blur=14))
    rrect(c, -w, -h, w, h, 24, P("#ff8a3d", shader=lin(0, -h, 0, h, ["#ffcf6a", "#ff7a4a", "#d43a8a", "#4a1a7a"], [0, .35, .65, 1])))
    oval(c, 0, -60, 150, 150, P("#ffe9b0", alpha=0.9))
    for i in range(6):
        c.drawRect(RECT(-w + 10 + i * 100, -20 + 20 * (i % 3) + 140, -w + 90 + i * 100, h - 10), P("#2a0f3a"))
        c.drawRect(RECT(-w + 30 + i * 100, 40 + 20 * (i % 3) + 140, -w + 44 + i * 100, 60 + 20 * (i % 3) + 140), P("#ff8fc1"))
    palm(c, -220, h, 320, t, lean=0.15, col_trunk="#2a0f3a", col_leaf="#2a0f3a")
    palm(c, 230, h, 260, t, lean=-0.15, col_trunk="#2a0f3a", col_leaf="#2a0f3a")
    f = F(R.RES.mx, 150)
    tw = f.measureText("GTA 6")
    c.drawString("GTA 6", -tw / 2, -h + 200, f, P("#14061f", "stroke", 18))
    c.drawString("GTA 6", -tw / 2, -h + 200, f, P("#ffffff"))
    rrect(c, -w, -h, w, h, 24, P("#ffffff", "stroke", 6, alpha=0.6))
    c.restore()


def price_tag(c, x, y, txt, k, col, fg, rot, s0=1.0, strike=0.0):
    if k <= 0:
        return
    s = lerp(2.6, 1.0, ease_out(clamp(k))) * s0
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    a = clamp(k * 3)
    f = F(R.RES.mx, 120)
    w = f.measureText(txt) + 90
    tg = skia.Path()
    tg.moveTo(-w / 2 - 60, 0)
    tg.lineTo(-w / 2, -95)
    tg.lineTo(w / 2, -95)
    tg.lineTo(w / 2, 95)
    tg.lineTo(-w / 2, 95)
    tg.close()
    glow(c, R.RES.g_lime if col == LIME else R.RES.g_mag, 0, 0, w * 0.8, 0.6 * a)
    c.drawPath(tg, P(col, alpha=a))
    oval(c, -w / 2 - 10, 0, 14, 14, P("#14061f", alpha=a))
    c.drawString(txt, -w / 2 + 40, 44, f, P(fg, alpha=a))
    if strike > 0:
        c.drawLine(-w / 2 + 20, 10, lerp(-w / 2 + 20, w / 2 - 10, strike), -20, P("#ff2a4a", "stroke", 16))
    c.restore()


def scene7(c, k):
    lt, T = k.lt, k.w
    hit = T(8) - 0.08
    imp = max(0, 1 - (lt - hit) / 0.35) if lt >= hit else 0
    sh = shake(k.t, 22 * imp)
    z = lerp(1.25, 1.0, ease_out(prog(lt, 0, 0.8))) * (1 + 0.08 * imp)
    c.save()
    c.translate(540 + sh[0], 1060 + sh[1])
    c.rotate(lerp(-8, 0, ease_out(prog(lt, 0, 0.8))) + 2 * math.sin(lt * 1.3))
    c.scale(z, z)
    c.translate(-540, -1060)
    V.neon_bg(c, k.t, top="#2a0a3a", bottom="#0a0414", grid=0.16, waves=False)
    spin = lerp(80, 0, ease_out(prog(lt, 0, 0.7))) + 14 * math.sin(lt * 1.6)
    game_box(c, 540, 1080, lerp(0.8, 0.9, prog(lt, 0, k.D)), spin, k.t)
    c.restore()
    if imp > 0:
        c.drawRect(RECT(0, 0, W, H), P("#ffffff", alpha=0.5 * imp ** 2))
    use("lime")
    R.burst(c, 560, 1180, lt - hit, dur=1.0, n=50, radius=480, seed=12, intensity=0.9)
    price_tag(c, 560, 1180, "$79.99", prog(lt, hit - 0.12, hit + 0.1), LIME, "#14061f", -8)
    tag(c, "PRECIO REPORTADO", 560, 1330, prog(lt, hit + 0.2, hit + 0.5), bg="#14061f", size=30, rot=-8)
    up = prog(lt, T(10) - 0.1, T(10) + 0.2)
    pop_text(c, "+$20", 840, 1420, 130, up, col="#ff3d7f", rot=8)
    g5 = prog(lt, T(12) - 0.2, T(12) + 0.15)
    if g5 > 0:
        price_tag(c, 280, 1560, "$59.99", g5, "#d9d4e6", "#14061f", 6, s0=0.55, strike=prog(lt, T(14), T(14) + 0.3))
        tag(c, "GTA 5", 280, 1450, g5, bg="#ff3d7f", size=34, rot=6)


# ----------------------------------------------------------------------------
# escena 8: lo que costó (la cámara sube por el rascacielos más alto)
# ----------------------------------------------------------------------------
TOWER_TOP = -3600


def tower_world(c, t):
    c.drawRect(RECT(-3000, TOWER_TOP - 2000, 4000, 2600), P("#ffb36a", shader=lin(0, TOWER_TOP - 1200, 0, 1900,
                                                                                   ["#1a1050", "#5a2a8a", "#ff5a8a", "#ffb36a", "#ffd8a0"],
                                                                                   [0, .3, .6, .85, 1])))
    glow(c, R.RES.glow_warm, 820, TOWER_TOP + 500, 900, 0.7, skia.BlendMode.kScreen)
    oval(c, 820, TOWER_TOP + 500, 150, 150, P("#ffe9b0"))
    for i in range(10):  # nubes a media altura
        y = TOWER_TOP + 1400 + (i % 4) * 300
        x = (i * 380 + t * 60) % 2400 - 700
        glow(c, cloud_img(), x, y, 300, 0.7, skia.BlendMode.kSrcOver)
    r = rng(71)
    for i in range(14):  # ciudad abajo
        x0 = -400 + i * 140
        h = 300 + r.random() * 600
        c.drawRect(RECT(x0, 1800 - h, x0 + 120, 1800), P("#3a1a4a", shader=lin(x0, 0, x0 + 120, 0, ["#4a2a5a", "#2a0f3a"])))
        for j in range(int(h / 60)):
            c.drawRect(RECT(x0 + 20, 1800 - h + 20 + j * 60, x0 + 100, 1800 - h + 40 + j * 60), P("#ffcf6a", alpha=0.35))
    c.drawRect(RECT(-3000, 1800, 4000, 2600), P("#1a0a24"))
    # la torre: escalonada y afilada
    tiers = [(1800, 260), (900, 210), (0, 165), (-900, 125), (-1800, 85), (-2600, 50), (-3200, 20)]
    for i in range(len(tiers) - 1):
        y0, w0 = tiers[i]
        y1, w1 = tiers[i + 1]
        p = skia.Path()
        p.moveTo(540 - w0, y0)
        p.lineTo(540 - w1, y1)
        p.lineTo(540 + w1, y1)
        p.lineTo(540 + w0, y0)
        p.close()
        c.drawPath(p, P("#8ab0d0", shader=lin(540 - w0, 0, 540 + w0, 0, ["#3a4a7a", "#bfe2ff", "#7a9ac8", "#2a3a6a"], [0, .35, .6, 1])))
        for j in range(int((y0 - y1) / 50)):
            yy = y0 - j * 50
            ww = lerp(w0, w1, j * 50 / (y0 - y1))
            c.drawLine(540 - ww, yy, 540 + ww, yy, P("#ffffff", "stroke", 2, alpha=0.18))
    spire = skia.Path()
    spire.moveTo(530, -3200)
    spire.lineTo(540, TOWER_TOP)
    spire.lineTo(550, -3200)
    spire.close()
    c.drawPath(spire, P("#dfeeff"))
    glow(c, R.RES.glow_white, 540, TOWER_TOP, 60, 0.6 + 0.4 * math.sin(t * 6))


def bill(c, x, y, rot, s):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s * (0.4 + 0.6 * abs(math.cos(math.radians(rot * 3)))))
    rrect(c, -70, -34, 70, 34, 6, P("#4fbf6a"))
    rrect(c, -60, -26, 60, 26, 4, P("#2f8f4a", "stroke", 4))
    oval(c, 0, 0, 18, 18, P("#2f8f4a"))
    text_center(c, "$", 0, 12, F(R.RES.mx, 30), P("#c8f5c8"))
    c.restore()


def scene8(c, k):
    lt, T = k.lt, k.w
    u = ease_in_out(prog(lt, 0.0, k.D - 0.4))
    cy = lerp(1500, TOWER_TOP + 700, u)
    z = lerp(1.25, 0.82, u)
    rot = lerp(6, -3, u) + 1.5 * math.sin(lt * 1.5)
    c.save()
    world_cam(c, 540, cy, z, rot, py=1000)
    tower_world(c, k.t)
    c.restore()
    r = rng(91)
    for i in range(26):  # billetes volando hacia arriba
        sp = 500 + r.random() * 600
        x = r.random() * 1200 - 60 + 80 * math.sin(k.t * 1.5 + i)
        y = 2100 - ((lt + r.random() * 4) * sp) % 2400
        bill(c, x, y, k.t * (60 + 80 * r.random()) + i * 40, 0.8 + 0.6 * r.random())
    mk = prog(lt, T(5) - 0.1, T(5) + 0.2)
    if mk > 0:
        pop_text(c, "$1.000 – 2.000", 540, 760, 104, mk, shader=lin(0, 680, 0, 760, ["#d4ff4a", "#4fbf6a"]))
        pop_text(c, "MILLONES", 540, 880, 92, prog(lt, T(9) - 0.1, T(9) + 0.2))
        tag(c, "ESTIMACIÓN DE ANALISTAS", 540, 970, prog(lt, T(9), T(9) + 0.3), bg="#14061f", size=30, rot=-2)
    bt = prog(lt, T(14) - 0.1, T(14) + 0.2)
    tag(c, "= EDIFICIO MÁS ALTO DEL MUNDO", 540, 1520, bt, bg=LIME, fg="#14061f", size=40, rot=-3)


# ----------------------------------------------------------------------------
# armado: cuadros, transiciones de barrido y subtítulos
# ----------------------------------------------------------------------------
SCENES = [scene1, scene2, scene3, ad_scene(2), scene5, scene6, scene7, scene8, ad_scene(7, final=True)]
WHIP = {2, 5, 6, 7}


def render_frame(c, t, vo, phr, total):
    global VO
    VO = vo
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(R.hexc("#000000"))
    k = R.Ctx(vo, si, t)
    lt = k.lt
    blur, dx = 0.0, 0.0
    if si in WHIP and lt < 0.22:  # barrido rápido entre escenas
        q = 1 - ease_out(lt / 0.22)
        blur, dx = 70 * q, 260 * q
    if si == 4 and lt < 0.3:  # vuelve a reproducir: se quita el difuminado
        blur = 22 * (1 - ease_out(lt / 0.3))
    if blur > 0.3:
        p = skia.Paint()
        p.setImageFilter(skia.ImageFilters.Blur(blur, blur * (0.08 if si in WHIP else 1), skia.TileMode.kClamp))
        c.saveLayer(None, p)
    c.save()
    c.translate(dx, 0)
    SCENES[si](c, k)
    c.restore()
    if blur > 0.3:
        c.restore()
    if si == 4 and lt < 0.45:  # ícono de "play" al volver
        q = lt / 0.45
        a = math.sin(math.pi * q)
        c.save()
        c.translate(540, 1050)
        c.scale(lerp(0.8, 1.2, q), lerp(0.8, 1.2, q))
        oval(c, 0, 0, 130, 130, P("#000000", alpha=0.45 * a))
        tri = skia.Path()
        tri.moveTo(-34, -56)
        tri.lineTo(60, 0)
        tri.lineTo(-34, 56)
        tri.close()
        c.drawPath(tri, P("#ffffff", alpha=a))
        c.restore()
    R.vignette(c, 0.4)
    fade_out = clamp((total - t) / 0.3)
    if fade_out < 1:
        c.drawRect(RECT(0, 0, W, H), P("#000000", alpha=1 - fade_out))
    R.draw_subs(c, t, phr)
    R.draw_watermark(c)


def install():
    V.install()
    R.SCENES = SCENES
    R.FADE_IN = 0.0
    R.render_frame = render_frame
    R.draw_subs = S.draw_subs
    R.draw_watermark = S.draw_watermark


if __name__ == "__main__":
    install()
    R.main()
