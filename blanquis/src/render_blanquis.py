"""Chocobananos Blanqui's — anuncio animado (Puerto Barrios, Izabal).

Todo animado en vector: productos dibujados a partir de las fotos del cliente, fondos tropicales
desenfocados, cámara en movimiento, selector de sabores de topogigios. Colores de marca:
borgoña #800020 y amarillo dorado #F5A623. Sin @ de Velto.
Uso:
  VIDEO_BUILD=$PWD/blanquis/build VO_TRIM=0.2 VO_GAP=0.4 VO_TAIL=2.5 \
    python3 blanquis/src/render_blanquis.py --out blanquis/build/video_mudo.mp4
"""
import math
import os
import sys

import numpy as np
import skia
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "velto", "src"))
sys.path.insert(0, os.path.join(REPO, "src"))
import render as R  # noqa: E402
import render_gta as G  # noqa: E402
from render import (P, lin, rad, rrect, oval, clamp, lerp, smooth, ease_out, ease_in_out, back_out, prog, rng,  # noqa: E402
                    glow, text_center, W, H)
from render import R as RECT  # noqa: E402

F = R.font
BORD, BORD2, GOLD, GOLD2, CREAM = "#800020", "#a8283e", "#F5A623", "#ffc85a", "#fdf7f2"
CHOC = ["#2a1006", "#4a2210", "#6e3618", "#5a2a14", "#2a1006"]
VO = None


class BRes(R.Res):
    def __init__(self):
        super().__init__()
        f = os.path.join(REPO, "velto", "assets", "fonts")
        self.mx = skia.Typeface.MakeFromFile(os.path.join(f, "Montserrat_800ExtraBold.ttf"))
        self.mb = skia.Typeface.MakeFromFile(os.path.join(f, "Montserrat_700Bold.ttf"))
        self.ms = skia.Typeface.MakeFromFile(os.path.join(f, "Montserrat_600SemiBold.ttf"))
        arr = np.asarray(Image.open(os.path.join(REPO, "blanquis", "assets", "logo.png")).convert("RGBA")).copy()
        self.logo = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType,
                                         alphaType=skia.kUnpremul_AlphaType).withDefaultMipmaps()
        self.g_gold = R.sprite(245, 166, 35, power=1.6)
        self.g_bord = R.sprite(128, 0, 32, power=1.6)
        self.cloud = R.sprite(255, 255, 255, n=96, power=1.25)


def blur_layer(c, sigma):
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(sigma, sigma, skia.TileMode.kClamp))
    c.saveLayer(None, p)


def blur_xy(c, sx, sy):
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(max(sx, 0.01), max(sy, 0.01), skia.TileMode.kClamp))
    c.saveLayer(None, p)


def sparkles(c, t, n=24, seed=3, area=(0, 500, W, 1800), a=0.8):
    r = rng(seed)
    x0, y0, x1, y1 = area
    for i in range(n):
        x = x0 + r.random() * (x1 - x0) + 20 * math.sin(t + i)
        y = y1 - ((r.random() + t * (0.03 + 0.04 * r.random())) % 1) * (y1 - y0)
        tw = 0.5 + 0.5 * math.sin(t * 3 + i * 1.7)
        glow(c, R.RES.g_gold, x, y, 30 + 30 * tw, 0.45 * a * tw)
        glow(c, R.RES.glow_white, x, y, 8 + 6 * tw, a * tw)


def label(c, txt, x, y, k, bg=GOLD, fg=BORD, size=44, rot=0.0):
    if k <= 0:
        return
    s = back_out(clamp(k), 2.0)
    f = F(R.RES.mx, size)
    tw = f.measureText(txt)
    w, h = tw + size * 1.3, size * 1.75
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    rrect(c, -w / 2 + 5, -h / 2 + 8, w / 2 + 5, h / 2 + 8, h / 2, P("#000000", alpha=0.3, blur=6))
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, h / 2, P(bg))
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, h / 2, P("#ffffff", "stroke", 3, alpha=0.6))
    c.drawString(txt, -tw / 2, size * 0.36, f, P(fg))
    c.restore()


def stick(c, x0, y0, x1, y1):
    rrect(c, x0, y0, x1, y1, (x1 - x0) / 2, P("#e6c38a", shader=lin(x0, 0, x1, 0, ["#d4ae6e", "#f4dcaa", "#d0a868"])))


def drop(c, x, y, s=1.0, col="#3a180a"):
    p = skia.Path()
    p.moveTo(x, y - 18 * s)
    p.cubicTo(x + 12 * s, y, x + 12 * s, y + 14 * s, x, y + 14 * s)
    p.cubicTo(x - 12 * s, y + 14 * s, x - 12 * s, y, x, y - 18 * s)
    c.drawPath(p, P(col))
    oval(c, x - 4 * s, y + 2 * s, 3 * s, 4 * s, P("#ffffff", alpha=0.5))


# ----------------------------------------------------------------------------
# productos (dibujados a partir de las fotos del cliente)
# ----------------------------------------------------------------------------


def banana_path():
    p = skia.Path()
    p.moveTo(-100, 250)
    p.cubicTo(-122, 100, -112, -120, -62, -262)
    p.cubicTo(-36, -334, 42, -352, 72, -300)
    p.cubicTo(112, -230, 122, -60, 112, 120)
    p.cubicTo(106, 232, 90, 292, 0, 302)
    p.cubicTo(-80, 302, -98, 282, -100, 250)
    p.close()
    return p


def gloss(c, path_pts, w=18, a=0.3):
    p = skia.Path()
    p.moveTo(*path_pts[0])
    for i in range(1, len(path_pts) - 1, 2):
        p.quadTo(*path_pts[i], *path_pts[i + 1])
    c.drawPath(p, P("#ffffff", "stroke", w, alpha=a, blur=4))


def toppings_on(c, body, kind, k, seed, n=40, area=(-110, -320, 120, 290), t=0.0):
    """Toppings que caen y se pegan sobre la cobertura. k = progreso de la caída (0..1)."""
    if k <= 0:
        return
    r = rng(seed)
    x0, y0, x1, y1 = area
    pts = []
    tries = 0
    while len(pts) < n and tries < 2000:
        tries += 1
        x, y = x0 + r.random() * (x1 - x0), y0 + r.random() * (y1 - y0)
        if body.contains(x, y):
            pts.append((x, y, r.random(), r.random() * 360, r.random()))
    for i, (x, y, rs, ang, dl) in enumerate(pts):
        u = clamp((k - dl * 0.5) / 0.5)
        if u <= 0:
            continue
        yy = y - (1 - ease_out(u)) * 700
        bounce = math.sin(u * math.pi * 2) * 8 * (1 - u)
        c.save()
        c.translate(x, yy - bounce)
        c.rotate(ang + (1 - u) * 200)
        if kind == "mania":
            s = 11 + 9 * rs
            pp = skia.Path()
            for j in range(6):
                a_ = j / 6 * 6.283
                rr = s * (0.75 + 0.4 * math.sin(j * 2.3 + rs * 9))
                (pp.moveTo if j == 0 else pp.lineTo)(math.cos(a_) * rr, math.sin(a_) * rr)
            pp.close()
            c.drawPath(pp, P("#f0cf8e", shader=lin(-s, -s, s, s, ["#fbe3b0", "#d9a95e"])))
            c.drawPath(pp, P("#b8853e", "stroke", 2))
        elif kind == "coco":
            sh = skia.Path()
            sh.moveTo(-14, 0)
            sh.quadTo(0, -8 - 6 * rs, 14, 0)
            c.drawPath(sh, P("#ffffff", "stroke", 5))
            c.drawPath(sh, P("#e8e2d8", "stroke", 2))
        else:  # chispas
            rrect(c, -7, -5, 7, 5, 3, P("#1a0702"))
            oval(c, -2, -2, 2.5, 1.5, P("#ffffff", alpha=0.6))
        c.restore()


def chocobanano(c, x, y, s, rot=0.0, spin=1.0, top=None, top_k=1.0, seed=1, t=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s * (abs(spin) if abs(spin) > 0.06 else 0.06), s)
    glow(c, R.RES.soft_dark, 30, 60, 420, 0.25, skia.BlendMode.kSrcOver)
    stick(c, -24, 230, 24, 540)
    body = banana_path()
    c.drawPath(body, P(CHOC[2], shader=lin(-115, 0, 120, 0, CHOC, [0, .22, .45, .72, 1])))
    c.save()
    c.clipPath(body, True)
    for i in range(8):  # chorreado de chocolate
        y0 = -270 + i * 72
        d = skia.Path()
        d.moveTo(-130, y0 + 40)
        d.cubicTo(-40, y0 + 10, 30, y0 + 30, 140, y0 - 34)
        c.drawPath(d, P("#260d04", "stroke", 11))
        c.drawPath(d, P("#8a4a26", "stroke", 3, alpha=0.7))
    c.restore()
    gloss(c, [(-62, -230), (-88, -40), (-78, 180)], 18, 0.32)
    gloss(c, [(70, -270), (92, -150), (92, -60)], 9, 0.25)
    c.drawPath(body, P("#1a0804", "stroke", 4))
    if top:
        toppings_on(c, body, top, top_k, seed, n=44 if top != "coco" else 70, t=t)
    c.restore()


def pine_seg(c, flip=1):
    blob = skia.Path()
    blob.moveTo(-130, -40)
    blob.cubicTo(-120, -120, -20, -130, 40, -110)
    blob.lineTo(140, 20)
    blob.cubicTo(130, 90, 20, 120, -60, 110)
    blob.cubicTo(-140, 90, -150, 20, -130, -40)
    blob.close()
    c.drawPath(blob, P(CHOC[2], shader=lin(-140, -100, 140, 100, ["#2a1006", "#6e3618", "#4a2210"])))
    face = skia.Path()
    face.moveTo(-10, -60)
    face.lineTo(160, 30)
    face.lineTo(20, 116)
    face.close()
    c.drawPath(face, P("#ffd84a", shader=lin(10, -40, 150, 100, ["#ffe680", "#ffc928"])))
    for j in range(7):
        c.drawLine(40, 40, 40 + math.cos(j * 0.4 - 0.9) * 110, 40 + math.sin(j * 0.4 - 0.9) * 80, P("#e8a818", "stroke", 2, alpha=0.6))
    choc = skia.Path()  # el chocolate chorrea sobre la cara de la piña
    choc.moveTo(10, -44)
    choc.quadTo(60, -10, 70, 20)
    choc.quadTo(40, 30, 30, 70)
    choc.lineTo(-20, 80)
    choc.close()
    c.drawPath(choc, P("#4a2210"))
    gloss(c, [(-100, -60), (-60, -100), (0, -104)], 12, 0.35)
    c.drawPath(blob, P("#1a0804", "stroke", 3, alpha=0.6))


def chocopina(c, x, y, s, rot=0.0, spin=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s * max(abs(spin), 0.06), s)
    glow(c, R.RES.soft_dark, 30, 60, 420, 0.25, skia.BlendMode.kSrcOver)
    stick(c, -14, 0, 14, 560)
    for i, yy in enumerate((-260, -20, 220)):
        c.save()
        c.translate((-10, 12, -6)[i], yy)
        c.scale(1.0 - 0.06 * (i == 0), 1.0)
        pine_seg(c)
        c.restore()
    c.restore()


def chocosandia(c, x, y, s, rot=0.0, spin=1.0, seed=4):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s * max(abs(spin), 0.06), s)
    glow(c, R.RES.soft_dark, 30, 60, 420, 0.25, skia.BlendMode.kSrcOver)
    stick(c, -24, 200, 24, 520)
    sl = skia.Path()
    sl.moveTo(0, -380)
    sl.cubicTo(30, -380, 240, 120, 270, 190)
    sl.quadTo(0, 250, -270, 190)
    sl.cubicTo(-240, 120, -30, -380, 0, -380)
    sl.close()
    c.drawPath(sl, P("#e8414a", shader=lin(0, -100, 0, 200, ["#ff5a5a", "#e03440", "#f2a0a0"], [0, .7, 1])))
    c.save()
    c.clipPath(sl, True)
    rind = skia.Path()
    rind.moveTo(-300, 150)
    rind.quadTo(0, 210, 300, 150)
    rind.lineTo(300, 300)
    rind.lineTo(-300, 300)
    rind.close()
    c.drawPath(rind, P("#d8f0a0"))
    rind2 = skia.Path()
    rind2.moveTo(-300, 175)
    rind2.quadTo(0, 240, 300, 175)
    rind2.lineTo(300, 300)
    rind2.lineTo(-300, 300)
    rind2.close()
    c.drawPath(rind2, P("#5ea83a", shader=lin(0, 175, 0, 260, ["#8fcf5a", "#3f7a2a"])))
    for sx, sy in ((-120, 120), (-30, 70), (70, 110), (150, 140), (10, 140), (-180, 160)):
        oval(c, sx, sy, 6, 10, P("#2a1208"))
    choc = skia.Path()
    choc.moveTo(-300, -40)
    for i in range(8):
        xx = -300 + i * 80
        choc.quadTo(xx + 40, 10 + 25 * (i % 2), xx + 80, -10)
    choc.lineTo(300, -500)
    choc.lineTo(-300, -500)
    choc.close()
    c.drawPath(choc, P(CHOC[2], shader=lin(-200, 0, 200, 0, CHOC, [0, .22, .45, .72, 1])))
    for i in range(6):
        d = skia.Path()
        y0 = -320 + i * 55
        d.moveTo(-200, y0 + 60)
        d.cubicTo(-60, y0 + 20, 60, y0 + 10, 200, y0 - 50)
        c.drawPath(d, P("#260d04", "stroke", 10))
        c.drawPath(d, P("#8a4a26", "stroke", 3, alpha=0.7))
    c.restore()
    body2 = skia.Op(sl, choc, skia.PathOp.kIntersect_PathOp)
    toppings_on(c, body2, "mania", 1.0, seed, n=34, area=(-200, -370, 200, 0))
    gloss(c, [(-40, -320), (-120, -150), (-170, -40)], 14, 0.3)
    c.drawPath(sl, P("#1a0804", "stroke", 3, alpha=0.5))
    c.restore()


def strawberry(c, x, y, s, leaves=False, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if leaves:
        for j in range(7):
            a = -160 + j * 23
            lf = skia.Path()
            ra = math.radians(a)
            lf.moveTo(0, -80)
            ex, ey = math.cos(ra) * 120, -80 + math.sin(ra) * 70
            lf.quadTo(ex * 0.5 - 20 * math.sin(ra), -80 + (ey + 80) * 0.5 - 30, ex, ey)
            lf.quadTo(ex * 0.5 + 20 * math.sin(ra), -80 + (ey + 80) * 0.5 + 10, 0, -80)
            c.drawPath(lf, P("#3f8f3a", shader=lin(0, -80, ex, ey, ["#2f6f2a", "#6fbf4a"])))
    body = skia.Path()
    body.moveTo(0, 95)
    body.cubicTo(-72, 64, -98, -30, -82, -62)
    body.cubicTo(-62, -98, 62, -98, 82, -62)
    body.cubicTo(98, -30, 72, 64, 0, 95)
    body.close()
    c.drawPath(body, P("#e8202a", shader=lin(0, -90, 0, 90, ["#ff4a3a", "#d0101e"])))
    r = rng(8)
    for i in range(14):
        sx, sy = -60 + r.random() * 120, -80 + r.random() * 50
        if body.contains(sx, sy):
            oval(c, sx, sy, 3, 4, P("#ffd84a"))
    c.save()
    c.clipPath(body, True)
    ch = skia.Path()
    ch.moveTo(-100, -38)
    for i in range(5):
        ch.quadTo(-80 + i * 40, -20 - 12 * (i % 2), -60 + i * 40, -40 + 8 * (i % 2))
    ch.lineTo(110, 120)
    ch.lineTo(-110, 120)
    ch.close()
    c.drawPath(ch, P(CHOC[2], shader=lin(-90, 0, 90, 0, CHOC, [0, .22, .45, .72, 1])))
    c.restore()
    gloss(c, [(-50, -10), (-60, 30), (-30, 60)], 12, 0.35)
    c.drawPath(body, P("#3a0a08", "stroke", 3, alpha=0.5))
    c.restore()


def chocofresa(c, x, y, s, rot=0.0, spin=1.0):
    """Chocofresa: CUATRO fresas individuales ensartadas en un mismo palillo."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s * max(abs(spin), 0.06), s)
    glow(c, R.RES.soft_dark, 30, 60, 420, 0.25, skia.BlendMode.kSrcOver)
    stick(c, -12, -420, 12, 560)
    for i, yy in enumerate((-300, -110, 80, 270)):
        strawberry(c, (6, -6, 5, -4)[i], yy, 1.15 - 0.03 * i, leaves=(i == 0), rot=(4, -5, 3, -2)[i])
    c.restore()


FLAVORS = [  # nombre, color claro, color oscuro, textura
    ("Mango", "#ffc23a", "#ff9a1a", "pulp"),
    ("Fresa con leche", "#ffc6d4", "#f28aa8", "swirl"),
    ("Coco", "#fffaf0", "#ece2d0", "flakes"),
    ("Maracuyá", "#ffe24a", "#ffc21a", "seeds"),
    ("Nance", "#f8c83a", "#e0a01a", "dots"),
    ("Tamarindo", "#a8733f", "#6e4422", "fibers"),
    ("Manía", "#ead7b4", "#cdb084", "specks"),
]


def topo_paths():
    body = skia.Path()
    body.moveTo(-26, -440)
    body.cubicTo(-70, -400, -150, -370, -152, -290)
    body.lineTo(-158, 345)
    body.quadTo(-158, 410, -95, 410)
    body.lineTo(95, 410)
    body.quadTo(158, 410, 158, 345)
    body.lineTo(152, -290)
    body.cubicTo(150, -370, 70, -400, 26, -440)
    body.close()
    return body


def flavor_fill(c, fi, x0, y0, x1, y1, t):
    name, c1, c2, tex = FLAVORS[fi]
    c.drawRect(RECT(x0, y0, x1, y1), P(c1, shader=lin(x0, 0, x1, 0, [c2, c1, c1, c2], [0, .3, .7, 1])))
    r = rng(50 + fi)
    if tex == "pulp":
        for i in range(30):
            oval(c, x0 + r.random() * (x1 - x0), y0 + r.random() * (y1 - y0), 14, 22, P("#ff8a10", alpha=0.25))
    elif tex == "swirl":
        for i in range(8):
            p = skia.Path()
            yy = y0 + i * (y1 - y0) / 8
            p.moveTo(x0, yy)
            p.cubicTo(-40, yy + 40, 40, yy - 20, x1, yy + 30)
            c.drawPath(p, P("#ffffff", "stroke", 10, alpha=0.5))
    elif tex == "flakes":
        for i in range(60):
            xx, yy = x0 + r.random() * (x1 - x0), y0 + r.random() * (y1 - y0)
            c.drawLine(xx, yy, xx + 10, yy + 4 * r.random(), P("#d8ccb8", "stroke", 3))
    elif tex == "seeds":
        for i in range(40):
            oval(c, x0 + r.random() * (x1 - x0), y0 + r.random() * (y1 - y0), 5, 7, P("#1a1206", alpha=0.85))
    elif tex == "dots":
        for i in range(40):
            oval(c, x0 + r.random() * (x1 - x0), y0 + r.random() * (y1 - y0), 6, 6, P("#c88a10", alpha=0.6))
    elif tex == "fibers":
        for i in range(40):
            xx, yy = x0 + r.random() * (x1 - x0), y0 + r.random() * (y1 - y0)
            c.drawLine(xx, yy, xx + 20 * (r.random() - 0.5), yy + 18, P("#4a2a12", "stroke", 3, alpha=0.6))
    else:
        for i in range(70):
            oval(c, x0 + r.random() * (x1 - x0), y0 + r.random() * (y1 - y0), 3.5, 3.5, P("#9a7448", alpha=0.7))
    for i in range(90):  # escarcha
        xx, yy = x0 + r.random() * (x1 - x0), y0 + r.random() * (y1 - y0)
        oval(c, xx, yy, 2 + 3 * r.random(), 2 + 3 * r.random(), P("#ffffff", alpha=0.25 + 0.2 * r.random()))


def topogigio(c, x, y, s, fi=0, fj=None, q=0.0, t=0.0, rot=0.0):
    """Topogigio: helado en bolsita plástica transparente amarrada arriba (sin palillo).
    fi = sabor actual; fj, q = sabor que entra y nivel de la ola de color (0..1)."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    glow(c, R.RES.soft_dark, 30, 80, 430, 0.22, skia.BlendMode.kSrcOver)
    body = topo_paths()
    c.save()
    c.clipPath(body, True)
    flavor_fill(c, fi, -165, -450, 165, 420, t)
    if fj is not None and q > 0:
        lvl = lerp(430, -470, ease_in_out(q))
        wave = skia.Path()
        wave.moveTo(-180, lvl)
        for i in range(10):
            xx = -180 + i * 40
            wave.quadTo(xx + 20, lvl + 18 * math.sin(t * 12 + i), xx + 40, lvl)
        wave.lineTo(220, 460)
        wave.lineTo(-180, 460)
        wave.close()
        c.save()
        c.clipPath(wave, True)
        flavor_fill(c, fj, -165, -450, 165, 420, t)
        c.restore()
        c.drawPath(wave, P("#ffffff", "stroke", 5, alpha=0.6 * math.sin(math.pi * q)))
    # brillos del plástico
    c.drawRect(RECT(-128, -380, -90, 380), P("#ffffff", shader=lin(-128, 0, -90, 0, ["#ffffff00", "#ffffff88", "#ffffff00"])))
    c.drawRect(RECT(100, -300, 116, 360), P("#ffffff", alpha=0.25))
    c.restore()
    c.drawPath(body, P("#ffffff", "stroke", 6, alpha=0.75))
    c.drawPath(body, P("#b8b8c0", "stroke", 2, alpha=0.6))
    # nudo y la punta de la bolsa
    oval(c, 0, -448, 24, 16, P("#f4f4f8", alpha=0.95))
    c.drawPath(skia.Path().addOval(RECT(-24, -464, 24, -432)), P("#c8c8d0", "stroke", 3))
    fl = skia.Path()
    fl.moveTo(-10, -460)
    fl.cubicTo(-60, -520, -110, -580, -120, -640)
    fl.lineTo(120, -640)
    fl.cubicTo(110, -580, 60, -520, 10, -460)
    fl.close()
    c.drawPath(fl, P("#ffffff", alpha=0.35))
    for i in range(5):
        c.drawLine(-6 + i * 3, -470, -90 + i * 45, -636, P("#c8c8d0", "stroke", 2, alpha=0.6))
    c.drawPath(fl, P("#ffffff", "stroke", 4, alpha=0.8))
    c.restore()


# ----------------------------------------------------------------------------
# fondos tropicales (se dibujan desenfocados)
# ----------------------------------------------------------------------------


def palm(c, x, base, h, t, lean=0.1, trunk="#9a6a3a", leaf="#2f8f4a", phase=0.0):
    top = (x + h * lean, base - h)
    tr = skia.Path()
    tr.moveTo(x, base)
    tr.quadTo(x + h * lean * 0.2, base - h * 0.5, *top)
    c.drawPath(tr, P(trunk, "stroke", h * 0.06))
    for i in range(8):
        a = -165 + i * 44 + 8 * math.sin(t * 1.6 + i + phase)
        ra = math.radians(a)
        L = h * 0.45
        lf = skia.Path()
        lf.moveTo(*top)
        ex, ey = top[0] + math.cos(ra) * L, top[1] + math.sin(ra) * L * 0.55 + L * 0.3
        lf.quadTo(top[0] + math.cos(ra) * L * 0.5, top[1] - L * 0.25, ex, ey)
        c.drawPath(lf, P(leaf, "stroke", h * 0.055))
    for j in range(3):
        oval(c, top[0] - 14 + j * 14, top[1] + 16, 14, 14, P("#6a4a1a"))


def gull(c, x, y, s, t):
    fl = math.sin(t * 6) * 14
    p = skia.Path()
    p.moveTo(x - 40 * s, y - fl * s)
    p.quadTo(x - 18 * s, y - 18 * s, x, y)
    p.quadTo(x + 18 * s, y - 18 * s, x + 40 * s, y - fl * s)
    c.drawPath(p, P("#ffffff", "stroke", 6 * s))


def sky(c, cols, pos=None, y1=1100):
    c.drawRect(RECT(-800, -2000, W + 800, H + 800), P(cols[-1], shader=lin(0, -400, 0, y1, cols, pos)))


def beach_bg(c, t, oy=0.0, ox=0.0):
    c.save()
    c.translate(ox, oy)
    sky(c, ["#2a8ae0", "#4fb4f0", "#bfe8ff"], y1=1050)
    glow(c, R.RES.glow_white, 820, 300, 500, 0.9)
    oval(c, 820, 300, 90, 90, P("#fffbe8"))
    for i in range(6):
        x = (i * 330 + t * 20) % 1700 - 300
        glow(c, R.RES.cloud, x, 150 + (i % 3) * 140 - 500, 220, 0.9, skia.BlendMode.kSrcOver)
        glow(c, R.RES.cloud, x + 120, 190 + (i % 3) * 140 - 500, 170, 0.9, skia.BlendMode.kSrcOver)
    c.drawRect(RECT(-800, 1000, W + 800, 1300), P("#1ab0c8", shader=lin(0, 1000, 0, 1300, ["#1a7ab8", "#22c0cc", "#7ff0e0"])))
    for i in range(20):
        x = (i * 140 + t * 40 * (1 + i % 3)) % 1500 - 200
        c.drawLine(x, 1040 + (i % 6) * 40, x + 70, 1040 + (i % 6) * 40, P("#ffffff", "stroke", 4, alpha=0.5))
    sh = 1300 + 18 * math.sin(t * 1.2)
    c.drawRect(RECT(-800, sh - 30, W + 800, sh + 10), P("#ffffff", alpha=0.7))
    c.drawRect(RECT(-800, 1300, W + 800, H + 1200), P("#f6e2b0", shader=lin(0, 1300, 0, 1920, ["#fbe9c0", "#e8c890"])))
    palm(c, 60, 1500, 900, t, 0.18)
    palm(c, 1040, 1450, 820, t, -0.2, phase=2)
    palm(c, -120, 1700, 1100, t, 0.25, phase=4)
    for i in range(3):
        gull(c, (300 + i * 180 + t * 60) % 1300 - 100, 520 + i * 60 - 400, 1.0, t + i)
    c.restore()


def monstera(c, x, y, s, rot, col="#2f7a3a"):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    lf = skia.Path()
    lf.moveTo(0, 0)
    lf.cubicTo(-220, -60, -240, -360, 0, -420)
    lf.cubicTo(240, -360, 220, -60, 0, 0)
    c.drawPath(lf, P(col, shader=lin(-200, -400, 200, 0, ["#4aa04a", col])))
    for i in range(5):
        c.drawLine(0, -60 - i * 70, -180 + i * 10, -120 - i * 60, P("#f4d9b0", "stroke", 12, alpha=0.0))
    c.drawLine(0, 0, 0, -400, P("#7fcf6a", "stroke", 5))
    c.restore()


def terrace_bg(c, t, ox=0.0, table=False):
    c.save()
    c.translate(ox, 0)
    c.drawRect(RECT(-800, -800, W + 800, H + 800), P("#f4d9b0", shader=lin(0, 0, 0, 1500, ["#ffe6c0", "#f0c890"])))
    rrect(c, 140, 380, 940, 1180, 20, P("#7fd0f0", shader=lin(0, 380, 0, 1180, ["#5ab4f0", "#bfe8ff", "#22c0cc"], [0, .6, 1])))
    palm(c, 300, 1180, 560, t, 0.15)
    palm(c, 780, 1180, 480, t, -0.15, phase=2)
    rrect(c, 140, 380, 940, 1180, 20, P("#8a5a32", "stroke", 26))
    c.drawLine(540, 380, 540, 1180, P("#8a5a32", "stroke", 16))
    for i in range(6):
        c.drawRect(RECT(-800 + i * 0, 120 + i * 0, W + 800, 160), P("#8a5a32"))
    for i in range(9):  # barandal
        c.drawRect(RECT(-200 + i * 160, 1250, -180 + i * 160, 1560), P("#a8723e"))
    c.drawRect(RECT(-800, 1240, W + 800, 1270), P("#8a5a32"))
    monstera(c, -40, 1500, 1.6, 40)
    monstera(c, 1120, 1450, 1.5, -40, "#2a6a34")
    monstera(c, 1100, 600, 1.1, -120)
    monstera(c, -20, 500, 1.0, 120, "#2a6a34")
    for i in range(4):  # rayos de sol
        p = skia.Path()
        p.moveTo(700 + i * 120, -100)
        p.lineTo(780 + i * 120, -100)
        p.lineTo(300 + i * 120 + 200 * math.sin(t * 0.3), 1900)
        p.lineTo(200 + i * 120 + 200 * math.sin(t * 0.3), 1900)
        p.close()
        c.drawPath(p, P("#ffffff", alpha=0.12))
    if table:
        c.drawRect(RECT(-800, 1380, W + 800, H + 800), P("#a8703a", shader=lin(0, 1380, 0, 1920, ["#c88a4a", "#7a4a22"])))
        for i in range(6):
            c.drawLine(-800, 1420 + i * 90, W + 800, 1420 + i * 90, P("#6a3a1a", "stroke", 4, alpha=0.5))
    c.restore()


def garden_bg(c, t, ox=0.0):
    c.save()
    c.translate(ox, 0)
    sky(c, ["#4fb4f0", "#a8dcff", "#e8f8ff"], y1=1100)
    for i in range(9):
        x = -400 + i * 330
        oval(c, x, 1000, 220, 200, P("#3a8a3a", shader=rad(x - 60, 940, 260, ["#6fbf4a", "#2f7a34"])))
        c.drawRect(RECT(x - 18, 1000, x + 18, 1180), P("#7a4a22"))
    c.drawRect(RECT(-800, 1150, 3000, H + 800), P("#6fbf4a", shader=lin(0, 1150, 0, 1920, ["#8fd65a", "#4a9a3a"])))
    for i in range(6):  # mesas con sombrilla de colores de la marca
        x = -300 + i * 420
        c.drawLine(x, 1000, x, 1400, P("#e8e0d0", "stroke", 12))
        um = skia.Path()
        um.moveTo(x - 200, 1020)
        um.quadTo(x, 860, x + 200, 1020)
        um.close()
        c.drawPath(um, P(BORD if i % 2 else GOLD))
        oval(c, x, 1400, 170, 36, P("#f4ecd8"))
        c.drawRect(RECT(x - 10, 1400, x + 10, 1520), P("#c8b898"))
    for i in range(40):
        oval(c, -400 + i * 70, 1600 + 60 * math.sin(i), 10, 10, P(["#ff6a8a", "#ffd84a", "#ffffff"][i % 3]))
    for i in range(30):  # luces colgantes
        x = -400 + i * 90
        y = 720 + 40 * math.sin(i * 0.7)
        glow(c, R.RES.g_gold, x, y, 40, 0.6 + 0.3 * math.sin(t * 3 + i))
    c.restore()


def park_bg(c, t, ox=0.0):
    c.save()
    c.translate(ox, 0)
    sky(c, ["#3a9ae8", "#8fd0ff", "#ffe8c0"], y1=1150)
    glow(c, R.RES.glow_white, 300, 400, 380, 0.8)
    for i in range(7):
        palm(c, -300 + i * 380, 1250, 700 + 120 * math.sin(i * 1.7), t, 0.1 * (-1) ** i, phase=i)
    c.drawRect(RECT(-800, 1200, 3000, H + 800), P("#7fcf5a", shader=lin(0, 1200, 0, 1920, ["#9fe06a", "#4a9a3a"])))
    # columpio dorado
    for dx in (700, 1100):
        c.drawLine(dx, 1300, dx + 80, 900, P(GOLD, "stroke", 18))
        c.drawLine(dx + 160, 1300, dx + 80, 900, P(GOLD, "stroke", 18))
    c.drawLine(780, 900, 1180, 900, P(GOLD, "stroke", 18))
    sw = 12 * math.sin(t * 1.8)
    for sx in (880, 1080):
        c.drawLine(sx, 900, sx + sw, 1160, P("#5a3a20", "stroke", 5))
        c.drawLine(sx - 50, 900, sx - 50 + sw, 1160, P("#5a3a20", "stroke", 5))
        rrect(c, sx - 70 + sw, 1150, sx + 20 + sw, 1172, 8, P(BORD))
    c.restore()


def sunset_bg(c, t, oy=0.0):
    c.save()
    c.translate(0, oy)
    sky(c, ["#5a1430", "#c8406a", "#ff8a4a", "#ffcf7a"], [0, .35, .7, 1], y1=1080)
    glow(c, R.RES.g_gold, 540, 1040, 700, 0.8, skia.BlendMode.kScreen)
    oval(c, 540, 1060, 150, 150, P("#ffe9b0"))
    c.drawRect(RECT(-800, 1060, W + 800, H + 800), P("#c8406a", shader=lin(0, 1060, 0, 1920, ["#ff9a5a", "#a8304a", "#4a1020"])))
    for i in range(14):
        w = 200 - i * 12
        c.drawLine(540 - w, 1090 + i * 30, 540 + w, 1090 + i * 30, P("#ffe9b0", "stroke", 6, alpha=0.6))
    palm(c, 80, 1400, 900, t, 0.2, trunk="#3a0a18", leaf="#3a0a18")
    palm(c, 1000, 1350, 800, t, -0.22, trunk="#3a0a18", leaf="#3a0a18", phase=2)
    c.restore()


# ----------------------------------------------------------------------------
# familia (estilo plano, expresiones naturales)
# ----------------------------------------------------------------------------


def fam_person(c, x, y, s, t, skin, hair, style, shirt, ph, hold, bite_k=0.0):
    """Medio cuerpo. (x, y) = cintura. hold(c, hx, hy) dibuja el producto en la mano."""
    c.save()
    c.translate(x, y + 6 * math.sin(t * 2 + ph))
    c.scale(s, s)
    if style == "woman":  # pelo largo detrás
        hp = skia.Path()
        hp.moveTo(-130, -520)
        hp.cubicTo(-170, -380, -150, -300, -110, -260)
        hp.lineTo(110, -260)
        hp.cubicTo(150, -300, 170, -380, 130, -520)
        hp.close()
        c.drawPath(hp, P(hair))
    torso = skia.Path()
    torso.moveTo(-160, -330)
    torso.quadTo(-170, -380, -110, -390)
    torso.lineTo(110, -390)
    torso.quadTo(170, -380, 160, -330)
    torso.lineTo(150, 300)
    torso.lineTo(-150, 300)
    torso.close()
    c.drawPath(torso, P(shirt, shader=lin(-160, 0, 160, 0, [R.mix_col(shirt, "#000000", 0.2), shirt, R.mix_col(shirt, "#000000", 0.15)])))
    rrect(c, -34, -470, 34, -380, 16, P(R.mix_col(skin, "#000000", 0.12)))
    neckl = skia.Path()
    neckl.moveTo(-50, -390)
    neckl.quadTo(0, -340, 50, -390)
    c.drawPath(neckl, P(R.mix_col(skin, "#000000", 0.12)))
    # cabeza
    for sd in (-1, 1):
        oval(c, sd * 108, -520, 18, 26, P(R.mix_col(skin, "#000000", 0.08)))
    oval(c, 0, -530, 108, 120, P(skin, shader=rad(-30, -570, 200, [R.mix_col(skin, "#ffffff", 0.15), skin])))
    hp = skia.Path()
    if style == "man":
        hp.moveTo(-110, -540)
        hp.cubicTo(-120, -680, 120, -680, 110, -540)
        hp.quadTo(90, -610, 40, -615)
        hp.quadTo(-60, -600, -110, -540)
    elif style == "woman":
        hp.moveTo(-118, -500)
        hp.cubicTo(-130, -690, 130, -690, 118, -500)
        hp.quadTo(70, -640, -20, -600)
        hp.quadTo(-90, -580, -118, -500)
    else:  # niño
        hp.moveTo(-112, -540)
        hp.cubicTo(-120, -690, 120, -690, 112, -540)
        hp.quadTo(60, -620, 20, -590)
        hp.quadTo(-10, -630, -40, -595)
        hp.quadTo(-80, -610, -112, -540)
    hp.close()
    c.drawPath(hp, P(hair))
    blink = 1.0 if (t * 0.6 + ph) % 3.2 > 0.12 else 0.1
    for sd in (-1, 1):
        ex, ey = sd * 40, -535
        oval(c, ex, ey, 13, 15 * blink, P("#2a1a10"))
        if blink > 0.5:
            oval(c, ex + 4, ey - 5, 4, 4, P("#ffffff"))
        c.drawLine(ex - 18, ey - 34, ex + 18, ey - 38 + sd * 2, P(R.mix_col(hair, "#000000", 0.2), "stroke", 7))
        oval(c, sd * 62, -490, 20, 11, P("#ff7a8a", alpha=0.35))
    nose = skia.Path()
    nose.moveTo(0, -515)
    nose.quadTo(-10, -490, 4, -485)
    c.drawPath(nose, P(R.mix_col(skin, "#000000", 0.25), "stroke", 4))
    m = skia.Path()
    if bite_k > 0.5:  # masticando: sonrisa cerrada
        m.moveTo(-22, -458)
        m.quadTo(0, -446 - 6 * math.sin(t * 14), 22, -458)
        c.drawPath(m, P("#8a2a2a", "stroke", 5))
    else:
        m.moveTo(-34, -462)
        m.quadTo(0, -462, 34, -462)
        m.quadTo(30, -420, 0, -418)
        m.quadTo(-30, -420, -34, -462)
        m.close()
        c.drawPath(m, P("#7a1a20"))
        c.drawRect(RECT(-26, -462, 26, -452), P("#ffffff"))
        oval(c, 0, -428, 14, 7, P("#ff7a8a"))
    # brazo con el producto
    hx = lerp(150, 70, bite_k)
    hy = lerp(-300, -430, bite_k)
    arm = skia.Path()
    arm.moveTo(140, -350)
    arm.quadTo(240, -200, hx + 20, hy + 40)
    c.drawPath(arm, P(shirt, "stroke", 54))
    hold(c, hx, hy)
    oval(c, hx + 8, hy + 20, 30, 34, P(skin))
    c.restore()


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def scene1(c, k):  # playa de Puerto Barrios, la cámara baja del cielo
    lt, T = k.lt, k.w
    d = ease_in_out(prog(lt, 0.0, 2.3))
    bl = 10 * smooth(prog(lt, 1.3, 2.4))
    blur_layer(c, max(bl, 0.01))
    c.save()
    z = lerp(1.25, 1.08, d) + 0.03 * math.sin(lt)
    c.translate(540, 960)
    c.scale(z, z)
    c.translate(-540, -960)
    beach_bg(c, k.t, oy=lerp(900, 0, d), ox=-40 * lt)
    c.restore()
    c.restore()
    e = ease_out(prog(lt, 1.5, 2.6))
    if e > 0:
        orbit = prog(lt, k.D - 0.55, k.D)
        spin = math.cos(math.pi * orbit)
        zp = lerp(1.15, 1.4, smooth(prog(lt, 1.5, k.D)))
        chocobanano(c, 540 + 80 * math.sin(lt * 0.8) * (1 - orbit), lerp(1900, 1080, e), zp,
                    rot=lerp(-14, 4, e) + 3 * math.sin(lt * 1.3), spin=spin, t=k.t)
        dk = ((lt - 2.6) % 1.6) / 1.6 if lt > 2.6 else -1
        if 0 <= dk < 1 and abs(spin) > 0.6:
            drop(c, 540 - 70 * zp, 1080 + lerp(80, 420, dk ** 2) * zp, 1.4)
    R.RES.glow_gold = R.RES.g_gold
    sparkles(c, k.t, n=18, seed=2, a=0.7 * e)


def scene2(c, k):  # terraza: chocobanano clásico y con manía
    lt, T = k.lt, k.w
    zoom = smooth(prog(lt, T(8) - 0.3, T(9) + 0.3))
    z = 1.0 + 0.05 * lt / k.D + 0.45 * zoom
    cx = lerp(540, 760, zoom)
    blur_layer(c, 11)
    terrace_bg(c, k.t, ox=-30 * lt - 120)
    c.restore()
    c.save()
    c.translate(540, 1080)
    c.scale(z, z)
    c.translate(-cx, -1080)
    spin = math.cos(math.pi * (1 - clamp(lt / 0.5)))
    mv = ease_out(prog(lt, 0.3, 1.0))
    chocobanano(c, lerp(540, 300, mv), 1080, lerp(1.3, 0.95, mv), rot=-6 + 2 * math.sin(lt * 1.5), spin=spin, t=k.t)
    dk = prog(lt, T(3) - 0.5, T(3))
    if dk > 0:
        yy = lerp(-400, 1080, ease_out(dk)) + 30 * math.sin(math.pi * clamp((lt - T(3)) / 0.3)) * (lt > T(3))
        chocobanano(c, 780, yy, 0.95, rot=6 + 2 * math.sin(lt * 1.3), top="mania",
                    top_k=0.6 + 0.4 * prog(lt, T(8) - 0.2, T(9) + 0.4), seed=3, t=k.t)
    c.restore()
    label(c, "CLÁSICO", 300, 1660, prog(lt, T(4) - 0.15, T(4) + 0.15) * (1 - clamp(zoom * 3)), rot=-3)
    label(c, "CON MANÍA", 780, 1660, prog(lt, T(8) - 0.15, T(8) + 0.15) if zoom < 0.5 else 0, rot=3)
    if zoom > 0.5:
        label(c, "CON MANÍA", 540, 1650, prog(lt, T(8) - 0.15, T(8) + 0.15), size=52, rot=-2)
    sparkles(c, k.t, n=14, seed=5, a=0.6)


FRUITS = [(330, "CHOCOPIÑA"), (1110, "CHOCOSANDÍA"), (1890, "CHOCOFRESA")]


def scene3(c, k):  # jardín: chocofrutas
    lt, T = k.lt, k.w
    seg = [0.0, 1.35, 2.7]
    if lt < 3.6:
        cxw = 330
        for i in (1, 2):
            cxw = lerp(cxw, FRUITS[i][0], ease_in_out(prog(lt, seg[i] - 0.35, seg[i] + 0.05)))
        z = 1.0 + 0.04 * math.sin(lt * 2)
    else:
        u = ease_in_out(prog(lt, 3.6, 4.4))
        cxw = lerp(1890, 1110, u)
        z = lerp(1.0, 0.5, u)
    blur_layer(c, 10)
    garden_bg(c, k.t, ox=-(cxw - 330) * 0.35 - 200)
    c.restore()
    c.save()
    c.translate(540, 1080)
    c.scale(z, z)
    c.translate(-cxw, -1080)
    for i, (x, name) in enumerate(FRUITS):
        e = prog(lt, seg[i] - 0.15, seg[i] + 0.3)
        if e <= 0:
            continue
        s = back_out(clamp(e), 1.6) * 0.9
        sw = 4 * math.sin(lt * 1.6 + i)
        yy = 1060 + 14 * math.sin(lt * 2 + i)
        if i == 0:
            chocopina(c, x, yy, s, rot=sw)
        elif i == 1:
            chocosandia(c, x, yy, s, rot=sw)
        else:
            chocofresa(c, x, yy - 20, s, rot=sw)
        dk = ((lt - seg[i]) % 1.3) / 1.3
        drop(c, x - 40, yy + lerp(200, 600, dk ** 2), 1.3)
        c.save()
        c.translate(x, 1650)
        eff = lerp(1.0, 0.62, clamp((1 - z) / 0.5))
        c.scale(eff / z, eff / z)
        label(c, name, 0, 0, prog(lt, seg[i] + 0.1, seg[i] + 0.4), size=48, rot=(-3, 2, -2)[i])
        c.restore()
    c.restore()
    sparkles(c, k.t, n=14, seed=6, a=0.6)


def scene4(c, k):  # momento familiar en el parque
    lt, T = k.lt, k.w
    zin = ease_in_out(prog(lt, k.D - 0.9, k.D + 0.1))
    cx = lerp(300, 760, ease_in_out(prog(lt, 0, k.D - 0.9)))
    kid_x, kid_y = 880, 1720
    blur_layer(c, 9)
    park_bg(c, k.t, ox=-(cx - 300) * 0.4)
    c.restore()
    # objetivo del zoom: el topogigio del niño
    tx, ty = kid_x + 150 * 0.72, kid_y - 300 * 0.72 - 120
    z = lerp(1.0, 2.6, zin)
    fx, fy = lerp(cx, tx, zin), lerp(1150, ty, zin)
    c.save()
    c.translate(540, lerp(1150, 980, zin))
    c.scale(z, z)
    c.translate(-fx, -fy)
    bite = lambda ph: max(0.0, math.sin(lt * 2.2 + ph)) ** 2  # noqa: E731
    fam_person(c, 160, 1760, 0.95, k.t, "#c98a62", "#2a1a10", "man", "#2a6ab8", 0.0,
               lambda c2, hx, hy: chocobanano(c2, hx, hy - 150, 0.42, rot=-20), bite(0))
    fam_person(c, 520, 1760, 0.9, k.t, "#f2c9a0", "#5a2a14", "woman", "#e85a8a", 1.3,
               lambda c2, hx, hy: chocofresa(c2, hx, hy - 160, 0.36, rot=-14), bite(1.8))
    fam_person(c, kid_x, kid_y, 0.72, k.t, "#e8b78c", "#3a2414", "kid", GOLD, 2.4,
               lambda c2, hx, hy: topogigio(c2, hx, hy - 120, 0.3, 0, t=k.t, rot=8), 0.0)
    c.restore()
    sparkles(c, k.t, n=12, seed=7, a=0.5)


SEL_WORDS = [6, 7, 10, 11, 12, 13, 15]


def sel_pos(k):
    lt = k.lt
    pos = 0.0
    for i in range(1, 7):
        a = k.w(SEL_WORDS[i]) - 0.32
        pos += ease_in_out(prog(lt, a, a + 0.3))
    return pos


def selector_bg(c, t):
    blur_layer(c, 16)
    beach_bg(c, t, ox=-20 * t % 200)
    c.restore()
    c.drawRect(RECT(0, 0, W, H), P(BORD, shader=rad(540, 980, 1200, [R.hexc(BORD, 0.35), R.hexc("#4a0012", 0.85)])))
    c.save()
    c.translate(540, 980)
    c.rotate(t * 12)
    for i in range(16):
        p = skia.Path()
        a0, a1 = math.radians(i * 22.5), math.radians(i * 22.5 + 9)
        p.moveTo(0, 0)
        p.lineTo(math.cos(a0) * 1600, math.sin(a0) * 1600)
        p.lineTo(math.cos(a1) * 1600, math.sin(a1) * 1600)
        p.close()
        c.drawPath(p, P(GOLD, alpha=0.08))
    c.restore()
    glow(c, R.RES.g_gold, 540, 980, 620, 0.45, skia.BlendMode.kScreen)
    for sd in (-1, 1):  # marco decorativo
        c.drawLine(540 + sd * 470, 560, 540 + sd * 470, 1420, P(GOLD, "stroke", 6, alpha=0.6))


def scene5(c, k):  # EL SELECTOR DE TOPOGIGIOS
    lt, T = k.lt, k.w
    selector_bg(c, k.t)
    pos = sel_pos(k)
    i0 = min(int(pos), 6)
    q = pos - i0
    fan = ease_in_out(prog(lt, T(16) - 0.2, T(16) + 0.5))
    ent = ease_out(clamp(lt / 0.4))
    s_main = lerp(2.0, 1.0, ent)
    if fan < 1:
        a = 1 - fan
        c.saveLayerAlpha(None, int(255 * a))
        topogigio(c, 540, lerp(1150, 1000, ent), s_main, i0, i0 + 1 if q > 0 and i0 < 6 else None, q, t=k.t)
        c.restore()
    if fan > 0:
        for j in range(7):
            ang = (j - 3) * 13
            x = 540 + (j - 3) * 140 * fan
            y = 1050 + abs(j - 3) * 40 * fan
            topogigio(c, x, y, lerp(1.0, 0.55, fan), j, t=k.t, rot=ang * fan)
        G.pop_text(c, "¡ELIGE TU FAVORITO!", 540, 1500, 78, prog(lt, T(16), T(16) + 0.3), col=GOLD, stroke=BORD)
    # barra del selector
    bk = ease_out(prog(lt, T(5) - 0.4, T(5)))
    if bk > 0 and fan < 1:
        a = bk * (1 - fan)
        y = 1590
        rrect(c, 40, y - 60, W - 40, y + 60, 60, P("#2a0010", alpha=0.7 * a))
        rrect(c, 40, y - 60, W - 40, y + 60, 60, P(GOLD, "stroke", 4, alpha=0.8 * a))
        rrect(c, 540 - 200, y - 50, 540 + 200, y + 50, 50, P(GOLD, alpha=a))
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(RECT(40, y - 60, W - 40, y + 60), 60, 60), True)
        for j, (name, *_) in enumerate(FLAVORS):
            x = 540 + (j - pos) * 400
            dist = abs(j - pos)
            sz = lerp(46, 34, clamp(dist))
            f = F(R.RES.mx, sz)
            w = f.measureText(name)
            col = BORD if dist < 0.5 else "#ffffff"
            c.drawString(name, x - w / 2, y + sz * 0.36, f, P(col, alpha=a * (1 - 0.4 * clamp(dist - 0.5))))
        c.restore()
        for sd in (-1, 1):  # flechitas
            tri = skia.Path()
            tri.moveTo(540 + sd * 220, y - 14)
            tri.lineTo(540 + sd * 236, y)
            tri.lineTo(540 + sd * 220, y + 14)
            c.drawPath(tri, P(BORD, alpha=a))
    if q > 0 and q < 1:
        R.RES.glow_gold = R.RES.g_gold
        R.burst(c, 540, 1000, q * 0.6, dur=0.6, n=24, radius=260, seed=int(pos * 7), intensity=0.6)
    sparkles(c, k.t, n=20, seed=8, a=0.8)


TOPS = [("mania", "MANÍA TRITURADA", 6), ("coco", "COCO RALLADO", 7), ("chispas", "CHISPAS DE CHOCOLATE", 10)]


def scene6(c, k):  # toppings sobre la mesa de madera
    lt, T = k.lt, k.w
    blur_layer(c, 10)
    terrace_bg(c, k.t, ox=40 * math.sin(lt * 0.5) - 60, table=True)
    c.restore()
    cur, prog_k, spin = None, 0.0, 1.0
    for kind, name, wi in TOPS:
        tw = T(wi)
        if lt >= tw - 0.3:
            cur = kind
            prog_k = prog(lt, tw - 0.1, tw + 0.9)
        sp = prog(lt, tw - 0.45, tw - 0.05)
        if 0 < sp < 1:
            spin = math.cos(math.pi * sp * 2)
            if sp < 0.5:
                cur_prev = [t_[0] for t_ in TOPS if T(t_[2]) < tw]
                cur = cur_prev[-1] if cur_prev else None
                prog_k = 1.0
    orbit = 10 * math.sin(lt * 0.9)
    z = 1.0 + 0.06 * math.sin(lt * 0.7)
    chocobanano(c, 540, 1040, 1.05 * z, rot=orbit * 0.5, spin=spin * (0.9 + 0.1 * math.cos(math.radians(orbit * 3))),
                top=cur, top_k=prog_k, seed=11 + (cur or "x").__len__(), t=k.t)
    for j, (kind, name, wi) in enumerate(TOPS):
        a = prog(lt, T(wi) - 0.1, T(wi) + 0.2)
        nxt = TOPS[j + 1][2] if j + 1 < 3 else 99
        a *= 1 - prog(lt, T(nxt) - 0.3, T(nxt) - 0.1) if nxt < 99 else 1
        label(c, name, 540, 1640, a, size=46, rot=(-3, 2, -2)[j])
    sparkles(c, k.t, n=14, seed=9, a=0.6)


def logo_circle(c, x, y, r, k, t):
    if k <= 0:
        return
    s = back_out(clamp(k), 1.8) * (1 + 0.02 * math.sin(t * 2))
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glow(c, R.RES.g_gold, 0, 0, r * 1.7, 0.55, skia.BlendMode.kScreen)
    oval(c, 8, 14, r, r, P("#000000", alpha=0.3, blur=10))
    oval(c, 0, 0, r, r, P(CREAM))
    oval(c, 0, 0, r, r, P(GOLD, "stroke", 10))
    c.save()
    c.clipPath(skia.Path().addCircle(0, 0, r - 5), True)
    img = R.RES.logo
    sz = r * 2 * 1.02
    c.drawImageRect(img, RECT(-sz / 2, -sz / 2, sz / 2, sz / 2), R.SAMP, skia.Paint())
    c.restore()
    c.restore()


def scene7(c, k):  # cierre al atardecer: productos, logo y dirección
    lt, T = k.lt, k.w
    u = ease_in_out(prog(lt, 0, 2.5))
    blur_layer(c, 9)
    c.save()
    z = lerp(1.15, 1.0, u)
    c.translate(540, 960)
    c.scale(z, z)
    c.translate(-540, -960)
    sunset_bg(c, k.t, oy=lerp(-200, 0, u))
    c.restore()
    c.restore()
    # composición de productos
    items = [
        (lambda x, y, s: topogigio(c, x, y, s * 0.62, 1, t=k.t, rot=-12), 170, 1560, 0.0),
        (lambda x, y, s: topogigio(c, x, y, s * 0.62, 3, t=k.t, rot=12), 910, 1560, 0.15),
        (lambda x, y, s: topogigio(c, x, y, s * 0.6, 5, t=k.t, rot=0), 540, 1500, 0.3),
        (lambda x, y, s: chocopina(c, x, y, s * 0.5, rot=-10), 300, 1640, 0.45),
        (lambda x, y, s: chocofresa(c, x, y, s * 0.48, rot=10), 780, 1650, 0.6),
        (lambda x, y, s: chocosandia(c, x, y, s * 0.5, rot=-4), 590, 1760, 0.75),
        (lambda x, y, s: chocobanano(c, x, y, s * 0.55, rot=-24), 120, 1780, 0.9),
        (lambda x, y, s: topogigio(c, x, y, s * 0.55, 0, t=k.t, rot=18), 980, 1800, 1.05),
    ]
    for fn, x, y, d in items:
        e = prog(lt, 0.2 + d, 0.6 + d)
        if e <= 0:
            continue
        fn(x, lerp(y + 700, y, back_out(clamp(e), 1.4)) + 8 * math.sin(k.t * 1.5 + x), 1.0)
    pulse = max(0, 1 - abs(lt - T(12)) / 0.4)
    logo_circle(c, 540, 830, 270 * (1 + 0.06 * pulse), prog(lt, 0.3, 0.9), k.t)
    R.RES.glow_gold = R.RES.g_gold
    R.burst(c, 540, 830, lt - T(12) + 0.1, dur=1.2, n=50, radius=520, seed=21, intensity=0.9)
    R.burst(c, 540, 830, lt - 0.5, dur=1.0, n=40, radius=420, seed=22, intensity=0.8)
    ak = prog(lt, T(0) - 0.1, T(0) + 0.3)
    if ak > 0:
        s = back_out(clamp(ak), 1.6)
        c.save()
        c.translate(540, 1240)
        c.scale(s, s)
        w, h = 480, 90
        rrect(c, -w + 6, -h + 10, w + 6, h + 10, 30, P("#000000", alpha=0.35, blur=8))
        rrect(c, -w, -h, w, h, 30, P(BORD))
        rrect(c, -w, -h, w, h, 30, P(GOLD, "stroke", 5))
        # pin de ubicación
        bob = 6 * math.sin(k.t * 4)
        pin = skia.Path()
        pin.moveTo(-405, 30 + bob)
        pin.cubicTo(-450, -10 + bob, -450, -60 + bob, -405, -60 + bob)
        pin.cubicTo(-360, -60 + bob, -360, -10 + bob, -405, 30 + bob)
        c.drawPath(pin, P(GOLD))
        oval(c, -405, -32 + bob, 12, 12, P(BORD))
        f1, f2 = F(R.RES.mx, 36), F(R.RES.mb, 32)
        c.drawString("Colonia El Progreso, Calle 13 de Mayo", -345, -14, f1, P("#ffffff"))
        c.drawString("Puerto Barrios, Izabal, Guatemala", -345, 40, f2, P(GOLD2))
        c.restore()
    sparkles(c, k.t, n=24, seed=10, a=0.8)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7]
WHIP = {1, 2, 4, 5}


def render_frame(c, t, vo, phr, total):
    global VO
    VO = vo
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(R.hexc("#000000"))
    k = R.Ctx(vo, si, t)
    lt = k.lt
    blur, dx = 0.0, 0.0
    if si in WHIP and lt < 0.25:  # barrido de cámara
        qq = 1 - ease_out(lt / 0.25)
        blur, dx = 60 * qq, 240 * qq
    if si == 3 and lt < 0.2:
        blur = 14 * (1 - lt / 0.2)
    if si == 6 and lt < 0.45:  # fundido hacia el atardecer
        R.SCENES = SCENES
        SCENES[5](c, R.Ctx(vo, 5, t))
        c.saveLayerAlpha(None, int(255 * smooth(lt / 0.45)))
    if blur > 0.3:
        blur_xy(c, blur, blur * 0.08)
    c.save()
    c.translate(dx, 0)
    SCENES[si](c, k)
    c.restore()
    if blur > 0.3:
        c.restore()
    if si == 6 and lt < 0.45:
        c.restore()
    # transición: una chocosandía pasa frente a la cámara (escena 3 -> 4)
    if len(vo) > 3:
        u = (t - (vo[3]["start"] - 0.35)) / 0.7
        if 0 < u < 1:
            chocosandia(c, lerp(1900, -800, ease_in_out(u)), 1000, 4.2, rot=-20)
    R.vignette(c, 0.35)
    fade_in = clamp(t / 0.3)
    fade_out = clamp((total - t) / 0.6)
    if min(fade_in, fade_out) < 1:
        c.drawRect(RECT(0, 0, W, H), P("#000000", alpha=1 - min(fade_in, fade_out)))
    draw_subs(c, t, phr)


def draw_subs(c, t, phr):
    """Subtítulos: palabras anteriores en blanco, la actual en dorado con borde borgoña."""
    f_past = F(R.RES.semi, 58)
    f_cur = F(R.RES.xbold, 72)
    for p in phr:
        if not (p["s"] <= t < p["e"]):
            continue
        fade = clamp((p["e"] - t) / 0.12)
        shown = [w for w in p["words"] if t >= w["s"] - 0.04]
        if not shown:
            continue
        cur = shown[-1]
        before = " ".join(w["w"] for w in shown[:-1])
        if before:
            lines, line = [], ""
            for wd in before.split():
                test = (line + " " + wd).strip()
                if f_past.measureText(test) > 900 and line:
                    lines.append(line)
                    line = wd
                else:
                    line = test
            lines.append(line)
            lines = lines[-2:]
            for i, ln in enumerate(lines):
                y = 360 - (len(lines) - 1 - i) * 68
                w = f_past.measureText(ln)
                c.drawString(ln, W / 2 - w / 2 + 3, y + 3, f_past, P("#000000", alpha=0.55 * fade, blur=5))
                c.drawString(ln, W / 2 - w / 2, y, f_past, P("#ffffff", alpha=0.92 * fade))
        kk = ease_out(clamp((t - cur["s"] + 0.04) / 0.12))
        w = f_cur.measureText(cur["w"])
        c.save()
        c.translate(W / 2, 452)
        c.scale(0.88 + 0.12 * kk, 0.88 + 0.12 * kk)
        c.drawString(cur["w"], -w / 2 + 4, 5, f_cur, P("#000000", alpha=0.5 * fade, blur=6))
        sp = P(BORD, "stroke", 12, alpha=fade)
        sp.setStrokeJoin(skia.Paint.kRound_Join)
        c.drawString(cur["w"], -w / 2, 0, f_cur, sp)
        c.drawString(cur["w"], -w / 2, 0, f_cur, P(GOLD, alpha=fade))
        c.restore()


def install():
    R.Res = BRes
    R.SCENES = SCENES
    R.SCENE_GRADE = {}
    R.render_frame = render_frame
    R.draw_subs = draw_subs
    R.draw_watermark = lambda c: None


if __name__ == "__main__":
    install()
    R.main()
