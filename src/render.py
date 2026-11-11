"""Renderizador 2D del video "El perfume que siempre quise" — Otto Aleman Perfumes.

Dibuja cada cuadro con skia (vectorial, antialias) y lo envía a ffmpeg.
Uso:
  python3 src/render.py --start 0 --end 8 --out build/prueba.mp4
  python3 src/render.py --out build/video.mp4 --jobs 4
"""
import argparse
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
import skia
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline  # noqa: E402

ROOT = timeline.ROOT
A = os.path.join(ROOT, "assets")
W, H, FPS = 1080, 1920, 30

# ----------------------------------------------------------------------------
# utilidades
# ----------------------------------------------------------------------------


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(max(0, min(1, a)) * 255))


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp(t)
    return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2


def back_out(t, s=1.7):
    t = clamp(t)
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def prog(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)


def mix_col(c1, c2, t):
    a, b = hexc(c1), hexc(c2)
    f = lambda x, y: int(lerp(x, y, clamp(t)))  # noqa: E731
    return skia.Color(f(skia.ColorGetR(a), skia.ColorGetR(b)), f(skia.ColorGetG(a), skia.ColorGetG(b)),
                      f(skia.ColorGetB(a), skia.ColorGetB(b)), 255)


def P(color, style="fill", width=1.0, cap=None, blend=None, shader=None, blur=None, alpha=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor(color if isinstance(color, int) else hexc(color))
    if style == "stroke":
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(width)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap is None else cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if shader is not None:
        p.setShader(shader)
    if blend is not None:
        p.setBlendMode(blend)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if alpha is not None:
        p.setAlphaf(clamp(alpha))
    return p


def lin(x0, y0, x1, y1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)],
                                          [hexc(c) if isinstance(c, str) else c for c in cols], pos)


def rad(cx, cy, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(cx, cy), r,
                                          [hexc(c) if isinstance(c, str) else c for c in cols], pos)


def R(x0, y0, x1, y1):
    return skia.Rect.MakeLTRB(x0, y0, x1, y1)


def rrect(c, x0, y0, x1, y1, r, paint):
    c.drawRRect(skia.RRect.MakeRectXY(R(x0, y0, x1, y1), r, r), paint)


def oval(c, cx, cy, rx, ry, paint):
    c.drawOval(R(cx - rx, cy - ry, cx + rx, cy + ry), paint)


def rng(seed):
    return np.random.default_rng(seed)


# ----------------------------------------------------------------------------
# recursos
# ----------------------------------------------------------------------------
SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


def load_img(name):
    arr = np.asarray(Image.open(os.path.join(A, name)).convert("RGBA")).copy()
    return skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType,
                                alphaType=skia.kUnpremul_AlphaType).withDefaultMipmaps()


def sprite(r, g, b, n=128, power=2.2):
    y, x = np.mgrid[0:n, 0:n]
    d = np.sqrt((x - n / 2 + .5) ** 2 + (y - n / 2 + .5) ** 2) / (n / 2)
    a = np.clip(1 - d, 0, 1) ** power
    arr = np.zeros((n, n, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = r, g, b
    arr[..., 3] = (a * 255).astype(np.uint8)
    return skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)


class Res:
    def __init__(self):
        f = os.path.join(A, "fonts")
        self.bold = skia.Typeface.MakeFromFile(os.path.join(f, "Poppins_700Bold.ttf"))
        self.semi = skia.Typeface.MakeFromFile(os.path.join(f, "Poppins_600SemiBold.ttf"))
        self.medium = skia.Typeface.MakeFromFile(os.path.join(f, "Poppins_500Medium.ttf"))
        self.xbold = skia.Typeface.MakeFromFile(os.path.join(f, "Poppins_800ExtraBold.ttf"))
        self.decant = load_img("decant.png")
        self.logo_gold = load_img("logo_gold.png")
        self.logo_white = load_img("logo_white.png")
        self.glow_gold = sprite(255, 196, 90)
        self.glow_warm = sprite(255, 150, 60, power=1.6)
        self.glow_white = sprite(255, 248, 225, power=3.0)
        self.soft_dark = sprite(0, 0, 0, power=1.5)
        self.glows = {k: sprite(*v, power=1.8) for k, v in {
            "rose": (255, 120, 160), "teal": (80, 220, 210), "violet": (170, 120, 255),
            "amber": (255, 170, 60), "emerald": (90, 230, 140), "gold": (255, 210, 110)}.items()}


RES = None


def font(tf, size):
    f = skia.Font(tf, size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def text_center(c, s, x, y, f, paint):
    w = f.measureText(s)
    c.drawString(s, x - w / 2, y, f, paint)
    return w


def draw_img(c, img, cx, cy, h, rot=0.0, alpha=1.0, blend=None):
    s = h / img.height()
    w = img.width() * s
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(clamp(alpha))
    if blend is not None:
        p.setBlendMode(blend)
    c.drawImageRect(img, R(-w / 2, -h / 2, w / 2, h / 2), SAMP, p)
    c.restore()


def glow(c, img, x, y, r, alpha, blend=skia.BlendMode.kPlus):
    if alpha <= 0.002 or r <= 0.5:
        return
    p = skia.Paint()
    p.setAlphaf(clamp(alpha))
    p.setBlendMode(blend)
    c.drawImageRect(img, R(x - r, y - r, x + r, y + r), SAMP, p)


# ----------------------------------------------------------------------------
# partículas doradas (sin estado: todo depende del tiempo)
# ----------------------------------------------------------------------------


def aroma(c, x, y, t, n=46, height=700, spread=60, intensity=1.0, seed=1, speed=0.32, size=1.0, tail=1.0):
    """Columna de aroma: chispas doradas que suben ondulando."""
    if intensity <= 0:
        return
    r = rng(seed)
    ph = r.random(n)
    sp = speed * (0.7 + 0.6 * r.random(n))
    sway = r.random(n) * 6.28
    sz = (3 + 9 * r.random(n) ** 2) * size
    for i in range(n):
        age = (t * sp[i] + ph[i]) % 1.0
        yy = y - age * height
        amp = spread * (0.3 + age * 1.6) * tail
        xx = x + math.sin(age * 7.0 + sway[i] + t * 0.8) * amp
        a = math.sin(math.pi * age) ** 1.3 * intensity
        tw = 0.65 + 0.35 * math.sin(t * 9 + sway[i] * 3)
        glow(c, RES.glow_gold, xx, yy, sz[i] * 4.2, a * 0.55 * tw)
        glow(c, RES.glow_white, xx, yy, sz[i] * 1.4, a * 0.9 * tw)


def dust(c, t, n=40, seed=7, alpha=0.5, area=(0, 0, W, H), col=None, big=False):
    """Polvo/bokeh dorado que flota lento por toda la escena."""
    r = rng(seed)
    x0, y0, x1, y1 = area
    px, py = r.random(n), r.random(n)
    sp = 0.01 + 0.02 * r.random(n)
    ph = r.random(n) * 6.28
    sz = 2 + 6 * r.random(n) ** 3
    if big:
        sz = 14 + 40 * r.random(n) ** 2
    img = col or RES.glow_gold
    for i in range(n):
        yy = y0 + ((py[i] - t * sp[i]) % 1.0) * (y1 - y0)
        xx = x0 + px[i] * (x1 - x0) + math.sin(t * 0.5 + ph[i]) * 25
        tw = 0.5 + 0.5 * math.sin(t * 2.3 + ph[i] * 2)
        if big:
            glow(c, img, xx, yy, sz[i], alpha * (0.25 + 0.2 * tw), skia.BlendMode.kScreen)
        else:
            glow(c, img, xx, yy, sz[i] * 3.5, alpha * 0.5 * tw)
            glow(c, RES.glow_white, xx, yy, sz[i], alpha * tw)


def burst(c, x, y, t, dur=1.2, n=60, radius=420, seed=3, intensity=1.0):
    """Explosión de chispas (destello mágico)."""
    k = t / dur
    if k < 0 or k > 1:
        return
    r = rng(seed)
    ang = r.random(n) * 6.28
    dist = (0.3 + 0.7 * r.random(n)) * radius
    sz = 3 + 8 * r.random(n)
    e = ease_out(k)
    a = (1 - k) ** 1.5 * intensity
    glow(c, RES.glow_warm, x, y, radius * (0.5 + 0.8 * e), a * 0.6)
    glow(c, RES.glow_white, x, y, radius * 0.35 * (1 - k), a)
    for i in range(n):
        xx = x + math.cos(ang[i]) * dist[i] * e
        yy = y + math.sin(ang[i]) * dist[i] * e - 60 * k
        glow(c, RES.glow_gold, xx, yy, sz[i] * 4, a * 0.6)
        glow(c, RES.glow_white, xx, yy, sz[i] * 1.2, a)


def orbit_sparkles(c, x, y, t, rx=230, ry=90, n=26, seed=11, intensity=1.0):
    r = rng(seed)
    ph = r.random(n) * 6.28
    sp = 0.6 + 0.8 * r.random(n)
    off = (r.random(n) - .5) * 120
    sz = 3 + 7 * r.random(n)
    for i in range(n):
        a = ph[i] + t * sp[i]
        xx = x + math.cos(a) * rx
        yy = y + math.sin(a) * ry + off[i] + math.sin(t + i) * 20
        tw = 0.5 + 0.5 * math.sin(t * 6 + i)
        glow(c, RES.glow_gold, xx, yy, sz[i] * 4, intensity * 0.5 * tw)
        glow(c, RES.glow_white, xx, yy, sz[i] * 1.2, intensity * tw)


# ----------------------------------------------------------------------------
# personaje
# ----------------------------------------------------------------------------
SKIN = ("#ffe2c8", "#f3b991")
EXPR = {
    "neutral": ("open", "flat", "neutral"),
    "dreamy": ("open", "happy", "smile"),
    "sad": ("open", "sad", "sad"),
    "worried": ("open", "sad", "worried"),
    "surprised": ("wide", "up", "o"),
    "bliss": ("closed", "happy", "smile"),
    "happy": ("open", "happy", "grin"),
    "joy": ("closed", "happy", "grin"),
}


def draw_kid(c, x, y, s, t, expr="neutral", look=(0.0, 0.0), hands=None, tilt=0.0, legs=(0.0, 0.0),
             bob=0.0, blink=True, behind_hand=None, front_props=None, style=None, talk=0.0):
    """Personaje (por defecto: chico de suéter azul). (x, y) = pies.
    hands = {'L': (hx, hy), 'R': (hx, hy)} en coords locales.
    style: shirt (3 colores), arm, pants (2), hair ('short'|'long'), lashes, earrings (color)."""
    st = {"shirt": ("#5a8cf0", "#3a68cf", "#2a4fae"), "hem": "#2c4fa8", "collar": "#2b4ca3", "arm": "#3a69cf",
          "arm_hl": "#5b8df0", "pants": ("#34498c", "#22346c"), "hair": "short", "hair_col": ("#2c2a3d", "#141320"),
          "lashes": False, "earrings": None, "lips": "#4a1f2a", "robe": False, "headwear": None,
          "head_col": ("#d9a066", "#a87440"), "ghutra": ("#ffffff", None), "beard": None, "glasses": False,
          "skin": ("#ffe6cf", "#f9caa5", "#eeb08a")}
    st.update(style or {})
    sk = st["skin"]
    eyes, brows, mouth = EXPR[expr]
    hands = hands or {}
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    # sombra en el piso
    glow(c, RES.soft_dark, 0, 0, 160, 0.55, skia.BlendMode.kSrcOver)
    c.save()
    c.scale(1.0, 0.18)
    glow(c, RES.soft_dark, 0, 0, 150, 0.6, skia.BlendMode.kSrcOver)
    c.restore()
    c.translate(0, bob)
    # piernas
    for side, ang in ((-1, legs[0]), (1, legs[1])):
        if st["robe"]:  # con túnica solo se ven las sandalias
            oval(c, side * 34 + ang * 0.8, -4, 34, 14, P("#7a5230"))
            continue
        c.save()
        c.translate(side * 32, -200)
        c.rotate(ang)
        rrect(c, -19, 0, 19, 186, 18, P("#2b3e7c", shader=lin(-19, 0, 19, 0, list(st["pants"]))))
        oval(c, side * 8, 186, 40, 20, P("#1f2537"))
        oval(c, side * 8 - 8, 180, 16, 6, P("#ffffff", alpha=0.12))
        c.restore()
    # torso (suéter)
    body = skia.Path()
    body.moveTo(-60, -402)
    body.quadTo(-94, -392, -98, -352)
    if st["robe"]:  # túnica larga hasta los pies
        body.lineTo(-128, -24)
        body.quadTo(-128, -2, -100, -2)
        body.lineTo(100, -2)
        body.quadTo(128, -2, 128, -24)
    else:
        body.lineTo(-106, -214)
        body.quadTo(-106, -178, -72, -178)
        body.lineTo(72, -178)
        body.quadTo(106, -178, 106, -214)
    body.lineTo(98, -352)
    body.quadTo(94, -392, 60, -402)
    body.close()
    c.drawPath(body, P("#3f72d6", shader=lin(-100, -400, 100, -180 if not st["robe"] else 0, list(st["shirt"]), [0, .55, 1])))
    if st["robe"]:
        c.drawLine(0, -395, 0, -250, P("#000000", "stroke", 3, alpha=0.12))
        c.drawLine(-40, -150, -50, -10, P("#000000", "stroke", 3, alpha=0.06))
        c.drawLine(40, -150, 50, -10, P("#000000", "stroke", 3, alpha=0.06))
    else:
        rrect(c, -106, -206, 106, -178, 18, P(st["hem"]))
    c.drawPath(body, P("#ffffff", "stroke", 3, alpha=0.08))
    oval(c, 0, -400, 44, 15, P(st["collar"]))
    # brazos
    out = {}
    for side, key in ((-1, "L"), (1, "R")):
        sx, sy = side * 84, -366
        tx, ty = hands.get(key, (side * 112, -190))
        l1, l2 = 108, 104
        dx, dy = tx - sx, ty - sy
        d = math.hypot(dx, dy)
        if d > l1 + l2 - 1:
            k = (l1 + l2 - 1) / d
            tx, ty = sx + dx * k, sy + dy * k
            d = l1 + l2 - 1
        d = max(d, 20)
        a = math.atan2(ty - sy, tx - sx)
        b = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1))
        ang = a + b * side  # codo hacia afuera
        ex, ey = sx + math.cos(ang) * l1, sy + math.sin(ang) * l1
        arm = skia.Path()
        arm.moveTo(sx, sy)
        arm.lineTo(ex, ey)
        arm.lineTo(tx, ty)
        c.drawPath(arm, P(st["arm"], "stroke", 38))
        c.drawPath(arm, P(st["arm_hl"], "stroke", 12, alpha=0.25))
        out[key] = (tx, ty)
    if behind_hand:
        behind_hand(c, out)
    for key, (tx, ty) in out.items():
        oval(c, tx, ty, 23, 23, P("#f6c09a", shader=rad(tx - 8, ty - 8, 30, [sk[0], sk[1]])))
    # cabeza
    c.save()
    c.translate(0, -508)
    c.rotate(tilt)
    if st["headwear"] == "ghutra":  # paño que cae por detrás hasta los hombros
        gcol, gpat = st["ghutra"]
        drape = skia.Path()
        drape.moveTo(-124, -10)
        drape.cubicTo(-136, -140, 136, -140, 124, -10)
        drape.lineTo(150, 170)
        drape.quadTo(150, 205, 110, 205)
        drape.lineTo(-110, 205)
        drape.quadTo(-150, 205, -150, 170)
        drape.close()
        c.drawPath(drape, P(gcol, shader=lin(0, -130, 0, 205, [gcol, "#e6e2da"])))
        if gpat:
            c.save()
            c.clipPath(drape, True)
            for i in range(-8, 9):
                c.drawLine(i * 26, -140, i * 26 + 80, 210, P(gpat, "stroke", 4, alpha=0.55))
                c.drawLine(i * 26, -140, i * 26 - 80, 210, P(gpat, "stroke", 4, alpha=0.55))
            c.restore()
    if st["hair"] == "long":  # melena por detrás de la cabeza
        back = skia.Path()
        back.moveTo(-118, 0)
        back.cubicTo(-130, -120, 130, -120, 118, 0)
        back.lineTo(128, 150)
        back.quadTo(130, 190, 90, 190)
        back.lineTo(-90, 190)
        back.quadTo(-130, 190, -128, 150)
        back.close()
        c.drawPath(back, P("#1d1c2a", shader=lin(0, -120, 0, 190, list(st["hair_col"]))))
    for side in (-1, 1):
        oval(c, side * 103, 8, 20, 24, P(sk[2]))
        if st["earrings"]:
            oval(c, side * 104, 40, 8, 8, P(st["earrings"]))
            oval(c, side * 102, 37, 3, 3, P("#ffffff", alpha=0.8))
    oval(c, 0, 0, 108, 102, P("#f6c09a", shader=rad(-34, -36, 170, list(sk), [0, .6, 1])))
    hair = skia.Path()
    if st["hair"] == "long":  # flequillo de lado
        hair.moveTo(-110, 30)
        hair.cubicTo(-118, -84, -54, -124, 4, -122)
        hair.cubicTo(72, -122, 118, -80, 110, 30)
        hair.quadTo(96, -30, 60, -52)
        hair.quadTo(10, -30, -60, -40)
        hair.quadTo(-96, -20, -110, 30)
        hair.close()
    else:
        hair.moveTo(-108, 4)
        hair.cubicTo(-114, -84, -54, -122, 4, -120)
        hair.cubicTo(70, -120, 116, -80, 108, 4)
        hair.lineTo(100, -30)
        hair.quadTo(82, -62, 52, -50)
        hair.quadTo(30, -72, 4, -54)
        hair.quadTo(-24, -72, -52, -50)
        hair.quadTo(-84, -60, -100, -30)
        hair.close()
    if st["hair"] != "none":
        c.drawPath(hair, P("#1d1c2a", shader=lin(0, -120, 0, -30, list(st["hair_col"]))))
        hl = skia.Path()
        hl.moveTo(-50, -100)
        hl.quadTo(-10, -114, 30, -106)
        c.drawPath(hl, P("#ffffff", "stroke", 6, alpha=0.18))
    hw = st["headwear"]
    if hw == "ghutra":
        gcol, gpat = st["ghutra"]
        top = skia.Path()
        top.moveTo(-122, 10)
        top.cubicTo(-130, -150, 130, -150, 122, 10)
        top.quadTo(110, -52, 0, -58)
        top.quadTo(-110, -52, -122, 10)
        top.close()
        c.drawPath(top, P(gcol))
        if gpat:
            c.save()
            c.clipPath(top, True)
            for i in range(-8, 9):
                c.drawLine(i * 26, -150, i * 26 + 60, 20, P(gpat, "stroke", 4, alpha=0.55))
                c.drawLine(i * 26, -150, i * 26 - 60, 20, P(gpat, "stroke", 4, alpha=0.55))
            c.restore()
        oval(c, 0, -84, 104, 26, P("#1a1a1a", "stroke", 9))  # agal
        oval(c, 0, -96, 98, 22, P("#1a1a1a", "stroke", 8))
    elif hw == "cap":
        hc = st["head_col"]
        dome = skia.Path()
        dome.moveTo(-112, -24)
        dome.cubicTo(-116, -128, 116, -128, 112, -24)
        dome.close()
        c.drawPath(dome, P(hc[0], shader=lin(0, -128, 0, -24, list(hc))))
        oval(c, 0, -26, 122, 22, P(hc[1]))
        oval(c, 0, -112, 10, 7, P(hc[1]))
    elif hw == "safari":
        oval(c, 0, -46, 170, 34, P("#c9a46a"))
        dome = skia.Path()
        dome.moveTo(-104, -46)
        dome.cubicTo(-110, -160, 110, -160, 104, -46)
        dome.close()
        c.drawPath(dome, P("#d9b47a", shader=lin(0, -160, 0, -46, ["#e9c88e", "#b8915a"])))
        c.drawRect(R(-104, -76, 104, -54), P("#7a5230"))
    lx, ly = look[0] * 9, look[1] * 7
    blinking = blink and eyes in ("open", "wide") and ((t + 0.7) % 3.6) < 0.11
    dark = P("#1a1a24")
    for side in (-1, 1):
        ex, ey = side * 38 + lx, 6 + ly
        if eyes == "closed" or blinking:
            pth = skia.Path()
            if eyes == "closed":
                pth.moveTo(ex - 15, ey + 4)
                pth.quadTo(ex, ey - 10, ex + 15, ey + 4)
            else:
                pth.moveTo(ex - 14, ey + 2)
                pth.lineTo(ex + 14, ey + 2)
            c.drawPath(pth, P("#1a1a24", "stroke", 6))
        else:
            rx, ry = (13, 16) if eyes == "open" else (16, 20)
            oval(c, ex, ey, rx, ry, dark)
            if st["lashes"]:
                lp = skia.Path()
                lp.moveTo(ex + side * (rx - 3), ey - ry + 6)
                lp.lineTo(ex + side * (rx + 8), ey - ry - 2)
                lp.moveTo(ex + side * (rx - 9), ey - ry + 1)
                lp.lineTo(ex + side * (rx - 2), ey - ry - 8)
                c.drawPath(lp, P("#1a1a24", "stroke", 4))
            oval(c, ex + 5, ey - 7, 5, 5, P("#ffffff"))
            oval(c, ex - 4, ey + 6, 2.2, 2.2, P("#ffffff", alpha=0.7))
    if st["glasses"]:
        for side in (-1, 1):
            rrect(c, side * 38 - 30, -16, side * 38 + 30, 26, 14, P("#14101c", alpha=0.92))
            rrect(c, side * 38 - 22, -10, side * 38 - 6, 2, 5, P("#ffffff", alpha=0.25))
        c.drawLine(-8, -2, 8, -2, P("#14101c", "stroke", 6))
    # cejas
    for side in (-1, 1):
        bx, by = side * 40 + lx * 0.5, -30 + ly * 0.4
        pth = skia.Path()
        if brows == "sad":
            pth.moveTo(bx - side * 15, by - 9)
            pth.lineTo(bx + side * 15, by + 3)
        elif brows == "up":
            pth.moveTo(bx - 15, by - 14)
            pth.quadTo(bx, by - 22, bx + 15, by - 14)
        elif brows == "happy":
            pth.moveTo(bx - 15, by - 2)
            pth.quadTo(bx, by - 10, bx + 15, by - 2)
        else:
            pth.moveTo(bx - 14, by - 3)
            pth.lineTo(bx + 14, by - 3)
        c.drawPath(pth, P("#1d1c2a", "stroke", 7))
    for side in (-1, 1):
        oval(c, side * 62, 38, 18, 10, P("#ff7f93", alpha=0.42))
    mx, my = lx * 0.6, 50 + ly * 0.4
    if st["beard"]:
        bd = skia.Path()
        bd.moveTo(-104, 0)
        bd.quadTo(-96, 112, 0, 116)
        bd.quadTo(96, 112, 104, 0)
        bd.quadTo(82, 70, 34, 72)
        bd.quadTo(0, 66, -34, 72)
        bd.quadTo(-82, 70, -104, 0)
        bd.close()
        c.drawPath(bd, P(st["beard"]))
        ms = skia.Path()
        ms.moveTo(mx - 30, my - 2)
        ms.quadTo(mx, my - 20, mx + 30, my - 2)
        ms.quadTo(mx, my - 8, mx - 30, my - 2)
        c.drawPath(ms, P(st["beard"]))
    m = skia.Path()
    if talk > 0.08:  # boca hablando (sincronizada con la voz)
        oval(c, mx, my + 6, 15 + 5 * talk, 4 + 15 * talk, P("#5a2230"))
        oval(c, mx, my + 8 + 9 * talk, 8 + 2 * talk, 2 + 4 * talk, P("#ff8a9a"))
    elif mouth == "smile":
        m.moveTo(mx - 20, my)
        m.quadTo(mx, my + 18, mx + 20, my)
        c.drawPath(m, P(st["lips"], "stroke", 6))
    elif mouth == "sad":
        m.moveTo(mx - 18, my + 10)
        m.quadTo(mx, my - 6, mx + 18, my + 10)
        c.drawPath(m, P(st["lips"], "stroke", 6))
    elif mouth == "worried":
        m.moveTo(mx - 18, my + 6)
        m.quadTo(mx - 9, my - 2, mx, my + 6)
        m.quadTo(mx + 9, my + 13, mx + 18, my + 5)
        c.drawPath(m, P(st["lips"], "stroke", 5.5))
    elif mouth == "o":
        oval(c, mx, my + 6, 12, 15, P("#5a2230"))
    elif mouth == "grin":
        m.moveTo(mx - 28, my - 4)
        m.quadTo(mx, my + 44, mx + 28, my - 4)
        m.close()
        c.drawPath(m, P("#5a2230"))
        oval(c, mx, my + 16, 11, 6, P("#ff8a9a"))
    else:
        m.moveTo(mx - 15, my + 4)
        m.quadTo(mx, my + 8, mx + 15, my + 4)
        c.drawPath(m, P(st["lips"], "stroke", 5.5))
    c.restore()
    if front_props:
        front_props(c, out)
    c.restore()
    return {k: (x + s * hx, y + s * (hy + bob)) for k, (hx, hy) in out.items()}


# ----------------------------------------------------------------------------
# props
# ----------------------------------------------------------------------------


def draw_bottle(c, x, y, s, rot=0.0, cap=True, glow_a=0.0):
    """Frasco grande dorado (perfume completo). (x, y) = base."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if glow_a > 0:
        glow(c, RES.glow_warm, 0, -140, 330, glow_a * 0.55)
    gold = lin(-82, 0, 82, 0, ["#7a4c12", "#e3ac4a", "#ffe7a6", "#f2c461", "#b47a24", "#6e430f"], [0, .25, .42, .6, .85, 1])
    rrect(c, -82, -214, 82, 0, 34, P("#d9a441", shader=gold))
    rrect(c, -64, -200, 64, -12, 26, P("#ffffff", alpha=0.0))
    rrect(c, -58, -194, -42, -24, 8, P("#ffffff", alpha=0.35))
    rrect(c, 38, -170, 48, -60, 5, P("#ffffff", alpha=0.18))
    rrect(c, -82, -124, 82, -98, 4, P("#a8711f", shader=lin(-82, 0, 82, 0, ["#6e430f", "#c99035", "#f6d585", "#c99035", "#6e430f"])))
    c.drawLine(-82, -111, 82, -111, P("#fff1c4", "stroke", 2, alpha=0.6))
    rrect(c, -26, -244, 26, -212, 6, P("#b8842e", shader=lin(-26, 0, 26, 0, ["#6e430f", "#f0cd78", "#7a4c12"])))
    if cap:
        rrect(c, -46, -326, 46, -240, 16, P("#d9a441", shader=lin(-46, 0, 46, 0, ["#7a4c12", "#f7d887", "#ffefbf", "#c8913a", "#6e430f"], [0, .3, .45, .75, 1])))
        rrect(c, -34, -316, -24, -252, 5, P("#ffffff", alpha=0.35))
    else:
        oval(c, 0, -244, 22, 6, P("#3a240a"))
    c.restore()


def draw_decant(c, x, y, h, rot=0.0, alpha=1.0, glow_a=0.0, glow_img=None, fill=None, shadow=True):
    """Decant real (foto del cliente). (x, y) = centro."""
    if glow_a > 0:
        glow(c, glow_img or RES.glow_gold, x, y, h * 0.85, glow_a * 0.6)
        glow(c, RES.glow_white, x, y, h * 0.35, glow_a * 0.25)
    if shadow and alpha > 0.05:
        c.save()
        c.translate(x, y + h * 0.5)
        c.scale(1, 0.16)
        glow(c, RES.soft_dark, 0, 0, h * 0.28, 0.6 * alpha, skia.BlendMode.kSrcOver)
        c.restore()
    draw_img(c, RES.decant, x, y, h, rot, alpha)
    if fill is not None and fill > 0:
        # líquido dorado subiendo en la ventanita (x 104-156, y 565-880 en la imagen 257x1070)
        sc = h / 1070.0
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        x0, x1 = (104 - 128.5) * sc, (156 - 128.5) * sc
        y0, y1 = (565 - 535) * sc, (880 - 535) * sc
        top = lerp(y1, y0 + 6 * sc, clamp(fill))
        c.clipRRect(skia.RRect.MakeRectXY(R(x0, y0, x1, y1), 22 * sc, 22 * sc), True)
        c.drawRect(R(x0, top, x1, y1), P("#f2b544", shader=lin(0, top, 0, y1, ["#ffe08a", "#e09a2c"]), alpha=0.92 * alpha))
        c.drawRect(R(x0, top - 2, x1, top + 3), P("#fff6d0", alpha=0.8 * alpha))
        c.restore()


def price_tag(c, x, y, rot, text, a=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.drawLine(0, -70, 0, -26, P("#d8c9a8", "stroke", 3, alpha=a))
    tag = skia.Path()
    tag.moveTo(-70, -10)
    tag.lineTo(-40, -32)
    tag.lineTo(70, -32)
    tag.lineTo(70, 32)
    tag.lineTo(-40, 32)
    tag.close()
    c.save()
    c.rotate(90)
    c.drawPath(tag, P("#fbf3e2", alpha=a))
    oval(c, -50, 0, 6, 6, P("#9b8a6b", alpha=a))
    c.restore()
    f = font(RES.xbold, 30)
    c.save()
    c.rotate(90)
    text_center(c, text, 12, 11, f, P("#b3262e", alpha=a))
    c.restore()
    c.restore()


def piggy(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for lx in (-38, -12, 18, 42):
        rrect(c, lx - 9, -10, lx + 9, 14, 6, P("#e98aa3"))
    oval(c, 0, -52, 78, 56, P("#f6a7bb", shader=rad(-20, -80, 110, ["#ffd1dc", "#f39ab2"])))
    oval(c, 74, -52, 18, 16, P("#f08aa6"))
    oval(c, 70, -54, 3, 4, P("#9c4560"))
    oval(c, 80, -54, 3, 4, P("#9c4560"))
    oval(c, 40, -72, 6, 7, P("#1a1a24"))
    tri = skia.Path()
    tri.moveTo(14, -100)
    tri.lineTo(30, -126)
    tri.lineTo(40, -96)
    tri.close()
    c.drawPath(tri, P("#f08aa6"))
    rrect(c, -22, -110, 18, -103, 3, P("#9c4560"))
    c.restore()


def coin(c, x, y, r, a=1.0):
    oval(c, x, y, r, r * 0.42, P("#c9902f", alpha=a))
    oval(c, x, y - r * 0.12, r, r * 0.42, P("#f4cf6a", shader=lin(x - r, y, x + r, y, ["#d9a441", "#ffe9a8", "#c9902f"]), alpha=a))


def thought(c, x, y, k, t):
    if k <= 0:
        return
    s = back_out(k)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for (bx, by, br) in ((-118, 178, 13), (-92, 132, 21)):
        oval(c, bx, by, br, br, P("#f4f1fb", alpha=0.95))
    for (bx, by, rx, ry) in ((-70, 10, 110, 92), (60, -10, 120, 100), (0, -60, 100, 80), (20, 60, 120, 70)):
        oval(c, bx, by, rx, ry, P("#f4f1fb"))
    draw_bottle(c, -35, 70, 0.42, rot=-6 + 3 * math.sin(t * 2))
    f = font(RES.xbold, 120)
    text_center(c, "?", 80, 50, f, P("#5a7bd8"))
    c.restore()


def pill(c, x, y, text, k, size=44, col_text="#2a1a08", bg="#fff8ea", border="#d6a24a"):
    if k <= 0:
        return
    s = back_out(k)
    f = font(RES.bold, size)
    w = f.measureText(text) + size * 1.1
    h = size * 1.7
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glow(c, RES.soft_dark, 0, 10, w * 0.6, 0.35, skia.BlendMode.kSrcOver)
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, h / 2, P(bg))
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, h / 2, P(border, "stroke", 4))
    text_center(c, text, 0, size * 0.36, f, P(col_text))
    c.restore()


def shopping_bag(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    h = skia.Path()
    h.moveTo(-22, 0)
    h.quadTo(-22, -38, 0, -38)
    h.quadTo(22, -38, 22, 0)
    c.drawPath(h, P("#c99a45", "stroke", 6))
    rrect(c, -50, 0, 50, 110, 6, P("#1b1620", shader=lin(-50, 0, 50, 0, ["#2a2330", "#121016"])))
    rrect(c, -50, 0, 50, 110, 6, P("#c99a45", "stroke", 3))
    draw_img(c, RES.logo_gold, 0, 55, 56)
    c.restore()


# ----------------------------------------------------------------------------
# escenarios
# ----------------------------------------------------------------------------


def night_sky(c, x0, y0, x1, y1, t, top="#17132c", bottom="#3a2a58", stars=70, seed=5):
    c.drawRect(R(x0, y0, x1, y1), P(top, shader=lin(0, y0, 0, y1, [top, bottom])))
    r = rng(seed)
    for i in range(stars):
        sx, sy = lerp(x0, x1, r.random()), lerp(y0, y1, r.random() ** 1.4)
        tw = 0.4 + 0.6 * abs(math.sin(t * (0.8 + r.random()) + i))
        oval(c, sx, sy, 1.6 + 1.4 * r.random(), 1.6 + 1.4 * r.random(), P("#ffffff", alpha=0.75 * tw))


def moon(c, x, y, r):
    glow(c, RES.glow_white, x, y, r * 4.0, 0.35)
    oval(c, x, y, r, r, P("#fffbe9", shader=rad(x - r * .3, y - r * .3, r * 1.2, ["#ffffff", "#f1ead1"])))


def city(c, x0, x1, base, col="#1d1830", seed=9):
    r = rng(seed)
    x = x0
    while x < x1:
        w = 40 + 70 * r.random()
        h = 40 + 150 * r.random()
        c.drawRect(R(x, base - h, x + w, base), P(col))
        if r.random() > .5:
            c.drawRect(R(x + w * .4, base - h - 30, x + w * .45, base - h), P(col))
        x += w + 4


def window(c, x0, y0, x1, y1, t, moon_pos=None):
    rrect(c, x0 - 22, y0 - 22, x1 + 22, y1 + 22, 10, P("#5a3a26", shader=lin(x0, y0, x1, y1, ["#6e4a31", "#3d2618"])))
    c.save()
    c.clipRect(R(x0, y0, x1, y1))
    night_sky(c, x0, y0, x1, y1, t, "#1f2a5a", "#5b4a88", stars=40)
    if moon_pos:
        moon(c, *moon_pos)
    city(c, x0, x1, y1, "#262043")
    c.restore()
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    c.drawRect(R(mx - 7, y0, mx + 7, y1), P("#5a3a26"))
    c.drawRect(R(x0, my - 7, x1, my + 7), P("#5a3a26"))
    rrect(c, x0 - 34, y1 + 14, x1 + 34, y1 + 34, 6, P("#6e4a31"))


def wall_and_floor(c, t, floor_y=1420, wall=("#2c2442", "#3b2e55"), floor=("#3d2618", "#1a0f09")):
    c.drawRect(R(-400, -400, W + 400, floor_y), P(wall[0], shader=lin(0, 0, 0, floor_y, list(wall))))
    c.drawRect(R(-400, floor_y, W + 400, H + 400), P(floor[0], shader=lin(0, floor_y, 0, H, list(floor))))
    for i in range(7):
        yy = floor_y + 30 + i * i * 14
        c.drawLine(-400, yy, W + 400, yy, P("#000000", "stroke", 2, alpha=0.18))
    c.drawRect(R(-400, floor_y - 14, W + 400, floor_y), P("#24172a"))


def bed(c, x0, y0, x1, y1):
    rrect(c, x1 - 40, y0 - 160, x1 + 10, y1, 14, P("#6e4a31", shader=lin(x1 - 40, 0, x1 + 10, 0, ["#7d5638", "#4a2f1e"])))
    rrect(c, x0, y0 + 40, x1, y1 - 20, 16, P("#5b3c27"))
    rrect(c, x0 + 6, y0, x1 - 30, y0 + 70, 22, P("#dfe3f2", shader=lin(0, y0, 0, y0 + 70, ["#f3f5fc", "#b9c0da"])))
    rrect(c, x1 - 190, y0 - 46, x1 - 46, y0 + 20, 30, P("#f6f6fb", shader=lin(0, y0 - 46, 0, y0 + 20, ["#ffffff", "#c9cde3"])))
    blanket = skia.Path()
    blanket.moveTo(x0 + 6, y0 + 10)
    blanket.lineTo(x1 - 210, y0 + 6)
    blanket.quadTo(x1 - 180, y0 + 50, x1 - 220, y0 + 110)
    blanket.lineTo(x0 - 10, y0 + 120)
    blanket.close()
    c.drawPath(blanket, P("#4d5fa8", shader=lin(x0, y0, x0, y0 + 120, ["#6378c4", "#3b4a8c"])))


def vignette(c, a=0.55):
    c.drawRect(R(0, 0, W, H), P("#000000", shader=rad(W / 2, H * 0.48, H * 0.75, [hexc("#000000", 0), hexc("#000000", 0), hexc("#000000", a)], [0, .55, 1])))


def grade(c, warm=0.0, cold=0.0, dark=0.0):
    if warm > 0:
        c.drawRect(R(0, 0, W, H), P("#ff9a3c", blend=skia.BlendMode.kSoftLight, alpha=0.55 * warm))
        c.drawRect(R(0, 0, W, H), P("#ffb35a", shader=rad(W / 2, H * .55, H * .7, [hexc("#ffb35a", .22 * warm), hexc("#ffb35a", 0)]),
                                    blend=skia.BlendMode.kScreen))
    if cold > 0:
        c.drawRect(R(0, 0, W, H), P("#3a5bd0", blend=skia.BlendMode.kSoftLight, alpha=0.5 * cold))
    if dark > 0:
        c.drawRect(R(0, 0, W, H), P("#0a0612", alpha=dark))


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


class Ctx:
    def __init__(self, vo, si, t):
        self.s = vo[si]
        self.lt = t - self.s["start"]
        self.D = self.s["end"] - self.s["start"]
        self.t = t

    def w(self, i):
        """inicio (local) de la palabra i de la escena"""
        tok = self.s["tokens"][min(i, len(self.s["tokens"]) - 1)]
        return tok["s"] - self.s["start"]


def camera(c, z, cx, cy, t):
    z *= 1 + 0.008 * math.sin(t * 0.9)
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-cx, -cy)


def scene1(c, k):  # escaparate de noche
    lt = k.lt
    sad = smooth(prog(lt, k.w(6) - 0.1, k.w(6) + 0.3))  # "pero"
    zo = ease_in_out(prog(lt, 0.6, 2.4))
    z = lerp(1.55, 1.0, zo) + 0.06 * smooth(prog(lt, 3.0, k.D))
    cx = lerp(700, 540, zo) + lerp(0, -90, smooth(prog(lt, 3.0, k.D)))
    cy = lerp(1000, 960, zo)
    camera(c, z, cx, cy, k.t)
    night_sky(c, -400, -400, W + 400, 1000, k.t)
    moon(c, 900, 520, 50)
    city(c, -400, W + 400, 760, "#211a38")
    c.drawRect(R(-400, 640, W + 400, 1430), P("#3a2b40", shader=lin(0, 640, 0, 1430, ["#45324a", "#2c2133"])))
    r = rng(3)
    for row in range(14):
        for col in range(14):
            bx = -400 + col * 140 + (70 if row % 2 else 0)
            by = 650 + row * 56
            rrect(c, bx, by, bx + 130, by + 48, 4, P("#ffffff", alpha=0.025 + 0.02 * r.random()))
    # toldo
    for i in range(9):
        xx = 380 + i * 70
        c.drawRect(R(xx, 650, xx + 70, 730), P("#b8323a" if i % 2 == 0 else "#f1e3c8"))
        oval(c, xx + 35, 730, 35, 22, P("#b8323a" if i % 2 == 0 else "#f1e3c8"))
    # vitrina
    rrect(c, 400, 760, 1020, 1320, 10, P("#4a2f22"))
    c.drawRect(R(422, 782, 998, 1298), P("#ffc982", shader=rad(710, 1080, 520, ["#ffe4ad", "#f0a55a", "#7a3d22"], [0, .5, 1])))
    for yy in (900, 1050):
        c.drawRect(R(430, yy, 990, yy + 10), P("#8a5636", alpha=0.6))
        for j in range(5):
            xx = 460 + j * 108
            if abs(xx - 690) > 100:
                rrect(c, xx, yy - 70, xx + 36, yy, 8, P("#ffffff", alpha=0.18))
    rrect(c, 595, 1182, 825, 1270, 8, P("#7a4a2e", shader=lin(0, 1182, 0, 1270, ["#9b6440", "#5a341f"])))
    draw_bottle(c, 710, 1186, 1.0, glow_a=0.6 + 0.3 * math.sin(k.t * 2))
    price_tag(c, 880, 1000, 8 * math.sin(k.t * 1.6), "Q1,500")
    aroma(c, 710, 860, k.t, n=40, height=520, spread=40, intensity=0.9, seed=2)
    glass = skia.Path()
    glass.moveTo(440, 1290)
    glass.lineTo(600, 790)
    glass.lineTo(680, 790)
    glass.lineTo(520, 1290)
    glass.close()
    c.drawPath(glass, P("#ffffff", alpha=0.08))
    c.drawRect(R(-400, 1420, W + 400, H + 400), P("#2a2230", shader=lin(0, 1420, 0, H, ["#3a2d3c", "#120d16"])))
    c.drawRect(R(-400, 1420, W + 400, 1440), P("#4a3a4c"))
    glow(c, RES.glow_warm, 710, 1500, 380, 0.25)
    expr = "sad" if sad > 0.5 else "dreamy"
    hand = (lerp(150, 110, sad), lerp(-470, -200, sad))
    draw_kid(c, 230, 1470, 1.06, k.t, expr, look=(1, lerp(-0.6, 0.3, sad)), tilt=lerp(6, -4, sad),
             hands={"R": hand, "L": (-112, -196)})
    # destello inicial (como la referencia)
    burst(c, 710, 1010, lt - 0.05, dur=1.3, n=50, radius=380, seed=21)


def bedroom_bg(c, t, cold=True):
    wall_and_floor(c, t, 1430, ("#232846", "#33335a") if cold else ("#3a2a4c", "#4a3354"))
    window(c, 110, 640, 520, 1040, t, moon_pos=(400, 740, 42))
    bed(c, 600, 1180, 1060, 1430)
    # mesita
    rrect(c, 150, 1250, 470, 1290, 8, P("#7d5638"))
    c.drawRect(R(170, 1290, 190, 1430), P("#5a3c27"))
    c.drawRect(R(430, 1290, 450, 1430), P("#5a3c27"))


def scene2(c, k):  # cuarto: duda
    lt = k.lt
    z = lerp(1.12, 1.0, ease_in_out(prog(lt, 0, 2.2)))
    cx = lerp(420, 540, ease_in_out(prog(lt, 0, 2.2)))
    camera(c, z, cx, 980, k.t)
    bedroom_bg(c, k.t)
    piggy(c, 290, 1250, 0.95)
    coin(c, 400, 1244, 18)
    coin(c, 432, 1240, 15)
    toss = prog(lt, 0.0, 0.6)
    hand_y = -330 + 40 * math.sin(toss * math.pi)
    hands = {"L": (-150, hand_y), "R": (90, -250)}

    def coin_in_hand(cc, out):
        hx, hy = out["L"]
        coin(cc, hx, hy - 30 - 30 * math.sin(toss * math.pi), 20)
    draw_kid(c, 640, 1480, 1.02, k.t, "worried", look=(-0.6, 0.2), tilt=-5 + 2 * math.sin(k.t),
             hands=hands, front_props=coin_in_hand)
    thought(c, 860, 690, prog(lt, k.w(3) - 0.2, k.w(3) + 0.3), k.t)
    dust(c, k.t, n=18, seed=4, alpha=0.25)


def scene3(c, k):  # descubrimiento del decant
    lt = k.lt
    z = lerp(1.0, 1.12, ease_in_out(prog(lt, 0.2, k.D)))
    camera(c, z, 600, 960, k.t)
    bedroom_bg(c, k.t)
    c.drawRect(R(-400, -400, W + 400, H + 400), P("#0c0716", alpha=0.62))
    glow(c, RES.glow_warm, 620, 940, 620, 0.35 + 0.1 * math.sin(k.t * 2))
    dust(c, k.t, n=30, seed=8, alpha=0.6)
    pop = back_out(prog(lt, 0.15, 0.85))
    bobv = math.sin(k.t * 2.2) * 14
    orbit_sparkles(c, 620, 960, k.t, 210, 80, intensity=pop)
    draw_decant(c, 620, 950 + bobv, 560 * pop, rot=6 * math.sin(k.t * 1.3), glow_a=1.0 * pop, shadow=False)
    burst(c, 620, 950, lt - 0.1, dur=1.4, n=70, radius=480, seed=33)
    draw_kid(c, 210, 1520, 0.9, k.t, "surprised", look=(1, -0.4), tilt=4,
             hands={"L": (-150, -470), "R": (150, -480)}, bob=-6 * abs(math.sin(lt * 3)) * (lt < 1.2))


def scene4(c, k):  # explicación: mismo perfume, fraccionado
    lt = k.lt
    z = lerp(1.0, 1.1, ease_in_out(prog(lt, 1.0, k.D)))
    cx = lerp(540, 620, ease_in_out(prog(lt, 1.0, k.D)))
    camera(c, z, cx, 980, k.t)
    c.drawRect(R(-400, -400, W + 400, H + 400), P("#1d1430", shader=rad(560, 900, 1100, ["#3a2758", "#1a1229", "#0d0916"], [0, .5, 1])))
    cone = skia.Path()
    cone.moveTo(470, -200)
    cone.lineTo(660, -200)
    cone.lineTo(980, 1420)
    cone.lineTo(260, 1420)
    cone.close()
    c.drawPath(cone, P("#ffffff", shader=lin(0, -200, 0, 1420, [hexc("#fff3d6", .10), hexc("#fff3d6", .02)])))
    c.drawRect(R(-400, 1400, W + 400, H + 400), P("#140e20", shader=lin(0, 1400, 0, H, ["#2a1f3c", "#0a0710"])))
    oval(c, 640, 1400, 330, 40, P("#ffffff", alpha=0.04))
    dust(c, k.t, n=26, seed=12, alpha=0.5)
    # frasco grande entra y se inclina para verter
    enter = ease_out(prog(lt, 0.0, 0.8))
    tilt = ease_in_out(prog(lt, 0.5, 1.4))
    bx, by = lerp(-150, 360, enter), 800
    rot = lerp(0, 118, tilt)
    c.save()
    c.translate(bx, by)
    c.rotate(rot)
    draw_bottle(c, 0, 160, 1.15, cap=False, glow_a=0.7)
    c.restore()
    a = math.radians(rot)
    d = 244 * 1.15 - 160
    tip = (bx + math.sin(a) * d, by - math.cos(a) * d)
    dec_x, dec_y, dec_h = 720, 1150, 470
    pour = prog(lt, 1.3, 1.6) * (1 - prog(lt, k.w(13) + 0.2, k.w(13) + 0.6))
    if pour > 0:
        top = dec_y - dec_h / 2 + 10
        stream = skia.Path()
        stream.moveTo(*tip)
        stream.cubicTo(tip[0] + 120, tip[1] + 10, dec_x - 10, top - 160, dec_x, top)
        c.drawPath(stream, P("#ffcf6a", "stroke", 26, alpha=0.25 * pour, blur=10))
        c.drawPath(stream, P("#ffd77a", "stroke", 9 * pour, shader=lin(tip[0], tip[1], dec_x, top, ["#fff0b8", "#e9a53a"])))
        meas = skia.PathMeasure(stream, False)
        L = meas.getLength()
        for i in range(14):
            u = (k.t * 0.9 + i / 14) % 1.0
            pos = meas.getPosTan(u * L)[0]
            if True:
                glow(c, RES.glow_white, pos.x(), pos.y(), 9, 0.8 * pour)
        glow(c, RES.glow_gold, dec_x, top, 90, 0.6 * pour)
    fill = smooth(prog(lt, 1.6, k.w(13) + 0.4))
    dec_in = back_out(prog(lt, 0.2, 0.9))
    draw_decant(c, dec_x, dec_y, dec_h * dec_in, rot=0, glow_a=0.6 + 0.4 * fill, fill=fill)
    orbit_sparkles(c, dec_x, dec_y, k.t, 150, 60, n=16, intensity=0.6 * fill)
    pill(c, 330, 1170, "100% original", prog(lt, k.w(6) - 0.15, k.w(6) + 0.35))
    pill(c, 330, 1290, "5 ml · 10 ml", prog(lt, k.w(13) - 0.15, k.w(13) + 0.35))


def scene5(c, k):  # lo prueba: aroma y luz cálida
    lt = k.lt
    warm = smooth(prog(lt, 1.2, 3.0))
    z = lerp(1.0, 1.06, ease_in_out(prog(lt, 0, k.D)))
    camera(c, z, 540, 1000, k.t)
    wall_and_floor(c, k.t, 1500, (mix_col("#232846", "#4a2f4c", warm), mix_col("#33335a", "#5a3a50", warm)))
    window(c, 640, 560, 1000, 940, k.t, moon_pos=(900, 650, 36))
    dust(c, k.t, n=22, seed=14, alpha=0.4, big=True, col=RES.glow_warm)
    spray = prog(lt, 0.9, 1.4)
    pressing = spray > 0 and spray < 1
    hands = {"R": (175, -470 - (8 if pressing else 0)), "L": (20, -290)}
    bliss = lt > 1.5

    def decant_in_hand(cc, out):
        hx, hy = out["R"]
        draw_decant(cc, hx + 4, hy - 60, 190, rot=-18, glow_a=0.5, shadow=False)
    hp = draw_kid(c, 540, 1960, 1.55, k.t, "bliss" if bliss else "happy", look=(-0.2, 0.3),
                  tilt=lerp(0, -6, warm) + 2 * math.sin(k.t * 1.2), hands=hands, front_props=decant_in_hand)
    if spray > 0:
        hx, hy = hp["R"]
        sx, sy = hx - 40, hy - 150 * 1.55
        burst(c, sx - 60, sy + 40, lt - 0.9, dur=1.0, n=40, radius=200, seed=55, intensity=0.6)
    lx, ly = hp["L"]
    aroma(c, lx - 40, ly - 60, k.t, n=60, height=900, spread=120, intensity=warm, seed=6, size=1.3)
    orbit_sparkles(c, 540, 1100, k.t, 380, 140, n=30, seed=9, intensity=warm * 0.8)
    k.grade = (warm * 0.6, (1 - warm) * 0.5)


def scene6(c, k):  # colección / fragancia difícil de encontrar
    lt = k.lt
    z = lerp(1.1, 1.0, ease_in_out(prog(lt, 0, 2.5)))
    camera(c, z, 540, 1000, k.t)
    c.drawRect(R(-400, -400, W + 400, H + 400), P("#3a2350", shader=rad(540, 950, 1000, ["#5a3768", "#2d1c40", "#140c1f"], [0, .55, 1])))
    dust(c, k.t, n=26, seed=16, alpha=0.45, big=True, col=RES.glow_warm)
    c.drawRect(R(-400, 1440, W + 400, H + 400), P("#1e1428", shader=lin(0, 1440, 0, H, ["#2b1d38", "#0e0915"])))
    cols = ["rose", "teal", "violet", "amber", "emerald", "gold"]
    n = len(cols)
    items = []
    angs = [175, 210, 238, 302, 330, 5]
    for i in range(n):
        ang = math.radians(angs[i] + 6 * math.sin(k.t * 0.8 + i))
        appear = back_out(prog(lt, 0.15 + i * 0.22, 0.65 + i * 0.22))
        x = 540 + math.cos(ang) * 400
        y = 1020 + math.sin(ang) * 330 + 14 * math.sin(k.t * 1.6 + i)
        items.append((-1 + 0.3 * (i % 2), x, y, appear, cols[i]))
    items.sort()
    special_k = prog(lt, k.w(4) - 0.2, k.w(4) + 0.3)

    def draw_items(front):
        for depth, x, y, ap, col in items:
            if (depth >= 0) != front or ap <= 0:
                continue
            h = (200 + 40 * depth) * ap
            draw_decant(c, x, y, h, rot=10 * math.sin(k.t + x), glow_a=0.9, glow_img=RES.glows[col], shadow=False)
    draw_items(False)
    draw_kid(c, 540, 1500, 1.0, k.t, "happy", look=(0.0, -0.3), tilt=3 * math.sin(k.t * 1.5),
             hands={"L": (-230, -430), "R": (230, -430)})
    draw_items(True)
    # la fragancia especial que no encontraba
    sk = back_out(special_k)
    if special_k > 0:
        sx, sy = 540, 640 + 10 * math.sin(k.t * 2)
        glow(c, RES.glow_warm, sx, sy, 330 * sk, 0.6)
        orbit_sparkles(c, sx, sy, k.t, 150, 60, n=22, seed=17, intensity=sk)
        draw_decant(c, sx, sy, 300 * sk, rot=5 * math.sin(k.t * 1.7), glow_a=1.2, shadow=False)
        pill(c, sx, sy + 210, "difícil de encontrar", prog(lt, k.w(5), k.w(5) + 0.4), size=38,
             col_text="#ffffff", bg="#7a3fd0", border="#f4cf6a")


def theatre(c, x, base, s, col):
    c.save()
    c.translate(x, base)
    c.scale(s, s)
    c.drawRect(R(-260, -40, 260, 0), P(col))
    c.drawRect(R(-240, -260, 240, -40), P(col))
    for i in range(6):
        cx = -200 + i * 80
        c.drawRect(R(cx - 14, -250, cx + 14, -50), P("#000000", alpha=0.25))
    tri = skia.Path()
    tri.moveTo(-260, -260)
    tri.lineTo(0, -360)
    tri.lineTo(260, -260)
    tri.close()
    c.drawPath(tri, P(col))
    c.drawRect(R(-120, -420, 120, -360), P(col))
    for i in range(6):
        cx = -200 + i * 80
        glow(c, RES.glow_warm, cx, -140, 30, 0.35)
    c.restore()


def scene7(c, k):  # Quetzaltenango
    lt = k.lt
    pan = ease_in_out(prog(lt, 0, 3.2))
    z = lerp(1.12, 1.0, pan)
    camera(c, z, lerp(700, 540, pan), 960, k.t)
    c.drawRect(R(-400, -400, W + 400, 1460), P("#2d2350", shader=lin(0, -400, 0, 1300, ["#1f1940", "#5a3a72", "#c8708a", "#f3a86a"], [0, .45, .75, 1])))
    for i in range(30):
        r = rng(i)
        oval(c, -400 + r.random() * 1900, -300 + r.random() * 700, 2, 2, P("#ffffff", alpha=0.5 + 0.4 * math.sin(k.t + i)))
    glow(c, RES.glow_warm, 300, 1150, 500, 0.35)
    # volcán Santa María
    v = skia.Path()
    v.moveTo(-200, 1300)
    v.lineTo(330, 610)
    v.quadTo(380, 580, 430, 615)
    v.lineTo(1000, 1300)
    v.close()
    c.drawPath(v, P("#6b4f86", shader=lin(0, 600, 0, 1300, ["#7d5f95", "#4c3866"])))
    snow = skia.Path()
    snow.moveTo(300, 650)
    snow.lineTo(330, 610)
    snow.quadTo(380, 580, 430, 615)
    snow.lineTo(460, 650)
    snow.quadTo(380, 630, 300, 650)
    c.drawPath(snow, P("#ffffff", alpha=0.18))
    city(c, -400, 1500, 1300, "#3c2b55", seed=21)
    theatre(c, 200, 1310, 0.9, "#4a3765")
    # tienda Otto Aleman Perfumes
    c.drawRect(R(470, 640, 1480, 1460), P("#e4b47a", shader=lin(470, 0, 1100, 0, ["#d9a066", "#b9804f"])))
    c.drawRect(R(470, 620, 1480, 660), P("#8a5a3a"))
    rrect(c, 520, 690, 1060, 920, 18, P("#16121b"))
    rrect(c, 520, 690, 1060, 920, 18, P("#d6a24a", "stroke", 6))
    sign_k = 0.8 + 0.2 * math.sin(k.t * 2)
    glow(c, RES.glow_gold, 790, 805, 360, 0.18 * sign_k)
    draw_img(c, RES.logo_gold, 640, 805, 170)
    f1 = font(RES.semi, 44)
    f2 = font(RES.medium, 30)
    c.drawString("OTTO ALEMAN", 738, 800, f1, P("#f6e2b0"))
    c.drawString("P E R F U M E S", 740, 848, f2, P("#d6a24a"))
    # puerta
    door = skia.Path()
    door.moveTo(600, 1440)
    door.lineTo(600, 1080)
    door.quadTo(700, 980, 800, 1080)
    door.lineTo(800, 1440)
    door.close()
    c.drawPath(door, P("#ffcf8a", shader=rad(700, 1250, 320, ["#fff0c8", "#f2a650", "#a8582a"], [0, .6, 1])))
    c.drawPath(door, P("#6e4128", "stroke", 14))
    rrect(c, 860, 1060, 1040, 1320, 10, P("#ffd79a", shader=rad(950, 1190, 200, ["#ffe8bd", "#d98b45"])))
    rrect(c, 860, 1060, 1040, 1320, 10, P("#6e4128", "stroke", 12))
    for j in range(3):
        xx = 892 + j * 52
        rrect(c, xx, 1250, xx + 26, 1300, 6, P("#3a2416", alpha=0.7))
    # farol
    c.drawRect(R(70, 900, 86, 1450), P("#231a2c"))
    rrect(c, 52, 860, 104, 920, 10, P("#231a2c"))
    glow(c, RES.glow_warm, 78, 890, 140, 0.8)
    glow(c, RES.glow_white, 78, 890, 30, 0.9)
    # suelo empedrado
    c.drawRect(R(-400, 1440, 1480, H + 400), P("#4a3a46", shader=lin(0, 1440, 0, H, ["#5a4652", "#1d1520"])))
    r = rng(77)
    for i in range(80):
        ex, ey = -400 + r.random() * 1880, 1460 + r.random() ** 1.5 * 460
        oval(c, ex, ey, 30 + 10 * r.random(), 10 + 4 * r.random(), P("#000000", alpha=0.12))
    glow(c, RES.glow_warm, 700, 1460, 360, 0.3)
    # el chico sale de la tienda
    walk = ease_in_out(prog(lt, 0.3, 3.4))
    kx = lerp(700, 330, walk)
    stepping = 0 < walk < 1
    sw = math.sin(lt * 9) * 20 * stepping
    hp = draw_kid(c, kx, 1480 - abs(math.sin(lt * 9)) * 8 * stepping, 0.92, k.t, "happy", look=(-0.7, 0),
                  tilt=-3, legs=(sw, -sw), hands={"L": (-130, -230 + sw), "R": (150, -330)})
    hx, hy = hp["R"]
    shopping_bag(c, hx, hy + 10, 0.9)
    if not stepping and lt > 3.4:
        burst(c, kx, 1000, lt - 3.4, dur=1.2, n=30, radius=260, seed=71, intensity=0.6)
    k.grade = (0.35, 0)


def scene8(c, k):  # cierre con logo
    lt = k.lt
    z = lerp(1.08, 1.0, ease_out(prog(lt, 0, 3.0)))
    camera(c, z, 540, 960, k.t)
    c.drawRect(R(-400, -400, W + 400, H + 400), P("#140c1d", shader=rad(540, 920, 1100, ["#3a2440", "#1a1022", "#08050b"], [0, .45, 1])))
    dust(c, k.t, n=28, seed=31, alpha=0.4, big=True, col=RES.glow_warm)
    dust(c, k.t, n=50, seed=32, alpha=0.7)
    aroma(c, 540, 1500, k.t, n=50, height=1300, spread=260, intensity=0.6, seed=41, speed=0.18)
    lg = back_out(prog(lt, 0.15, 1.0), 1.3)
    glow(c, RES.glow_warm, 540, 880, 520, 0.55 * lg)
    if lg > 0:
        draw_img(c, RES.logo_gold, 540, 880, 470 * lg)
        # brillo que cruza el logo
        sweep = prog(lt, 1.1, 2.2)
        if 0 < sweep < 1:
            c.saveLayer(None, None)
            draw_img(c, RES.logo_white, 540, 880, 470 * lg)
            bx = lerp(200, 880, sweep)
            c.drawRect(R(0, 0, W, H), P("#ffffff", blend=skia.BlendMode.kSrcIn,
                                         shader=lin(bx - 90, 0, bx + 90, 60, [hexc("#ffffff", 0), hexc("#ffffff", .85), hexc("#ffffff", 0)])))
            c.restore()
    burst(c, 540, 880, lt - 0.2, dur=1.4, n=70, radius=520, seed=81, intensity=0.9)
    ta = ease_out(prog(lt, 0.8, 1.5))
    f1 = font(RES.semi, 68)
    f2 = font(RES.medium, 38)
    c.save()
    c.translate(0, 30 * (1 - ta))
    text_center(c, "Otto Aleman Perfumes", 540, 1240, f1, P("#fff4dc", alpha=ta))
    text_center(c, "Quetzaltenango, Guatemala", 540, 1305, f2, P("#e2b45e", alpha=ta))
    c.drawLine(380, 1340, 700, 1340, P("#e2b45e", "stroke", 2, alpha=0.6 * ta))
    c.restore()
    da = back_out(prog(lt, 1.2, 1.9))
    for side in (-1, 1):
        draw_decant(c, 540 + side * 395, 900 + 12 * math.sin(k.t * 2 + side), 360 * da, rot=side * 10,
                    glow_a=0.7, shadow=False)
    ca = ease_out(prog(lt, k.w(7) - 0.2, k.w(7) + 0.3))  # "Escribinos"
    pill(c, 540, 1440, "Escribinos por DM", ca, size=40, col_text="#1d1206", bg="#f4cf6a", border="#fff2c8")


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8]
SCENE_GRADE = {0: (0, .25), 1: (0, .55), 2: (0, .2), 3: (.1, 0), 5: (.25, 0), 7: (.2, 0)}

# ----------------------------------------------------------------------------
# subtítulos y marca de agua (en pantalla, fuera de la cámara)
# ----------------------------------------------------------------------------
SUB_SIZE = 62
SUB_Y = 380
SUB_LINE = 80
SUB_MAXW = 920
BLUE = "#2f6bff"
SUB_BOX, SUB_BOX_BORDER, SUB_TEXT_ACTIVE = BLUE, "#8fb2ff", "#ffffff"
SUB_PLATE = False


def layout_phrase(p):
    f = font(RES.bold, SUB_SIZE)
    sp = f.measureText(" ")
    ws = [(w, f.measureText(w["w"])) for w in p["words"]]
    lines, cur, cw = [], [], 0
    for w, wd in ws:
        add = wd if not cur else cw + sp + wd
        if cur and add > SUB_MAXW:
            lines.append((cur, cw))
            cur, cw = [(w, wd)], wd
        else:
            cur.append((w, wd))
            cw = add
    if cur:
        lines.append((cur, cw))
    out = []
    for li, (ln, lw) in enumerate(lines):
        x = W / 2 - lw / 2
        for w, wd in ln:
            out.append((w, x, SUB_Y + li * SUB_LINE, wd))
            x += wd + sp
    return out


def draw_subs(c, t, phr):
    f = font(RES.bold, SUB_SIZE)
    for p in phr:
        if not (p["s"] <= t < p["e"]):
            continue
        fade = clamp((p["e"] - t) / 0.12)
        lay = p.setdefault("_lay", layout_phrase(p))
        shown = [i for i, (w, _, _, _) in enumerate(lay) if t >= w["s"] - 0.04]
        cur = shown[-1] if shown else -1
        if SUB_PLATE and cur >= 0:  # placa oscura que crece con las palabras dichas
            vis = lay[:cur + 1]
            for ly in sorted(set(y for _, _, y, _ in vis)):
                row = [(x, wd) for _, x, y, wd in vis if y == ly]
                x0 = min(x for x, _ in row) - 24
                x1 = max(x + wd for x, wd in row) + 24
                rrect(c, x0, ly - SUB_SIZE * 0.98, x1, ly + SUB_SIZE * 0.42, 22, P("#0c0818", alpha=0.55 * fade))
        last = lay[-1][0]
        for i, (w, x, y, wd) in enumerate(lay):
            if i > cur:
                continue
            active = i == cur and not (i == len(lay) - 1 and t > last["e"] + 0.25)
            if active:
                k = ease_out((t - w["s"] + 0.04) / 0.12)
                s = 0.88 + 0.12 * k
                c.save()
                c.translate(x + wd / 2, y - SUB_SIZE * 0.33)
                c.scale(s, s)
                pad_x, pad_y = 14, 10
                bx0, by0 = -wd / 2 - pad_x, -SUB_SIZE * 0.5 - pad_y
                bx1, by1 = wd / 2 + pad_x, SUB_SIZE * 0.5 + pad_y - 2
                glow(c, RES.soft_dark, 0, 6, wd * 0.75 + 40, 0.35 * fade, skia.BlendMode.kSrcOver)
                rrect(c, bx0, by0, bx1, by1, 14, P(SUB_BOX, alpha=0.95 * fade))
                rrect(c, bx0, by0, bx1, by1, 14, P(SUB_BOX_BORDER, "stroke", 3, alpha=0.9 * fade))
                c.drawString(w["w"], -wd / 2, SUB_SIZE * 0.33 + 1, f, P(SUB_TEXT_ACTIVE, alpha=fade))
                c.restore()
            else:
                c.drawString(w["w"], x + 2, y + 3, f, P("#000000", alpha=0.45 * fade, blur=5))
                c.drawString(w["w"], x, y, f, P("#e4e1ea", alpha=0.78 * fade))


def draw_watermark(c):
    f = font(RES.bold, 34)
    txt = "@ottoaleman.perfumesgt"
    w = f.measureText(txt)
    x0, x1 = W / 2 - w / 2 - 34, W / 2 + w / 2 + 34
    y0, y1 = 1528, 1594
    rrect(c, x0, y0, x1, y1, 33, P("#140c08", alpha=0.55))
    rrect(c, x0, y0, x1, y1, 33, P("#c9a05a", "stroke", 2.5, alpha=0.75))
    c.drawString(txt, W / 2 - w / 2, 1573, f, P("#efe8dc"))


# ----------------------------------------------------------------------------
# cuadro completo
# ----------------------------------------------------------------------------
TRANS = 0.45
FADE_IN = 0.35


def render_scene(c, vo, si, t):
    k = Ctx(vo, si, t)
    k.grade = SCENE_GRADE.get(si, (0, 0))
    c.save()
    SCENES[si](c, k)
    c.restore()
    warm, cold = k.grade
    grade(c, warm=warm, cold=cold)


def render_frame(c, t, vo, phr, total):
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(hexc("#000000"))
    lt = t - vo[si]["start"]
    if si > 0 and lt < TRANS:
        render_scene(c, vo, si - 1, t)
        c.saveLayerAlpha(None, int(255 * smooth(lt / TRANS)))
        render_scene(c, vo, si, t)
        c.restore()
        # destello dorado en la transición
        k = lt / TRANS
        glow(c, RES.glow_warm, W / 2, H * 0.5, 900, 0.22 * math.sin(math.pi * k))
    else:
        render_scene(c, vo, si, t)
    vignette(c)
    fade_in = clamp(t / FADE_IN) if FADE_IN > 0 else 1.0
    fade_out = clamp((total - t) / 0.5)
    if fade_in < 1 or fade_out < 1:
        c.drawRect(R(0, 0, W, H), P("#000000", alpha=1 - min(fade_in, fade_out)))
    draw_subs(c, t, phr)
    draw_watermark(c)


def worker(args):
    f0, f1, out, total = args
    global RES
    RES = Res()
    vo, _ = timeline.load()
    phr = timeline.phrases(vo)
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                           "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        render_frame(c, fi / FPS, vo, phr, total)
        ff.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    ff.stdin.close()
    ff.wait()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--out", default=os.path.join(timeline.BUILD, "video_mudo.mp4"))
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--still", type=float, nargs="*", help="exporta PNG de estos segundos")
    a = ap.parse_args()
    vo, total = timeline.load()
    if a.still:
        global RES
        RES = Res()
        phr = timeline.phrases(vo)
        surf = skia.Surface(W, H)
        for t in a.still:
            render_frame(surf.getCanvas(), t, vo, phr, total)
            p = os.path.join(timeline.BUILD, f"still_{t:05.2f}.png")
            surf.makeImageSnapshot().save(p, skia.kPNG)
            print(p)
        return
    end = total if a.end is None else min(a.end, total)
    f0, f1 = int(round(a.start * FPS)), int(round(end * FPS))
    n = max(1, a.jobs)
    step = math.ceil((f1 - f0) / n)
    parts = [(s, min(s + step, f1), os.path.join(timeline.BUILD, f"part_{i:02d}.mp4"), total)
             for i, s in enumerate(range(f0, f1, step))]
    with Pool(len(parts)) as pool:
        outs = pool.map(worker, parts)
    lst = os.path.join(timeline.BUILD, "parts.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{os.path.abspath(o)}'\n" for o in outs)
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", a.out])
    for o in outs:
        os.remove(o)
    print(a.out, f"{(f1 - f0) / FPS:.2f}s")


if __name__ == "__main__":
    main()
