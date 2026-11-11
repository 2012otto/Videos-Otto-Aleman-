"""Video Velto — "El caos de Ana". Reutiliza el motor 2D de src/render.py con la marca Velto.

Uso (desde la raíz del repo):
  VIDEO_BUILD=velto/build VO_TRIM=0.3 python3 velto/src/render_velto.py --start 0 --end 8 --out velto/build/prueba.mp4
  VIDEO_BUILD=velto/build VO_TRIM=0.3 python3 velto/src/render_velto.py --out velto/build/video_mudo.mp4
"""
import math
import os
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "src"))
import render as R  # noqa: E402
from render import (P, R as RECT, back_out, clamp, ease_in_out, ease_out, font, glow, hexc, lerp, lin,  # noqa: E402,F401
                    oval, prog, rad, rrect, smooth, text_center, draw_img, draw_kid, rng, W, H)

VA = os.path.join(REPO, "velto", "assets")
VIO, VIO2, VIO_D, LIME, LIME2 = "#8a2be2", "#a64dff", "#4b1590", "#b8f51a", "#d4ff4a"

ANA = {"shirt": ("#c084ff", "#8a2be2", "#5d18a8"), "hem": "#5a1aa0", "collar": "#5a1aa0", "arm": "#8a3ae6",
       "arm_hl": "#d0a6ff", "pants": ("#2f2856", "#1a1533"), "hair": "long", "hair_col": ("#4a2c1c", "#22140c"),
       "lashes": True, "earrings": "#f4cf6a", "lips": "#b23a55"}
CLIENTE = {"shirt": ("#e2ff7a", "#b8f51a", "#7fb80a"), "hem": "#6f9f08", "collar": "#6f9f08", "arm": "#a8e01a",
           "arm_hl": "#f0ffb0", "pants": ("#34306a", "#201c48")}


class VeltoRes(R.Res):
    def __init__(self):
        super().__init__()
        f = os.path.join(VA, "fonts")
        self.mx = skia.Typeface.MakeFromFile(os.path.join(f, "Montserrat_800ExtraBold.ttf"))
        self.mxi = skia.Typeface.MakeFromFile(os.path.join(f, "Montserrat_800ExtraBold_Italic.ttf"))
        self.mb = skia.Typeface.MakeFromFile(os.path.join(f, "Montserrat_700Bold.ttf"))
        self.ms = skia.Typeface.MakeFromFile(os.path.join(f, "Montserrat_600SemiBold.ttf"))
        self.bold = self.mx  # subtítulos en Montserrat, como la publicidad
        import numpy as np
        from PIL import Image
        arr = np.asarray(Image.open(os.path.join(VA, "v_logo.png")).convert("RGBA")).copy()
        self.vlogo = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType,
                                          alphaType=skia.kUnpremul_AlphaType).withDefaultMipmaps()
        arr2 = np.asarray(Image.open(os.path.join(VA, "logo_cliente.png")).convert("RGBA")).copy()
        self.logo_cliente = skia.Image.fromarray(arr2, colorType=skia.kRGBA_8888_ColorType,
                                                 alphaType=skia.kUnpremul_AlphaType).withDefaultMipmaps()
        self.g_vio = R.sprite(170, 80, 255, power=1.8)
        self.g_lime = R.sprite(190, 255, 40, power=1.8)
        self.g_mag = R.sprite(220, 90, 255, power=1.4)
        self.glow_gold = self.g_vio
        self.glow_warm = self.g_mag


def RES():
    return R.RES


def use(colors="vio"):
    """Elige el color de las partículas de los helpers del motor."""
    r = R.RES
    if colors == "lime":
        r.glow_gold, r.glow_warm = r.g_lime, r.g_lime
    else:
        r.glow_gold, r.glow_warm = r.g_vio, r.g_mag


def F(tf, size):
    return font(tf, size)


# ----------------------------------------------------------------------------
# fondos y elementos de marca
# ----------------------------------------------------------------------------


def neon_bg(c, t, top="#14072b", bottom="#05020b", grid=0.10, waves=True, wy=1500):
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P(top, shader=lin(0, -200, 0, H, [top, "#0c0420", bottom], [0, .55, 1])))
    glow(c, R.RES.g_vio, 540, 300, 900, 0.18, skia.BlendMode.kScreen)
    g = P("#9b5cff", "stroke", 2, alpha=grid)
    for i in range(-4, 16):
        x = i * 120
        c.drawLine(x, -500, x, H + 500, g)
    for j in range(-4, 22):
        y = j * 120
        c.drawLine(-500, y, W + 500, y, g)
    if waves:
        wave(c, t, wy)


def wave(c, t, y0=1500, a=1.0):
    for k, (amp, off, wdt) in enumerate(((60, 0, 6), (40, 1.7, 3), (80, 3.1, 2))):
        pth = skia.Path()
        pth.moveTo(-200, y0 + 80)
        for i in range(0, 15):
            x = -200 + i * 110
            y = y0 + 40 * k + amp * math.sin(x / 260 + t * 0.9 + off)
            pth.lineTo(x, y)
        sh = lin(-200, 0, W + 200, 0, [VIO, "#c84dff", LIME])
        c.drawPath(pth, P(VIO, "stroke", wdt * 5, shader=sh, blur=12, alpha=0.45 * a))
        c.drawPath(pth, P(VIO, "stroke", wdt, shader=sh, alpha=0.95 * a))


def v_logo(c, x, y, h, a=1.0, glow_a=1.0, rot=0.0):
    if glow_a > 0:
        glow(c, R.RES.g_vio, x - h * 0.2, y, h * 1.2, 0.55 * glow_a * a)
        glow(c, R.RES.g_lime, x + h * 0.35, y - h * 0.1, h * 0.8, 0.35 * glow_a * a)
    draw_img(c, R.RES.vlogo, x, y, h, rot, a)


def wordmark(c, x, y, size, a=1.0, slogan=True):
    f = F(R.RES.mx, size)
    w = f.measureText("VELTO")
    c.drawString("VELTO", x - w / 2, y, f, P("#ffffff", alpha=a))
    fr = F(R.RES.mb, size * 0.22)
    c.drawString("®", x + w / 2 + 6, y - size * 0.62, fr, P("#ffffff", alpha=a))
    if slogan:
        fs = F(R.RES.ms, size * 0.32)
        parts = [("Tu negocio, ", "#ffffff"), ("en", "#b46bff"), (" versión digital.", "#ffffff")]
        tw = sum(fs.measureText(p) for p, _ in parts)
        xx = x - tw / 2
        yy = y + size * 0.55
        for txt, col in parts:
            c.drawString(txt, xx, yy, fs, P(col, alpha=a))
            xx += fs.measureText(txt)
        sw = skia.Path()
        sw.moveTo(x - tw * 0.32, yy + size * 0.32)
        sw.quadTo(x, yy + size * 0.12, x + tw * 0.42, yy + size * 0.2)
        c.drawPath(sw, P(VIO, "stroke", size * 0.07, shader=lin(x - tw * .3, 0, x + tw * .4, 0, [VIO, LIME]), alpha=a))


def sparkle(c, x, y, r, a=1.0):
    """Destello de 4 puntas."""
    if a <= 0.01:
        return
    st = skia.Path()
    for i in range(8):
        ang = -math.pi / 2 + i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.18
        (st.moveTo if i == 0 else st.lineTo)(x + math.cos(ang) * rr, y + math.sin(ang) * rr)
    st.close()
    glow(c, R.RES.glow_white, x, y, r * 1.3, 0.6 * a)
    c.drawPath(st, P("#ffffff", alpha=a))


def full_logo(c, x, y, s, t=0.0, v_a=1.0, txt_a=1.0, txt_dx=0.0, glow_a=1.0, v_pos=None):
    """Logo Velto completo (V + VELTO® + eslogan + onda), rehecho en vectores. Ancho ~2050*s, centro (x, y)."""
    vx, vy, vh = (x - 640 * s, y - 5 * s, 500 * s) if v_pos is None else v_pos
    if v_a > 0:
        v_logo(c, vx, vy, vh, a=v_a, glow_a=glow_a)
        tw1 = 0.5 + 0.5 * math.sin(t * 3.1)
        tw2 = 0.5 + 0.5 * math.sin(t * 2.3 + 2)
        sparkle(c, vx - vh * 0.52, vy - vh * 0.44, vh * 0.13 * (0.6 + 0.4 * tw1), v_a * tw1)
        sparkle(c, vx + vh * 0.55, vy - vh * 0.46, vh * 0.10 * (0.6 + 0.4 * tw2), v_a * tw2)
    if txt_a <= 0:
        return
    c.save()
    c.translate(x + txt_dx, y)
    c.scale(s, s)
    f = F(R.RES.mx, 320)
    tw = f.measureText("VELTO")
    c.save()
    c.translate(-300, 95)
    c.scale(1180 / tw, 1.0)
    c.drawString("VELTO", 0, 0, f, P("#ffffff", alpha=txt_a))
    c.restore()
    fr = F(R.RES.mb, 70)
    oval(c, 925, -150, 34, 34, P("#ffffff", "stroke", 6, alpha=txt_a))
    text_center(c, "R", 925, -128, fr if False else F(R.RES.mb, 46), P("#ffffff", alpha=txt_a))
    fs = F(R.RES.ms, 96)
    parts = [("Tu negocio, ", "#ffffff"), ("en", "#b46bff"), (" versión digital.", "#ffffff")]
    total = sum(fs.measureText(p) for p, _ in parts)
    c.save()
    c.translate(-330, 225)
    c.scale(1240 / total, 1.0)
    xx = 0
    for txt, col in parts:
        c.drawString(txt, xx, 0, fs, P(col, alpha=txt_a))
        xx += fs.measureText(txt)
    c.restore()
    sw = skia.Path()
    sw.moveTo(-20, 300)
    sw.cubicTo(180, 250, 420, 238, 640, 262)
    sw.cubicTo(420, 278, 180, 285, -20, 300)
    sw.close()
    c.drawPath(sw, P(VIO, shader=lin(-20, 0, 640, 0, [VIO, "#c84dff", LIME]), alpha=txt_a))
    c.drawPath(sw, P(VIO, "stroke", 9, shader=lin(-20, 0, 640, 0, [VIO, "#c84dff", LIME]), alpha=txt_a))
    c.restore()


def client_logo(c, x, y, width, a=1.0):
    """Logo original del cliente, tal cual (sin efectos)."""
    img = R.RES.logo_cliente
    h = width * img.height() / img.width()
    draw_img(c, img, x, y, h, 0.0, a)


def glass_card(c, x, y, w, h, k=1.0, r=36):
    if k <= 0:
        return
    s = back_out(k)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glow(c, R.RES.g_vio, 0, 0, max(w, h) * 0.8, 0.35)
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, r, P("#2a1050", shader=lin(0, -h / 2, 0, h / 2, ["#4a1c8a", "#1c0a38"]), alpha=0.92))
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, r, P("#c48bff", "stroke", 3, alpha=0.8))
    c.restore()


def pill(c, x, y, text, k, size=40, bg=LIME, fg="#14061f", tf=None, border=None, arrow=False):
    if k <= 0:
        return
    s = back_out(k)
    f = F(tf or R.RES.mx, size)
    tw = f.measureText(text) + (size * 1.6 if arrow else 0)
    w, h = tw + size * 1.3, size * 1.9
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glow(c, R.RES.g_lime if bg == LIME else R.RES.g_vio, 0, 0, w * 0.7, 0.45)
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, h / 2, P(bg))
    if border:
        rrect(c, -w / 2, -h / 2, w / 2, h / 2, h / 2, P(border, "stroke", 3))
    c.drawString(text, -tw / 2, size * 0.36, f, P(fg))
    if arrow:
        ax = tw / 2 - size * 0.55
        ar = skia.Path()
        ar.moveTo(ax - size * 0.5, 0)
        ar.lineTo(ax + size * 0.35, 0)
        ar.moveTo(ax, -size * 0.35)
        ar.lineTo(ax + size * 0.38, 0)
        ar.lineTo(ax, size * 0.35)
        c.drawPath(ar, P(fg, "stroke", size * 0.13))
    c.restore()


# ----------------------------------------------------------------------------
# joyería e íconos
# ----------------------------------------------------------------------------
GOLD = ["#8a5a17", "#f7d27a", "#fff1c4", "#d9a441"]


def necklace(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for i in range(15):
        u = i / 14
        px = lerp(-60, 60, u)
        py = -42 + 70 * (1 - (2 * u - 1) ** 2)
        oval(c, px, py, 4.5, 4.5, P("#f4cf6a"))
    gem = skia.Path()
    gem.moveTo(0, 26)
    gem.lineTo(16, 44)
    gem.lineTo(0, 70)
    gem.lineTo(-16, 44)
    gem.close()
    c.drawPath(gem, P(VIO2, shader=lin(-16, 26, 16, 70, ["#e2c2ff", VIO2, "#5d18a8"])))
    oval(c, -4, 40, 3, 5, P("#ffffff", alpha=0.8))
    c.restore()


def ring(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, 14, 36, 32, P("#f4cf6a", "stroke", 10, shader=lin(-36, 0, 36, 0, GOLD)))
    gem = skia.Path()
    gem.moveTo(-18, -18)
    gem.lineTo(18, -18)
    gem.lineTo(26, -8)
    gem.lineTo(0, 16)
    gem.lineTo(-26, -8)
    gem.close()
    c.drawPath(gem, P(LIME, shader=lin(-26, -18, 26, 16, ["#f0ffb0", LIME, "#5f9a00"])))
    c.drawLine(-26, -8, 26, -8, P("#ffffff", "stroke", 2, alpha=0.6))
    c.restore()


def earrings(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for side in (-1, 1):
        oval(c, side * 26, -30, 5, 5, P("#f4cf6a"))
        c.drawLine(side * 26, -26, side * 26, -6, P("#f4cf6a", "stroke", 3))
        drop = skia.Path()
        drop.moveTo(side * 26, -8)
        drop.quadTo(side * 26 + 18, 18, side * 26, 32)
        drop.quadTo(side * 26 - 18, 18, side * 26, -8)
        c.drawPath(drop, P("#ff6fb1", shader=lin(0, -8, 0, 32, ["#ffc2de", "#e0368a"])))
    c.restore()


def bracelet(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, 0, 46, 22, P("#f4cf6a", "stroke", 6))
    for i in range(10):
        a = i / 10 * 6.283
        oval(c, math.cos(a) * 46, math.sin(a) * 22, 7, 7, P(VIO2 if i % 2 else LIME))
    star = skia.Path()
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 16 if i % 2 == 0 else 7
        (star.moveTo if i == 0 else star.lineTo)(math.cos(a) * r, 34 + math.sin(a) * r)
    star.close()
    c.drawPath(star, P("#f4cf6a"))
    c.restore()


PRODUCTS = [("Collar Luna", "Q175", necklace), ("Anillo Sol", "Q120", ring),
            ("Aretes Gota", "Q95", earrings), ("Pulsera Estrella", "Q140", bracelet)]


def sneaker(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    sh = skia.Path()
    sh.moveTo(-70, 20)
    sh.lineTo(-66, -26)
    sh.quadTo(-40, -30, -20, -10)
    sh.quadTo(10, -20, 40, 0)
    sh.quadTo(72, 6, 72, 22)
    sh.close()
    c.drawPath(sh, P("#efe8ff"))
    rrect(c, -72, 18, 74, 32, 7, P("#b9a6e0"))
    for i in range(3):
        c.drawLine(-36 + i * 12, -18 + i * 3, -26 + i * 12, -4 + i * 3, P(VIO, "stroke", 3))
    c.restore()


def headphones(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    arc = skia.Path()
    arc.addArc(RECT(-52, -60, 52, 50), 180, 180)
    c.drawPath(arc, P("#d9c4ff", "stroke", 12))
    for side in (-1, 1):
        rrect(c, side * 52 - 18, -6, side * 52 + 18, 46, 14, P(VIO2, shader=lin(0, -6, 0, 46, ["#c99bff", "#6a22c0"])))
    c.restore()


def cupcake(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    cup = skia.Path()
    cup.moveTo(-40, 0)
    cup.lineTo(40, 0)
    cup.lineTo(30, 46)
    cup.lineTo(-30, 46)
    cup.close()
    c.drawPath(cup, P(LIME, shader=lin(-40, 0, 40, 0, ["#d4ff4a", "#7fb80a"])))
    for (bx, by, r) in ((-24, -8, 22), (0, -22, 26), (24, -8, 22)):
        oval(c, bx, by, r, r * 0.85, P("#ffd1ec"))
    oval(c, 0, -46, 9, 9, P("#e0368a"))
    c.restore()


def perfume(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -34, -20, 34, 50, 10, P(VIO2, shader=lin(-34, 0, 34, 0, ["#5d18a8", "#c084ff", "#5d18a8"]), alpha=0.95))
    rrect(c, -26, -10, -18, 40, 4, P("#ffffff", alpha=0.35))
    rrect(c, -14, -44, 14, -20, 5, P("#f4cf6a", shader=lin(-14, 0, 14, 0, GOLD)))
    c.restore()


# ----------------------------------------------------------------------------
# teléfono y chat
# ----------------------------------------------------------------------------


def phone(c, cx, cy, w, h, screen, rot=0.0, shake=0.0, glow_a=0.6):
    c.save()
    c.translate(cx + shake, cy)
    c.rotate(rot)
    if glow_a > 0:
        glow(c, R.RES.g_vio, 0, 0, max(w, h) * 0.75, 0.35 * glow_a)
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, w * 0.13, P("#121018", shader=lin(-w / 2, 0, w / 2, 0, ["#3a3446", "#121018", "#2a2534"])))
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, w * 0.13, P("#b98aff", "stroke", 3, alpha=0.6))
    m = w * 0.04
    x0, y0, x1, y1 = -w / 2 + m, -h / 2 + m, w / 2 - m, h / 2 - m
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(RECT(x0, y0, x1, y1), w * 0.1, w * 0.1), True)
    c.drawRect(RECT(x0, y0, x1, y1), P("#0e0a1a", shader=lin(0, y0, 0, y1, ["#1a0f30", "#0b0716"])))
    screen(c, x0, y0, x1, y1)
    c.restore()
    rrect(c, -w * 0.14, y0 + 8, w * 0.14, y0 + 8 + w * 0.06, w * 0.03, P("#000000"))
    c.restore()


def bubble(c, x, y, text, out, size, maxw, k=1.0, col=None, txtcol="#ffffff", tf=None):
    """Burbuja de chat. out=True a la derecha (enviado). (x, y) = esquina sup. del borde correspondiente."""
    if k <= 0:
        return 0
    f = F(tf or R.RES.ms, size)
    tw = min(f.measureText(text), maxw)
    w, h = tw + size * 1.2, size * 1.9
    s = back_out(k)
    c.save()
    bx = x - w if out else x
    c.translate(bx + (w if out else 0), y)
    c.scale(s, s)
    c.translate(-(w if out else 0), 0)
    rrect(c, 0, 0, w, h, size * 0.7, P(col or (VIO if out else "#2c2540")))
    tail = skia.Path()
    if out:
        tail.moveTo(w - 18, h - 16)
        tail.lineTo(w + 8, h + 2)
        tail.lineTo(w - 30, h - 4)
    else:
        tail.moveTo(18, h - 16)
        tail.lineTo(-8, h + 2)
        tail.lineTo(30, h - 4)
    c.drawPath(tail, P(col or (VIO if out else "#2c2540")))
    c.drawString(text, size * 0.6, h * 0.5 + size * 0.36, f, P(txtcol))
    c.restore()
    return h


def chat_icon(c, x, y, r, col=LIME):
    oval(c, x, y, r, r, P(col))
    t = skia.Path()
    t.moveTo(x - r * 0.55, y + r * 0.55)
    t.lineTo(x - r * 0.95, y + r * 1.0)
    t.lineTo(x - r * 0.1, y + r * 0.85)
    c.drawPath(t, P(col))
    for i in (-1, 0, 1):
        oval(c, x + i * r * 0.36, y, r * 0.12, r * 0.12, P("#14061f"))


def badge(c, x, y, text, k=1.0):
    if k <= 0:
        return
    f = F(R.RES.mx, 30)
    w = max(52, f.measureText(text) + 26)
    s = back_out(k)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -w / 2, -26, w / 2, 26, 26, P("#ff3b5c"))
    text_center(c, text, 0, 11, f, P("#ffffff"))
    c.restore()


def catalog_screen(k, t, step):
    """Pantalla del catálogo de Ana. step: dict con progresos 0..1 (logo, prods[4], precios, desc, boton)."""
    def draw(c, x0, y0, x1, y1):
        w = x1 - x0
        cx = (x0 + x1) / 2
        sc = w / 520.0
        c.save()
        c.translate(x0, y0)
        c.scale(sc, sc)
        # cabecera
        c.drawRect(RECT(0, 0, 520, 230), P(VIO, shader=lin(0, 0, 520, 230, ["#6a1fc0", "#3a0f7a"])))
        lg = step.get("logo", 1)
        if lg > 0:
            s = back_out(lg)
            c.save()
            c.translate(90, 150)
            c.scale(s, s)
            oval(c, 0, 0, 56, 56, P("#fff6e0"))
            oval(c, 0, 0, 56, 56, P(LIME, "stroke", 5))
            ring(c, 0, -2, 0.75)
            c.restore()
            name = "Ana Joyas"
            n = int(len(name) * clamp(lg * 1.5))
            c.drawString(name[:n], 165, 150, F(R.RES.mx, 44), P("#ffffff"))
            c.drawString("Joyería artesanal", 167, 190, F(R.RES.ms, 24), P("#e6d4ff", alpha=clamp(lg * 2 - 1)))
        # enlace
        lk = step.get("link", 0)
        if lk > 0:
            rrect(c, 300, 30, 500, 76, 23, P(LIME, alpha=lk))
            c.drawString("tu enlace", 340, 61, F(R.RES.mb, 22), P("#14061f", alpha=lk))
            ch = skia.Path()
            ch.addOval(RECT(312, 44, 330, 62))
            c.drawPath(ch, P("#14061f", "stroke", 3, alpha=lk))
        # descripción
        d = step.get("desc", 1)
        desc = "Joyería hecha a mano con amor. Envíos a todo el país."
        n = int(len(desc) * clamp(d))
        fdes = F(R.RES.ms, 24)
        c.drawString(desc[:min(n, 30)], 28, 280, fdes, P("#d9cdf0"))
        if n > 30:
            c.drawString(desc[30:n], 28, 314, fdes, P("#d9cdf0"))
        # productos 2x2
        prods = step.get("prods", [1, 1, 1, 1])
        pr = step.get("precios", 1)
        for i, (nm, price, icon) in enumerate(PRODUCTS):
            kk = prods[i]
            if kk <= 0:
                continue
            col, row = i % 2, i // 2
            px, py = 28 + col * 240, 350 + row * 300
            s = back_out(kk)
            c.save()
            c.translate(px + 110, py + 135)
            c.scale(s, s)
            rrect(c, -110, -135, 110, 135, 26, P("#24183c"))
            rrect(c, -110, -135, 110, 135, 26, P("#7a4bc4", "stroke", 2, alpha=0.7))
            rrect(c, -96, -122, 96, 20, 20, P("#fdf6ff"))
            icon(c, 0, -52, 1.15)
            c.drawString(nm, -96, 60, F(R.RES.mb, 23), P("#ffffff"))
            if pr > 0:
                c.drawString(price, -96 + 30 * (1 - ease_out(pr)), 100, F(R.RES.mx, 30), P(LIME, alpha=pr))
            c.restore()
        # botón
        b = step.get("boton", 0)
        if b > 0:
            press = step.get("press", 0)
            s = 1 - 0.08 * math.sin(math.pi * clamp(press))
            c.save()
            c.translate(260, 990)
            c.scale(s, s)
            glow(c, R.RES.g_lime, 0, 0, 260, 0.35 * b)
            rrect(c, -230, -44, 230, 44, 44, P(LIME, alpha=b))
            text_center(c, "Pedir por mensaje", 22, 12, F(R.RES.mx, 32), P("#14061f", alpha=b))
            chat_icon(c, -170, -4, 18, "#14061f")
            c.restore()
            if 0 < press < 1:
                glow(c, R.RES.glow_white, 300, 990, 140 * ease_out(press), 0.8 * (1 - press))
        # pie
        c.drawString("Hecho con", 160, 1075, F(R.RES.ms, 20), P("#9a8ab8"))
        draw_img(c, R.RES.vlogo, 278, 1068, 26)
        c.drawString("Velto", 296, 1075, F(R.RES.mx, 20), P("#ffffff"))
        c.restore()
    return draw


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def workshop_bg(c, t):
    c.drawRect(RECT(-500, -500, W + 500, 1430), P("#241040", shader=lin(0, 0, 0, 1430, ["#1a0a32", "#2e1450"])))
    g = P("#9b5cff", "stroke", 2, alpha=0.06)
    for i in range(-4, 14):
        c.drawLine(i * 120, -500, i * 120, 1430, g)
    # estantería con bustos de joyería
    c.drawRect(RECT(80, 640, 1000, 660), P("#5a3a7a"))
    c.drawRect(RECT(80, 860, 1000, 880), P("#5a3a7a"))
    for i, fn in enumerate((necklace, ring, earrings, bracelet, necklace)):
        fn(c, 170 + i * 185, 590, 0.9)
    for i, fn in enumerate((ring, bracelet, earrings, ring, necklace)):
        fn(c, 170 + i * 185, 815, 0.8)
    # lámpara colgante
    c.drawLine(880, -100, 880, 470, P("#3a2a50", "stroke", 4))
    tri = skia.Path()
    tri.moveTo(830, 520)
    tri.lineTo(930, 520)
    tri.lineTo(900, 470)
    tri.lineTo(860, 470)
    tri.close()
    c.drawPath(tri, P("#3a2a50"))
    glow(c, R.RES.glow_warm, 880, 560, 260, 0.35)
    c.drawRect(RECT(-500, 1430, W + 500, H + 500), P("#1a0d28", shader=lin(0, 1430, 0, H, ["#2a1640", "#0a0512"])))


def table(c, x0, x1, y):
    rrect(c, x0, y, x1, y + 34, 10, P("#6e4a8a", shader=lin(0, y, 0, y + 34, ["#8a62a8", "#4a2c62"])))
    c.drawRect(RECT(x0 + 30, y + 34, x0 + 52, 1440), P("#3a2450"))
    c.drawRect(RECT(x1 - 52, y + 34, x1 - 30, 1440), P("#3a2450"))


def scene1(c, k):  # Ana y el caos de mensajes
    lt = k.lt
    zo = ease_in_out(prog(lt, 0.5, 2.2))
    z = lerp(1.6, 1.0, zo)
    camera(c, z, lerp(560, 540, zo), lerp(860, 980, zo), k.t)
    workshop_bg(c, k.t)
    table(c, 560, 1000, 1290)
    necklace(c, 680, 1240, 0.9)
    ring(c, 800, 1255, 0.8)
    earrings(c, 910, 1250, 0.8)
    caos = prog(lt, k.w(8), k.w(13))
    shake = math.sin(lt * 60) * 6 * (0.4 + caos) * (lt > 0.2)
    expr = "happy" if lt < k.w(8) else ("worried" if lt < k.w(13) else "surprised")

    def held_phone(cc, out):
        hx, hy = out["R"]
        phone(cc, hx + 10 + shake, hy - 70, 120, 220, lambda c2, a, b, d, e: chat_lines(c2, a, b, d, e, lt), rot=-8, glow_a=0.4)
    hp = draw_kid(c, 380, 1470, 1.05, k.t, expr, look=(0.6, -0.2), tilt=-4 + 3 * math.sin(k.t * 2) * caos,
                  hands={"R": (150, -400), "L": (-120, -200 + 40 * caos)}, style=ANA, front_props=held_phone)
    px, py = hp["R"]
    use("vio")
    msgs = ["¿Precio?", "¿Info?", "¿Tienes en dorado?", "¿Hacen envíos?", "¿Precio??", "¿Y este?", "¿Sigue disponible?"]
    pos = [(560, 760), (150, 820), (600, 980), (120, 1060), (640, 640), (180, 690), (560, 1140)]
    t0 = k.w(8) - 0.3
    for i, (m, (bx, by)) in enumerate(zip(msgs, pos)):
        st = t0 + i * 0.32
        kk = prog(lt, st, st + 0.25)
        bubble(c, bx - 20, by + 6 * math.sin(k.t * 3 + i), m, False, 44, 600, kk, col="#2c2540")
    n = int(lerp(3, 99, prog(lt, 0.3, k.w(13))))
    badge(c, px + 60, py - 160, "99+" if n >= 99 else str(n), prog(lt, 0.2, 0.5))
    if lt > 0.2:
        for j in range(3):
            a = (lt * 2 + j / 3) % 1
            arc = skia.Path()
            arc.addArc(RECT(px - 90 - a * 60, py - 160 - a * 60, px + 110 + a * 60, py + 40 + a * 60), -60, 120)
            c.drawPath(arc, P(LIME2, "stroke", 4, alpha=(1 - a) * 0.7))


def chat_lines(c, x0, y0, x1, y1, lt):
    w = x1 - x0
    for i in range(5):
        yy = y0 + 30 + i * 36 - (lt * 40) % 36
        out = i % 2 == 0
        bw = w * (0.45 + 0.2 * ((i * 37) % 3) / 3)
        bx = x1 - 8 - bw if out else x0 + 8
        rrect(c, bx, yy, bx + bw, yy + 24, 10, P(VIO if out else "#3a3150"))


def scene2(c, k):  # chat caótico en primer plano
    lt = k.lt
    camera(c, lerp(1.0, 1.06, prog(lt, 0, k.D)), 540, 1000, k.t)
    neon_bg(c, k.t, grid=0.06, waves=False)
    T = lambda i: k.w(i)  # noqa: E731
    items = [  # (texto o producto, enviado?, momento)
        ("p0", True, T(0)), ("¿Precio?", False, T(0) + 0.45), ("Q175", True, T(1)),
        ("p1", True, T(2)), ("¿Precio?", False, T(2) + 0.35), ("Q120", True, T(3)),
        ("p2", True, T(3) + 0.3), ("¿Precio??", False, T(4)), ("¿Hola?", False, T(5)),
        ("Mejor ya no...", False, T(8)),
    ]

    def screen(c2, x0, y0, x1, y1):
        c2.drawRect(RECT(x0, y0, x1, y0 + 110), P("#1f1636"))
        oval(c2, x0 + 70, y0 + 66, 30, 30, P("#6a5a8a"))
        c2.drawString("Cliente", x0 + 115, y0 + 76, F(R.RES.mb, 30), P("#ffffff"))
        shown = [it for it in items if lt >= it[2] - 0.05]
        y = y1 - 40
        heights = []
        for txt, out, tm in reversed(shown):
            h = 200 if txt.startswith("p") else 72
            heights.append(h)
        total = sum(heights) + 18 * len(heights)
        y = y1 - 30 - total
        for txt, out, tm in shown:
            kk = prog(lt, tm - 0.05, tm + 0.2)
            if txt.startswith("p"):
                i = int(txt[1])
                h = 200
                bx = x1 - 30 - 240
                s = back_out(kk)
                c2.save()
                c2.translate(bx + 120, y + 100)
                c2.scale(s, s)
                rrect(c2, -120, -100, 120, 100, 24, P(VIO))
                rrect(c2, -108, -88, 108, 88, 18, P("#fdf6ff"))
                PRODUCTS[i][2](c2, 0, -4, 1.3)
                c2.restore()
            else:
                h = 72
                col = "#c2183f" if txt.startswith("Mejor") else None
                if out:
                    bubble(c2, x1 - 30, y, txt, True, 34, 500, kk, tf=R.RES.mb)
                else:
                    bubble(c2, x0 + 30, y, txt, False, 34, 500, kk, col=col)
            y += h + 18
        c2.drawRect(RECT(x0, y1 - 0, x1, y1), P("#000000"))
    phone(c, 540, 1010, 600, 1040, screen, rot=2 * math.sin(k.t * 1.2), glow_a=0.5)
    # reloj del cliente impaciente
    wait = prog(lt, T(5) - 0.2, T(5) + 0.2)
    if wait > 0:
        s = back_out(wait)
        c.save()
        c.translate(900, 640)
        c.scale(s, s)
        oval(c, 0, 0, 62, 62, P("#ffffff"))
        oval(c, 0, 0, 62, 62, P("#ff3b5c", "stroke", 8))
        a = lt * 6
        c.drawLine(0, 0, math.cos(a) * 40, math.sin(a) * 40, P("#14061f", "stroke", 6))
        c.drawLine(0, 0, 0, -28, P("#14061f", "stroke", 6))
        c.restore()


def scene3(c, k):  # página web cara y complicada
    lt = k.lt
    z = lerp(1.0, 1.1, ease_in_out(prog(lt, 0, k.D)))
    camera(c, z, 560, 1000, k.t)
    workshop_bg(c, k.t)
    table(c, 380, 1040, 1250)
    # laptop
    c.save()
    c.translate(720, 1250)
    rrect(c, -250, -360, 250, -20, 18, P("#2a2534"))
    c.drawRect(RECT(-232, -342, 232, -38), P("#f4f2f8"))
    c.drawString("Página web", -200, -280, F(R.RES.mx, 42), P("#2a1a40"))
    lines = [("Desde Q8,000", "#d62a4a", R.RES.mx, 50, 0.3), ("+ programador", "#4a3a60", R.RES.mb, 34, 0.9),
             ("+ hosting y dominio", "#4a3a60", R.RES.mb, 34, 1.4), ("+ semanas de espera", "#4a3a60", R.RES.mb, 34, 1.9)]
    for i, (txt, col, tf, sz, tm) in enumerate(lines):
        a = ease_out(prog(lt, tm, tm + 0.3))
        c.drawString(txt, -200 + 30 * (1 - a), -200 + i * 52, F(tf, sz), P(col, alpha=a))
    rrect(c, -290, -20, 290, 4, 8, P("#3a3446"))
    c.restore()
    sad = prog(lt, k.w(6) - 0.2, k.w(6) + 0.2)
    draw_kid(c, 250, 1480, 1.0, k.t, "worried" if sad < 0.5 else "sad", look=(0.8, 0.2), tilt=-6 * sad,
             hands={"R": (130, -260), "L": (-110, -200)}, style=ANA)
    # se apaga el color
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#808080", blend=skia.BlendMode.kSaturation, alpha=0.75 * sad))
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#05030a", alpha=0.3 * sad))
    # nube gris de "complicado"
    if sad > 0:
        for j in range(5):
            r = rng(j)
            ox, oy = 250 + (r.random() - .5) * 200, 820 + (r.random() - .5) * 60
            oval(c, ox, oy - 12 * math.sin(k.t * 2 + j), 60 + 20 * r.random(), 40, P("#5a5566", alpha=0.6 * sad))


def scene4(c, k):  # aparece Velto
    lt = k.lt
    camera(c, lerp(1.08, 1.0, ease_out(prog(lt, 0, 1.0))), 540, 960, k.t)
    light = ease_out(prog(lt, 0.35, 1.0))
    neon_bg(c, k.t, grid=0.04 + 0.16 * light, wy=1480)
    # estela que dibuja la V
    use("vio")
    pts = [(-100, 500), (380, 700), (540, 1120), (720, 760), (1180, 560)]
    path = skia.Path()
    path.moveTo(*pts[0])
    path.cubicTo(150, 520, 330, 600, pts[2][0], pts[2][1])
    path.cubicTo(650, 980, 820, 680, pts[4][0], pts[4][1])
    meas = skia.PathMeasure(path, False)
    L = meas.getLength()
    u = ease_in_out(prog(lt, 0.0, 0.7))
    if u > 0:
        seg = skia.Path()
        meas.getSegment(max(0, u - 0.45) * L, u * L, seg, True)
        c.drawPath(seg, P(VIO, "stroke", 40, shader=lin(0, 0, W, 0, [VIO, "#d06bff", LIME]), blur=18, alpha=0.6 * (1 - light * 0.8)))
        c.drawPath(seg, P(VIO, "stroke", 10, shader=lin(0, 0, W, 0, [VIO, "#e2b8ff", LIME]), alpha=1 - light * 0.8))
        p = meas.getPosTan(u * L)[0]
        glow(c, R.RES.glow_white, p.x(), p.y(), 70, 0.9 * (1 - light))
        glow(c, R.RES.g_lime if u > 0.5 else R.RES.g_vio, p.x(), p.y(), 180, 0.7 * (1 - light))
    lg = ease_out(prog(lt, 0.55, 1.0))
    if lg > 0:
        client_logo(c, 540, 860, 980 * (0.9 + 0.1 * lg), a=lg)
    draw_kid(c, 210, 1530, 0.78, k.t, "surprised", look=(1, -0.6), tilt=6, style=ANA,
             hands={"L": (-150, -470), "R": (150, -480)}, bob=-8 * abs(math.sin(lt * 5)) * (lt > 0.6))


def scene5(c, k):  # arma su catálogo en minutos
    lt = k.lt
    z = lerp(1.0, 1.05, ease_in_out(prog(lt, 0, k.D)))
    camera(c, z, 560, 980, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1520)
    use("vio")
    R.dust(c, k.t, n=30, seed=4, alpha=0.6)
    T = k.w
    prods = [prog(lt, T(10) - 0.2 + i * 0.18, T(10) + i * 0.18 + 0.15) for i in range(4)]
    step = {"logo": prog(lt, T(8) - 0.25, T(8) + 0.35), "prods": prods,
            "precios": prog(lt, T(11) - 0.1, T(11) + 0.35), "desc": prog(lt, T(13) - 0.4, T(13) + 0.6),
            "boton": prog(lt, T(14), T(14) + 0.3)}
    if lt < T(8) - 0.25:
        build = lambda c2, *a: empty_builder(c2, *a, lt)  # noqa: E731
    else:
        build = catalog_screen(k, k.t, step)
    phone(c, 610, 980, 560, 1080, build, rot=-3 + 1.5 * math.sin(k.t * 0.9), glow_a=0.9)
    use("lime")
    R.orbit_sparkles(c, 610, 980, k.t, 330, 520, n=26, seed=3, intensity=0.6)
    use("vio")
    joy = lt > T(14)
    draw_kid(c, 150, 1560, 0.72, k.t, "joy" if joy else "happy", look=(1, -0.3), tilt=5, style=ANA,
             hands={"R": (170, -460) if joy else (150, -330), "L": (-150, -460) if joy else (-110, -200)})
    pill(c, 300, 690, "Sin código", prog(lt, T(14), T(14) + 0.35), size=36)


def empty_builder(c, x0, y0, x1, y1, lt):
    cx = (x0 + x1) / 2
    w = x1 - x0
    text_center(c, "Crea tu catálogo", cx, y0 + 260, F(R.RES.mx, 40), P("#ffffff"))
    for i in range(3):
        a = ease_out(prog(lt, 0.2 + i * 0.25, 0.5 + i * 0.25))
        yy = y0 + 360 + i * 120
        rrect(c, x0 + 40, yy, x1 - 40, yy + 84, 20, P("#24183c", alpha=a))
        rrect(c, x0 + 40, yy, x1 - 40, yy + 84, 20, P("#7a4bc4", "stroke", 2, alpha=0.7 * a))
        c.drawString(["+ Logo", "+ Productos", "+ Descripción"][i], x0 + 70, yy + 54, F(R.RES.mb, 30), P("#d9cdf0", alpha=a))
    p = clamp(lt / 1.6)
    rrect(c, x0 + 40, y1 - 160, x1 - 40, y1 - 140, 10, P("#2c2540"))
    rrect(c, x0 + 40, y1 - 160, lerp(x0 + 60, x1 - 40, p), y1 - 140, 10, P(LIME))


def scene6(c, k):  # el cliente pide por mensaje
    lt = k.lt
    camera(c, 1.0, 540, 980, k.t)
    neon_bg(c, k.t, grid=0.08, wy=1540)
    T = k.w
    press = prog(lt, T(12) - 0.15, T(12) + 0.25)
    step = {"logo": 1, "prods": [1, 1, 1, 1], "precios": 1, "desc": 1, "boton": 1, "press": press,
            "link": prog(lt, T(6) - 0.2, T(6) + 0.2)}
    scroll = ease_in_out(prog(lt, 0.2, 1.6))
    phone(c, 360, 865 - 20 * scroll, 400, 770, catalog_screen(k, k.t, step), rot=-4, glow_a=0.7)
    # dedo que toca el botón
    tap = prog(lt, T(12) - 0.5, T(12) - 0.1)
    if tap > 0 and lt < T(13) + 0.6:
        fx, fy = lerp(540, 392, ease_out(tap)), lerp(1375, 1185, ease_out(tap))
        oval(c, fx, fy, 30, 34, P("#f6c09a", shader=rad(fx - 8, fy - 8, 40, ["#ffe2c8", "#f3b991"])))
    draw_kid(c, 140, 1600, 0.62, k.t, "happy", look=(0.6, -0.6), style=CLIENTE, hands={"R": (150, -360), "L": (-100, -210)})
    # el mensaje vuela hacia Ana
    fly = ease_in_out(prog(lt, T(12) + 0.1, T(13) + 0.3))
    if 0 < fly < 1:
        ax, ay = lerp(390, 820, fly), lerp(1175, 860, fly) - 260 * math.sin(math.pi * fly)
        use("lime")
        R.aroma(c, ax, ay + 40, k.t, n=14, height=120, spread=20, intensity=0.8, seed=9, speed=1.2)
        chat_icon(c, ax, ay, 34)
    got = prog(lt, T(13) + 0.3, T(13) + 0.6)
    joy = got > 0.5
    draw_kid(c, 830, 1520, 0.85, k.t, "joy" if joy else "neutral", look=(-0.5, -0.3), style=ANA, tilt=-4,
             hands={"R": (160, -470), "L": (-160, -470)} if joy else {"R": (120, -220), "L": (-120, -220)},
             bob=-14 * abs(math.sin(lt * 7)) * joy)
    if got > 0:
        s = back_out(got)
        c.save()
        c.translate(820, 760)
        c.scale(s, s)
        glow(c, R.RES.g_lime, 0, 0, 260, 0.4)
        rrect(c, -190, -110, 190, 110, 28, P("#1b1230"))
        rrect(c, -190, -110, 190, 110, 28, P(LIME, "stroke", 4))
        rrect(c, -190, -110, 190, -50, 28, P(LIME))
        c.drawRect(RECT(-190, -80, 190, -50), P(LIME))
        c.drawString("Nuevo pedido", -150, -68, F(R.RES.mx, 32), P("#14061f"))
        c.drawString("1 x Collar Luna", -160, 6, F(R.RES.mb, 30), P("#ffffff"))
        c.drawString("Total: Q175", -160, 62, F(R.RES.mx, 34), P(LIME))
        c.restore()
        use("lime")
        R.burst(c, 820, 760, lt - T(13) - 0.3, dur=1.1, n=40, radius=320, seed=12)


GLOBE_PINS = [("Guatemala", -60, 40), ("México", -170, -60), ("El Salvador", 20, 120), ("Honduras", 110, 60),
              ("Costa Rica", 150, 170), ("Estados Unidos", -110, -190), ("Colombia", 170, 210)]


def scene7(c, k):  # emprendedores de Guatemala y otros países
    lt = k.lt
    camera(c, lerp(1.06, 1.0, ease_out(prog(lt, 0, 2))), 540, 980, k.t)
    neon_bg(c, k.t, grid=0.10, wy=1560)
    icons = [(sneaker, "Tenis"), (perfume, "Perfumes"), (headphones, "Audio"), (cupcake, "Postres")]
    for i, (fn, label) in enumerate(icons):
        kk = prog(lt, 0.1 + i * 0.18, 0.4 + i * 0.18)
        x, y = 160 + i * 253, 650 + 10 * math.sin(k.t * 2 + i)
        glass_card(c, x, y, 210, 220, kk)
        if kk > 0:
            s = back_out(kk)
            c.save()
            c.translate(x, y)
            c.scale(s, s)
            fn(c, 0, -20, 1.0)
            text_center(c, label, 0, 80, F(R.RES.mb, 26), P("#ffffff"))
            c.restore()
    gx, gy, gr = 540, 1170, 290
    glow(c, R.RES.g_vio, gx, gy, gr * 1.8, 0.5)
    oval(c, gx, gy, gr, gr, P("#1c0a38", shader=rad(gx - 80, gy - 90, gr * 1.4, ["#4a1c8a", "#1c0a38", "#0a0416"])))
    c.save()
    c.clipPath(skia.Path().addOval(RECT(gx - gr, gy - gr, gx + gr, gy + gr)), True)
    for i in range(8):
        ph = (i / 8 + k.t * 0.05) % 1
        rx = abs(math.cos(ph * math.pi)) * gr
        oval(c, gx, gy, rx, gr, P("#b46bff", "stroke", 2, alpha=0.35))
    for j in range(-3, 4):
        yy = gy + j * gr / 4
        hw = math.sqrt(max(0, gr * gr - (yy - gy) ** 2))
        c.drawLine(gx - hw, yy, gx + hw, yy, P("#b46bff", "stroke", 2, alpha=0.3))
    c.restore()
    oval(c, gx, gy, gr, gr, P("#c48bff", "stroke", 3, alpha=0.8))
    T = k.w
    gt = GLOBE_PINS[0]
    for i, (name, px, py) in enumerate(GLOBE_PINS):
        st = T(2) - 0.2 if i == 0 else T(5) - 0.2 + (i - 1) * 0.22
        kk = prog(lt, st, st + 0.3)
        if kk <= 0:
            continue
        x, y = gx + px, gy + py
        if i > 0:
            arc = skia.Path()
            arc.moveTo(gx + gt[1], gy + gt[2])
            arc.quadTo((gx + gt[1] + x) / 2, min(gy + gt[2], y) - 90, x, y)
            meas = skia.PathMeasure(arc, False)
            seg = skia.Path()
            meas.getSegment(0, meas.getLength() * ease_out(kk), seg, True)
            c.drawPath(seg, P(LIME, "stroke", 4, alpha=0.9))
        s = back_out(kk)
        col = LIME if i == 0 else "#d9a6ff"
        c.save()
        c.translate(x, y)
        c.scale(s, s)
        pin = skia.Path()
        pin.moveTo(0, 0)
        pin.quadTo(-22, -26, -22, -40)
        pin.cubicTo(-22, -70, 22, -70, 22, -40)
        pin.quadTo(22, -26, 0, 0)
        glow(c, R.RES.g_lime if i == 0 else R.RES.g_vio, 0, -40, 70, 0.6)
        c.drawPath(pin, P(col))
        oval(c, 0, -42, 8, 8, P("#14061f"))
        if i == 0:
            f = F(R.RES.mx, 34)
            tw = f.measureText(name)
            lx, ly = -110, 70
            rrect(c, lx - tw / 2 - 16, ly - 24, lx + tw / 2 + 16, ly + 24, 24, P("#14061f", alpha=0.9))
            rrect(c, lx - tw / 2 - 16, ly - 24, lx + tw / 2 + 16, ly + 24, 24, P(LIME, "stroke", 3))
            text_center(c, name, lx, ly + 12, f, P(LIME))
        c.restore()


def scene8(c, k):  # cierre con logo y llamado a la acción
    lt = k.lt
    camera(c, lerp(1.08, 1.0, ease_out(prog(lt, 0, 3))), 540, 960, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1640)
    use("vio")
    R.dust(c, k.t, n=40, seed=31, alpha=0.6)
    lg = ease_out(prog(lt, 0.1, 0.6))
    if lg > 0:
        client_logo(c, 540, 860, 980 * (0.9 + 0.1 * lg), a=lg)
    T = k.w
    # "Hasta 50 clientes completamente gratis"
    gk = prog(lt, T(6) - 0.15, T(6) + 0.35)
    if gk > 0:
        sc = back_out(gk)
        c.save()
        c.translate(540, 1180)
        c.scale(sc, sc)
        glow(c, R.RES.g_lime, 0, 0, 420, 0.4)
        rrect(c, -400, -95, 400, 95, 40, P("#14061f", alpha=0.92))
        rrect(c, -400, -95, 400, 95, 40, P(LIME, "stroke", 4))
        text_center(c, "Hasta", -250, -10, F(R.RES.mb, 40), P("#ffffff"))
        text_center(c, "50", -105, 42, F(R.RES.mx, 120), P(LIME))
        c.drawString("clientes", 10, -14, F(R.RES.mx, 50), P("#ffffff"))
        c.drawString("100% GRATIS", 10, 48, F(R.RES.mx, 50), P(LIME))
        c.restore()
    pill(c, 540, 1395, "Escríbenos y crea tu catálogo", prog(lt, T(11) - 0.15, T(11) + 0.3), size=40,
         tf=R.RES.mxi, arrow=True)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8]
camera = R.camera


def draw_watermark(c):
    f = F(R.RES.mb, 34)
    txt = "@veltodigital.gt"
    w = f.measureText(txt)
    x0, x1 = W / 2 - w / 2 - 34, W / 2 + w / 2 + 34
    y0, y1 = 1528, 1594
    rrect(c, x0, y0, x1, y1, 33, P("#0c0618", alpha=0.65))
    rrect(c, x0, y0, x1, y1, 33, P(VIO, "stroke", 2.5, shader=lin(x0, 0, x1, 0, [VIO2, LIME]), alpha=0.9))
    c.drawString(txt, W / 2 - w / 2, 1573, f, P("#ffffff"))


def install():
    R.Res = VeltoRes
    R.SCENES = SCENES
    R.SCENE_GRADE = {}
    R.draw_watermark = draw_watermark
    R.SUB_BOX, R.SUB_BOX_BORDER, R.SUB_TEXT_ACTIVE = LIME, "#efffb0", "#14061f"
    R.SUB_SIZE = 60


if __name__ == "__main__":
    install()
    R.main()
