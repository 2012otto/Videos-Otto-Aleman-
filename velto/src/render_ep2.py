"""Velto — serie con Ana, episodio 2: "Si no te encuentran... no te compran".

Uso (desde la raíz del repo):
  VIDEO_BUILD=$PWD/velto/build_ep2 VO_TRIM=0.3 python3 velto/src/render_ep2.py --start 0 --end 8 --out velto/build_ep2/prueba.mp4
"""
import math
import os
import subprocess
import sys

import numpy as np
import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_velto as V  # noqa: E402
from render_velto import (R, P, RECT, ANA, CLIENTE, VIO, VIO2, LIME, F, back_out, clamp, ease_in_out,  # noqa: E402
                          ease_out, glow, lerp, lin, oval, prog, rrect, smooth, text_center, draw_kid, rng,
                          neon_bg, phone, catalog_screen, client_logo, chat_icon, ring, necklace, earrings,
                          bracelet, use, W, H)
import timeline  # noqa: E402

camera = R.camera
ENV = None  # envolvente de la voz (60 valores por segundo) para mover la boca de Ana


def build_env():
    vo, total = timeline.load()
    fps = 60
    env = np.zeros(int(total * fps) + 2)
    for s in vo:
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", s["file"], "-ac", "1", "-ar", "8000",
                                       "-f", "s16le", "-"])
        x = np.frombuffer(raw, np.int16).astype(float) / 32768
        hop = 8000 // fps
        n = len(x) // hop
        r = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1))
        i0 = int(s["vo_start"] * fps)
        m = min(n, len(env) - i0)
        env[i0:i0 + m] = np.maximum(env[i0:i0 + m], r[:m])
    env /= np.percentile(env[env > 0], 95) + 1e-9
    return np.clip(env, 0, 1)


def talk(t):
    if ENV is None:
        return 0.0
    i = int(t * 60)
    if i < 0 or i >= len(ENV):
        return 0.0
    v = ENV[i]
    return clamp((v - 0.12) * 1.5)


def big_text(c, lines, x, y, size, lh, k=1.0):
    """Texto gigante centrado; lines = [(texto, color)]."""
    f = F(R.RES.mx, size)
    for i, (txt, col) in enumerate(lines):
        yy = y + i * lh
        w = f.measureText(txt)
        c.drawString(txt, x - w / 2 + 4, yy + 6, f, P("#000000", alpha=0.45 * k, blur=6))
        c.drawString(txt, x - w / 2, yy, f, P(col, alpha=k))


def star(c, x, y, r, paint):
    pth = skia.Path()
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        (pth.moveTo if i == 0 else pth.lineTo)(x + math.cos(a) * rr, y + math.sin(a) * rr)
    pth.close()
    c.drawPath(pth, paint)


def magnifier(c, x, y, r, col="#ffffff"):
    oval(c, x, y, r, r, P(col, "stroke", r * 0.32))
    c.drawLine(x + r * 0.7, y + r * 0.7, x + r * 1.5, y + r * 1.5, P(col, "stroke", r * 0.36))


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def scene1(c, k):  # GANCHO
    lt = k.lt
    camera(c, 1.0 + 0.03 * ease_out(prog(lt, 0, k.D)), 540, 960, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1600)
    punch = 1 + 0.07 * (1 - ease_out(prog(lt, 0, 0.35)))
    c.save()
    c.translate(540, 720)
    c.scale(punch, punch)
    big_text(c, [("¿TU NEGOCIO", "#ffffff"), ("EXISTE EN", "#ffffff"), ("INTERNET?", LIME)], 0, -40, 108, 112)
    c.restore()
    # buscador
    x0, y0, x1, y1 = 110, 990, 970, 1440
    rrect(c, x0, y0, x1, y1, 36, P("#1b1230", alpha=0.95))
    rrect(c, x0, y0, x1, y1, 36, P("#b98aff", "stroke", 3, alpha=0.7))
    rrect(c, x0 + 30, y0 + 28, x1 - 30, y0 + 108, 40, P("#ffffff"))
    magnifier(c, x0 + 82, y0 + 62, 16, "#6a5a8a")
    q = "joyería en Xela"
    n = int(len(q) * prog(lt, 0.15, 1.1))
    c.drawString(q[:n], x0 + 125, y0 + 82, F(R.RES.mb, 40), P("#1b1230"))
    if (lt * 2) % 1 < 0.5 and n < len(q):
        c.drawLine(x0 + 130 + F(R.RES.mb, 40).measureText(q[:n]), y0 + 48, x0 + 130 + F(R.RES.mb, 40).measureText(q[:n]),
                   y0 + 90, P("#1b1230", "stroke", 3))
    shops = [("Joyas Luna", "4.8"), ("Plata Fina", "4.6"), ("Brillo GT", "4.9")]
    for i, (nm, st) in enumerate(shops):
        kk = ease_out(prog(lt, 1.2 + i * 0.15, 1.45 + i * 0.15))
        if kk <= 0:
            continue
        yy = y0 + 140 + i * 82
        c.save()
        c.translate(30 * (1 - kk), 0)
        rrect(c, x0 + 30, yy, x0 + 100, yy + 62, 14, P("#3a2a5a", alpha=kk))
        [ring, necklace, earrings][i](c, x0 + 65, yy + 32, 0.45)
        c.drawString(nm, x0 + 125, yy + 42, F(R.RES.mb, 36), P("#ffffff", alpha=kk))
        star(c, x1 - 150, yy + 31, 15, P("#f4cf6a", alpha=kk))
        c.drawString(st, x1 - 128, yy + 42, F(R.RES.mb, 32), P("#f4cf6a", alpha=kk))
        c.restore()
    zk = prog(lt, 2.0, 2.25)
    if zk > 0:
        blink = 0.65 + 0.35 * (math.sin(lt * 14) > 0)
        sh = math.sin(lt * 50) * 8 * (1 - prog(lt, 2.25, 2.7))
        c.save()
        c.translate(sh, 0)
        s = back_out(zk)
        c.translate(540, y1 - 18)
        c.scale(s, s)
        rrect(c, -360, -40, 360, 40, 20, P("#ff3b5c", alpha=blink))
        text_center(c, "Tu negocio: 0 resultados", 0, 14, F(R.RES.mx, 38), P("#ffffff"))
        c.restore()


def shop_card(c, x, y, kind, k, hl=0.0, t=0.0):
    if k <= 0:
        return
    s = back_out(k)
    w, h = 290, 400
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if hl > 0:
        glow(c, R.RES.g_lime if kind == 2 else R.RES.g_vio, 0, 0, 300, 0.5 * hl)
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, 28, P("#1d1432"))
    border = LIME if kind == 2 else "#6a5a8a"
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, 28, P(border, "stroke", 3 + 3 * hl))
    c.drawString(["Tienda A", "Tienda B", "Tienda C"][kind], -w / 2 + 22, -h / 2 + 46, F(R.RES.mb, 30), P("#ffffff"))
    for i in range(4):
        cx, cy = -66 + (i % 2) * 132, -60 + (i // 2) * 150
        if kind == 0:  # fotos borrosas
            oval(c, cx, cy, 52, 52, P("#5a5068", blur=14))
            oval(c, cx + 10, cy - 8, 30, 26, P("#8a7a9a", blur=12))
        else:
            rrect(c, cx - 56, cy - 56, cx + 56, cy + 40, 14, P("#fdf6ff"))
            [ring, necklace, earrings, bracelet][i](c, cx, cy - 10, 0.6)
            if kind == 1:
                c.drawString("Q ??", cx - 40, cy + 82, F(R.RES.mx, 28), P("#ff5c7a"))
            else:
                c.drawString(["Q120", "Q175", "Q95", "Q140"][i], cx - 44, cy + 82, F(R.RES.mx, 28), P(LIME))
    c.restore()


def scene2(c, k):  # el cliente compara
    lt = k.lt
    camera(c, lerp(1.04, 1.0, ease_out(prog(lt, 0, 1.5))), 540, 980, k.t)
    neon_bg(c, k.t, grid=0.08, wy=1620)
    T = k.w
    focus = 0 if lt < T(8) - 0.1 else (1 if lt < T(12) - 0.1 else 2)
    for i in range(3):
        kk = prog(lt, 0.05 + i * 0.15, 0.4 + i * 0.15)
        hl = 1.0 if (i == focus and lt > T(6) - 0.2) else 0.0
        shop_card(c, 200 + i * 340, 820 + 8 * math.sin(k.t * 2 + i), i, kk, hl, k.t)
    look = [(-1, -0.7), (0, -0.9), (1, -0.7)][focus] if lt > T(6) - 0.2 else (0, 0.4)

    def held(cc, out):
        hx, hy = out["R"]
        phone(cc, hx - 30, hy - 40, 90, 160, lambda *a: None, rot=10, glow_a=0.2)
    draw_kid(c, 540, 1590, 0.78, k.t, "neutral" if focus < 2 else "happy", look=look, style=CLIENTE,
             hands={"R": (60, -300), "L": (-110, -200)}, front_props=held)


def scene3(c, k):  # perfil desordenado y "precio por inbox"
    lt = k.lt
    camera(c, 1.0, 540, 980, k.t)
    neon_bg(c, k.t, grid=0.08, wy=1620)
    T = k.w
    swipe = ease_in_out(prog(lt, T(14) - 0.1, T(14) + 0.5))

    def messy(c2, x0, y0, x1, y1):
        oval(c2, x0 + 70, y0 + 90, 40, 40, P("#6a5a8a"))
        c2.drawString("mi_tienda_gt", x0 + 125, y0 + 102, F(R.RES.mb, 30), P("#ffffff"))
        r = rng(4)
        tw = (x1 - x0 - 40) / 3
        for i in range(9):
            cx = x0 + 20 + (i % 3) * tw + tw / 2
            cy = y0 + 200 + (i // 3) * tw + tw / 2
            c2.save()
            c2.translate(cx, cy)
            c2.rotate((r.random() - .5) * 18)
            col = ["#7a5a6a", "#4a4a5a", "#8a7a5a", "#5a3a4a", "#6a6a7a"][i % 5]
            rrect(c2, -tw / 2 + 6, -tw / 2 + 6, tw / 2 - 6, tw / 2 - 6, 8, P(col, blur=3 if i % 2 else 0))
            c2.restore()
    c.save()
    c.translate(-700 * swipe, 0)
    c.rotate(-10 * swipe)
    phone(c, 360, 1000, 460, 840, messy, rot=-3, glow_a=0.4 * (1 - swipe))
    for j, (sx, sy, rot) in enumerate(((330, 900, -12), (420, 1110, 9), (300, 1260, -6))):
        kk = prog(lt, T(11) - 0.15 + j * 0.22, T(11) + 0.1 + j * 0.22)
        if kk <= 0:
            continue
        s = back_out(kk, 2.5)
        c.save()
        c.translate(sx, sy)
        c.rotate(rot)
        c.scale(s, s)
        rrect(c, -170, -38, 170, 38, 14, P("#ff3b5c"))
        rrect(c, -170, -38, 170, 38, 14, P("#ffffff", "stroke", 4))
        text_center(c, "Precio por inbox", 0, 12, F(R.RES.mx, 34), P("#ffffff"))
        c.restore()
    c.restore()
    # la tienda que sí se lo pone fácil
    good = prog(lt, T(16) - 0.3, T(16) + 0.2)
    shop_card(c, 760, 820 + 8 * math.sin(k.t * 2), 2, good, hl=1.0 if good > 0.5 else 0.0)
    happy = lt > T(18)
    expr = "worried" if lt > T(8) - 0.1 and not happy else ("happy" if happy else "neutral")
    look = (-1, -0.4) if swipe < 0.5 else (1, -0.6)
    draw_kid(c, 820 if not happy else 640, 1590, 0.74, k.t, expr, look=look, style=CLIENTE,
             hands={"R": (130, -240), "L": (-130, -240)} if not happy else {"R": (180, -470), "L": (-120, -220)})
    if swipe > 0 and swipe < 1:
        glow(c, R.RES.glow_white, lerp(500, 100, swipe), 1000, 120, 0.4 * (1 - swipe))


def scene4(c, k):  # Ana: "Pero ojo"
    lt = k.lt
    camera(c, lerp(1.06, 1.0, ease_out(prog(lt, 0, 1.2))), 540, 980, k.t)
    neon_bg(c, k.t, grid=0.10, wy=1640)
    T = k.w
    ojo = lt > T(1) - 0.15
    hands = {"R": (150, -600) if ojo and lt < T(7) else (130, -260), "L": (-120, -230)}
    if lt > T(8) - 0.1:
        hands = {"R": (220, -560), "L": (-120, -230)}
    draw_kid(c, 540, 1930, 1.42, k.t, "happy", look=(0, 0), tilt=3 * math.sin(k.t * 1.3), style=ANA, hands=hands,
             talk=talk(k.t))
    # página carísima tachada
    ck = prog(lt, T(4) - 0.2, T(4) + 0.2) * (1 - prog(lt, T(7) - 0.2, T(7) + 0.05))
    if ck > 0:
        s = back_out(min(1, ck * 1.5))
        c.save()
        c.translate(540, 760)
        c.scale(s, s)
        rrect(c, -300, -150, 300, 150, 30, P("#f4f2f8", alpha=ck))
        c.drawString("Página web", -250, -70, F(R.RES.mx, 50), P("#2a1a40", alpha=ck))
        c.drawString("Q8,000+", -250, 30, F(R.RES.mx, 84), P("#d62a4a", alpha=ck))
        c.drawString("+ programador", -250, 100, F(R.RES.mb, 34), P("#4a3a60", alpha=ck))
        x = ease_out(prog(lt, T(6) - 0.1, T(6) + 0.2))
        if x > 0:
            c.drawLine(-320, -170, -320 + 640 * x, -170 + 340 * x, P(LIME, "stroke", 26, alpha=ck))
            c.drawLine(320, -170, 320 - 640 * x, -170 + 340 * x, P(LIME, "stroke", 26, alpha=ck))
        c.restore()
    tk = prog(lt, T(8) - 0.15, T(8) + 0.25)
    if tk > 0:
        s = back_out(tk, 2.2)
        c.save()
        c.translate(540, 780)
        c.scale(s, s)
        glow(c, R.RES.g_lime, 0, -40, 380, 0.7)
        f = F(R.RES.mx, 360)
        text_center(c, "3", 0, 90, f, P(LIME))
        text_center(c, "cosas", 0, 190, F(R.RES.mx, 70), P("#ffffff"))
        c.restore()
        use("lime")
        R.burst(c, 540, 760, lt - T(8) + 0.1, dur=1.0, n=40, radius=360, seed=4, intensity=0.8)


CHECKS = [("1", "Fotos y precios", "fotos"), ("2", "Un enlace en tu bio", "enlace"), ("3", "Pedidos por mensaje", "mensaje")]


def scene5(c, k):  # checklist 1-2-3
    lt = k.lt
    camera(c, 1.0, 540, 980, k.t)
    neon_bg(c, k.t, grid=0.10, wy=1640)
    T = k.w
    starts, ends = [T(0), T(7), T(14)], [T(6), T(13), T(20)]
    for i, (num, title, kind) in enumerate(CHECKS):
        kk = prog(lt, starts[i] - 0.15, starts[i] + 0.25)
        if kk <= 0:
            continue
        x, y = 430, 660 + i * 250
        s = back_out(kk)
        active = starts[i] - 0.15 <= lt < (starts[i + 1] - 0.15 if i < 2 else 99)
        c.save()
        c.translate(x, y)
        c.scale(s, s)
        if active:
            glow(c, R.RES.g_vio, 0, 0, 420, 0.45)
        rrect(c, -350, -100, 350, 100, 30, P("#1d1432", alpha=0.96))
        rrect(c, -350, -100, 350, 100, 30, P(LIME if active else "#7a5aa8", "stroke", 4 if active else 2))
        oval(c, -280, 0, 44, 44, P(LIME))
        text_center(c, num, -280, 20, F(R.RES.mx, 54), P("#14061f"))
        # ícono
        if kind == "fotos":
            rrect(c, -210, -60, -110, 40, 14, P("#fdf6ff"))
            ring(c, -160, -18, 0.6)
            c.drawString("Q120", -200, 76, F(R.RES.mx, 26), P(LIME))
        elif kind == "enlace":
            rrect(c, -220, -26, -100, 26, 26, P(LIME))
            oval(c, -196, 0, 10, 10, P("#14061f", "stroke", 4))
            oval(c, -180, 0, 10, 10, P("#14061f", "stroke", 4))
            c.drawString("bio", -160, 10, F(R.RES.mx, 26), P("#14061f"))
        else:
            chat_icon(c, -160, 0, 40)
        ft = F(R.RES.mx, 38)
        sc = min(1.0, 400 / ft.measureText(title))
        c.save()
        c.translate(-80, 14)
        c.scale(sc, sc)
        c.drawString(title, 0, 0, ft, P("#ffffff"))
        c.restore()
        ck = prog(lt, ends[i], ends[i] + 0.25)
        if ck > 0:
            cs = back_out(ck, 2.4)
            c.save()
            c.translate(300, -60)
            c.scale(cs, cs)
            oval(c, 0, 0, 34, 34, P(LIME))
            m = skia.Path()
            m.moveTo(-15, 0)
            m.lineTo(-4, 12)
            m.lineTo(17, -12)
            c.drawPath(m, P("#14061f", "stroke", 8))
            c.restore()
        c.restore()
    point = [(-200, -420), (-220, -380), (-200, -300)][min(2, sum(lt >= s - 0.15 for s in starts) - 1)] \
        if lt > starts[0] - 0.15 else (-120, -220)
    draw_kid(c, 930, 1620, 0.72, k.t, "happy", look=(-0.8, -0.3), style=ANA, tilt=-4,
             hands={"L": point, "R": (120, -220)}, talk=talk(k.t))


def scene6(c, k):  # eso hace Velto
    lt = k.lt
    camera(c, 1.0, 540, 980, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1640)
    T = k.w
    lk = ease_out(prog(lt, T(6) - 0.25, T(6) + 0.2))
    if lk > 0:
        client_logo(c, 540, 640, 760 * (0.92 + 0.08 * lk), a=lk)
    b = lambda a: prog(lt, a, a + 0.3)  # noqa: E731
    step = {"logo": b(0.2), "prods": [b(0.5 + i * 0.2) for i in range(4)], "precios": b(1.5),
            "desc": prog(lt, 1.6, 2.4), "boton": b(2.6)}
    phone(c, 680, 1130, 400, 740, catalog_screen(k, k.t, step), rot=3, glow_a=0.8)
    use("lime")
    R.orbit_sparkles(c, 680, 1130, k.t, 240, 380, n=20, seed=8, intensity=0.5)
    draw_kid(c, 210, 1620, 0.74, k.t, "happy", look=(0.8, -0.3), style=ANA, tilt=4,
             hands={"R": (190, -420), "L": (-120, -220)}, talk=talk(k.t))


def scene7(c, k):  # Comenta ANA
    lt = k.lt
    camera(c, 1.0, 540, 960, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1640)
    T = k.w
    # lluvia de comentarios "ANA"
    r = rng(21)
    start = T(1)
    for i in range(22):
        side = -1 if i % 2 == 0 else 1
        x = 540 + side * (330 + r.random() * 160)
        t0 = start + i * 0.16
        u = (lt - t0) / 2.6
        if u <= 0 or u >= 1:
            continue
        y = lerp(1500, 520, u)
        a = math.sin(math.pi * u)
        txt = ["ANA", "¡ANA!", "ANA!!", "ANA"][i % 4]
        f = F(R.RES.mx, 34)
        w = f.measureText(txt) + 80
        c.save()
        c.translate(x + 20 * math.sin(lt * 2 + i), y)
        rrect(c, -w / 2, -30, w / 2, 30, 30, P("#2c2540", alpha=0.9 * a))
        oval(c, -w / 2 + 30, 0, 18, 18, P([VIO2, LIME, "#ff6fb1", "#5ad1ff"][i % 4], alpha=a))
        c.drawString(txt, -w / 2 + 58, 12, f, P("#ffffff", alpha=a))
        c.restore()
    client_logo(c, 540, 630, 700, a=ease_out(prog(lt, 0, 0.4)))
    # caja de comentario
    bk = ease_out(prog(lt, 0.1, 0.4))
    c.save()
    c.translate(540, 880)
    rrect(c, -380, -56, 380, 56, 56, P("#ffffff", alpha=bk))
    oval(c, -320, 0, 34, 34, P(VIO, alpha=bk))
    typed = "ANA"[: int(3 * prog(lt, T(1) - 0.35, T(1) + 0.05))]
    if typed:
        c.drawString(typed, -265, 18, F(R.RES.mx, 50), P("#14061f", alpha=bk))
    else:
        c.drawString("Agrega un comentario...", -265, 14, F(R.RES.ms, 34), P("#8a7aa8", alpha=bk))
    send = prog(lt, T(1) + 0.1, T(1) + 0.3)
    oval(c, 320, 0, 38, 38, P(LIME if send > 0 else "#d9d0ea", alpha=bk))
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
    joy = lt > T(8)
    draw_kid(c, 180, 1630, 0.68, k.t, "joy" if joy and talk(k.t) < 0.1 else "happy", look=(0.7, -0.4), style=ANA,
             hands={"R": (170, -480 + 30 * math.sin(lt * 9)), "L": (-120, -220)}, talk=talk(k.t))


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7]


def install():
    global ENV
    V.install()
    R.SCENES = SCENES
    R.FADE_IN = 0.0  # el gancho se ve desde el primer cuadro
    ENV = build_env()


if __name__ == "__main__":
    install()
    R.main()
