"""Otto Aleman Perfumes — "Estás haciendo esto mal con tu perfume" (adaptación olfativa), en bucle. Versión 2.

Cada escena en un lugar distinto (cuarto al amanecer, calle, dentro de la cabeza, cronómetro, cocina, oficina,
fiesta, cafetería, parque, tocador, tienda Otto Aleman, Black Friday) con cámara que viaja: paneos siguiendo al
personaje, barridos entre lugares y la cámara que entra a la cabeza. Textos grandes y de colores palabra por
palabra (sin tapar la cara). Solo el personaje A va de traje; las demás personas son gente normal.
Uso:
  VIDEO_BUILD=$PWD/otto_serie/build_nariz VO_TRIM=0.15 VO_GAP=0.25 VO_TAIL=0.8 \
    python3 otto_serie/src/render_nariz.py --out otto_serie/build_nariz/video_mudo.mp4
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
from render_decant_tarde import (R, P, lin, rad, oval, rrect, clamp, lerp, smooth, ease_out, ease_in_out, back_out,  # noqa: E402
                                 prog, rng, glow, text_center, W, H, RECT, F, M, OVER, decant)

A = M.STYLES["A"]
INK = "#14101a"
FEET = 1600
HS = 0.8                           # escala del personaje (la cabeza queda debajo de y≈780; el texto va arriba)


# ----------------------------------------------------------------------------
# utilidades
# ----------------------------------------------------------------------------


def person(c, k, x, y, s, keys, style=A, talk=True, hold_fn=None, walk=0.0):
    p = D.track(k.lt, keys)
    if walk > 0:
        p = M.walk(p, k.t, amp=walk)
    tk = M.talk_amount(k.t, k.s["tokens"]) if (talk and style is A) else 0.0
    M.draw(c, x, y, s, k.t, p, style=style, talk=tk, hold_fn=hold_fn)


def hold_decant(t, a=-8, h=190):
    return lambda c, x, y: decant(c, x, y - 80, h, a, t, 0.7)


def big_text(words, y, k, size=130, cols=("#ffffff",), stroke=INK, x=540, rot=-3, stagger=0.12, shake=0.0):
    """Texto grande palabra por palabra (sin cuadro). Fijo en pantalla."""
    if k <= 0:
        return

    def d(c):
        f = F(R.RES.xbold, size)
        ws = [w + " " for w in words]
        tot = sum(f.measureText(w) for w in ws) - f.measureText(" ")
        sc = min(1.0, 980 / max(tot, 1))
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.scale(sc, sc)
        xx = -tot / 2
        for i, w in enumerate(ws):
            kk = clamp((k - i * stagger) / 0.35)
            ww = f.measureText(w.strip())
            if kk > 0:
                s = back_out(kk, 2.4)
                col = cols[i % len(cols)]
                c.save()
                c.translate(xx + ww / 2, 0)
                if shake:
                    c.translate(shake * math.sin(k * 60 + i), shake * math.cos(k * 50 + i))
                c.scale(s, s)
                c.drawString(w.strip(), -ww / 2 + 7, 9, f, P("#000000", alpha=0.3, blur=6))
                sp = P(stroke, "stroke", size * 0.16)
                sp.setStrokeJoin(skia.Paint.kRound_Join)
                c.drawString(w.strip(), -ww / 2, 0, f, sp)
                c.drawString(w.strip(), -ww / 2, 0, f, P(col))
                c.restore()
            xx += f.measureText(w)
        c.restore()
    OVER.append(d)


def mist(c, x, y, t0, lt, n=30, size=1.0, col="#ffffff", dirx=1.0):
    u = lt - t0
    if not (0 < u < 1.6):
        return
    r = rng(int(t0 * 10) % 97)
    for i in range(n):
        a = math.radians(-35 + r.random() * 70)
        d = (80 + r.random() * 260) * ease_out(clamp(u / 1.0)) * size
        oval(c, x + math.cos(a) * d * dirx, y + math.sin(a) * d - 30 * u, (8 + 14 * r.random()) * size, (8 + 14 * r.random()) * size,
             P(col, alpha=0.6 * (1 - u / 1.6)))


def heart(c, x, y, s, a=1.0, col="#ff3d6a"):
    hp = skia.Path()
    hp.moveTo(x, y + 18 * s)
    hp.cubicTo(x - 32 * s, y - 2 * s, x - 16 * s, y - 28 * s, x, y - 10 * s)
    hp.cubicTo(x + 16 * s, y - 28 * s, x + 32 * s, y - 2 * s, x, y + 18 * s)
    c.drawPath(hp, P(col, alpha=a))


def wall_floor(c, wall, floor, y=1500, x0=-600, x1=2400):
    c.drawRect(RECT(x0, -600, x1, y), P(wall[0], shader=lin(0, -600, 0, y, list(wall))))
    c.drawRect(RECT(x0, y, x1, 2600), P(floor[0], shader=lin(0, y, 0, 2300, list(floor))))


def window(c, x0, y0, x1, y1, sky, sun=None, frame="#ffffff"):
    rrect(c, x0, y0, x1, y1, 10, P(sky[0], shader=lin(0, y0, 0, y1, list(sky))))
    if sun:
        glow(c, R.RES.glow_warm, sun[0], sun[1], 160, 0.7)
        oval(c, sun[0], sun[1], 50, 50, P("#fff4c0"))
    rrect(c, x0, y0, x1, y1, 10, P(frame, "stroke", 18))
    c.drawLine((x0 + x1) / 2, y0, (x0 + x1) / 2, y1, P(frame, "stroke", 10))
    c.drawLine(x0, (y0 + y1) / 2, x1, (y0 + y1) / 2, P(frame, "stroke", 10))


def plant(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -60, -110, 60, 0, 16, P("#d8784a"))
    for i in range(7):
        a = math.radians(-150 + i * 20)
        lf = skia.Path()
        lf.moveTo(0, -100)
        lf.quadTo(math.cos(a) * 80, -100 + math.sin(a) * 120 - 40, math.cos(a) * 150, -100 + math.sin(a) * 200)
        c.drawPath(lf, P("#2f9a4a", "stroke", 26))
    c.restore()


# ----------------------------------------------------------------------------
# escenarios
# ----------------------------------------------------------------------------


def bedroom(c, t):
    wall_floor(c, ("#ffd9b8", "#f4b890"), ("#c88a5a", "#8a5a34"))
    window(c, 120, 520, 560, 1020, ("#ffb070", "#ffe0a0", "#a8d8ff"), sun=(380, 900))
    for i in range(6):  # rayos de sol
        p = skia.Path()
        p.moveTo(200 + i * 60, 560)
        p.lineTo(240 + i * 60, 560)
        p.lineTo(700 + i * 120, 1600)
        p.lineTo(620 + i * 120, 1600)
        p.close()
        c.drawPath(p, P("#fff4d0", alpha=0.12))
    rrect(c, 760, 1200, 1300, 1520, 30, P("#ffffff"))   # cama
    rrect(c, 760, 1260, 1300, 1520, 30, P("#7a9aef", shader=lin(0, 1260, 0, 1520, ["#9ab8ff", "#5a7ad8"])))
    rrect(c, 800, 1160, 980, 1240, 30, P("#ffffff"))
    rrect(c, -200, 1220, 80, 1500, 10, P("#a8703a"))      # tocador con perfumes
    for i, col in enumerate(("#ffb04a", "#c8402a", "#7ad0ff")):
        rrect(c, -150 + i * 70, 1150, -110 + i * 70, 1220, 10, P(col))
        c.drawRect(RECT(-140 + i * 70, 1130, -120 + i * 70, 1150), P("#3a3a44"))
    rrect(c, 900, 560, 1180, 820, 8, P("#ffffff"))         # cuadro
    rrect(c, 920, 580, 1160, 800, 4, P("#7ad0a0", shader=lin(0, 580, 0, 800, ["#a8e0ff", "#7ad070"])))


def street(c, t, camx):
    c.drawRect(RECT(-600, -600, 4000, 1300), P("#7ac8ff", shader=lin(0, -200, 0, 1300, ["#4aa8f0", "#bfe8ff"])))
    for i in range(6):
        glow(c, R.RES.cloud, 200 + i * 600 + camx * 0.85, 360 + (i % 2) * 120, 200, 0.8, skia.BlendMode.kSrcOver)
    c.save()
    c.translate(camx * 0.5, 0)       # paralaje: edificios lejanos
    r = rng(3)
    for i in range(16):
        x0 = -400 + i * 230
        h = 400 + r.random() * 400
        c.drawRect(RECT(x0, 1300 - h, x0 + 210, 1300), P(["#c8b8e8", "#b8d8e8", "#e8d0b8"][i % 3]))
        for j in range(int(h / 80)):
            c.drawRect(RECT(x0 + 30, 1300 - h + 30 + j * 80, x0 + 180, 1300 - h + 60 + j * 80), P("#ffffff", alpha=0.5))
    c.restore()
    cols = ["#ff8a6a", "#ffd04a", "#6ad0b0", "#ff6aa8", "#8a9aff", "#ffb04a"]
    for i in range(8):  # tiendas cercanas
        x0 = -300 + i * 470
        c.drawRect(RECT(x0, 820, x0 + 450, 1340), P(cols[i % 6]))
        rrect(c, x0 + 40, 1000, x0 + 410, 1260, 10, P("#bfe8ff", alpha=0.9))
        for j in range(6):  # toldo a rayas
            c.drawRect(RECT(x0 + j * 75, 900, x0 + j * 75 + 75, 960), P("#ffffff" if j % 2 else cols[(i + 2) % 6]))
    c.drawRect(RECT(-600, 1340, 4000, 1660), P("#e8e0d4"))
    for i in range(30):
        c.drawLine(-600 + i * 160, 1340, -600 + i * 160, 1660, P("#d0c8bc", "stroke", 3))
    c.drawRect(RECT(-600, 1660, 4000, 2600), P("#5a5a66"))
    for i in range(14):
        c.drawRect(RECT(-500 + i * 300, 1820, -350 + i * 300, 1840), P("#ffffff", alpha=0.8))
    for i in range(6):  # árboles
        x = 100 + i * 620
        c.drawRect(RECT(x - 18, 1100, x + 18, 1350), P("#7a4a22"))
        for (dx, dy, rr) in ((0, 1000, 130), (-90, 1060, 100), (90, 1060, 100)):
            oval(c, x + dx, dy, rr, rr, P("#3aa04a", shader=rad(x + dx - 40, dy - 40, rr * 1.3, ["#6ad070", "#2a8a3a"])))


def head_inside(c, t):
    c.drawRect(RECT(-600, -600, 1700, 2600), P("#1a1060", shader=rad(540, 1000, 1400, ["#3a2ab0", "#120a40"])))
    r = rng(7)
    for i in range(40):  # neuronas
        x, y = r.random() * 1080, 400 + r.random() * 1300
        x2, y2 = x + (r.random() - 0.5) * 300, y + (r.random() - 0.5) * 300
        a = 0.3 + 0.3 * math.sin(t * 3 + i)
        c.drawLine(x, y, x2, y2, P("#8ad0ff", "stroke", 3, alpha=a))
        oval(c, x, y, 6, 6, P("#c8f0ff", alpha=a + 0.3))


def brain(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glow(c, R.RES.glow_warm, 0, 0, 380, 0.25)
    for (bx, by, r) in ((-120, -40, 120), (0, -90, 130), (120, -40, 120), (-80, 60, 110), (80, 60, 110), (0, 20, 120)):
        oval(c, bx, by, r, r * 0.85, P("#ff9ab8", shader=rad(bx - r * 0.3, by - r * 0.3, r * 1.4, ["#ffd0dc", "#ff7aa0"])))
    for i in range(7):
        p = skia.Path()
        p.moveTo(-200 + i * 60, -120)
        p.cubicTo(-180 + i * 60, -40, -220 + i * 60, 20, -190 + i * 60, 100)
        c.drawPath(p, P("#d85a80", "stroke", 7, alpha=0.6))
    for sd in (-1, 1):  # ojitos
        oval(c, sd * 60, -10, 22, 26, P("#ffffff"))
        oval(c, sd * 60, -6, 11, 13, P("#1a1010"))
    c.restore()


def switch(c, x, y, s, on, label, col_on="#2fbf71"):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -110, -60, 110, 60, 60, P(col_on if on > 0.5 else "#5a5a6a"))
    rrect(c, -110, -60, 110, 60, 60, P("#ffffff", "stroke", 6))
    oval(c, lerp(-50, 50, on), 0, 46, 46, P("#ffffff"))
    text_center(c, label, 0, 120, F(R.RES.xbold, 50), P("#ffffff"))
    c.restore()


def kitchen(c, t, alarm=0.0):
    wall_floor(c, ("#d8f0e8", "#b0e0d0"), ("#f4ece0", "#d8c8b0"))
    for i in range(12):  # azulejos
        for j in range(4):
            rrect(c, -100 + i * 110, 1000 + j * 110, -10 + i * 110, 1090 + j * 110, 8, P("#ffffff", alpha=0.5))
    c.drawRect(RECT(-200, 1400, 1300, 1460), P("#8a8e98"))      # mesón
    c.drawRect(RECT(-200, 1460, 1300, 1900), P("#5a7ad8"))
    rrect(c, 520, 1330, 900, 1400, 10, P("#2a2a34"))           # estufa
    for i in range(2):
        cx = 610 + i * 200
        for j in range(8):
            a = j * math.pi / 4
            h = 20 + 10 * math.sin(t * 14 + j)
            c.drawLine(cx + math.cos(a) * 30, 1330, cx + math.cos(a) * 36, 1330 - h, P("#4a8aff", "stroke", 8))
    rrect(c, -100, 560, 400, 820, 14, P("#ffffff"))           # alacena
    rrect(c, 600, 560, 1180, 820, 14, P("#ffffff"))
    if alarm > 0:
        blink = 0.5 + 0.5 * math.sin(t * 14)
        oval(c, 880, 480, 50, 50, P("#ff3030", alpha=alarm))
        glow(c, R.RES.glow_warm, 880, 480, 220, 0.7 * alarm * blink)
        c.drawRect(RECT(-600, -600, 1700, 2600), P("#ff2020", alpha=0.15 * alarm * blink))
        r = rng(4)
        for i in range(10):
            u = ((t * 0.4 + i / 10) % 1)
            oval(c, 560 + r.random() * 300, 1300 - u * 700, 40 + 70 * u, 40 + 70 * u, P("#9a9aa8", alpha=0.35 * (1 - u)))


def office(c, t):
    wall_floor(c, ("#eef4ff", "#cfdcf4"), ("#9aa8c0", "#6a7890"))
    window(c, -60, 520, 1140, 1060, ("#5ab0f0", "#bfe8ff"), frame="#e0e6f0")
    r = rng(5)
    for i in range(12):  # skyline por la ventana
        x0 = -40 + i * 100
        h = 120 + r.random() * 260
        c.drawRect(RECT(x0, 1050 - h, x0 + 90, 1050), P("#8a9ac8", alpha=0.7))
    rrect(c, -100, 1300, 1200, 1340, 10, P("#c8a070"))           # escritorio
    for x in (120, 760):
        rrect(c, x, 1120, x + 260, 1290, 12, P("#2a2a34"))
        rrect(c, x + 14, 1134, x + 246, 1276, 6, P("#4a8aff", shader=lin(0, 1134, 0, 1276, ["#6ab0ff", "#2a6ad8"])))
        c.drawRect(RECT(x + 110, 1290, x + 150, 1300), P("#2a2a34"))
    plant(c, 1020, 1300, 0.9)


def party(c, t):
    c.drawRect(RECT(-600, -600, 1700, 2600), P("#1a0a3a", shader=rad(540, 800, 1500, ["#4a1a8a", "#0a041a"])))
    for i in range(6):  # luces de colores
        a = t * 1.2 + i
        x = 540 + math.cos(a) * 500
        col = ["#ff3d9a", "#2ff0ff", "#ffe04a", "#7aff6a"][i % 4]
        p = skia.Path()
        p.moveTo(540, 300)
        p.lineTo(x - 80, 1800)
        p.lineTo(x + 80, 1800)
        p.close()
        c.drawPath(p, P(col, alpha=0.12))
    oval(c, 540, 330, 60, 60, P("#d8d8e0", shader=rad(520, 310, 70, ["#ffffff", "#8a8a96"])))  # bola disco
    c.drawRect(RECT(-600, 1560, 1700, 2600), P("#2a1a4a"))
    for i in range(12):
        c.drawRect(RECT(-300 + i * 140, 1560, -170 + i * 140, 1700), P(["#ff3d9a", "#2ff0ff", "#ffe04a"][i % 3], alpha=0.25))


def cafe(c, t):
    wall_floor(c, ("#6a3a22", "#4a2814"), ("#d8b890", "#a8865a"))
    rrect(c, 140, 820, 940, 1120, 16, P("#1a1a1a"))               # pizarrón del menú
    for i, (txt, pr) in enumerate((("Espresso", "Q15"), ("Latte", "Q22"), ("Capuccino", "Q25"))):
        c.drawString(txt, 200, 900 + i * 80, F(R.RES.semi, 46), P("#f4f0e8"))
        c.drawString(pr, 780, 900 + i * 80, F(R.RES.semi, 46), P("#ffd04a"))
    rrect(c, -100, 1240, 1200, 1300, 10, P("#8a5a32"))           # barra
    c.drawRect(RECT(-100, 1300, 1200, 1700), P("#a8703a", shader=lin(0, 1300, 0, 1700, ["#b88050", "#6a4020"])))
    rrect(c, 960, 1020, 1200, 1240, 20, P("#c8c8d0", shader=lin(960, 0, 1200, 0, ["#8a8e98", "#ffffff", "#8a8e98"])))  # cafetera
    for i in range(3):
        u = ((t * 0.5 + i / 3) % 1)
        oval(c, 1060 + 30 * math.sin(u * 6), 1000 - u * 160, 20 + 20 * u, 20 + 20 * u, P("#ffffff", alpha=0.4 * (1 - u)))


def coffee_bag(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    p = skia.Path()
    p.moveTo(-150, 0)
    p.lineTo(-130, -360)
    p.lineTo(130, -360)
    p.lineTo(150, 0)
    p.close()
    c.drawPath(p, P("#c8a070", shader=lin(-150, 0, 150, 0, ["#a88050", "#e0c090", "#a88050"])))
    text_center(c, "CAFÉ", 0, -180, F(R.RES.xbold, 70), P("#4a2a14"))
    r = rng(4)
    for i in range(14):
        bx, by = -140 + r.random() * 280, -400 + r.random() * 60
        c.save()
        c.translate(bx, by)
        c.rotate(r.random() * 180)
        oval(c, 0, 0, 22, 15, P("#4a2a14", shader=rad(-6, -4, 26, ["#7a4a24", "#2a140a"])))
        c.drawLine(-14, 0, 14, 0, P("#1a0a04", "stroke", 3))
        c.restore()
    c.restore()


def park(c, t):
    c.drawRect(RECT(-600, -600, 1700, 1300), P("#6ac0ff", shader=lin(0, -200, 0, 1300, ["#3aa0f0", "#c8f0ff"])))
    glow(c, R.RES.glow_warm, 880, 820, 260, 0.6)
    oval(c, 880, 820, 70, 70, P("#fff4c0"))
    for i in range(4):
        glow(c, R.RES.cloud, 100 + i * 330 + (t * 20) % 200, 900 + (i % 2) * 90, 170, 0.8, skia.BlendMode.kSrcOver)
    oval(c, 300, 1350, 900, 260, P("#5ac05a"))
    oval(c, 900, 1380, 800, 240, P("#4ab04a"))
    c.drawRect(RECT(-600, 1350, 1700, 2600), P("#5ac05a", shader=lin(0, 1350, 0, 2000, ["#6ad06a", "#3a9a3a"])))
    p = skia.Path()  # sendero
    p.moveTo(380, 2000)
    p.quadTo(520, 1600, 640, 1380)
    p.lineTo(720, 1380)
    p.quadTo(700, 1600, 820, 2000)
    p.close()
    c.drawPath(p, P("#e8d8b0"))
    for x in (60, 1040):
        c.drawRect(RECT(x - 22, 1050, x + 22, 1400), P("#7a4a22"))
        for (dx, dy, rr) in ((0, 950, 170), (-110, 1030, 120), (110, 1030, 120)):
            oval(c, x + dx, dy, rr, rr, P("#3aa04a", shader=rad(x + dx - 50, dy - 50, rr * 1.3, ["#7ad070", "#2a8a3a"])))
    for i in range(3):  # pajaritos
        bx = (t * 80 + i * 300) % 1400 - 200
        by = 1000 + i * 50
        fl = 10 * math.sin(t * 8 + i)
        bp = skia.Path()
        bp.moveTo(bx - 20, by - fl)
        bp.quadTo(bx - 8, by - 10, bx, by)
        bp.quadTo(bx + 8, by - 10, bx + 20, by - fl)
        c.drawPath(bp, P("#2a2a34", "stroke", 4))


def vanity(c, t):
    wall_floor(c, ("#ffe0ec", "#f4b8d0"), ("#e8d0d8", "#c8a8b8"))
    rrect(c, 140, 820, 940, 1300, 240, P("#bfe8ff", shader=lin(140, 0, 940, 0, ["#a8d8f0", "#e8f8ff", "#a8d8f0"])))  # espejo
    rrect(c, 140, 820, 940, 1300, 240, P("#d6a24a", "stroke", 18))
    for i in range(10):
        oval(c, 180 + i * 80, 800, 14, 14, P("#fff4c0"))
        glow(c, R.RES.glow_warm, 180 + i * 80, 800, 50, 0.5)
    rrect(c, -100, 1300, 1200, 1350, 10, P("#ffffff"))
    c.drawRect(RECT(-100, 1350, 1200, 1800), P("#f4d0e0"))


def store(c, t):
    wall_floor(c, ("#2a1a10", "#1a0e08"), ("#3a2a1a", "#1a0e08"))
    for row in range(3):  # estantes con frascos
        y = 960 + row * 180
        c.drawRect(RECT(-100, y, 1200, y + 20), P("#d6a24a"))
        for i in range(10):
            col = ["#ffb04a", "#c8402a", "#7ad0ff", "#b08aff", "#e0a060", "#2a2a34"][(i + row) % 6]
            x = -40 + i * 125
            rrect(c, x, y - 110, x + 60, y, 12, P(col, alpha=0.9))
            c.drawRect(RECT(x + 18, y - 140, x + 42, y - 110), P("#d6a24a"))
    rrect(c, -100, 1440, 1200, 1500, 10, P("#d6a24a"))           # mostrador
    c.drawRect(RECT(-100, 1500, 1200, 1900), P("#1a1a20"))


def store_logo(c):
    img = M.logo()
    w = 200
    h = w * img.height() / img.width()
    glow(c, R.RES.glow_warm, 540, 470, 220, 0.5)
    c.drawImageRect(img, RECT(540 - w / 2, 470 - h / 2, 540 + w / 2, 470 + h / 2), R.SAMP, skia.Paint())


def black_friday(c, t):
    c.drawRect(RECT(-600, -600, 1700, 2600), P("#0a0a0a", shader=rad(540, 900, 1400, ["#2a0a0a", "#000000"])))
    for i in range(14):
        a = t * 0.6 + i * 0.45
        p = skia.Path()
        p.moveTo(540, 900)
        p.lineTo(540 + math.cos(a) * 1600, 900 + math.sin(a) * 1600)
        p.lineTo(540 + math.cos(a + 0.18) * 1600, 900 + math.sin(a + 0.18) * 1600)
        p.close()
        c.drawPath(p, P("#e0203a" if i % 2 else "#ffd04a", alpha=0.08))


def stopwatch_scene(c, t, sec):
    c.drawRect(RECT(-600, -600, 1700, 2600), P("#ffd04a", shader=rad(540, 1000, 1300, ["#ffe680", "#ffb020"])))
    c.save()
    c.translate(540, 1100)
    oval(c, 0, 0, 330, 330, P("#ffffff"))
    oval(c, 0, 0, 330, 330, P(INK, "stroke", 26))
    rrect(c, -50, -400, 50, -330, 14, P(INK))
    sweep = skia.Path()
    sweep.moveTo(0, 0)
    sweep.arcTo(RECT(-300, -300, 300, 300), -90, max(0.1, 360 * (sec / 120)), False)
    sweep.close()
    c.drawPath(sweep, P("#ff5a3a", alpha=0.85))
    for i in range(12):
        a = i * math.pi / 6
        c.drawLine(math.cos(a) * 270, math.sin(a) * 270, math.cos(a) * 310, math.sin(a) * 310, P(INK, "stroke", 8))
    m, ss = int(sec // 60), int(sec % 60)
    text_center(c, f"{m}:{ss:02d}", 0, 50, F(R.RES.xbold, 150), P(INK))
    c.restore()


def color_decant(c, x, y, h, col, t, rot=0.0):
    sys.modules["render_ep4"].decant_vec(c, x, y, h, rot, t, 0.7, 0.0)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    rrect(c, -h * 0.1, h * 0.12, h * 0.1, h * 0.36, h * 0.08, P(col, alpha=0.9))
    c.restore()


DEC_COLS = ["#ffb04a", "#ff6a8a", "#7ad0ff", "#b08aff", "#7ad070", "#e0a060"]


# ----------------------------------------------------------------------------
# escenas: cada una devuelve su cámara (z, fx, fy, rot) y una función que dibuja el mundo
# ----------------------------------------------------------------------------


def cam_basic(k, z0, z1, fx0, fx1, fy0, fy1, rot=0.0):
    u = ease_in_out(clamp(k.lt / max(k.D, 0.1)))
    return (lerp(z0, z1, u), lerp(fx0, fx1, u) + 10 * math.sin(k.t * 0.7), lerp(fy0, fy1, u) + 8 * math.sin(k.t * 0.5), rot)


def punch(k, words, z):
    for wi in words:
        d = k.lt - k.w(wi)
        if 0 <= d < 0.5:
            z *= 1 + 0.07 * math.exp(-d * 9) * math.sin(min(d * 30, math.pi / 2))
    return z


def s0(k):  # cuarto al amanecer: se atomiza
    def draw(c):
        bedroom(c, k.t)
        person(c, k, 600, FEET, HS, [(0, "sostiene"), (k.w(3) + 0.2, "pulgar")], hold_fn=hold_decant(k.t))
        for j in range(3):
            mist(c, 760, 760, 0.15 + j * 0.45, k.lt, n=24)
    z, fx, fy, r = cam_basic(k, 1.25, 1.02, 640, 560, 1050, 1000)
    big_text(["¡LO", "ESTÁS"], 540, prog(k.lt, k.w(0) - 0.1, k.w(1) + 0.3), size=140, stroke="#e0203a")
    big_text(["HACIENDO", "MAL!"], 700, prog(k.lt, k.w(2) - 0.1, k.w(3) + 0.3), size=150, cols=("#ffe04a", "#ff3d3d"))
    return punch(k, (0, 3), z), fx, fy, r, draw


def s1(k):  # la calle: camina, y a la hora ya no huele
    camx = lerp(0, 900, ease_in_out(clamp(k.lt / k.D)))

    def draw(c):
        street(c, k.t, camx)
        x = 540 + camx
        stop = prog(k.lt, k.w(9) - 0.3, k.w(9))
        person(c, k, x, FEET, HS, [(0, "neutral"), (k.w(9), "piensa"), (k.w(13), "encoge")], walk=1 - stop, talk=False)
        sx = x + 330
        rrect(c, sx - 14, 980, sx + 14, 1340, 6, P("#3a3a44"))        # poste con reloj
        D.clock(c, sx, 920, 90, lerp(8, 9, ease_in_out(prog(k.lt, k.w(6), k.w(10)))))
    big_text(["8:00", "→", "9:00"], 600, prog(k.lt, k.w(6), k.w(9)) * (1 - prog(k.lt, k.w(11), k.w(12) - 0.1)), size=110,
             cols=("#ffffff", "#ffe04a", "#ffffff"))
    big_text(["¿YA", "NO", "HUELE?"], 600, prog(k.lt, k.w(12) - 0.1, k.w(14) + 0.3), size=130, cols=("#ffffff", "#ff3d3d", "#ffffff"))
    return 1.0, 540 + camx, 1000 + 6 * math.sin(k.t), 0, draw


def s2(k):  # acercamiento: no se fue → la cámara entra a la cabeza
    hx, hy = 1440, FEET - 874 * HS

    def draw(c):
        street(c, k.t, 900)
        person(c, k, 1440, FEET, HS, [(0, "piensa")], talk=False)
    e = ease_in_out(prog(k.lt, k.D - 0.7, k.D))
    z = lerp(1.25, 1.45, clamp(k.lt / k.D)) * (1 + 4 * e ** 2)
    if k.lt < k.w(4) - 0.1:
        big_text(["NO", "SE", "FUE"], 520, prog(k.lt, k.w(0), k.w(3) + 0.2), size=150, cols=("#2fbf71",))
    big_text(["TU", "NARIZ", "TE", "MIENTE"], 540, prog(k.lt, k.w(4) - 0.1, k.w(8)) * (1 - e), size=120,
             cols=("#ffffff", "#ffe04a", "#ffffff", "#ff3d3d"))
    return z, hx, lerp(hy + 150, hy + 20, e), 0, draw


def s3(k):  # dentro de la cabeza: el cerebro apaga PERFUME
    def draw(c):
        head_inside(c, k.t)
        brain(c, 540, 1060, 1.2, k.t)
        switch(c, 540, 1440, 1.0, 1 - prog(k.lt, k.w(6), k.w(8)), "PERFUME")
    e = ease_out(clamp(k.lt / 0.8))
    big_text(["ADAPTACIÓN"], 520, prog(k.lt, k.w(2) - 0.1, k.w(2) + 0.3), size=130, cols=("#ffe04a",), rot=-2)
    big_text(["OLFATIVA"], 670, prog(k.lt, k.w(3) - 0.1, k.w(3) + 0.3), size=130, rot=-2)
    return punch(k, (8,), lerp(2.4, 1.0, e)), 540, 1050, 0, draw


def s4(k):  # cronómetro: la mitad en 2 minutos
    sec = 120 * ease_in_out(prog(k.lt, k.w(9) - 0.3, k.w(17)))

    def draw(c):
        stopwatch_scene(c, k.t, sec)
    big_text(["POCAS", "RESPIRACIONES"], 560, prog(k.lt, k.w(7) - 0.1, k.w(8) + 0.3) * (1 - prog(k.lt, k.w(11), k.w(12) - 0.1)),
             size=110, cols=("#ffffff", "#ffffff"))
    big_text(["LA", "MITAD", "EN", "2", "MIN"], 560, prog(k.lt, k.w(12) - 0.1, k.w(17) + 0.2), size=110,
             cols=("#ffffff", "#ff3d3d", "#ffffff", "#ff3d3d", "#ffffff"))
    z = lerp(1.15, 1.0, ease_out(clamp(k.lt / 0.6)))
    return punch(k, (9, 12, 16), z), 540, 1060, 2 * math.sin(k.lt * 1.3), draw


def s5(k):  # cocina: el cerebro te protege para detectar gas o humo
    al = prog(k.lt, k.w(13) - 0.1, k.w(13) + 0.1)

    def draw(c):
        kitchen(c, k.t, al)
        person(c, k, 400, FEET, HS, [(0, "neutral"), (k.w(13), "espera")], talk=False)
    big_text(["TE", "PROTEGE"], 560, prog(k.lt, k.w(5) - 0.1, k.w(5) + 0.4) * (1 - prog(k.lt, k.w(12), k.w(13))), size=140,
             cols=("#2f6bff", "#ffffff"))
    big_text(["¡GAS!"], 600, al, size=200, cols=("#ff3d3d",), shake=6 * al)
    z, fx, fy, r = cam_basic(k, 1.0, 1.12, 520, 580, 1000, 1060)
    return punch(k, (13,), z), fx, fy, r, draw


def s6(k):  # oficina: vos no te olés, pero los demás sí
    wk = ease_out(prog(k.lt, 0.1, k.w(6)))

    def draw(c):
        office(c, k.t)
        person(c, k, 330, FEET, HS, [(0, "neutral")])
        px = lerp(1300, 820, wk)
        person(c, k, px, FEET, HS, [(0, "neutral"), (k.w(6), "enamorado")], style=M.STYLES["P3"], walk=1 - wk)
        if k.lt > k.w(6):
            for i in range(4):
                u = ((k.t * 0.6 + i / 4) % 1)
                heart(c, px + 60 + 40 * math.sin(u * 6 + i), FEET - 980 - u * 260, 1.4, 1 - u)
    big_text(["VOS", "NO", "TE", "OLÉS"], 520, prog(k.lt, k.w(2) - 0.1, k.w(5) + 0.2), size=110, stroke="#2f6bff")
    big_text(["LOS", "DEMÁS", "SÍ"], 680, prog(k.lt, k.w(7) - 0.1, k.w(9) + 0.3), size=140, cols=("#ff3d6a", "#ff3d6a", "#ffe04a"))
    z, fx, fy, r = cam_basic(k, 1.0, 1.1, 480, 620, 1050, 1050)
    return z, fx, fy, r, draw


def s7(k):  # fiesta: te echás más y más (error)
    def draw(c):
        party(c, k.t)
        e = prog(k.lt, k.w(8), k.w(11) + 0.8)
        for x, st in ((150, "P1"), (930, "P2"), (40, "P4")):
            dx = (-1 if x < 540 else 1) * 600 * e
            person(c, k, x + dx, FEET + 60, 0.62, [(0, "neutral" if e < 0.05 else "encoge")], style=M.STYLES[st],
                   walk=min(1, e * 3))
        person(c, k, 540, FEET, HS, [(0, "sostiene"), (k.w(11) + 0.4, "espera")], hold_fn=hold_decant(k.t))
        for j, wi in enumerate((6, 7, 9, 11)):
            mist(c, 700, 760, k.w(wi), k.lt, n=30 + j * 14, size=1 + j * 0.5, col="#fff0d0")
        fog = prog(k.lt, k.w(7), k.w(11) + 0.5)
        if fog > 0:
            c.drawRect(RECT(-600, -600, 1700, 2600), P("#f4e8c8", alpha=0.3 * fog))
    big_text(["ERROR"], 560, prog(k.lt, k.w(4) - 0.1, k.w(4) + 0.3) * (1 - prog(k.lt, k.w(7) - 0.3, k.w(7) - 0.1)),
             size=180, cols=("#ff3d3d",), shake=4)
    big_text(["MÁS"], 560, prog(k.lt, k.w(7), k.w(7) + 0.3) * (1 - prog(k.lt, k.w(9) - 0.1, k.w(9))), size=170)
    big_text(["MÁS", "Y", "MÁS"], 560, prog(k.lt, k.w(9), k.w(11) + 0.3), size=160, cols=("#ffe04a", "#ffffff", "#ff3d3d"))
    z, fx, fy, r = cam_basic(k, 1.0, 1.2, 540, 560, 1050, 980)
    return punch(k, (6, 7, 9, 11), z), fx, fy, 2 * math.sin(k.lt * 4) * prog(k.lt, k.w(9), k.D), draw


def s8(k):  # cafetería: oler café es un mito
    def draw(c):
        cafe(c, k.t)
        coffee_bag(c, 330, 1240, 1.0)
        person(c, k, 800, FEET, HS, [(0, "piensa"), (k.w(6), "encoge")], talk=False)
    mk = prog(k.lt, k.w(6) - 0.1, k.w(6) + 0.3)
    big_text(["¿OLER", "CAFÉ?"], 560, prog(k.lt, k.w(2) - 0.1, k.w(5)) * (1 - mk), size=130, cols=("#ffffff", "#ffd04a"))
    big_text(["MITO"], 600, mk, size=220, cols=("#ff3d3d",), rot=-8)
    z, fx, fy, r = cam_basic(k, 1.15, 1.0, 420, 560, 1100, 1000)
    return punch(k, (6,), z), fx, fy, r, draw


def s9(k):  # parque: lo que sí ayuda (tres consejos)
    def draw(c):
        park(c, k.t)
        person(c, k, 700, FEET, HS, [(0, "neutral"), (k.w(10), "celebra"), (k.w(15), "pulgar")], talk=False)
    tips = [(4, "OLÉ TU PIEL", "#2fbf71"), (10, "AIRE FRESCO", "#2f9ad8"), (15, "PREGUNTÁ", "#ff8a1a")]
    for i, (wi, txt, col) in enumerate(tips):
        nxt = tips[i + 1][0] if i + 1 < 3 else None
        kk = prog(k.lt, k.w(wi) - 0.1, k.w(wi) + 0.3)
        if nxt is not None:
            kk *= 1 - prog(k.lt, k.w(nxt) - 0.25, k.w(nxt) - 0.05)
        big_text([f"{i + 1}.", txt], 580, kk, size=130, cols=(col, "#ffffff"))
    big_text(["LO", "QUE", "SÍ", "AYUDA"], 580, prog(k.lt, 0.0, 0.4) * (1 - prog(k.lt, k.w(4) - 0.25, k.w(4) - 0.05)), size=120,
             cols=("#ffffff", "#ffffff", "#2fbf71", "#ffffff"))
    z, fx, fy, r = cam_basic(k, 1.1, 1.0, 600, 580, 1100, 1000)
    return punch(k, (4, 10, 15), z), fx, fy, r, draw


def s10(k):  # tocador: rotar perfumes (carrusel de decants)
    def draw(c):
        vanity(c, k.t)
        for i in range(6):
            a = (i - 2.5) * 0.9 + k.lt * 0.7
            x = 540 + math.sin(a) * 380
            depth = math.cos(a)
            if depth < -0.2:
                continue
            color_decant(c, x, 1200 - 20 * depth, 230 + 120 * depth, DEC_COLS[i], k.t)
    big_text(["ROTÁ", "TUS", "PERFUMES"], 580, prog(k.lt, k.w(5) - 0.1, k.w(6) + 0.3), size=120, cols=("#ff3d9a", "#ffffff", "#ff3d9a"))
    z, fx, fy, r = cam_basic(k, 1.05, 1.12, 540, 540, 1050, 1120)
    return punch(k, (5,), z), fx, fy, 1.5 * math.sin(k.lt), draw


def s11(k):  # tienda Otto Aleman: decants 5 y 10 ml
    def draw(c):
        store(c, k.t)
        store_logo(c)
        person(c, k, 860, FEET, HS, [(0, "saludo"), (k.w(9), "señala")])
        d5 = prog(k.lt, k.w(9) - 0.2, k.w(9) + 0.2)
        d10 = prog(k.lt, k.w(11) - 0.2, k.w(11) + 0.2)
        if d5 > 0:
            decant(c, 220, lerp(1900, 1350, back_out(d5, 1.3)), 300, -4, k.t, 0.7)
        if d10 > 0:
            decant(c, 470, lerp(1900, 1320, back_out(d10, 1.3)), 380, 4, k.t, 0.7)
    big_text(["OTTO", "ALEMAN"], 640, prog(k.lt, k.w(3) - 0.1, k.w(4) + 0.3) * (1 - prog(k.lt, k.w(8), k.w(9) - 0.2)), size=130,
             cols=("#ffd04a",))
    big_text(["5", "ML"], 700, prog(k.lt, k.w(9) - 0.1, k.w(9) + 0.3), size=100, x=240, rot=-4)
    big_text(["10", "ML"], 700, prog(k.lt, k.w(11) - 0.1, k.w(11) + 0.3), size=100, x=520, rot=4)
    e = ease_out(clamp(k.lt / 1.0))
    return punch(k, (3, 9, 11), lerp(1.3, 1.0, e)), lerp(540, 560, e), lerp(760, 1000, e), 0, draw


def s12(k):  # Black Friday 3x2
    def draw(c):
        black_friday(c, k.t)
        for i in range(2):
            dk = prog(k.lt, k.w(11) - 0.2 + i * 0.25, k.w(11) + 0.2 + i * 0.25)
            if dk > 0:
                color_decant(c, 250 + i * 200, lerp(1900, 1360, back_out(dk, 1.3)), 300, DEC_COLS[i], k.t, (-6, 6)[i])
        fk = prog(k.lt, k.w(16) - 0.2, k.w(17))
        if fk > 0:
            c.drawString("+", 600, 1380, F(R.RES.xbold, 110), P("#2fbf71", alpha=fk))
            color_decant(c, 820, lerp(1900, 1360, back_out(fk, 1.3)), 300, DEC_COLS[2], k.t, 8)
        if k.lt > k.w(17):
            r = rng(3)
            for i in range(60):
                x = r.random() * W
                y = -50 + ((k.lt - k.w(17)) * (400 + 400 * r.random()) + r.random() * 200)
                if y > H:
                    continue
                c.save()
                c.translate(x, y)
                c.rotate(k.t * 200 + i * 30)
                c.drawRect(RECT(-11, -6, 11, 6), P(["#d6a24a", "#e0203a", "#2fbf71", "#ffffff"][i % 4]))
                c.restore()
    big_text(["BLACK", "FRIDAY"], 540, prog(k.lt, k.w(5) - 0.2, k.w(6) + 0.2), size=150, cols=("#ffffff", "#ffd04a"), stroke="#e0203a")
    big_text(["3x2"], 860, prog(k.lt, k.w(7) - 0.1, k.w(9) + 0.1), size=280, cols=("#ffd04a",), rot=0)
    big_text(["¡GRATIS!"], 1110, prog(k.lt, k.w(17) - 0.1, k.w(17) + 0.3), size=110, cols=("#2fbf71",), x=820, rot=6)
    z = lerp(1.1, 1.0, ease_out(clamp(k.lt / 0.8)))
    return punch(k, (5, 7, 11, 17), z), 540, 1000, 1.0 * math.sin(k.lt * 2), draw


def s13(k):  # vuelve al cuarto: no hagas esto con tu perfume
    def draw(c):
        bedroom(c, k.t)
        person(c, k, 600, FEET, HS, [(0, "señala"), (k.w(4), "sostiene")], hold_fn=hold_decant(k.t))
    big_text(["NO", "HAGAS", "ESTO"], 580, prog(k.lt, k.w(4) - 0.1, k.w(6) + 0.3), size=140, cols=("#ffffff", "#ff3d3d", "#ffffff"),
             stroke="#e0203a")
    z, fx, fy, r = cam_basic(k, 1.0, 1.15, 560, 600, 1000, 1030)
    return z, fx, fy, r, draw


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13]
WHIP = {1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}


def render_scene(c, si, k):
    OVER.clear()
    z, fx, fy, rot, draw = SCENES[si](k)
    c.save()
    c.translate(540, 960)
    c.rotate(rot)
    c.scale(z, z)
    c.translate(-fx, -fy)
    draw(c)
    c.restore()


def render_frame(c, t, vo, phr, total):
    D.VO = vo
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(R.hexc("#000000"))
    loop_t = vo[-1]["tokens"][-1]["e"] + 0.2
    if t >= loop_t:  # bucle: vuelve exactamente al primer cuadro
        render_scene(c, 0, R.Ctx(vo, 0, 0.0))
        OVER.clear()
    else:
        k = R.Ctx(vo, si, t)
        lt = k.lt
        blur, dx = 0.0, 0.0
        if si in WHIP and lt < 0.22:  # barrido rápido de un lugar al otro
            q = 1 - ease_out(lt / 0.22)
            blur, dx = 70 * q, 300 * q
        if blur > 0.3:
            p = skia.Paint()
            p.setImageFilter(skia.ImageFilters.Blur(blur, blur * 0.06, skia.TileMode.kClamp))
            c.saveLayer(None, p)
        c.save()
        c.translate(dx, 0)
        render_scene(c, si, k)
        c.restore()
        if blur > 0.3:
            c.restore()
        if si == 2 and lt > k.D - 0.25:  # entra a la cabeza
            c.drawRect(RECT(0, 0, W, H), P("#2a1a90", alpha=(lt - (k.D - 0.25)) / 0.25))
        for fn in OVER:
            fn(c)
    R.vignette(c, 0.25)
    draw_subs(c, t, phr)
    draw_watermark(c)


def draw_subs(c, t, phr):
    """Subtítulos abajo, sin cuadro: blancos con borde, palabra actual en amarillo."""
    f = F(R.RES.xbold, 54)
    for p in phr:
        if not (p["s"] <= t < p["e"]):
            continue
        lines, line, wsum = [], [], 0
        for w in p["words"]:
            ww = f.measureText(w["w"] + " ")
            if wsum + ww > 900 and line:
                lines.append(line)
                line, wsum = [], 0
            line.append(w)
            wsum += ww
        lines.append(line)
        top = 1680 - (len(lines) - 1) * 66
        for li, ln in enumerate(lines):
            lw = sum(f.measureText(w["w"] + " ") for w in ln)
            x = 540 - lw / 2
            y = top + li * 66
            for w in ln:
                cur = w["s"] - 0.03 <= t < w["e"] + 0.05
                sp = P(INK, "stroke", 12)
                sp.setStrokeJoin(skia.Paint.kRound_Join)
                c.drawString(w["w"], x, y, f, sp)
                c.drawString(w["w"], x, y, f, P("#ffe04a" if cur else "#ffffff"))
                x += f.measureText(w["w"] + " ")


def draw_watermark(c):
    f = F(R.RES.semi, 28)
    txt = "@ottoaleman.perfumesgt"
    w = f.measureText(txt)
    c.drawString(txt, 540 - w / 2, 1810, f, P(INK, "stroke", 6, alpha=0.6))
    c.drawString(txt, 540 - w / 2, 1810, f, P("#ffffff", alpha=0.9))


class NRes(R.Res):
    def __init__(self):
        super().__init__()
        self.cloud = R.sprite(255, 255, 255, n=96, power=1.25)


def install():
    R.Res = NRes
    R.SCENES = SCENES
    R.render_frame = render_frame
    R.draw_subs = draw_subs
    R.draw_watermark = draw_watermark


if __name__ == "__main__":
    install()
    R.main()
