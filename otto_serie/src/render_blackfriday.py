"""Otto Aleman Perfumes — "¡Esto SÍ son ofertas!" Black Friday… ¡NAVIDEÑO! 3x2 en decants. En bucle. Voz David.

Escenarios: tienda gris de "oferta falsa" que se rompe como vidrio, calle de noche con neón y luces navideñas,
grito NAVIDEÑO con letras rojas y verdes y foquitos, tienda Otto Aleman decorada (árbol, guirnaldas, regalos)
con el personaje A en el mostrador, 3x2 dorado, mesa vista desde arriba con sello GRATIS, carrusel desierto /
pasarela / teléfono con los perfumes reales, 5 y 10 ml contra frasco completo, "corré que vuela", comentarios.
Uso:
  VIDEO_BUILD=$PWD/otto_serie/build_bf VO_TRIM=0.15 VO_GAP=0.22 VO_TAIL=0.6 \
    python3 otto_serie/src/render_blackfriday.py --out otto_serie/build_bf/video_mudo.mp4
"""
import math
import os
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "velto", "src"))
import render_nariz as N  # noqa: E402
import render_elixir as EL  # noqa: E402
import render_ep2 as E2  # noqa: E402
import bottles_bf as B  # noqa: E402
from render_decant_tarde import (R, P, lin, rad, oval, rrect, clamp, lerp, smooth, ease_out, ease_in_out, back_out,  # noqa: E402
                                 prog, rng, glow, text_center, W, H, RECT, F, M, OVER)
from render_nariz import person, big_text, punch, color_decant, INK, FEET, wall_floor, heart  # noqa: E402

A = M.STYLES["A"]
S = M.STYLES
RED, GREEN, GOLD = "#e8203a", "#1fa64a", "#ffd04a"
HS = 0.8
CROWD = ["M1", "P2", "M2", "P3", "M3", "P4", "M4", "P1"]


# ----------------------------------------------------------------------------
# Navidad: foquitos, guirnaldas, árbol, regalos, nieve
# ----------------------------------------------------------------------------
BULBS = [RED, GREEN, GOLD, "#3aa0ff", "#ff6ad0"]


def bulb(c, x, y, r, col, t, i):
    on = 0.55 + 0.45 * math.sin(t * 6 + i * 1.7)
    glow(c, R.RES.glow_white, x, y, r * 4, 0.25 * on)
    oval(c, x, y, r, r * 1.25, P(col, shader=rad(x - r * 0.3, y - r * 0.4, r * 1.6, [M.mix(col, "#ffffff", 0.6 * on), col])))
    rrect(c, x - r * 0.45, y - r * 1.6, x + r * 0.45, y - r * 1.0, 2, P("#5a5a5a"))


def garland(c, x0, x1, y, sag, t, n=14, r=11):
    p = skia.Path()
    p.moveTo(x0, y)
    p.quadTo((x0 + x1) / 2, y + sag * 2, x1, y)
    c.drawPath(p, P("#1a5a2a", "stroke", 22))
    c.drawPath(p, P("#2f8a3a", "stroke", 10))
    for i in range(n):
        u = (i + 0.5) / n
        bx = lerp(x0, x1, u)
        by = y + sag * 4 * u * (1 - u) + 16
        bulb(c, bx, by, r, BULBS[i % len(BULBS)], t, i)


def xmas_tree(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, 0, 200, 26, P("#000000", alpha=0.3))
    rrect(c, -30, -90, 30, 0, 6, P("#6a3a1a"))
    for i, (w, y0, y1) in enumerate([(230, -90, -330), (190, -250, -480), (140, -400, -610), (90, -530, -720)]):
        p = skia.Path()
        p.moveTo(-w, y0)
        p.quadTo(0, y0 + 30, w, y0)
        p.lineTo(0, y1)
        p.close()
        c.drawPath(p, P("#1f8a3a", shader=lin(-w, 0, w, 0, ["#0f5a24", "#2fae4a", "#1a7a34"])))
    # cadena de foquitos en espiral
    for i in range(26):
        u = i / 26
        yy = lerp(-110, -680, u)
        ww = lerp(210, 50, u)
        bulb(c, ww * math.sin(u * 14), yy, 11, BULBS[i % 5], t, i)
    # estrella
    st = skia.Path()
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = 60 if i % 2 == 0 else 26
        (st.moveTo if i == 0 else st.lineTo)(math.cos(a) * rr, -740 + math.sin(a) * rr)
    st.close()
    glow(c, R.RES.glow_gold, 0, -740, 160, 0.6 + 0.2 * math.sin(t * 4))
    c.drawPath(st, P(GOLD))
    c.restore()


def gift(c, x, y, w, h, col, rib=GOLD):
    rrect(c, x - w / 2, y - h, x + w / 2, y, 6, P(col, shader=lin(x - w / 2, 0, x + w / 2, 0, [M.mix(col, "#ffffff", 0.2), col, M.mix(col, "#000000", 0.25)])))
    c.drawRect(RECT(x - w * 0.08, y - h, x + w * 0.08, y), P(rib))
    rrect(c, x - w / 2 - 6, y - h - 4, x + w / 2 + 6, y - h + h * 0.18, 4, P(M.mix(col, "#000000", 0.1)))
    c.drawRect(RECT(x - w * 0.08, y - h - 4, x + w * 0.08, y - h + h * 0.18), P(rib))
    for sd in (-1, 1):
        oval(c, x + sd * w * 0.16, y - h - 16, w * 0.16, 14, P(rib, "stroke", 8))


def snow(c, t, n=70, seed=5, speed=120, area=(-300, 1400)):
    r = rng(seed)
    for i in range(n):
        x = lerp(*area, r.random()) + 30 * math.sin(t + i)
        y = (r.random() * 2400 + t * speed * (0.6 + r.random())) % 2400 - 300
        oval(c, x, y, 4 + 6 * r.random(), 4 + 6 * r.random(), P("#ffffff", alpha=0.75))


def xmas_text(word, y, k, size=200, x=540, rot=-4):
    """¡NAVIDEÑO! con letras rojas y verdes, borde blanco y dorado, foquitos alrededor y nieve encima."""
    if k <= 0:
        return

    def d(c):
        f = F(R.RES.xbold, size)
        tot = f.measureText(word)
        sc = min(1.0, 1000 / tot)
        c.save()
        c.translate(x, y)
        c.rotate(rot + 3 * math.sin(k * 20) * (1 - clamp(k)))
        c.scale(sc * back_out(clamp(k / 0.5), 2.6), sc * back_out(clamp(k / 0.5), 2.6))
        xx = -tot / 2
        # foquitos arriba y abajo
        for row, yy in ((0, -size * 0.92), (1, size * 0.28)):
            p = skia.Path()
            p.moveTo(-tot / 2 - 30, yy)
            for j in range(6):
                p.quadTo(-tot / 2 + (j + 0.5) * (tot + 60) / 6 - 30, yy + 34, -tot / 2 + (j + 1) * (tot + 60) / 6 - 30, yy)
            c.drawPath(p, P("#1a5a2a", "stroke", 8))
            for j in range(16):
                bx = -tot / 2 - 20 + j * (tot + 40) / 15
                bulb(c, bx, yy + 20, 14, BULBS[(j + row) % 5], k * 3 + row, j)
        for i, ch in enumerate(word):
            ww = f.measureText(ch)
            bounce = -14 * abs(math.sin(k * 8 + i * 0.7))
            col = RED if i % 2 == 0 else GREEN
            c.drawString(ch, xx + 10, 12 + bounce, f, P("#000000", alpha=0.35, blur=8))
            sp = P(GOLD, "stroke", size * 0.2)
            sp.setStrokeJoin(skia.Paint.kRound_Join)
            c.drawString(ch, xx, bounce, f, sp)
            sp = P("#ffffff", "stroke", size * 0.1)
            sp.setStrokeJoin(skia.Paint.kRound_Join)
            c.drawString(ch, xx, bounce, f, sp)
            c.drawString(ch, xx, bounce, f, P(col, shader=lin(0, -size * 0.7 + bounce, 0, bounce,
                                                              [M.mix(col, "#ffffff", 0.35), col])))
            oval(c, xx + ww * 0.5, -size * 0.7 + bounce, ww * 0.38, 12, P("#ffffff"))   # nieve encima
            xx += ww
        c.restore()
    OVER.append(d)


def neon_text(words, y, k, t, size=150, col="#ff2a6a", x=540, rot=-3):
    if k <= 0:
        return

    def d(c):
        f = F(R.RES.xbold, size)
        flick = 1.0 if (int(t * 9) % 7) else 0.35
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        for li, w in enumerate(words):
            ww = f.measureText(w)
            yy = li * size * 1.0
            a = clamp(k * 2 - li * 0.4) * flick
            if a <= 0:
                continue
            for bw, al in ((40, 0.25), (18, 0.5)):
                c.drawString(w, -ww / 2, yy, f, P(col, "stroke", bw, alpha=al * a, blur=bw * 0.6))
            c.drawString(w, -ww / 2, yy, f, P(col, "stroke", 8, alpha=a))
            c.drawString(w, -ww / 2, yy, f, P("#ffffff", alpha=0.95 * a))
        c.restore()
    OVER.append(d)


def gold3d(word, y, k, size=330, x=540, rot=-5):
    """Texto dorado 3D con sombra larga (para el 3x2)."""
    if k <= 0:
        return

    def d(c):
        f = F(R.RES.xbold, size)
        ww = f.measureText(word)
        s = back_out(clamp(k / 0.45), 2.2)
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.scale(s, s)
        for i in range(40, 0, -2):                     # sombra larga
            c.drawString(word, -ww / 2 + i * 1.6, i * 1.6, f, P("#000000", alpha=0.035))
        for i in range(16, 0, -1):                     # extrusión
            c.drawString(word, -ww / 2 + i * 0.8, i * 1.1, f, P("#8a5a10"))
        sp = P("#5a3a08", "stroke", 14)
        sp.setStrokeJoin(skia.Paint.kRound_Join)
        c.drawString(word, -ww / 2, 0, f, sp)
        c.drawString(word, -ww / 2, 0, f, P(GOLD, shader=lin(0, -size * 0.75, 0, 0, ["#fff6c0", "#ffd04a", "#d08a10", "#ffe080"], [0, .4, .75, 1])))
        sh = (k * 1.5 % 2.0) - 0.5                       # destello que cruza
        c.save()
        c.clipRect(RECT(-ww / 2, -size, ww / 2, 20))
        c.drawRect(RECT(-ww / 2 + sh * ww - 60, -size, -ww / 2 + sh * ww, 20), P("#ffffff", alpha=0.0))
        c.restore()
        c.restore()
    OVER.append(d)


def stamp(word, x, y, k, col=GREEN, size=110, rot=-12):
    if k <= 0:
        return

    def d(c):
        s = lerp(2.6, 1.0, ease_out(clamp(k / 0.25)))
        f = F(R.RES.xbold, size)
        ww = f.measureText(word)
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.scale(s, s)
        a = clamp(k / 0.15)
        rrect(c, -ww / 2 - 40, -size * 0.95, ww / 2 + 40, size * 0.35, 24, P(col, "stroke", 14, alpha=a))
        rrect(c, -ww / 2 - 26, -size * 0.83, ww / 2 + 26, size * 0.23, 16, P(col, alpha=0.22 * a))
        c.drawString(word, -ww / 2, 0, f, P(col, alpha=a))
        c.restore()
    OVER.append(d)


def confetti(c, t0, lt, seed=3, n=70, x0=0, x1=W):
    if lt < t0:
        return
    r = rng(seed)
    for i in range(n):
        x = lerp(x0, x1, r.random()) + 40 * math.sin(lt * 3 + i)
        y = -80 + (lt - t0) * (500 + 500 * r.random()) + r.random() * 300 - 300
        if y > H + 600:
            continue
        c.save()
        c.translate(x, y)
        c.rotate((lt * 300 + i * 40))
        c.drawRect(RECT(-12, -6, 12, 6), P([GOLD, RED, GREEN, "#ffffff", "#3aa0ff"][i % 5]))
        c.restore()


def logo_on_wall(c, x, y, w=230, a=1.0):
    img = M.logo()
    h = w * img.height() / img.width()
    glow(c, R.RES.glow_warm, x, y, w * 1.1, 0.5 * a)
    c.drawImageRect(img, RECT(x - w / 2, y - h / 2, x + w / 2, y + h / 2), R.SAMP, skia.Paint())


# ----------------------------------------------------------------------------
# escenarios
# ----------------------------------------------------------------------------


def gray_store(c, t):
    """La 'oferta' falsa: tienda gris, cartel -5%, foco que parpadea, señor aburrido."""
    wall_floor(c, ("#9a9a9e", "#7a7a80"), ("#6a6a70", "#4a4a50"), y=1450)
    flick = 0.6 + 0.4 * (1 if int(t * 5) % 9 else 0)
    oval(c, 540, 120, 260, 60, P("#ffffff", alpha=0.15 * flick))
    c.drawRect(RECT(300, 90, 780, 110), P("#d8d8d8", alpha=flick))
    for row in range(2):
        y = 1000 + row * 200
        c.drawRect(RECT(40, y, 1040, y + 18), P("#5a5a60"))
        for i in range(7):
            rrect(c, 80 + i * 140, y - 110, 140 + i * 140, y, 8, P("#8a8a90"))
    c.save()
    c.translate(540, 520)
    c.rotate(-4 + 2 * math.sin(t * 1.3))
    c.drawLine(-120, -260, -120, -150, P("#4a4a4a", "stroke", 5))
    c.drawLine(120, -260, 120, -150, P("#4a4a4a", "stroke", 5))
    rrect(c, -230, -150, 230, 150, 10, P("#d8d8d0"))
    rrect(c, -230, -150, 230, 150, 10, P("#5a5a5a", "stroke", 6))
    text_center(c, "OFERTA", 0, -70, F(R.RES.bold, 60), P("#6a6a6a"))
    text_center(c, "-5%", 0, 90, F(R.RES.xbold, 150), P("#7a7a7a"))
    c.restore()
    rrect(c, -100, 1380, 1180, 1450, 8, P("#5a5a60"))


GRAY = dict(S["P1"], jacket="#8a8a8a", shirt="#8a8a8a", pants="#5a5a5a", shoes="#4a4a4a", hair="#4a4a4a",
            skin=("#c8c0b8", "#a8a098"))


def xmas_store(c, t, tree_x=900, counter=True, logo=True):
    """Tienda Otto Aleman decorada de Navidad."""
    wall_floor(c, ("#3a1418", "#1a0a0c"), ("#4a2a1a", "#1a0e08"), y=1450)
    # estantes con frascos de colores
    for row in range(3):
        y = 900 + row * 170
        c.drawRect(RECT(-200, y, 1300, y + 18), P("#d6a24a"))
        for i in range(12):
            col = ["#ffb04a", "#c8402a", "#7ad0ff", "#b08aff", "#e0a060", "#ff6aa8"][(i + row) % 6]
            x = -160 + i * 125
            rrect(c, x, y - 100, x + 56, y, 12, P(col, alpha=0.9))
            c.drawRect(RECT(x + 16, y - 128, x + 40, y - 100), P("#d6a24a"))
    garland(c, -200, 560, 230, 60, t, 12)
    garland(c, 520, 1300, 230, 60, t + 1, 12)
    if logo:
        logo_on_wall(c, 540, 470)
    xmas_tree(c, tree_x, 1450, 0.95, t)
    for gx, col in ((tree_x - 170, RED), (tree_x + 160, GREEN), (tree_x - 40, "#3aa0ff")):
        gift(c, gx, 1450, 110, 90, col)
    if counter:
        rrect(c, -200, 1440, 1300, 1500, 10, P("#d6a24a"))
        c.drawRect(RECT(-200, 1500, 1300, 2100), P("#2a1a14", shader=lin(0, 1500, 0, 2000, ["#3a2418", "#120a06"])))
        garland(c, -200, 1300, 1510, 30, t + 2, 20, 9)


def night_street(c, t, camx):
    c.drawRect(RECT(-1200, -600, 3600, 2600), P("#0a0a20", shader=lin(0, -600, 0, 1500, ["#05051a", "#1a1040", "#3a1a40"])))
    snow(c, t, 60, 9, 90, (-1000, 3200))
    r = rng(4)
    for i in range(12):  # edificios del fondo con parallax
        bx = -1200 + i * 380 + camx * 0.4
        bh = 500 + r.random() * 500
        c.drawRect(RECT(bx, 1250 - bh, bx + 340, 1500), P("#141430"))
        for wy in range(int(1250 - bh) + 40, 1400, 90):
            for wx in range(3):
                if r.random() > 0.4:
                    c.drawRect(RECT(bx + 40 + wx * 100, wy, bx + 90 + wx * 100, wy + 45), P("#ffd88a", alpha=0.5))
    # fachada de la tienda
    c.drawRect(RECT(80, 520, 1000, 1500), P("#2a1418"))
    rrect(c, 160, 900, 920, 1480, 14, P("#ffcf80", shader=lin(0, 900, 0, 1480, ["#ffe0a0", "#e89a40"])))  # vitrina iluminada
    for i in range(9):
        rrect(c, 200 + i * 80, 1200, 240 + i * 80, 1290, 8, P(["#ffb04a", "#c8402a", "#7ad0ff", "#b08aff"][i % 4]))
    xmas_tree(c, 820, 1460, 0.4, t)
    garland(c, 80, 1000, 540, 40, t, 16, 12)
    garland(c, 160, 920, 890, 30, t + 0.5, 12, 10)
    logo_on_wall(c, 540, 690, 200)
    c.drawRect(RECT(-1200, 1500, 3600, 2600), P("#1a1a28"))
    c.drawRect(RECT(-1200, 1490, 3600, 1510), P("#3a3a50"))


def table_top(c, t):
    c.drawRect(RECT(-800, -800, 1900, 2700), P("#8a5a34", shader=lin(-800, 0, 1900, 0, ["#7a4a28", "#a8703e", "#8a5a34"])))
    for i in range(-8, 20):
        c.drawLine(-800, i * 140, 1900, i * 140 + 30, P("#6a3e20", "stroke", 4, alpha=0.5))
    # mantel navideño
    rrect(c, 60, 560, 1020, 1560, 30, P(RED))
    for i in range(12):
        c.drawLine(60 + i * 80, 560, 60 + i * 80, 1560, P("#ffffff", "stroke", 6, alpha=0.18))
        c.drawLine(60, 560 + i * 85, 1020, 560 + i * 85, P("#ffffff", "stroke", 6, alpha=0.18))
    # bastones y esferas de adorno
    for (x, y, col) in ((150, 400, GOLD), (960, 420, GREEN), (130, 1700, "#3aa0ff"), (950, 1720, GOLD)):
        oval(c, x + 10, y + 14, 60, 60, P("#000000", alpha=0.25, blur=8))
        oval(c, x, y, 60, 60, P(col, shader=rad(x - 20, y - 20, 90, [M.mix(col, "#ffffff", 0.6), col])))


def desert(c, t, x0):
    c.save()
    c.translate(x0, 0)
    c.drawRect(RECT(-200, -600, 1300, 2600), P("#ffb04a", shader=lin(0, -600, 0, 1400, ["#ff7a3a", "#ffc070", "#ffe0a0"])))
    glow(c, R.RES.glow_warm, 760, 520, 300, 0.8)
    oval(c, 760, 520, 110, 110, P("#fff0c0"))
    for i, (yy, col) in enumerate(((1250, "#e8a050"), (1380, "#d88a3a"), (1520, "#c8782a"))):
        p = skia.Path()
        p.moveTo(-200, yy)
        for j in range(5):
            p.quadTo(-50 + j * 320, yy - 120 + 40 * i, 110 + j * 320, yy)
        p.lineTo(1300, 2600)
        p.lineTo(-200, 2600)
        p.close()
        c.drawPath(p, P(col))
    c.restore()


def runway(c, t, x0):
    c.save()
    c.translate(x0, 0)
    c.drawRect(RECT(-200, -600, 1300, 2600), P("#100818", shader=rad(540, 900, 1200, ["#3a1a50", "#08040c"])))
    pr = skia.Path()
    pr.moveTo(420, 700)
    pr.lineTo(660, 700)
    pr.lineTo(1100, 2000)
    pr.lineTo(-20, 2000)
    pr.close()
    c.drawPath(pr, P("#e8e0f0", shader=lin(0, 700, 0, 2000, ["#4a3a5a", "#e8e0f0"])))
    r = rng(int(t * 6))
    for i in range(14):  # flashes del público
        side = -1 if i % 2 else 1
        fx = 540 + side * (380 + 120 * (i % 3)) + 30 * math.sin(i)
        fy = 800 + i * 80
        if r.random() > 0.65:
            glow(c, R.RES.glow_white, fx, fy, 120, 0.9)
        oval(c, fx, fy + 60, 40, 50, P("#1a1024"))
    c.restore()


def phone_world(c, t, x0):
    c.save()
    c.translate(x0, 0)
    c.drawRect(RECT(-200, -600, 1300, 2600), P("#ff5a9a", shader=lin(0, -600, 0, 2000, ["#7a3aff", "#ff5a9a", "#ffb04a"])))
    rrect(c, 160, 420, 920, 1640, 70, P("#111116"))
    rrect(c, 184, 444, 896, 1616, 54, P("#fdf6ff"))
    rrect(c, 470, 464, 610, 494, 15, P("#111116"))
    for i in range(10):
        hx = 200 + (i * 173) % 720
        hy = 1600 - ((t * 260 + i * 190) % 1300)
        heart(c, hx, hy, 1.6, 0.9, ["#ff3d6a", "#ff7ab0", RED][i % 3])
    c.restore()


def studio(c, t, col1="#ffd9e8", col2="#ffb0c8"):
    c.drawRect(RECT(-600, -600, 1700, 2600), P(col1, shader=rad(540, 800, 1300, [col1, col2])))
    c.drawRect(RECT(-600, 1450, 1700, 2600), P(col2, shader=lin(0, 1450, 0, 2000, [M.mix(col2, "#000000", 0.1), M.mix(col2, "#000000", 0.35)])))


def long_shadow(c, x, y, w, h, a=0.25):
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.lineTo(x + w / 2, y)
    p.lineTo(x + w / 2 + h * 0.9, y - 30)
    p.lineTo(x - w / 2 + h * 0.9, y - 30)
    p.close()
    c.drawPath(p, P("#000000", alpha=a, blur=10))


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def shards():
    r = rng(11)
    cols, rows = 5, 8
    pts = {}
    for i in range(cols + 1):
        for j in range(rows + 1):
            jx = 0 if i in (0, cols) else (r.random() - 0.5) * 120
            jy = 0 if j in (0, rows) else (r.random() - 0.5) * 120
            pts[i, j] = (-300 + i * 1680 / cols + jx, -400 + j * 2700 / rows + jy)
    out = []
    for i in range(cols):
        for j in range(rows):
            a, b, cc, d = pts[i, j], pts[i + 1, j], pts[i + 1, j + 1], pts[i, j + 1]
            for tri in ((a, b, cc), (a, cc, d)):
                out.append((tri, r.random(), r.random()))
    return out


SHARDS = shards()


def s0(k):  # tienda gris "¿eso es una oferta?" → se rompe → ¡ESTO SÍ SON OFERTAS!
    br = k.w(4) - 0.15
    u = clamp((k.lt - br) / 0.9)

    def draw(c):
        if k.lt < br:
            gray_store(c, k.t)
            person(c, k, 840, FEET, HS, [(0, "neutral"), (k.w(1), "encoge")], style=GRAY, talk=False)
            return
        xmas_store(c, k.t)
        person(c, k, 260, FEET, HS, [(0, "saludo"), (k.w(5), "celebra")])
        confetti(c, br + 0.2, k.lt, 7)
        if u < 1:
            for tri, r1, r2 in SHARDS:  # el vidrio gris se rompe
                cx = sum(p[0] for p in tri) / 3
                cy = sum(p[1] for p in tri) / 3
                dx, dy = (cx - 540) * (1.2 + r1) * ease_out(u), (cy - 900) * (0.8 + r2) * ease_out(u) + 1400 * u * u
                p = skia.Path()
                p.moveTo(*tri[0])
                p.lineTo(*tri[1])
                p.lineTo(*tri[2])
                p.close()
                c.save()
                c.translate(dx, dy)
                c.translate(cx, cy)
                c.rotate((r1 - 0.5) * 200 * u)
                c.translate(-cx, -cy)
                c.save()
                c.clipPath(p, True)
                gray_store(c, k.t)
                c.restore()
                c.drawPath(p, P("#ffffff", "stroke", 3, alpha=0.6 * (1 - u)))
                c.restore()
    big_text(["¿ESO", "ES", "UNA", "OFERTA?"], 330, prog(k.lt, 0.0, k.w(3) + 0.3) * (1 - prog(k.lt, br - 0.1, br)),
             size=96, cols=("#d8d8d8",), stroke="#4a4a4a", rot=-2)
    big_text(["¡ESTO", "SÍ", "SON", "OFERTAS!"], 240, prog(k.lt, k.w(4) - 0.05, k.w(7) + 0.2), size=150,
             cols=("#ffffff", GOLD, "#ffffff", RED), stroke=INK, shake=6)
    if k.lt < br:
        z, fx, fy = lerp(1.0, 1.12, k.lt / max(br, 0.1)), 560, 900
        rot = 0
    else:
        e = ease_out(clamp((k.lt - br) / 0.8))
        z, fx, fy, rot = lerp(1.5, 1.0, e), lerp(540, 520, e), lerp(400, 1000, e), lerp(-8, 0, e)
    return punch(k, (4, 7), z), fx, fy, rot, draw


def s1(k):  # calle de noche: BLACK FRIDAY en neón, gente entrando
    camx = -k.lt * 260

    def draw(c):
        night_street(c, k.t, camx)
        for i, n in enumerate(("M2", "P3", "M1", "P4")):
            x = -200 + i * 230 + k.lt * 420
            if -200 < x < 1300:
                person(c, k, x, FEET + 40, 0.62, [(0, "neutral")], style=S[n], talk=False, walk=1.0)
    neon_text(["BLACK", "FRIDAY"], 330, prog(k.lt, 0, 0.4), k.t, size=170, col="#ff2a6a")
    return lerp(1.25, 1.0, ease_out(clamp(k.lt / 1.2))), 540 - camx * 0.3, 1000, -2 + 2 * clamp(k.lt), draw


def s2(k):  # ¡NAVIDEÑO!
    def draw(c):
        c.drawRect(RECT(-600, -600, 1700, 2600), P(RED, shader=rad(540, 960, 1300, ["#ff4a5a", "#a80a20", "#3a0008"])))
        for i in range(16):  # rayos verdes y rojos
            a = k.t * 0.8 + i * math.pi / 8
            p = skia.Path()
            p.moveTo(540, 960)
            p.lineTo(540 + math.cos(a) * 1800, 960 + math.sin(a) * 1800)
            p.lineTo(540 + math.cos(a + 0.2) * 1800, 960 + math.sin(a + 0.2) * 1800)
            p.close()
            c.drawPath(p, P(GREEN if i % 2 else "#ffffff", alpha=0.18))
        snow(c, k.t, 90, 2, 200)
        xmas_tree(c, 180, 1650, 0.55, k.t)
        xmas_tree(c, 900, 1650, 0.55, k.t + 1)
        for gx, col in ((360, GREEN), (720, "#3aa0ff"), (540, GOLD)):
            gift(c, gx, 1650, 130, 110, col, RED if col == GOLD else GOLD)
    xmas_text("¡NAVIDEÑO!", 900, k.lt * 1.6 + 0.05, size=210)
    z = 1.0 + 0.12 * math.exp(-k.lt * 5)
    sh = 14 * math.exp(-k.lt * 4)
    return z, 540 + sh * math.sin(k.t * 70), 960 + sh * math.cos(k.t * 60), 2 * math.sin(k.lt * 9) * math.exp(-k.lt * 2), draw


def s3(k):  # dentro de la tienda decorada: personaje A en el mostrador
    def draw(c):
        xmas_store(c, k.t)
        person(c, k, 380, FEET, HS, [(0, "saludo"), (k.w(2), "señala")])
        snow(c, k.t, 25, 4, 60)
    big_text(["OTTO", "ALEMAN"], 230, prog(k.lt, k.w(2) - 0.1, k.w(3) + 0.2), size=150, cols=(GOLD,), stroke="#5a0a14", rot=-4)
    big_text(["PERFUMES"], 360, prog(k.lt, k.w(4) - 0.1, k.w(4) + 0.3), size=110, cols=("#ffffff",), stroke=RED, rot=-4)
    e = ease_in_out(clamp(k.lt / max(k.D, 0.1)))
    return punch(k, (2, 4), lerp(0.9, 1.08, e)), lerp(700, 560, e), lerp(860, 900, e), lerp(3, 0, e), draw


def s4(k):  # 3x2: dos decants en el mostrador, el tercero cae del cielo
    def draw(c):
        xmas_store(c, k.t, tree_x=1050)
        person(c, k, 820, FEET, HS, [(0, "sostiene"), (k.w(2), "señala"), (k.w(4), "celebra")])
        for i in range(2):
            dk = prog(k.lt, 0.1 + i * 0.2, 0.4 + i * 0.2)
            if dk > 0:
                long_shadow(c, 200 + i * 170, 1440, 70, 160)
                color_decant(c, 200 + i * 170, lerp(1300, 1290, dk) - 150 * (1 - back_out(dk, 1.4)), 300, ["#ff6aa8", "#ffb04a"][i], k.t, 0)
        fk = prog(k.lt, k.w(3) - 0.2, k.w(4))
        if fk > 0:
            y = lerp(-300, 1290, ease_in_out(fk) if fk < 1 else 1)
            if fk >= 1:
                glow(c, R.RES.glow_gold, 540, 1290, 260, 0.6)
            long_shadow(c, 540, 1440, 70, 160, 0.25 * fk)
            color_decant(c, 540, y, 300, "#7ad0ff", k.t, 20 * (1 - fk))
    gold3d("3x2", 640, prog(k.lt, k.w(0) - 0.1, k.w(2) + 0.2) * 2, size=360)
    big_text(["EN", "DECANTS"], 880, prog(k.lt, k.w(3) - 0.1, k.w(4) + 0.2), size=100, cols=("#ffffff", GOLD), stroke=RED, rot=3)
    z = lerp(1.15, 1.0, ease_out(clamp(k.lt / 0.8)))
    return punch(k, (0, 2, 4), z), 540, lerp(1150, 1050, ease_out(clamp(k.lt))), -1.5 * math.sin(k.lt * 1.4), draw


def s5(k):  # mesa desde arriba: compras dos… y el tercero ¡GRATIS!
    gk = prog(k.lt, k.w(6) - 0.15, k.w(6) + 0.15)

    def draw(c):
        table_top(c, k.t)
        hands = [(0.0, 300), (k.w(1) - 0.3, 540)]
        for i, (t0, x) in enumerate(hands):
            dk = prog(k.lt, t0, t0 + 0.35)
            if dk > 0:
                oval(c, x + 22, 1010, 70, 190, P("#000000", alpha=0.25, blur=10))
                color_decant(c, lerp(x - 400 if i == 0 else x, x, ease_out(dk)), lerp(1000, 980, dk) + (0 if i == 0 else 400 * (1 - ease_out(dk))),
                             400, ["#ff6aa8", "#ffb04a"][i], k.t, 0)
                rrect(c, x - 50, 1230, x + 50, 1310, 20, P("#ffffff"))
                text_center(c, str(i + 1), x, 1295, F(R.RES.xbold, 70), P(INK))
        tk = prog(k.lt, k.w(4) - 0.3, k.w(5))
        if tk > 0:
            x = 780
            oval(c, x + 22, 1010, 70, 190, P("#000000", alpha=0.25 * tk, blur=10))
            sc = lerp(1.8, 1.0, ease_out(tk))
            c.save()
            c.translate(x, 980)
            c.scale(sc, sc)
            if gk > 0:
                glow(c, R.RES.glows["emerald"], 0, 0, 300, 0.7 * gk)
            color_decant(c, 0, 0, 400, "#7ad070", k.t, 0)
            c.restore()
        confetti(c, k.w(6), k.lt, 5, 90)
    big_text(["COMPRÁS", "2"], 420, prog(k.lt, 0.0, k.w(1) + 0.2), size=130, cols=("#ffffff", GOLD), stroke=INK, rot=-3)
    stamp("¡GRATIS!", 780, 1400, gk, GREEN, 120)
    return punch(k, (1, 6), lerp(1.12, 0.98, ease_in_out(clamp(k.lt / max(k.D, .1))))), 540, 980, lerp(-10, 6, ease_in_out(clamp(k.lt / max(k.D, .1)))), draw


def s6(k):  # carrusel: desierto (árabes) → pasarela (diseñador) → teléfono (virales)
    t1, t2 = k.w(4) - 0.25, k.w(6) - 0.1
    u1 = ease_in_out(clamp((k.lt - t1) / 0.35))
    u2 = ease_in_out(clamp((k.lt - t2) / 0.35))
    fx = 540 + 1400 * u1 + 1400 * u2

    def spin(i):
        return 4 * math.sin(k.t * 2 + i)

    def draw(c):
        desert(c, k.t, 0)
        runway(c, k.t, 1400)
        phone_world(c, k.t, 2800)
        a1 = prog(k.lt, 0.1, 0.5)
        B.yara_candy(c, 330, 1350, 0.95 * back_out(a1, 1.4), k.t, glow_a=0.6, rot=spin(0))
        E2.hawas(c, 760, 1350, 1.35 * back_out(a1, 1.4), rot=spin(1), glow_a=0.6)
        a2 = prog(k.lt, t1 + 0.2, t1 + 0.6)
        B.valentino(c, 1400 + 320, 1400, 1.0 * back_out(a2, 1.4), k.t, "intense", glow_a=0.5, rot=spin(2))
        B.valentino(c, 1400 + 770, 1400, 1.0 * back_out(a2, 1.4), k.t, "yellow", glow_a=0.5, rot=spin(3))
        a3 = prog(k.lt, t2 + 0.2, t2 + 0.6)
        EL.elixir(c, 2800 + 360, 1300, 0.95 * back_out(a3, 1.4), k.t, look=EL.ORIG, rot=spin(4))
        EL.elixir(c, 2800 + 730, 1300, 0.95 * back_out(a3, 1.4), k.t, rot=spin(5))
    on1 = prog(k.lt, k.w(2) - 0.1, k.w(3) + 0.2) * (1 - prog(k.lt, t1, t1 + 0.15))
    on2 = prog(k.lt, k.w(5) - 0.1, k.w(5) + 0.2) * (1 - prog(k.lt, t2, t2 + 0.15))
    on3 = prog(k.lt, k.w(8) - 0.1, k.w(9) + 0.2)
    big_text(["ÁRABES"], 520, on1, size=170, cols=(GOLD,), stroke="#6a2a08", rot=-4)
    big_text(["DE", "DISEÑADOR"], 520, on2, size=140, cols=("#ffffff", "#e0b0ff"), stroke="#2a0a3a", rot=3)
    big_text(["LOS", "MÁS", "VIRALES"], 340, on3, size=130, cols=("#ffffff", "#ffffff", "#ffe04a"), stroke="#a01060", rot=-3)
    z = 1.0 - 0.12 * math.sin(math.pi * clamp((k.lt - t1) / 0.35)) - 0.12 * math.sin(math.pi * clamp((k.lt - t2) / 0.35))
    return z, fx, 1050, 3 * math.sin(k.lt * 1.3), draw


def s7(k):  # 5 y 10 ml contra frasco completo
    xk = prog(k.lt, k.w(7) - 0.1, k.w(8) + 0.1)

    def draw(c):
        studio(c, k.t, "#fff0d0", "#ffc890")
        long_shadow(c, 820, 1450, 330, 600, 0.2)
        B.valentino(c, 820, 1450, 1.15, k.t, "intense", rot=0)
        if xk > 0:
            for sd in (-1, 1):
                L = 300 * ease_out(xk)
                c.drawLine(820 - L, 1180 - sd * L * 1.1, 820 + L, 1180 + sd * L * 1.1, P(RED, "stroke", 34, cap=skia.Paint.kRound_Cap))
        d5 = prog(k.lt, k.w(1) - 0.2, k.w(1) + 0.2)
        d10 = prog(k.lt, k.w(3) - 0.2, k.w(3) + 0.2)
        if d5 > 0:
            long_shadow(c, 150, 1450, 70, 200)
            color_decant(c, 150, lerp(2100, 1290, back_out(d5, 1.3)), 300, "#ffb04a", k.t, -4)
        if d10 > 0:
            long_shadow(c, 450, 1450, 90, 260)
            color_decant(c, 450, lerp(2100, 1250, back_out(d10, 1.3)), 380, "#ff6aa8", k.t, 4)
    big_text(["5", "ML"], 980, prog(k.lt, k.w(1) - 0.1, k.w(1) + 0.3), size=85, x=150, rot=-6, cols=("#ffffff", GOLD))
    big_text(["10", "ML"], 940, prog(k.lt, k.w(3) - 0.1, k.w(3) + 0.3), size=85, x=450, rot=5, cols=("#ffffff", GOLD))
    big_text(["SIN", "GASTAR", "DE", "MÁS"], 420, prog(k.lt, k.w(6) - 0.1, k.w(7) + 0.3), size=120, cols=("#ffffff", RED), rot=-3)
    e = ease_in_out(clamp(k.lt / max(k.D, .1)))
    return punch(k, (1, 3, 7), lerp(1.05, 0.95, e)), lerp(530, 550, e), 1060, lerp(-2, 2, e), draw


def s8(k):  # ¡corré, que vuela!: decants salen volando, gente corre
    def draw(c):
        xmas_store(c, k.t, tree_x=-200, counter=False)
        c.drawRect(RECT(-300, 1450, 1400, 2600), P("#2a1a14"))
        r = rng(12)
        for i in range(16):
            x0 = -100 + (i % 8) * 160
            y0 = 900 + (i // 8) * 170 - 160
            d = clamp((k.lt - 0.1 - i * 0.04) / 0.8)
            ang = r.random() * 2 * math.pi
            x = x0 + math.cos(ang) * 900 * ease_in_out(d)
            y = y0 - 400 * math.sin(math.pi * d) + 600 * d * d
            color_decant(c, x, y, 160, N.DEC_COLS[i % 6], k.t, d * 720 * (1 if i % 2 else -1))
        for i, n in enumerate(("M4", "P2", "M1", "P1")):
            x = 1300 - (k.lt * 900 + i * 260) % 1700
            person(c, k, x, FEET + 30, 0.6, [(0, "celebra")], style=S[n], talk=False, walk=1.4)
    big_text(["¡CORRÉ!"], 420, prog(k.lt, k.w(0), k.w(1) + 0.2), size=190, cols=(RED,), stroke="#ffffff", shake=8)
    big_text(["QUE", "VUELA"], 620, prog(k.lt, k.w(2) - 0.1, k.w(3) + 0.2), size=150, cols=("#ffffff", GOLD), stroke=INK, rot=4)
    return 1.0 + 0.1 * math.sin(k.lt * 3), 540, 1000, 10 * math.sin(k.lt * 2.6), draw


def s9(k):  # escribinos: burbujas de comentarios y mensajes
    def draw(c):
        xmas_store(c, k.t, tree_x=880, logo=False)
        person(c, k, 420, FEET, HS, [(0, "señala"), (k.w(4), "pulgar")])
        r = rng(21)
        for i in range(12):
            t0 = 0.1 + i * 0.14
            if k.lt < t0:
                continue
            u = k.lt - t0
            x = 100 + r.random() * 880
            y = 1500 - u * (300 + 200 * r.random()) - r.random() * 200
            s = back_out(clamp(u / 0.3), 2)
            c.save()
            c.translate(x, y)
            c.scale(s, s)
            if i % 2:
                rrect(c, -110, -50, 110, 50, 40, P("#ffffff"))
                p = skia.Path()
                p.moveTo(-60, 46)
                p.lineTo(-90, 80)
                p.lineTo(-20, 46)
                c.drawPath(p, P("#ffffff"))
                for j in range(3):
                    oval(c, -50 + j * 50, 0, 12, 12, P("#9a9aa8"))
            else:
                oval(c, 0, 0, 60, 60, P("#3a7aff", shader=lin(-60, -60, 60, 60, ["#ff5ad0", "#7a3aff"])))
                p = skia.Path()
                p.moveTo(-28, -18)
                p.lineTo(28, -18)
                p.lineTo(28, 16)
                p.lineTo(-28, 16)
                p.close()
                c.drawPath(p, P("#ffffff", "stroke", 6))
                c.drawLine(-28, -18, 0, 4, P("#ffffff", "stroke", 6))
                c.drawLine(28, -18, 0, 4, P("#ffffff", "stroke", 6))
                oval(c, 44, -44, 18, 18, P(RED))
            c.restore()
    big_text(["AL", "PRIVADO"], 230, prog(k.lt, k.w(1) - 0.1, k.w(2) + 0.2), size=120, cols=("#ffffff", "#7ad0ff"), stroke="#1a2a6a", rot=-4)
    big_text(["O", "EN", "COMENTARIOS"], 370, prog(k.lt, k.w(4) - 0.1, k.w(6) + 0.2), size=110, cols=("#ffffff", "#ffffff", GOLD), stroke=RED, rot=3)
    big_text(["@ottoaleman.perfumesgt"], 500, prog(k.lt, k.w(5), k.w(6) + 0.3), size=80, cols=("#ffffff",), stroke=INK, rot=0)
    e = ease_in_out(clamp(k.lt / max(k.D, .1)))
    return lerp(1.0, 1.12, e), lerp(560, 460, e), lerp(1000, 960, e), 0, draw


def s10(k):  # porque esto SÍ son ofertas: todos celebran
    def draw(c):
        xmas_store(c, k.t)
        for i, n in enumerate(("M1", "P3", "M4", "P2")):
            x = [80, 300, 780, 1000][i]
            person(c, k, x, FEET + 50, 0.6, [(0, "neutral"), (k.w(2) - 0.1 + i * 0.05, "celebra")], style=S[n], talk=False)
        person(c, k, 540, FEET, HS, [(0, "señala"), (k.w(2), "celebra")])
        confetti(c, k.w(2), k.lt, 9, 90)
    big_text(["¡ESTO", "SÍ", "SON", "OFERTAS!"], 240, prog(k.lt, k.w(1) - 0.1, k.w(4) + 0.2), size=150,
             cols=("#ffffff", GOLD, "#ffffff", RED), stroke=INK, shake=5)
    e = ease_out(clamp(k.lt / max(k.D, .1)))
    return punch(k, (2, 4), lerp(1.2, 1.0, e)), 540, lerp(900, 1020, e), lerp(-4, 0, e), draw


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
N.SCENES[:] = SCENES
N.WHIP.clear()
N.WHIP.update({1, 3, 4, 5, 6, 7, 8, 9, 10})


def render_frame(c, t, vo, phr, total):
    N.D.VO = vo
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(R.hexc("#000000"))
    loop_t = vo[-1]["tokens"][-1]["e"] + 0.25
    if t >= loop_t:  # bucle: vuelve exactamente al primer cuadro
        N.render_scene(c, 0, R.Ctx(vo, 0, 0.0))
        OVER.clear()
    else:
        k = R.Ctx(vo, si, t)
        blur, dx = 0.0, 0.0
        if si in N.WHIP and k.lt < 0.22:  # barrido rápido de un lugar al otro
            q = 1 - ease_out(k.lt / 0.22)
            blur, dx = 70 * q, 300 * q * (1 if si % 2 else -1)
        if si == 2 and k.lt < 0.12:  # destello blanco al gritar NAVIDEÑO
            pass
        if blur > 0.3:
            p = skia.Paint()
            p.setImageFilter(skia.ImageFilters.Blur(blur, blur * 0.06, skia.TileMode.kClamp))
            c.saveLayer(None, p)
        c.save()
        c.translate(dx, 0)
        N.render_scene(c, si, k)
        c.restore()
        if blur > 0.3:
            c.restore()
        if si == 2 and k.lt < 0.15:
            c.drawRect(RECT(0, 0, W, H), P("#ffffff", alpha=0.8 * (1 - k.lt / 0.15)))
        for fn in OVER:
            fn(c)
    R.vignette(c, 0.25)
    N.draw_subs(c, t, phr)
    N.draw_watermark(c)


def install():
    N.install()
    R.SCENES = SCENES
    R.render_frame = render_frame


if __name__ == "__main__":
    install()
    R.main()
