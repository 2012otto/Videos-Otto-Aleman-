"""Velto — serie con Ana, episodio 3: "No son tus seguidores" (3 errores).

Uso (desde la raíz del repo):
  VIDEO_BUILD=$PWD/velto/build_ep3 VO_TRIM=0.3 python3 velto/src/render_ep3.py --start 0 --end 8 --out velto/build_ep3/prueba.mp4
"""
import math
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_ep2 as E2  # noqa: E402
from render_velto import (R, P, RECT, ANA, CLIENTE, VIO, VIO2, LIME, F, back_out, clamp, ease_in_out,  # noqa: E402
                          ease_out, glow, lerp, lin, rad, oval, prog, rrect, text_center, draw_kid, rng,
                          neon_bg, phone, catalog_screen, client_logo, chat_icon, ring, necklace, earrings,
                          bracelet, use, bubble, W, H)
from render_ep2 import big_text, star, magnifier, talk  # noqa: E402

camera = R.camera
RED = "#ff3b5c"


# ----------------------------------------------------------------------------
# elementos nuevos
# ----------------------------------------------------------------------------


def persp_floor(c, t, horizon=1180, alpha=1.0):
    """Piso de cuadrícula neón en perspectiva (escenario)."""
    c.drawRect(RECT(-500, horizon, W + 500, H + 500), P("#0a0416", shader=lin(0, horizon, 0, H, ["#1a0838", "#05020b"])))
    vx = 540
    for i in range(-14, 15):
        x = vx + i * 160
        c.drawLine(vx + i * 12, horizon, x, H + 200, P("#a64dff", "stroke", 2.5, alpha=0.5 * alpha))
    off = (t * 0.6) % 1.0
    for j in range(12):
        u = ((j + off) / 12) ** 2.2
        y = horizon + u * (H + 200 - horizon)
        c.drawLine(-500, y, W + 500, y, P(LIME if j % 4 == 0 else "#a64dff", "stroke", 2, alpha=(0.25 + 0.5 * u) * alpha))
    c.drawLine(-500, horizon, W + 500, horizon, P(LIME, "stroke", 4, blur=6, alpha=0.8 * alpha))
    c.drawLine(-500, horizon, W + 500, horizon, P(LIME, "stroke", 2, alpha=alpha))


def spotlight(c, x, top, bottom, w0, w1, a=0.12):
    cone = skia.Path()
    cone.moveTo(x - w0, top)
    cone.lineTo(x + w0, top)
    cone.lineTo(x + w1, bottom)
    cone.lineTo(x - w1, bottom)
    cone.close()
    c.drawPath(cone, P("#ffffff", shader=lin(0, top, 0, bottom, [R.hexc("#e9d6ff", a), R.hexc("#e9d6ff", a * 0.2)])))


def error_tag(c, num, text, k, y=590):
    if k <= 0:
        return
    s = back_out(k)
    c.save()
    c.translate(540, y)
    c.scale(s, s)
    f1, f2 = F(R.RES.mx, 40), F(R.RES.mx, 44)
    w1 = f1.measureText(f"ERROR {num}") + 50
    w2 = f2.measureText(text) + 60
    tot = w1 + w2
    x0 = -tot / 2
    glow(c, R.RES.g_mag, 0, 0, tot * 0.6, 0.35)
    rrect(c, x0, -42, x0 + w1, 42, 20, P(RED))
    c.drawString(f"ERROR {num}", x0 + 25, 14, f1, P("#ffffff"))
    rrect(c, x0 + w1 - 10, -42, x0 + tot, 42, 20, P("#ffffff"))
    c.drawRect(RECT(x0 + w1 - 10, -42, x0 + w1 + 10, 42), P(RED))
    c.drawString(text, x0 + w1 + 30, 15, f2, P("#14061f"))
    c.restore()


def cloud(c, x, y, text, k, size=40):
    if k <= 0:
        return
    s = back_out(k)
    f = F(R.RES.mx, size)
    w = f.measureText(text) + 80
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for (bx, by, r) in ((w * 0.35, 90, 12), (w * 0.28, 62, 18)):
        oval(c, bx, by, r, r, P("#f4f1fb"))
    for (bx, by, rx, ry) in ((-w * 0.3, 0, w * 0.32, 52), (w * 0.25, -6, w * 0.32, 56), (0, -30, w * 0.36, 50),
                             (0, 18, w * 0.45, 44)):
        oval(c, bx, by, rx, ry, P("#f4f1fb"))
    text_center(c, text, 0, 12, f, P("#3a2a5a"))
    c.restore()


def walk_kid(c, x, y, s, t, lt, moving, **kw):
    sw = math.sin(lt * 10) * 22 * moving
    return draw_kid(c, x, y - abs(math.sin(lt * 10)) * 8 * moving, s, t, legs=(sw, -sw), **kw)


# ---- miniaturas de la galería -------------------------------------------------


def tile_cat(c, x, y, w):
    c.drawRect(RECT(x, y, x + w, y + w), P("#6ec6ff"))
    cx, cy, r = x + w / 2, y + w * 0.55, w * 0.3
    for side in (-1, 1):
        ear = skia.Path()
        ear.moveTo(cx + side * r * 0.9, cy - r * 0.4)
        ear.lineTo(cx + side * r * 0.75, cy - r * 1.35)
        ear.lineTo(cx + side * r * 0.2, cy - r * 0.85)
        ear.close()
        c.drawPath(ear, P("#ff9a3c"))
    oval(c, cx, cy, r, r * 0.9, P("#ff9a3c"))
    for side in (-1, 1):
        oval(c, cx + side * r * 0.38, cy - r * 0.1, r * 0.13, r * 0.18, P("#14061f"))
        c.drawLine(cx + side * r * 0.5, cy + r * 0.25, cx + side * r * 1.2, cy + r * 0.15, P("#14061f", "stroke", 2))
    oval(c, cx, cy + r * 0.2, r * 0.1, r * 0.07, P("#ff5c7a"))
    text_center(c, "LUNES", cx, y + w * 0.2, F(R.RES.mx, w * 0.16), P("#ffffff"))


def tile_jaja(c, x, y, w):
    c.drawRect(RECT(x, y, x + w, y + w), P("#ffd23f"))
    text_center(c, "JAJA", x + w / 2, y + w * 0.6, F(R.RES.mx, w * 0.3), P("#14061f"))


def tile_pizza(c, x, y, w):
    c.drawRect(RECT(x, y, x + w, y + w), P("#ff6f61"))
    p = skia.Path()
    p.moveTo(x + w * 0.2, y + w * 0.25)
    p.lineTo(x + w * 0.8, y + w * 0.25)
    p.lineTo(x + w * 0.5, y + w * 0.85)
    p.close()
    c.drawPath(p, P("#ffd27a"))
    c.drawRect(RECT(x + w * 0.2, y + w * 0.2, x + w * 0.8, y + w * 0.28), P("#c98a3c"))
    for (u, v) in ((0.4, 0.38), (0.6, 0.4), (0.5, 0.58)):
        oval(c, x + w * u, y + w * v, w * 0.05, w * 0.05, P("#c2183f"))


def tile_laugh(c, x, y, w):
    c.drawRect(RECT(x, y, x + w, y + w), P("#7a5aff"))
    cx, cy, r = x + w / 2, y + w / 2, w * 0.32
    oval(c, cx, cy, r, r, P("#ffd23f"))
    for side in (-1, 1):
        a = skia.Path()
        a.moveTo(cx + side * r * 0.55, cy - r * 0.15)
        a.quadTo(cx + side * r * 0.35, cy - r * 0.45, cx + side * r * 0.15, cy - r * 0.15)
        c.drawPath(a, P("#14061f", "stroke", 3))
        oval(c, cx + side * r * 0.75, cy, r * 0.12, r * 0.22, P("#5ad1ff"))
    m = skia.Path()
    m.moveTo(cx - r * 0.5, cy + r * 0.15)
    m.quadTo(cx, cy + r * 0.9, cx + r * 0.5, cy + r * 0.15)
    m.close()
    c.drawPath(m, P("#5a2230"))


def tile_ana_old(c, x, y, w, t):
    c.save()
    c.clipRect(RECT(x, y, x + w, y + w), True)
    c.drawRect(RECT(x, y, x + w, y + w), P("#c9a77c"))
    s = w / 330
    draw_kid(c, x + w / 2, y + w * 0.5 + 508 * s, s, t, "happy", style=ANA, blink=False,
             hands={"R": (170, -560), "L": (-112, -196)})
    c.drawRect(RECT(x, y, x + w, y + w), P("#8a6a40", blend=skia.BlendMode.kMultiply, alpha=0.45))
    c.drawRect(RECT(x, y, x + w, y + w), P("#808080", blend=skia.BlendMode.kSaturation, alpha=0.6))
    c.restore()
    rrect(c, x + 6, y + w - 30, x + 76, y + w - 8, 6, P("#14061f", alpha=0.6))
    c.drawString("2019", x + 14, y + w - 12, F(R.RES.mb, 16), P("#ffffff"))


def tile_product(c, x, y, w):
    c.drawRect(RECT(x, y, x + w, y + w), P("#fdf6ff"))
    necklace(c, x + w / 2, y + w * 0.42, w / 160)
    c.drawString("Q175", x + 10, y + w - 12, F(R.RES.mx, w * 0.16), P("#7a2be2"))


GALLERY = (["cat", "ana", "jaja", "pizza", "ana", "laugh", "jaja", "cat", "ana", "laugh", "pizza", "ana",
            "cat", "jaja", "ana", "laugh", "pizza", "cat", "ana", "jaja", "laugh", "ana", "cat", "pizza",
            "jaja", "ana", "laugh", "cat", "product", "ana"])


def draw_tile(c, kind, x, y, w, t):
    if kind == "cat":
        tile_cat(c, x, y, w)
    elif kind == "jaja":
        tile_jaja(c, x, y, w)
    elif kind == "pizza":
        tile_pizza(c, x, y, w)
    elif kind == "laugh":
        tile_laugh(c, x, y, w)
    elif kind == "ana":
        tile_ana_old(c, x, y, w, t)
    else:
        tile_product(c, x, y, w)


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def scene1(c, k):  # GANCHO: no son tus seguidores
    lt = k.lt
    camera(c, 1.0 + 0.03 * ease_out(prog(lt, 0, k.D)), 540, 960, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1620)
    punch = 1 + 0.07 * (1 - ease_out(prog(lt, 0, 0.35)))
    c.save()
    c.translate(540, 660)
    c.scale(punch, punch)
    big_text(c, [("NO SON TUS", "#ffffff"), ("SEGUIDORES", LIME)], 0, -20, 116, 120)
    c.restore()
    # perfil
    x0, y0, x1, y1 = 100, 880, 980, 1180
    rrect(c, x0, y0, x1, y1, 36, P("#1b1230", alpha=0.96))
    rrect(c, x0, y0, x1, y1, 36, P("#b98aff", "stroke", 3, alpha=0.7))
    oval(c, x0 + 110, y0 + 110, 70, 70, P("#fdf6ff"))
    oval(c, x0 + 110, y0 + 110, 76, 76, P(VIO, "stroke", 8, shader=lin(x0 + 40, 0, x0 + 180, 0, [VIO2, LIME])))
    ring(c, x0 + 110, y0 + 108, 1.2)
    c.drawString("anajoyas.gt", x0 + 40, y0 + 250, F(R.RES.mb, 34), P("#ffffff"))
    stats = [("48", "publicaciones"), ("312", "seguidores"), ("180", "seguidos")]
    for i, (n, lab) in enumerate(stats):
        sx = x0 + 330 + i * 200
        text_center(c, n, sx, y0 + 115, F(R.RES.mx, 54), P("#ffffff"))
        text_center(c, lab, sx, y0 + 160, F(R.RES.ms, 26), P("#c9b8e8"))
    st = ease_out(prog(lt, k.w(7) - 0.1, k.w(8) + 0.1))
    if st > 0:
        cx = x0 + 530
        c.drawLine(cx - 110, y0 + 60, cx - 110 + 220 * st, y0 + 60 + 120 * st, P(LIME, "stroke", 16))
        c.drawLine(cx - 110, y0 + 60, cx - 110 + 220 * st, y0 + 60 + 120 * st, P(LIME, "stroke", 30, blur=10, alpha=0.5))
    shake = math.sin(lt * 9) * 9 * (1 - prog(lt, 1.6, 2.2))
    draw_kid(c, 880, 1650, 0.62, k.t, "happy", look=(-0.5, -0.2), tilt=shake, style=ANA,
             hands={"R": (130, -230), "L": (-160, -470)}, talk=talk(k.t))


def scene2(c, k):  # 3 ERRORES en el escenario
    lt = k.lt
    camera(c, lerp(1.1, 1.0, ease_out(prog(lt, 0, 1.2))), 540, 960, k.t)
    neon_bg(c, k.t, grid=0.12, waves=False)
    persp_floor(c, k.t, 1250)
    spotlight(c, 540, -100, 1300, 120, 420, 0.13)
    tk = prog(lt, k.w(4) - 0.2, k.w(4) + 0.2)
    if tk > 0:
        s = back_out(tk, 2.2)
        c.save()
        c.translate(540, 850)
        c.scale(s, s)
        glow(c, R.RES.g_lime, 0, -60, 380, 0.7)
        text_center(c, "3", 0, 60, F(R.RES.mx, 380), P(LIME))
        text_center(c, "ERRORES", 0, 190, F(R.RES.mx, 96), P("#ffffff"))
        c.restore()
        use("lime")
        R.burst(c, 540, 820, lt - k.w(4) + 0.1, dur=1.0, n=40, radius=380, seed=4, intensity=0.8)
    E2_pill(c, 540, 1180, "¿Cometes alguno?", prog(lt, k.w(5) + 0.1, k.w(5) + 0.4))
    draw_kid(c, 190, 1660, 0.62, k.t, "happy", look=(0.7, -0.4), style=ANA, tilt=3,
             hands={"R": (170, -470), "L": (-120, -220)}, talk=talk(k.t))


def E2_pill(c, x, y, text, kk):
    from render_velto import pill
    pill(c, x, y, text, kk, size=44, bg="#14061f", fg=LIME, border=LIME)


def scene3(c, k):  # ERROR 1: vitrina sin precios
    lt = k.lt
    camera(c, 1.0, 540, 980, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1640)
    error_tag(c, 1, "Escondes tus precios", prog(lt, 0.0, 0.35))
    # vitrina
    x0, x1, top, bot = 110, 970, 820, 1250
    glow(c, R.RES.glow_warm, 540, 1000, 520, 0.25)
    rrect(c, x0, top, x1, bot, 24, P("#2a1450", shader=lin(0, top, 0, bot, ["#3a1c6a", "#1a0a32"])))
    c.drawRect(RECT(x0 + 20, top + 20, x1 - 20, bot - 110), P("#e9d6ff", alpha=0.08))
    rrect(c, x0 - 20, bot - 110, x1 + 20, bot - 70, 10, P("#c9b8e8", alpha=0.85))
    rrect(c, x0, bot - 70, x1, bot + 120, 16, P(VIO, shader=lin(0, bot - 70, 0, bot + 120, ["#6a22c0", "#2a0a5a"])))
    items = [necklace, ring, earrings, bracelet]
    for i, fn in enumerate(items):
        ix = x0 + 110 + i * 215
        rrect(c, ix - 60, bot - 230, ix + 60, bot - 110, 16, P("#4a1c7a"))
        fn(c, ix, bot - 200, 1.0)
        # etiqueta colgante sin precio
        sw = 10 * math.sin(k.t * 2 + i)
        c.save()
        c.translate(ix + 50, top + 60)
        c.rotate(sw)
        c.drawLine(0, 0, 0, 40, P("#d9c8f0", "stroke", 2))
        rrect(c, -48, 40, 48, 92, 10, P(RED))
        text_center(c, "Q ???", 0, 76, F(R.RES.mx, 26), P("#ffffff"))
        c.restore()
    sk = prog(lt, k.w(2) - 0.2, k.w(2) + 0.15)
    if sk > 0:
        s = back_out(sk, 2.5)
        c.save()
        c.translate(540, bot + 40)
        c.rotate(-4)
        c.scale(s, s)
        rrect(c, -230, -44, 230, 44, 16, P(RED))
        rrect(c, -230, -44, 230, 44, 16, P("#ffffff", "stroke", 5))
        text_center(c, "Precio por inbox", 0, 14, F(R.RES.mx, 42), P("#ffffff"))
        c.restore()
    # el cliente mira... y se va
    leave = ease_in_out(prog(lt, k.w(13) - 0.1, k.w(15) + 0.5))
    moving = 1.0 if 0 < leave < 1 else 0.0
    expr = "neutral" if lt < k.w(8) else "worried"
    cloud(c, 480, 1395, "¿Será muy caro?", prog(lt, k.w(8) - 0.2, k.w(8) + 0.2) * (1 - prog(lt, k.w(13), k.w(13) + 0.2)))
    walk_kid(c, lerp(860, 1300, leave), 1660, 0.62, k.t, lt, moving, expr=expr,
             look=(-0.8, -0.5) if leave < 0.05 else (1, 0), style=CLIENTE,
             hands={"R": (120, -220), "L": (-120, -220)})


def scene4(c, k):  # ERROR 2: galería llena de memes
    lt = k.lt
    camera(c, 1.0, 540, 980, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1640)
    error_tag(c, 2, "Productos perdidos", prog(lt, 0.0, 0.35))
    T = k.w
    stop = T(12)
    scroll = ease_in_out(prog(lt, 0.3, stop)) * 1130
    hl = None
    if T(7) - 0.1 <= lt < T(8) - 0.1:
        hl = ("cat", "jaja", "pizza", "laugh")
    elif T(8) - 0.1 <= lt < T(10) - 0.1:
        hl = ("story",)
    elif T(10) - 0.1 <= lt < T(12):
        hl = ("ana",)
    found = prog(lt, T(13), T(14))

    def gallery(c2, x0, y0, x1, y1):
        w = x1 - x0
        c2.drawRect(RECT(x0, y0, x1, y1), P("#0e0a1a"))
        tw = (w - 16) / 3
        top = y0 + 190 - scroll
        for i, kind in enumerate(GALLERY):
            tx = x0 + 4 + (i % 3) * (tw + 4)
            ty = top + (i // 3) * (tw + 4)
            if ty > y1 or ty + tw < y0 + 170:
                continue
            draw_tile(c2, kind, tx, ty, tw, k.t)
            if hl and kind in hl:
                c2.drawRect(RECT(tx + 3, ty + 3, tx + tw - 3, ty + tw - 3), P(LIME, "stroke", 6))
            if kind == "product" and found > 0:
                c2.drawRect(RECT(tx + 3, ty + 3, tx + tw - 3, ty + tw - 3), P(LIME, "stroke", 8, alpha=found))
        # barra de stories arriba
        c2.drawRect(RECT(x0, y0, x1, y0 + 170), P("#160f26"))
        for j in range(5):
            sx = x0 + 60 + j * (w - 60) / 5
            oval(c2, sx, y0 + 100, 44, 44, P(VIO, "stroke", 6, shader=lin(sx - 44, 0, sx + 44, 0, [VIO2, LIME])))
            oval(c2, sx, y0 + 100, 36, 36, P(["#ff6f61", "#6ec6ff", "#ffd23f", "#7a5aff", "#ff9a3c"][j]))
            if hl == ("story",):
                oval(c2, sx, y0 + 100, 52, 52, P(LIME, "stroke", 5))
    phone(c, 540, 1090, 560, 900, gallery, rot=-2, glow_a=0.6)
    if found > 0:
        magnifier(c, 700, 1380, 40 * back_out(found), LIME)
    bored = lt > T(12)
    draw_kid(c, 150, 1660, 0.6, k.t, "sad" if bored else "neutral", look=(0.8, -0.6), style=CLIENTE,
             hands={"R": (110, -230), "L": (-110, -230)}, tilt=-8 * bored)
    if bored:
        for j in range(3):
            a = ((lt - T(12)) * 0.8 + j / 3) % 1
            c.drawString("z", 210 + j * 18 + a * 30, 1270 - a * 90, F(R.RES.mx, 30 + j * 8), P("#d9c8f0", alpha=1 - a))


MAZE = ["#.#####", "#...#.#", "##.#..#", "#..#.##", "#.##..#", "#....##"]
MAZE_PATH = [(1, 0), (1, 1), (2, 1), (2, 2), (2, 3), (1, 3), (1, 4), (1, 5), (2, 5), (3, 5), (4, 5), (4, 4),
             (5, 4), (5, 3), (4, 3), (4, 2), (4, 1), (5, 1)]


def scene5(c, k):  # ERROR 3: laberinto de mensajes
    lt = k.lt
    camera(c, 1.0, 540, 980, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1660)
    error_tag(c, 3, "Comprarte es un laberinto", prog(lt, 0.0, 0.35))
    T = k.w
    cs = 130
    ox, oy = 540 - 3.5 * cs, 720
    wall = P("#a64dff", "stroke", 10)
    wall_g = P("#a64dff", "stroke", 26, blur=10, alpha=0.5)
    for r_, row in enumerate(MAZE):
        for c_, ch in enumerate(row):
            if ch == "#":
                x, y = ox + c_ * cs, oy + r_ * cs
                rr = skia.RRect.MakeRectXY(RECT(x + 10, y + 10, x + cs - 10, y + cs - 10), 18, 18)
                c.drawRRect(rr, wall_g)
                c.drawRRect(rr, wall)
    u = clamp(prog(lt, 0.4, T(15)))
    pos = u * (len(MAZE_PATH) - 1)
    i0 = int(pos)
    i1 = min(i0 + 1, len(MAZE_PATH) - 1)
    f = pos - i0
    (c0, r0), (c1, r1) = MAZE_PATH[i0], MAZE_PATH[i1]
    px = ox + lerp(c0, c1, f) * cs + cs / 2
    py = oy + lerp(r0, r1, f) * cs + cs / 2
    tired = lt > T(14) - 0.1
    walk_kid(c, px, py + 60, 0.26, k.t, lt, 0.0 if tired else 1.0, expr="sad" if tired else "worried",
             look=(0.3, 0.3), style=CLIENTE, hands={"R": (120, -220), "L": (-120, -220)})
    msgs = ["¿Talla?", "¿Color?", "Manda captura", "¿Dirección?", "¿Y el envío?", "¿Transferencia?"]
    spots = [(150, 760), (650, 830), (120, 1010), (640, 1120), (160, 1290), (590, 1400)]
    for i, (m, (bx, by)) in enumerate(zip(msgs, spots)):
        kk = prog(lt, 1.0 + i * 0.55, 1.25 + i * 0.55)
        bubble(c, bx, by + 6 * math.sin(k.t * 3 + i), m, i % 2 == 1 and False, 36, 600, kk,
               col=["#2c2540", VIO][i % 2])
    n = int(lerp(1, 14, prog(lt, 0.8, T(15))))
    ck = prog(lt, 0.6, 0.9)
    if ck > 0:
        s = back_out(ck)
        c.save()
        c.translate(870, 700)
        c.scale(s, s)
        rrect(c, -150, -40, 150, 40, 40, P(RED))
        text_center(c, f"Mensaje {n}", 0, 14, F(R.RES.mx, 38), P("#ffffff"))
        c.restore()


def scene6(c, k):  # el giro: balanza
    lt = k.lt
    camera(c, 1.0, 540, 980, k.t)
    neon_bg(c, k.t, grid=0.12, waves=False)
    persp_floor(c, k.t, 1400, alpha=0.8)
    T = k.w
    tilt = 13 * ease_in_out(prog(lt, T(6) - 0.2, T(7) + 0.3))
    px, py, L = 540, 760, 380
    c.drawRect(RECT(526, py, 554, 1330), P("#c9b8e8"))
    rrect(c, 420, 1320, 660, 1360, 12, P("#c9b8e8"))
    oval(c, px, py, 22, 22, P(LIME))
    a = math.radians(tilt)
    ends = [(px - L * math.cos(a), py - L * math.sin(a)), (px + L * math.cos(a), py + L * math.sin(a))]
    c.drawLine(ends[0][0], ends[0][1], ends[1][0], ends[1][1], P("#e9d6ff", "stroke", 14))
    for side, (ex, ey) in enumerate(ends):
        pan_y = ey + 210
        c.drawLine(ex, ey, ex - 110, pan_y, P("#c9b8e8", "stroke", 3))
        c.drawLine(ex, ey, ex + 110, pan_y, P("#c9b8e8", "stroke", 3))
        pan = skia.Path()
        pan.moveTo(ex - 140, pan_y)
        pan.quadTo(ex, pan_y + 70, ex + 140, pan_y)
        pan.close()
        c.drawPath(pan, P(VIO if side == 0 else LIME, alpha=0.9))
        if side == 0:  # 10 mil que solo miran: ojos
            for j in range(14):
                jx = ex - 110 + (j % 7) * 36
                jy = pan_y - 30 - (j // 7) * 40
                oval(c, jx, jy, 16, 11, P("#ffffff", alpha=0.85))
                oval(c, jx + 2 * math.sin(k.t * 2 + j), jy, 6, 6, P("#14061f"))
            lab = [("10 mil", "#e9d6ff"), ("solo miran", "#c9b8e8")]
        else:  # 300 que compran: bolsitas
            for j in range(4):
                jx = ex - 85 + j * 56
                rrect(c, jx - 20, pan_y - 60, jx + 20, pan_y - 10, 6, P("#14061f"))
                c.drawPath(skia.Path().addArc(RECT(jx - 11, pan_y - 78, jx + 11, pan_y - 50), 180, 180),
                           P(LIME, "stroke", 4))
            lab = [("300", LIME), ("te compran", "#ffffff")]
        for li, (txt, col) in enumerate(lab):
            text_center(c, txt, ex, pan_y + 90 + li * 50, F(R.RES.mx, 54 if li == 0 else 34), P(col))
    gt = prog(lt, T(6), T(6) + 0.3)
    if gt > 0:
        s = back_out(gt, 2.4)
        c.save()
        c.translate(540, 640)
        c.scale(s, s)
        glow(c, R.RES.g_lime, 0, 0, 160, 0.6)
        text_center(c, ">", 0, 40, F(R.RES.mx, 140), P(LIME))
        c.restore()
    draw_kid(c, 170, 1680, 0.58, k.t, "happy", look=(0.6, -0.5), style=ANA,
             hands={"R": (170, -470), "L": (-120, -220)}, talk=talk(k.t))


def scene7(c, k):  # la solución
    lt = k.lt
    camera(c, 1.0, 540, 980, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1660)
    T = k.w
    client_logo(c, 540, 620, 720 * (0.92 + 0.08 * ease_out(prog(lt, 0, 0.4))), a=ease_out(prog(lt, 0, 0.4)))
    step = {"logo": 1, "prods": [1, 1, 1, 1], "precios": 1, "desc": 1, "boton": 1,
            "link": prog(lt, T(9) - 0.2, T(9) + 0.2), "press": prog(lt, T(14) - 0.1, T(14) + 0.3)}
    phone(c, 320, 1140, 380, 720, catalog_screen(k, k.t, step), rot=-3, glow_a=0.7)
    items = [("Precios claros", T(4)), ("Todo en un enlace", T(6)), ("Pedidos en un mensaje", T(11))]
    for i, (txt, tm) in enumerate(items):
        kk = prog(lt, tm - 0.2, tm + 0.2)
        if kk <= 0:
            continue
        s = back_out(kk)
        c.save()
        c.translate(780, 900 + i * 170)
        c.scale(s, s)
        rrect(c, -250, -62, 250, 62, 30, P("#1d1432", alpha=0.95))
        rrect(c, -250, -62, 250, 62, 30, P(LIME, "stroke", 3))
        oval(c, -190, 0, 34, 34, P(LIME))
        m = skia.Path()
        m.moveTo(-205, 0)
        m.lineTo(-194, 12)
        m.lineTo(-174, -12)
        c.drawPath(m, P("#14061f", "stroke", 8))
        f = F(R.RES.mx, 32)
        sc = min(1.0, 330 / f.measureText(txt))
        c.save()
        c.translate(-140, 12)
        c.scale(sc, sc)
        c.drawString(txt, 0, 0, f, P("#ffffff"))
        c.restore()
        c.restore()


def scene8(c, k):  # Comenta ERRORES
    lt = k.lt
    camera(c, 1.0, 540, 960, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1640)
    T = k.w
    word = "ERRORES"
    r = rng(23)
    for i in range(24):
        side = -1 if i % 2 == 0 else 1
        x = 540 + side * (330 + r.random() * 160)
        u = (lt - (T(1) + i * 0.15)) / 2.6
        if u <= 0 or u >= 1:
            continue
        y = lerp(1500, 520, u)
        a = math.sin(math.pi * u)
        txt = [word, "¡" + word + "!", word + "!!", word][i % 4]
        f = F(R.RES.mx, 30)
        w = f.measureText(txt) + 76
        c.save()
        c.translate(x + 20 * math.sin(lt * 2 + i), y)
        rrect(c, -w / 2, -28, w / 2, 28, 28, P("#2c2540", alpha=0.9 * a))
        oval(c, -w / 2 + 28, 0, 16, 16, P([VIO2, LIME, "#ff6fb1", "#5ad1ff"][i % 4], alpha=a))
        c.drawString(txt, -w / 2 + 54, 11, f, P("#ffffff", alpha=a))
        c.restore()
    client_logo(c, 540, 630, 700, a=ease_out(prog(lt, 0, 0.4)))
    bk = ease_out(prog(lt, 0.1, 0.4))
    c.save()
    c.translate(540, 880)
    rrect(c, -380, -56, 380, 56, 56, P("#ffffff", alpha=bk))
    oval(c, -320, 0, 34, 34, P(VIO, alpha=bk))
    typed = word[: int(len(word) * prog(lt, T(1) - 0.5, T(1) + 0.15))]
    if typed:
        c.drawString(typed, -265, 18, F(R.RES.mx, 50), P("#14061f", alpha=bk))
    else:
        c.drawString("Agrega un comentario...", -265, 14, F(R.RES.ms, 34), P("#8a7aa8", alpha=bk))
    oval(c, 320, 0, 38, 38, P(LIME if lt > T(1) + 0.2 else "#d9d0ea", alpha=bk))
    ar = skia.Path()
    ar.moveTo(305, -16)
    ar.lineTo(338, 0)
    ar.lineTo(305, 16)
    ar.close()
    c.drawPath(ar, P("#14061f", alpha=bk))
    c.restore()
    gk = prog(lt, T(6) - 0.2, T(6) + 0.25)
    if gk > 0:
        s = back_out(gk)
        c.save()
        c.translate(540, 1100)
        c.scale(s, s)
        glow(c, R.RES.g_lime, 0, 0, 420, 0.5)
        rrect(c, -390, -100, 390, 100, 44, P(LIME))
        text_center(c, "Te hacemos tu página", 0, -18, F(R.RES.mx, 50), P("#14061f"))
        text_center(c, "100% GRATIS", 0, 56, F(R.RES.mx, 70), P("#14061f"))
        c.restore()
        use("lime")
        R.burst(c, 540, 1100, lt - T(7) + 0.1, dur=1.1, n=50, radius=420, seed=7, intensity=0.8)
    draw_kid(c, 180, 1630, 0.68, k.t, "happy", look=(0.7, -0.4), style=ANA,
             hands={"R": (170, -480 + 30 * math.sin(lt * 9)), "L": (-120, -220)}, talk=talk(k.t))


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8]


def install():
    E2.install()
    R.SCENES = SCENES


if __name__ == "__main__":
    install()
    R.main()
