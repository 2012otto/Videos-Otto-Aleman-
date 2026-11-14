"""Velto Studio — Dato curioso: "11 días sin dormir" (Randy Gardner, 1964) con anuncio de $5 a la mitad y al final.

Estilo "dato curioso": fondos bokeh, personaje de proporciones realistas, subtítulos arriba
(palabra actual en blanco, anteriores en gris). Voz: clon ElevenLabs "Voz Referencia Otto".
Uso:
  VIDEO_BUILD=$PWD/velto/build_sueno VO_TRIM=0.3 python3 velto/src/render_sueno.py --out velto/build_sueno/video_mudo.mp4
"""
import math
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_velto as V  # noqa: E402
from render_velto import (R, P, RECT, VIO, VIO2, LIME, F, back_out, clamp, ease_in_out, ease_out, glow, lerp,  # noqa: E402
                          lin, rad, oval, prog, rrect, smooth, text_center, rng, use, W, H, draw_img, bubble)

camera = R.camera
SKIN = ["#f8d6b8", "#e8b08a", "#c98a62"]


# ----------------------------------------------------------------------------
# fondo bokeh y personaje realista
# ----------------------------------------------------------------------------


def bokeh(c, t, top, bottom, cols, n=26, seed=3):
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P(top, shader=lin(0, -200, 0, H, [top, bottom])))
    r = rng(seed)
    for i in range(n):
        x = r.random() * 1300 - 100 + 30 * math.sin(t * 0.3 + i)
        y = r.random() * 2000 - 100 + 20 * math.cos(t * 0.25 + i)
        rr = 60 + r.random() * 180
        col = cols[i % len(cols)]
        spr = R.sprite(*[int(col[j:j + 2], 16) for j in (1, 3, 5)], n=64, power=1.2) if False else None
        p = P(col, shader=rad(x, y, rr, [R.hexc(col, 0.35), R.hexc(col, 0.12), R.hexc(col, 0.0)], [0, .6, 1]))
        p.setBlendMode(skia.BlendMode.kScreen)
        c.drawCircle(x, y, rr, p)


def person(c, x, y, s, t, tired=0.0, mood="neutral", look=(0.0, 0.0), arms="down", yawn=0.0, sleep=False):
    """Chico de 1964: corte militar, camisa a cuadros. (x, y) = pies. tired 0..1: párpados y ojeras."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glow(c, R.RES.soft_dark, 0, 0, 160, 0.5, skia.BlendMode.kSrcOver)
    # piernas
    for side in (-1, 1):
        rrect(c, side * 52 - 30, -330, side * 52 + 30, -10, 26, P("#3a4a6a", shader=lin(side * 52 - 30, 0, side * 52 + 30, 0, ["#2a3650", "#4a5c80", "#2a3650"])))
        oval(c, side * 56, -6, 46, 18, P("#2a1e18"))
    # torso con camisa a cuadros
    body = skia.Path()
    body.moveTo(-70, -620)
    body.quadTo(-140, -610, -150, -560)
    body.lineTo(-130, -320)
    body.quadTo(-128, -300, -100, -300)
    body.lineTo(100, -300)
    body.quadTo(128, -300, 130, -320)
    body.lineTo(150, -560)
    body.quadTo(140, -610, 70, -620)
    body.close()
    c.drawPath(body, P("#c0392b", shader=lin(-150, 0, 150, 0, ["#8a2a22", "#d24a3a", "#e05a48", "#a83228"], [0, .35, .55, 1])))
    c.save()
    c.clipPath(body, True)
    for i in range(-6, 7):
        c.drawLine(i * 26, -640, i * 26, -290, P("#2a1410", "stroke", 3, alpha=0.35))
    for j in range(14):
        c.drawLine(-160, -620 + j * 24, 160, -620 + j * 24, P("#2a1410", "stroke", 3, alpha=0.3))
    c.restore()
    collar = skia.Path()
    collar.moveTo(-56, -622)
    collar.lineTo(0, -570)
    collar.lineTo(56, -622)
    c.drawPath(collar, P("#f4ead2", "stroke", 12))
    # brazos
    for side in (-1, 1):
        if arms == "down":
            pts = [(side * 140, -580), (side * 165, -440), (side * 155, -330)]
        elif arms == "point":
            pts = [(side * 140, -580), (side * 230, -520), (side * 320, -600)] if side > 0 else [(side * 140, -580), (side * 165, -440), (side * 155, -330)]
        else:  # "head": manos en la cabeza
            pts = [(side * 140, -580), (side * 220, -680), (side * 110, -760)]
        arm = skia.Path()
        arm.moveTo(*pts[0])
        arm.lineTo(*pts[1])
        arm.lineTo(*pts[2])
        c.drawPath(arm, P("#c0392b", "stroke", 52))
        c.drawPath(arm, P("#2a1410", "stroke", 52, alpha=0.0))
        oval(c, pts[2][0], pts[2][1] + 10, 26, 30, P(SKIN[1], shader=rad(pts[2][0] - 8, pts[2][1], 40, SKIN[:2])))
    # cuello y cabeza
    rrect(c, -30, -680, 30, -610, 14, P(SKIN[2]))
    c.save()
    c.translate(0, -770)
    c.rotate(3 * math.sin(t * 0.8) + (8 if sleep else 0))
    for side in (-1, 1):
        oval(c, side * 84, 10, 16, 26, P(SKIN[2]))
    face = skia.Path()
    face.addOval(RECT(-85, -105, 85, 115))
    c.drawPath(face, P(SKIN[0], shader=rad(-30, -40, 190, SKIN)))
    # pelo corte militar
    hair = skia.Path()
    hair.moveTo(-90, 10)
    hair.cubicTo(-100, -130, 100, -130, 90, 10)
    hair.quadTo(84, -40, 60, -50)
    hair.quadTo(0, -40, -60, -50)
    hair.quadTo(-84, -40, -90, 10)
    hair.close()
    c.drawPath(hair, P("#3a2414", shader=lin(0, -130, 0, -10, ["#5a3a22", "#2a180c"])))
    for i in range(9):
        c.drawLine(-60 + i * 15, -96 + abs(i - 4) * 4, -56 + i * 15, -60, P("#6a4a30", "stroke", 2, alpha=0.5))
    lx, ly = look[0] * 8, look[1] * 6
    for side in (-1, 1):
        ex, ey = side * 36, 6
        # ojeras
        if tired > 0.05:
            oval(c, ex, ey + 22, 26, 12, P("#7a4a6a", alpha=0.45 * tired))
        oval(c, ex, ey, 22, 14, P("#ffffff"))
        if not sleep:
            oval(c, ex + lx, ey + ly, 10, 11, P("#5a3a20"))
            oval(c, ex + lx, ey + ly, 5, 6, P("#14100c"))
            oval(c, ex + lx + 3, ey + ly - 4, 2.5, 2.5, P("#ffffff"))
        lid = 0.15 + 0.7 * tired if not sleep else 1.0  # párpado superior
        c.save()
        c.clipPath(skia.Path().addOval(RECT(ex - 22, ey - 14, ex + 22, ey + 14)), True)
        c.drawRect(RECT(ex - 24, ey - 16, ex + 24, ey - 16 + 30 * lid), P(SKIN[1]))
        c.restore()
        c.drawLine(ex - 22, ey - 14 + 28 * lid, ex + 22, ey - 14 + 28 * lid, P("#3a2414", "stroke", 3))
        bx, by = side * 38, -30
        br = skia.Path()
        tilt = {"neutral": 0, "worried": -8, "blank": 0, "happy": 4, "confused": -12 if side < 0 else 4}[mood]
        br.moveTo(bx - 24, by + (tilt if side < 0 else 0))
        br.lineTo(bx + 24, by + (0 if side < 0 else tilt))
        c.drawPath(br, P("#3a2414", "stroke", 8))
    nose = skia.Path()
    nose.moveTo(-4, 10)
    nose.quadTo(-16, 48, 0, 52)
    nose.quadTo(12, 54, 14, 46)
    c.drawPath(nose, P(SKIN[2], "stroke", 5))
    m = skia.Path()
    if yawn > 0.05:
        oval(c, 0, 80, 20 + 6 * yawn, 10 + 26 * yawn, P("#5a2230"))
    elif mood == "happy":
        m.moveTo(-28, 74)
        m.quadTo(0, 96, 28, 74)
        c.drawPath(m, P("#8a3a3a", "stroke", 5))
    elif mood in ("worried", "confused"):
        m.moveTo(-24, 86)
        m.quadTo(0, 74, 24, 86)
        c.drawPath(m, P("#8a3a3a", "stroke", 5))
    else:
        c.drawLine(-22, 82, 22, 82, P("#8a3a3a", "stroke", 5))
    c.restore()
    c.restore()


def calendar(c, x, y, day, k=1.0, s=1.0):
    if k <= 0:
        return
    sc = back_out(k) * s
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    glow(c, R.RES.soft_dark, 6, 14, 150, 0.4, skia.BlendMode.kSrcOver)
    rrect(c, -100, -110, 100, 110, 16, P("#fbf6ee"))
    rrect(c, -100, -110, 100, -40, 16, P("#d63a3a"))
    c.drawRect(RECT(-100, -60, 100, -40), P("#d63a3a"))
    for dx in (-50, 0, 50):
        oval(c, dx, -100, 8, 8, P("#ffffff"))
    text_center(c, "DÍA", 0, -60, F(R.RES.semi, 34), P("#ffffff"))
    text_center(c, str(day), 0, 72, F(R.RES.xbold, 110), P("#1a1a1a"))
    c.restore()


def wall_clock(c, x, y, r, t, speed=1.0):
    glow(c, R.RES.soft_dark, x + 6, y + 10, r * 1.3, 0.4, skia.BlendMode.kSrcOver)
    oval(c, x, y, r, r, P("#fbf6ee"))
    oval(c, x, y, r, r, P("#4a3220", "stroke", r * 0.12))
    for i in range(12):
        a = i * math.pi / 6
        c.drawLine(x + math.cos(a) * r * 0.75, y + math.sin(a) * r * 0.75, x + math.cos(a) * r * 0.86,
                   y + math.sin(a) * r * 0.86, P("#4a3220", "stroke", 4))
    am = t * speed * 6.283
    c.drawLine(x, y, x + math.cos(am - 1.57) * r * 0.7, y + math.sin(am - 1.57) * r * 0.7, P("#1a1a1a", "stroke", 6))
    ah = am / 12
    c.drawLine(x, y, x + math.cos(ah - 1.57) * r * 0.45, y + math.sin(ah - 1.57) * r * 0.45, P("#1a1a1a", "stroke", 9))
    oval(c, x, y, 8, 8, P("#d63a3a"))


def caption(c, text, k, x=80, y=620):
    if k <= 0:
        return
    f = F(R.RES.semi, 42)
    w = f.measureText(text) + 44
    c.save()
    c.translate(-30 * (1 - ease_out(k)), 0)
    rrect(c, x, y - 40, x + w, y + 16, 14, P("#000000", alpha=0.45 * k))
    c.drawString(text, x + 22, y, f, P("#ffffff", alpha=k))
    c.restore()


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def bedroom(c, t, warm=0.0):
    bokeh(c, t, R.mix_col("#1a1a3a", "#3a2a1a", warm), R.mix_col("#2a1a40", "#4a3020", warm),
          ["#8a6aff", "#ff9a5a", "#5ab0ff", "#ff6aa0"], seed=4)
    c.drawRect(RECT(-500, 1420, W + 500, H + 500), P("#2a1e2a", shader=lin(0, 1420, 0, H, ["#3a2a3a", "#0e0a10"])))


def scene1(c, k):  # gancho
    lt = k.lt
    T = k.w
    camera(c, lerp(1.12, 1.0, ease_out(prog(lt, 0, 3))), 540, 980, k.t)
    bedroom(c, k.t)
    wall_clock(c, 820, 720, 110, k.t, speed=0.6 + 3 * prog(lt, T(7), T(9)))
    day = 1 if lt < T(8) - 0.1 else min(11, 1 + int((lt - T(8) + 0.1) * 12))
    calendar(c, 240, 760, day, prog(lt, T(5) - 0.2, T(5) + 0.2))
    caption(c, "1964", prog(lt, T(1) - 0.2, T(1) + 0.3), x=440, y=640)
    person(c, 540, 1560, 1.0, k.t, tired=0.0, mood="happy" if lt < T(12) else "neutral", look=(0, -0.2))


def scene2(c, k):  # la feria de ciencias
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 980, k.t)
    bokeh(c, k.t, "#3a2a1a", "#1a1420", ["#ffb25a", "#ff7a5a", "#ffd88a", "#8a6aff"], seed=8)
    c.drawRect(RECT(-500, 1300, W + 500, 1340), P("#8a5a3a"))
    c.drawRect(RECT(-500, 1340, W + 500, H + 500), P("#3a2a20", shader=lin(0, 1340, 0, H, ["#5a3e2a", "#1a120c"])))
    # cartel de la feria (tríptico)
    c.save()
    c.translate(330, 1000)
    for i, (dx, sk) in enumerate(((-210, 0.92), (0, 1.0), (210, 0.92))):
        rrect(c, dx - 100, -250 * sk, dx + 100, 290 * sk, 10, P("#f4ecd8"))
        rrect(c, dx - 100, -250 * sk, dx + 100, 290 * sk, 10, P("#8a6a4a", "stroke", 4))
    text_center(c, "¿CUÁNTO", 0, -190, F(R.RES.xbold, 30), P("#1a3a6a"))
    text_center(c, "AGUANTA UN", 0, -154, F(R.RES.xbold, 30), P("#1a3a6a"))
    text_center(c, "HUMANO SIN", 0, -118, F(R.RES.xbold, 30), P("#1a3a6a"))
    text_center(c, "DORMIR?", 0, -82, F(R.RES.xbold, 30), P("#d63a3a"))
    # cerebro
    for (bx, by, r) in ((-30, 30, 50), (20, 20, 56), (40, 60, 44), (-20, 70, 46)):
        oval(c, bx, by, r, r * 0.8, P("#f4a0b0"))
    c.drawLine(0, -10, 0, 110, P("#c06070", "stroke", 4))
    for i in range(5):
        c.drawLine(-190, -150 + i * 50, -130, -150 + i * 50, P("#8a8a8a", "stroke", 4))
        c.drawLine(150, -150 + i * 50, 230, -150 + i * 50, P("#8a8a8a", "stroke", 4))
    c.restore()
    oval(c, 560, 640, 34, 34, P("#2a6ad6"))
    for i in range(2):
        tri = skia.Path()
        tri.moveTo(548 + i * 24, 664)
        tri.lineTo(536 + i * 24, 730)
        tri.lineTo(560 + i * 24, 716)
        tri.close()
        c.drawPath(tri, P("#2a6ad6"))
    person(c, 820, 1580, 0.95, k.t, tired=0.1, mood="happy", look=(-0.6, -0.2), arms="point")
    caption(c, "Randy Gardner · 17 años", prog(lt, T(2) - 0.2, T(3) + 0.2), x=60, y=590)


def street_sign(c, x, y, s, morph, t):
    """Señal de tránsito que se transforma en una persona (alucinación)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    wob = 6 * math.sin(t * 5) * morph
    pole = P("#9aa0aa", alpha=1 - morph)
    c.drawRect(RECT(-8, -500, 8, 0), pole)
    oval(c, 0, -540, 80, 80, P("#d63a3a", alpha=1 - morph))
    oval(c, 0, -540, 64, 64, P("#ffffff", alpha=1 - morph))
    rrect(c, -46, -552, 46, -528, 6, P("#d63a3a", alpha=1 - morph))
    if morph > 0:
        a = morph
        glow(c, R.RES.g_vio, 0, -300, 320, 0.4 * a)
        oval(c, wob, -560, 70 * a + 10, 80 * a + 10, P("#2a2a3a", alpha=0.85 * a))
        body = skia.Path()
        body.moveTo(-90 * a + wob, -470)
        body.quadTo(-130 * a, -200, -60 * a, 0)
        body.lineTo(60 * a, 0)
        body.quadTo(130 * a, -200, 90 * a - wob, -470)
        body.close()
        c.drawPath(body, P("#2a2a3a", alpha=0.85 * a))
        for side in (-1, 1):
            oval(c, side * 24 + wob, -570, 8, 8, P("#ffe08a", alpha=a))
    c.restore()


def scene3(c, k):  # día 2 (visión doble) y día 4 (alucinación)
    lt = k.lt
    T = k.w
    split = T(9) - 0.1
    if lt < split:
        camera(c, 1.0, 540, 980, k.t)
        bedroom(c, k.t)
        dbl = smooth(prog(lt, T(4), T(6)))
        for off, a in ((-28 * dbl, 0.5 if dbl > 0 else 1.0), (28 * dbl, 0.5)):
            if a < 1 or off == 0:
                c.saveLayerAlpha(None, int(255 * a))
            c.save()
            c.translate(off, 0)
            person(c, 540, 2300, 1.9, k.t, tired=0.35, mood="worried", look=(0.3 * math.sin(k.t * 2), 0))
            c.restore()
            if a < 1 or off == 0:
                c.restore()
            if dbl <= 0:
                break
        calendar(c, 860, 620, 2, prog(lt, 0.0, 0.3), 0.8)
    else:
        u = lt - split
        camera(c, lerp(1.0, 1.08, ease_in_out(prog(u, 0, 4))), 540, 980, k.t)
        bokeh(c, k.t, "#0a0e22", "#1a1030", ["#5a7aff", "#ffcf6a", "#8a4aff"], seed=12)
        c.drawRect(RECT(-500, 1360, W + 500, H + 500), P("#1a1a26", shader=lin(0, 1360, 0, H, ["#2a2a3a", "#0a0a12"])))
        c.drawRect(RECT(-60, 500, -40, 1380), P("#3a3a4a"))
        glow(c, R.RES.glow_warm, -40, 520, 260, 0.6)
        morph = smooth(prog(lt, T(15) - 0.2, T(22)))
        street_sign(c, 780, 1380, 1.0, morph, k.t)
        person(c, 330, 1620, 0.85, k.t, tired=0.6, mood="confused", look=(0.8, -0.3))
        calendar(c, 860, 620, 4, prog(u, 0.0, 0.3), 0.8)


def ad_scene(final=False):
    def scene(c, k):
        lt = k.lt
        T = k.w
        camera(c, 1.0, 540, 960, k.t)
        c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#000000"))
        R.dust(c, k.t, n=18, seed=5, alpha=0.25, col=R.RES.g_vio)
        draw_img(c, R.RES.vlogo, 120, 230, 90)  # la V de Velto en la esquina
        ph = ease_out(prog(lt, 0.0, 0.5))
        fy = 1020 + 18 * math.sin(k.t * 1.6) + 200 * (1 - ph)

        def screen(c2, x0, y0, x1, y1):
            c2.drawRect(RECT(x0, y0, x1, y1), P("#1a1030", shader=lin(0, y0, 0, y1, ["#3a1a6a", "#120a20"])))
            for i in range(6):
                oval(c2, x0 + 60 + i * 60, y0 + 160 + 90 * math.sin(i * 1.7), 50, 50,
                     P(["#8a6aff", "#ff9a5a", "#5ab0ff"][i % 3], alpha=0.25))
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            pulse = 1 + 0.06 * math.sin(k.t * 4)
            oval(c2, cx, cy, 90 * pulse, 90 * pulse, P("#ffffff", alpha=0.95))
            tri = skia.Path()
            tri.moveTo(cx - 26, cy - 40)
            tri.lineTo(cx + 44, cy)
            tri.lineTo(cx - 26, cy + 40)
            tri.close()
            c2.drawPath(tri, P(VIO))
            prg = (k.t * 0.2) % 1
            rrect(c2, x0 + 30, y1 - 70, x1 - 30, y1 - 60, 5, P("#ffffff", alpha=0.3))
            rrect(c2, x0 + 30, y1 - 70, lerp(x0 + 30, x1 - 30, prg), y1 - 60, 5, P(LIME))
        if ph > 0:
            V.phone(c, 540, fy, 440, 860, screen, rot=-4 + 2 * math.sin(k.t), glow_a=0.9 * ph)
        price_i = 21 if final else 19
        pk = prog(lt, T(price_i) - 0.15, T(price_i) + 0.2)
        if pk > 0:
            s = back_out(pk, 2.2)
            c.save()
            c.translate(760, fy - 300)
            c.rotate(14)
            c.scale(s, s)
            c.drawLine(-90, -20, -160, -70, P("#e9e4f0", "stroke", 4))
            tag = skia.Path()
            tag.moveTo(-110, 0)
            tag.lineTo(-70, -60)
            tag.lineTo(110, -60)
            tag.lineTo(110, 60)
            tag.lineTo(-70, 60)
            tag.close()
            glow(c, R.RES.g_lime, 0, 0, 220, 0.6)
            c.drawPath(tag, P(LIME))
            oval(c, -76, 0, 10, 10, P("#000000"))
            text_center(c, "$5", 20, 34, F(R.RES.mx, 96), P("#14061f"))
            c.restore()
            use("lime")
            R.burst(c, 760, fy - 300, lt - T(price_i) + 0.1, dur=0.9, n=36, radius=300, seed=6, intensity=0.8)
        text_center(c, "VELTO STUDIO", 540, 1560, F(R.RES.mx, 40), P("#ffffff", alpha=0.85 * ph))
        if final:
            word = "VIDEO"
            r = rng(29)
            for i in range(20):
                side = -1 if i % 2 == 0 else 1
                x = 540 + side * (400 + r.random() * 80)
                u = (lt - (T(13) + i * 0.15)) / 2.6
                if u <= 0 or u >= 1:
                    continue
                yy = lerp(1500, 520, u)
                a = math.sin(math.pi * u)
                tx = [word, "¡" + word + "!", word + "!!", word][i % 4]
                f = F(R.RES.mx, 24)
                w = f.measureText(tx) + 64
                c.save()
                c.translate(x + 20 * math.sin(lt * 2 + i), yy)
                rrect(c, -w / 2, -26, w / 2, 26, 26, P("#2c2540", alpha=0.9 * a))
                oval(c, -w / 2 + 26, 0, 14, 14, P([VIO2, LIME, "#ff6fb1", "#5ad1ff"][i % 4], alpha=a))
                c.drawString(tx, -w / 2 + 50, 9, f, P("#ffffff", alpha=a))
                c.restore()
            bk = ease_out(prog(lt, T(13) - 0.4, T(13)))
            if bk > 0:
                c.save()
                c.translate(540, 1460)
                rrect(c, -300, -48, 300, 48, 48, P("#ffffff", alpha=bk))
                oval(c, -250, 0, 28, 28, P(VIO, alpha=bk))
                typed = word[: int(len(word) * prog(lt, T(14) - 0.4, T(14) + 0.1))]
                if typed:
                    c.drawString(typed, -205, 16, F(R.RES.mx, 44), P("#14061f", alpha=bk))
                else:
                    c.drawString("Comenta...", -205, 12, F(R.RES.ms, 30), P("#8a7aa8", alpha=bk))
                c.restore()
    return scene


def scene5(c, k):  # día 11
    lt = k.lt
    T = k.w
    camera(c, lerp(1.0, 1.1, ease_in_out(prog(lt, 0, k.D))), 540, 1000, k.t)
    bedroom(c, k.t)
    person(c, 540, 2300, 1.9, k.t, tired=1.0, mood="blank", look=(0, 0.2), yawn=max(0, math.sin(lt * 1.4)) * (lt > T(10)))
    calendar(c, 860, 620, 11, prog(lt, 0.0, 0.3), 0.8)
    sk = prog(lt, T(4) - 0.2, T(4) + 0.2)
    if sk > 0:
        txt = "hoooolaaa..."
        n = int(len(txt) * clamp((lt - T(4)) / 1.6))
        bubble(c, 120, 660, txt[:max(1, n)], False, 46, 600, sk, col="#ffffff", txtcol="#1a1a1a")
    fk = prog(lt, T(6) - 0.2, T(6) + 0.2)
    if fk > 0:
        a = 1 - prog(lt, T(9), T(11))
        bubble(c, 160, 800, "¿qué... estaba... diciendo?", False, 38, 700, fk, col=R.hexc("#ffffff", a), txtcol=R.hexc("#1a1a1a", a))


def scene6(c, k):  # durmió 14 horas
    lt = k.lt
    T = k.w
    u = prog(lt, 0.2, k.D)
    camera(c, 1.0, 540, 980, k.t)
    bedroom(c, k.t, warm=u)
    win = (180, 600, 520, 940)
    c.drawRect(RECT(*win), P("#1a2448", shader=lin(0, 600, 0, 940, [R.mix_col("#0a1030", "#7ac0ff", u), R.mix_col("#2a2a50", "#ffd8a8", u)])))
    oval(c, 350, lerp(980, 700, u), 50, 50, P("#ffd27a", alpha=u))
    c.drawRect(RECT(*win), P("#4a3220", "stroke", 18))
    wall_clock(c, 820, 720, 110, k.t, speed=3.0)
    # cama
    rrect(c, 120, 1240, 980, 1440, 30, P("#6a4a30"))
    rrect(c, 140, 1180, 960, 1300, 40, P("#e8e4f4"))
    rrect(c, 160, 1150, 340, 1230, 30, P("#ffffff"))
    c.save()
    c.translate(250, 1180)
    c.rotate(-90)
    c.restore()
    person_head = (250, 1150)
    c.save()
    c.translate(*person_head)
    c.rotate(-80)
    c.scale(0.55, 0.55)
    c.translate(0, 770)
    person(c, 0, 0, 1.0, k.t, sleep=True, mood="happy")
    c.restore()
    rrect(c, 300, 1170, 980, 1320, 50, P("#5a7ad6", shader=lin(0, 1170, 0, 1320, ["#7a9aef", "#3a5ab6"])))
    for i in range(3):
        a = ((lt * 0.8 + i / 3) % 1)
        text_center(c, "z", 360 + i * 40 + a * 60, 1080 - a * 200, F(R.RES.xbold, 50 + i * 16), P("#ffffff", alpha=1 - a))
    hk = prog(lt, T(3) - 0.2, T(3) + 0.2)
    if hk > 0:
        s = back_out(hk)
        c.save()
        c.translate(820, 920)
        c.scale(s, s)
        rrect(c, -150, -46, 150, 46, 46, P("#000000", alpha=0.6))
        text_center(c, "14 HORAS", 0, 16, F(R.RES.xbold, 46), P("#ffffff"))
        c.restore()


def scene7(c, k):  # el récord ya no se registra
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 980, k.t)
    bokeh(c, k.t, "#2a1018", "#120810", ["#ff5a5a", "#ffb25a", "#8a4aff"], seed=15)
    bk = ease_out(prog(lt, 0.0, 0.5))
    c.save()
    c.translate(540, 1060)
    c.scale(bk, bk)
    c.rotate(-3)
    rrect(c, -330, -230, 330, 230, 18, P("#6a1a20"))
    rrect(c, -310, -215, 0, 215, 8, P("#fbf6ee"))
    rrect(c, 0, -215, 310, 215, 8, P("#f4ecdc"))
    text_center(c, "RÉCORDS", -155, -150, F(R.RES.xbold, 40), P("#6a1a20"))
    text_center(c, "MUNDIALES", -155, -104, F(R.RES.xbold, 34), P("#6a1a20"))
    for i in range(5):
        c.drawLine(-280, -40 + i * 40, -40, -40 + i * 40, P("#c8c0b0", "stroke", 5))
    text_center(c, "Más tiempo", 155, -120, F(R.RES.bold, 34), P("#1a1a1a"))
    text_center(c, "sin dormir", 155, -78, F(R.RES.bold, 34), P("#1a1a1a"))
    text_center(c, "264 h", 155, 10, F(R.RES.xbold, 70), P("#1a1a1a"))
    c.restore()
    sk = prog(lt, T(8) - 0.15, T(8) + 0.2)
    if sk > 0:
        s = lerp(2.0, 1.0, ease_out(sk))
        c.save()
        c.translate(560, 1080)
        c.rotate(-12)
        c.scale(s, s)
        rrect(c, -300, -70, 300, 60, 16, P("#d63a3a", "stroke", 12, alpha=clamp(sk * 3)))
        text_center(c, "PELIGROSO", 0, 26, F(R.RES.xbold, 96), P("#d63a3a", alpha=clamp(sk * 3)))
        c.restore()
    wk = prog(lt, T(10) - 0.2, T(10) + 0.2)
    if wk > 0:
        s = back_out(wk)
        c.save()
        c.translate(540, 1460)
        c.scale(s, s)
        tri = skia.Path()
        tri.moveTo(0, -90)
        tri.lineTo(100, 80)
        tri.lineTo(-100, 80)
        tri.close()
        c.drawPath(tri, P("#ffcf3a"))
        c.drawPath(tri, P("#1a1a1a", "stroke", 8))
        text_center(c, "!", 0, 62, F(R.RES.xbold, 110), P("#1a1a1a"))
        c.restore()


SCENES = [scene1, scene2, scene3, ad_scene(False), scene5, scene6, scene7, ad_scene(True)]


# ----------------------------------------------------------------------------
# subtítulos estilo "dato curioso" y marca de agua pequeña
# ----------------------------------------------------------------------------


def draw_subs(c, t, phr):
    f_past = F(R.RES.semi, 60)
    f_cur = F(R.RES.xbold, 70)
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
            lines = []
            line = ""
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
                y = 360 - (len(lines) - 1 - i) * 70
                w = f_past.measureText(ln)
                c.drawString(ln, W / 2 - w / 2 + 3, y + 3, f_past, P("#000000", alpha=0.5 * fade, blur=5))
                c.drawString(ln, W / 2 - w / 2, y, f_past, P("#c9c6d2", alpha=0.8 * fade))
        k = ease_out(clamp((t - cur["s"] + 0.04) / 0.12))
        w = f_cur.measureText(cur["w"])
        c.save()
        c.translate(W / 2, 450)
        c.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k)
        c.drawString(cur["w"], -w / 2 + 4, 4, f_cur, P("#000000", alpha=0.55 * fade, blur=6))
        c.drawString(cur["w"], -w / 2, 0, f_cur, P("#ffffff", alpha=fade))
        c.restore()


def draw_watermark(c):
    c.save()
    c.translate(W / 2, 1640)
    c.scale(0.72, 0.72)
    f = F(R.RES.mb, 34)
    txt = "@veltodigital.gt"
    w = f.measureText(txt)
    rrect(c, -w / 2 - 30, -33, w / 2 + 30, 33, 33, P("#000000", alpha=0.45))
    c.drawString(txt, -w / 2, 12, f, P("#ffffff", alpha=0.9))
    c.restore()


def install():
    V.install()
    R.SCENES = SCENES
    R.FADE_IN = 0.0
    R.HARD_CUTS = {3, 4, 7}
    R.draw_subs = draw_subs
    R.draw_watermark = draw_watermark


if __name__ == "__main__":
    install()
    R.main()
