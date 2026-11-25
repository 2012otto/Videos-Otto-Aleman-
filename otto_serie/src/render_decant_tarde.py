"""Otto Aleman Perfumes — "Te enamoró en la mañana… y en la tarde ya no": por qué probar en decant.

Estilo de la referencia: personaje (diseño A, otto_serie/src/mascota.py) con poses y expresiones,
fondos crema que cambian de color con la emoción, títulos grandes arriba, cursiva elegante y
subtítulos abajo en pastilla. Decant negro y perfumes reales animados. Voz: David.
Uso:
  VIDEO_BUILD=$PWD/otto_serie/build_decant VO_TRIM=0.15 VO_GAP=0.2 VO_TAIL=1.8 \
    python3 otto_serie/src/render_decant_tarde.py --out otto_serie/build_decant/video_mudo.mp4
"""
import math
import os
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src"))
import render as R  # noqa: E402
from render import (P, lin, rad, oval, rrect, clamp, lerp, smooth, ease_out, ease_in_out, back_out, prog, rng,  # noqa: E402
                    glow, text_center, W, H)
import mascota as M  # noqa: E402
import render_ep2 as O2  # noqa: E402
import render_ep4 as O4  # noqa: E402

RECT = R.R
ST = M.STYLES["A"]
INK, GOLDD, CREAM = "#1a1010", "#b8862a", "#f6efe4"


def F(tf, size):
    return R.font(tf, size)


# ----------------------------------------------------------------------------
# fondos y textos
# ----------------------------------------------------------------------------


def bg(c, t, mood="cream", k=1.0, room=True):
    cols = {"cream": ("#fbf5ec", "#efe3d0"), "gold": ("#fff1c8", "#f6cf7a"), "gray": ("#d8d6d4", "#a8a6a8"),
            "green": ("#d8f0c0", "#8ccf6a"), "pink": ("#ffe0ec", "#f4a8c8"), "white": ("#ffffff", "#f2eee8")}[mood]
    c.drawRect(RECT(-200, -200, W + 200, H + 200), P(cols[0], shader=rad(540, 900, 1300, list(cols))))
    if mood in ("gold", "green"):
        c.save()
        c.translate(540, 1000)
        c.rotate(t * 8)
        for i in range(18):
            p = skia.Path()
            a0, a1 = math.radians(i * 20), math.radians(i * 20 + 9)
            p.moveTo(0, 0)
            p.lineTo(math.cos(a0) * 1800, math.sin(a0) * 1800)
            p.lineTo(math.cos(a1) * 1800, math.sin(a1) * 1800)
            p.close()
            c.drawPath(p, P("#ffffff", alpha=0.25))
        c.restore()
    if room and mood in ("cream", "gray"):
        dim = 0.0 if mood == "cream" else 0.25
        # ventana, cuadro y repisa (como una habitación sencilla)
        rrect(c, 700, 640, 960, 980, 10, P(R.mix_col("#bfe0f4", "#8a8a96", dim)))
        rrect(c, 700, 640, 960, 980, 10, P("#c8b090", "stroke", 14))
        c.drawLine(830, 640, 830, 980, P("#c8b090", "stroke", 10))
        c.drawLine(700, 810, 960, 810, P("#c8b090", "stroke", 10))
        rrect(c, 110, 680, 330, 830, 8, P("#ffffff"))
        rrect(c, 110, 680, 330, 830, 8, P("#c8b090", "stroke", 8))
        tri = skia.Path()
        tri.moveTo(140, 810)
        tri.lineTo(200, 740)
        tri.lineTo(250, 790)
        tri.lineTo(280, 760)
        tri.lineTo(310, 810)
        tri.close()
        c.drawPath(tri, P("#d8c8b0"))
        c.drawRect(RECT(-200, 1470, W + 200, H + 200), P("#e6d6bc", shader=lin(0, 1470, 0, H, ["#e8d8be", "#d8c4a4"])))
    if mood == "pink":
        r = rng(4)
        for i in range(16):  # papelitos
            x = r.random() * W
            y = (r.random() * H + t * 120) % H
            c.save()
            c.translate(x, y)
            c.rotate(t * 90 + i * 30)
            c.drawRect(RECT(-12, -12, 12, 12), P("#ffffff", alpha=0.7))
            c.restore()


def title(c, txt, k, y=330, size=84, col=INK, rot=0.0):
    if k <= 0:
        return
    s = back_out(clamp(k), 1.8)
    f = F(R.RES.xbold, size)
    lines = txt.split("\n")
    c.save()
    c.translate(540, y)
    c.rotate(rot)
    c.scale(s, s)
    for i, ln in enumerate(lines):
        w = f.measureText(ln)
        c.drawString(ln, -w / 2, i * size * 1.05, f, P(col))
    c.restore()


def italic(c, txt, k, y=460, size=52, col="#6a4a2a"):
    if k <= 0:
        return
    f = F(R.RES.medium, size)
    w = f.measureText(txt)
    c.save()
    c.translate(540, y)
    c.skew(-0.22, 0)
    c.drawString(txt, -w / 2, 0, f, P(col, alpha=clamp(k * 2)))
    c.restore()


def sticker(c, txt, x, y, k, bg_col=INK, fg="#ffffff", size=40, rot=-6, border=None):
    if k <= 0:
        return
    s = back_out(clamp(k), 2.2)
    f = F(R.RES.xbold, size)
    w = f.measureText(txt) + size * 1.2
    h = size * 1.7
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    rrect(c, -w / 2 + 4, -h / 2 + 6, w / 2 + 4, h / 2 + 6, 14, P("#000000", alpha=0.2))
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, 14, P(bg_col))
    if border:
        rrect(c, -w / 2, -h / 2, w / 2, h / 2, 14, P(border, "stroke", 5))
    c.drawString(txt, -f.measureText(txt) / 2, size * 0.36, f, P(fg))
    c.restore()


# ----------------------------------------------------------------------------
# personaje
# ----------------------------------------------------------------------------


def track(lt, keys, dur=0.25):
    """keys: [(t, pose)], pose = nombre o dict. Interpola entre poses consecutivas."""
    def get(p):
        return M.POSES[p] if isinstance(p, str) else p
    cur = get(keys[0][1])
    for i in range(1, len(keys)):
        t0, p = keys[i]
        if lt >= t0:
            u = clamp((lt - t0) / dur)
            cur = M.blend(cur, get(p), ease_in_out(u))
    return cur


def hero(c, k, x, y, s, keys, talk=False, hold_fn=None):
    p = track(k.lt, keys)
    tk = M.talk_amount(k.t, k.s["tokens"]) if talk else 0.0
    M.draw(c, x, y, s, k.t, p, style=ST, talk=tk, hold_fn=hold_fn)


def small_person(c, x, y, s, t, style, pose):
    M.draw(c, x, y, s, t, M.POSES[pose], style=M.STYLES[style])


# ----------------------------------------------------------------------------
# objetos
# ----------------------------------------------------------------------------


def decant(c, x, y, h, rot=0.0, t=0.0, glow_a=0.0):
    O4.decant_vec(c, x, y, h, rot, t, 0.62, glow_a)


def hold_decant(t):
    return lambda c, x, y: decant(c, x, y - 70, 150, -6, t)


BOTTLES = [O2.odyssey, O2.asad, O2.hawas]


def bottle(c, i, x, y, s, rot=0.0, glow_a=0.0):
    BOTTLES[i % 3](c, x, y, s, rot, glow_a)


def phone(c, x, y, s, draw_screen, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    rrect(c, -150, -300, 150, 300, 40, P("#1a1a1e"))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(RECT(-136, -286, 136, 286), 30, 30), True)
    draw_screen(c)
    c.restore()
    rrect(c, -40, -280, 40, -262, 9, P("#000000"))
    c.restore()


def review_screen(style, pose, t, hearts=True):
    def d(c):
        c.drawRect(RECT(-140, -290, 140, 290), P("#f4ece2"))
        M.draw(c, 0, 250, 0.42, t, M.POSES[pose], style=M.STYLES[style])
        if hearts:
            for i in range(3):
                u = (t * 0.7 + i / 3) % 1
                hp = skia.Path()
                hx, hy = 100, 200 - u * 300
                hp.moveTo(hx, hy + 12)
                hp.cubicTo(hx - 20, hy - 2, hx - 10, hy - 18, hx, hy - 6)
                hp.cubicTo(hx + 10, hy - 18, hx + 20, hy - 2, hx, hy + 12)
                c.drawPath(hp, P("#ff3d6a", alpha=1 - u))
    return d


def laptop(c, x, y, s, t, click):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -300, -330, 300, 0, 20, P("#2a2a30"))
    rrect(c, -284, -314, 284, -16, 10, P("#ffffff"))
    rrect(c, -260, -290, -60, -60, 12, P("#f4ece2"))
    bottle(c, 1, -160, -110, 0.55)
    c.drawString("Perfume viral", -40, -250, F(R.RES.bold, 34), P(INK))
    c.drawString("★★★★★", -40, -205, F(R.RES.bold, 28), P("#e0a020"))
    c.drawString("Q500", -40, -150, F(R.RES.xbold, 44), P(INK))
    pr = click
    rrect(c, -40, -120 + 4 * pr, 200, -66 + 4 * pr, 27, P("#b8862a" if pr < 0.5 else "#8a6018"))
    text_center(c, "COMPRAR", 80, -82 + 4 * pr, F(R.RES.xbold, 30), P("#ffffff"))
    base = skia.Path()
    base.moveTo(-340, 0)
    base.lineTo(340, 0)
    base.lineTo(370, 30)
    base.lineTo(-370, 30)
    base.close()
    c.drawPath(base, P("#c8c4cc"))
    c.restore()


def box(c, x, y, s, open_k, rip=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(RECT(-200, -150, 200, 120), P("#c8925a", shader=lin(-200, 0, 200, 0, ["#d8a26a", "#b8824a"])))
    for sd in (-1, 1):  # solapas
        c.save()
        c.translate(sd * 200, -150)
        c.rotate(-sd * 140 * ease_out(open_k))
        c.drawRect(RECT(-200 if sd > 0 else 0, -60, 0 if sd > 0 else 200, 0), P("#d8a26a"))
        c.restore()
    if open_k < 0.3:
        c.drawRect(RECT(-30, -150, 30, 120), P("#e8d8b8", alpha=0.7 * (1 - rip)))
    rrect(c, -150, -60, 0, 0, 6, P("#ffffff"))
    for i in range(3):
        c.drawLine(-130, -46 + i * 14, -30, -46 + i * 14, P("#b0a8a0", "stroke", 3))
    c.restore()


def mist(c, x, y, t0, lt, n=26, dirx=1.0):
    u = lt - t0
    if not (0 < u < 1.4):
        return
    r = rng(7)
    for i in range(n):
        a = math.radians(-20 + r.random() * 40)
        d = (120 + r.random() * 260) * ease_out(clamp(u / 1.0))
        px = x + math.cos(a) * d * dirx
        py = y + math.sin(a) * d - 20 * u
        oval(c, px, py, 6 + 10 * r.random(), 6 + 10 * r.random(), P("#ffffff", alpha=0.7 * (1 - u / 1.4)))


def clock(c, x, y, r, hours):
    oval(c, x, y, r, r, P("#ffffff"))
    oval(c, x, y, r, r, P(INK, "stroke", r * 0.08))
    for i in range(12):
        a = i * math.pi / 6
        c.drawLine(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78, x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9, P(INK, "stroke", 5))
    ah = (hours % 12) / 12 * 2 * math.pi - math.pi / 2
    am = (hours % 1) * 2 * math.pi - math.pi / 2
    c.drawLine(x, y, x + math.cos(ah) * r * 0.5, y + math.sin(ah) * r * 0.5, P(INK, "stroke", 12))
    c.drawLine(x, y, x + math.cos(am) * r * 0.75, y + math.sin(am) * r * 0.75, P(INK, "stroke", 7))
    oval(c, x, y, 10, 10, P(GOLDD))


def note_icon(c, kind, x, y, s, a):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if kind == 0:  # cítrico
        oval(c, 0, 0, 34, 34, P("#ffc83a", alpha=a))
        for i in range(6):
            ang = i * math.pi / 3
            c.drawLine(0, 0, math.cos(ang) * 28, math.sin(ang) * 28, P("#fff4c0", "stroke", 3, alpha=a))
    elif kind == 1:  # hoja verde
        lf = skia.Path()
        lf.moveTo(0, 30)
        lf.quadTo(-34, 0, 0, -34)
        lf.quadTo(34, 0, 0, 30)
        c.drawPath(lf, P("#6abf4a", alpha=a))
    elif kind == 2:  # flor
        for i in range(5):
            ang = i * 2 * math.pi / 5
            oval(c, math.cos(ang) * 16, math.sin(ang) * 16, 14, 14, P("#ff9ac0", alpha=a))
        oval(c, 0, 0, 10, 10, P("#ffe04a", alpha=a))
    else:  # fondo pesado (resina/vainilla)
        oval(c, 0, 0, 30, 30, P("#7a4a6a", alpha=a))
        oval(c, -8, -8, 10, 10, P("#a87a9a", alpha=a))
    c.restore()


def scale_balance(c, x, y, tilt, left_fn, right_fn):
    c.save()
    c.translate(x, y)
    c.drawRect(RECT(-14, -340, 14, 120), P("#8a6a4a"))
    rrect(c, -120, 110, 120, 140, 14, P("#6a4a2a"))
    c.save()
    c.translate(0, -340)
    c.rotate(tilt)
    c.drawRect(RECT(-380, -10, 380, 10), P("#b8862a"))
    pans = []
    for sd in (-1, 1):
        px = sd * 360
        c.drawLine(px, 0, px - 90, 170, P("#8a6a4a", "stroke", 4))
        c.drawLine(px, 0, px + 90, 170, P("#8a6a4a", "stroke", 4))
        pans.append(px)
    c.restore()
    for sd, fn in ((-1, left_fn), (1, right_fn)):
        a = math.radians(tilt)
        px, py = sd * 360 * math.cos(a), -340 + sd * 360 * math.sin(a)
        c.save()
        c.translate(px, py + 170)
        pan = skia.Path()
        pan.addArc(RECT(-110, -40, 110, 40), 0, 180)
        c.drawPath(pan, P("#d6a24a"))
        fn(c)
        c.restore()
    c.restore()


def stamp_card(c, x, y, s, n, t, free_k):
    def d(c2):
        c2.drawRect(RECT(-140, -290, 140, 290), P("#1a1a1e", shader=lin(0, -290, 0, 290, ["#2a2216", "#0e0c0a"])))
        img = M.logo()
        w = 120
        h = w * img.height() / img.width()
        c2.drawImageRect(img, RECT(-w / 2, -250, w / 2, -250 + h), R.SAMP, skia.Paint())
        text_center(c2, "TARJETA DE SELLOS", 0, -120, F(R.RES.bold, 22), P("#f4e2b8"))
        for i in range(6):
            cx, cy = -70 + (i % 3) * 70, -50 + (i // 3) * 80
            oval(c2, cx, cy, 28, 28, P("#3a3226"))
            oval(c2, cx, cy, 28, 28, P("#b8862a", "stroke", 3))
            if i < n:
                ss = back_out(clamp((n - i) * 1.0), 2)
                c2.save()
                c2.translate(cx, cy)
                c2.scale(min(1, ss), min(1, ss))
                oval(c2, 0, 0, 24, 24, P("#d6a24a"))
                text_center(c2, "OA", 0, 8, F(R.RES.xbold, 18), P("#1a1010"))
                c2.restore()
        text_center(c2, f"{min(n, 6)}/6", 0, 120, F(R.RES.xbold, 40), P("#ffffff"))
        if free_k > 0:
            rrect(c2, -110, 160, 110, 230, 20, P("#2fbf71", alpha=free_k))
            text_center(c2, "¡GRATIS!", 0, 208, F(R.RES.xbold, 36), P("#ffffff", alpha=free_k))
    phone(c, x, y, s, d)


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------
FEET = 1480
S0 = 0.86


def scene1(c, k):  # ¡Ey! Si te gustan los perfumes…
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    for i in range(3):  # frascos flotando
        a = k.t * 0.8 + i * 2.1
        bottle(c, i, 540 + math.cos(a) * 360, 820 + math.sin(a * 1.3) * 140, 0.5, 10 * math.sin(a), 0.4)
    c.save()
    z = lerp(1.15, 1.0, ease_out(prog(lt, 0, 0.6)))
    c.translate(540, 1300)
    c.scale(z, z)
    c.translate(-540, -1300)
    hero(c, k, 540, FEET, S0, [(0, "espera"), (T(6) - 0.1, "señala")], talk=True)
    c.restore()
    title(c, "¡EY!", prog(lt, T(0) - 0.1, T(0) + 0.15) * (1 - prog(lt, T(5), T(6) - 0.1)), size=130)
    title(c, "¿TE HA PASADO?", prog(lt, T(6) - 0.1, T(6) + 0.2), size=90)


def scene2(c, k):  # lo ves en todos lados
    lt, T = k.lt, k.w
    bg(c, k.t, "cream", room=False)
    title(c, "LO VES EN\nTODOS LADOS", prog(lt, 0.05, 0.35), y=310, size=80)
    if lt < T(10) - 0.2:
        for i, (st, pose, lab, rot) in enumerate((("C", "enamorado", "JOYAZO", -8), ("D", "pulgar", "OBLIGATORIO", 6), ("B", "celebra", "10/10", -4))):
            ki = prog(lt, T(2 + i * 2) - 0.3, T(2 + i * 2))
            if ki <= 0:
                continue
            x = 240 + i * 300
            y = lerp(1900, 1020, back_out(ki, 1.2))
            phone(c, x, y, 0.8, review_screen(st, pose, k.t), rot)
            sticker(c, lab, x + 40, y - 250, prog(lt, T(2 + i * 2), T(2 + i * 2) + 0.3), bg_col=INK, rot=rot * 1.5, size=34)
    else:
        u = lt - (T(10) - 0.2)
        small_person(c, 230, FEET, 0.6, k.t, "C", "señala")
        small_person(c, 850, FEET, 0.6, k.t, "D", "pulgar")
        hero(c, k, 540, FEET, 0.78, [(0, "neutral"), (T(14) - 0.2, "piensa"), (T(19), "enamorado")])
        bk = prog(u, T(14) - T(10) - 0.2, T(14) - T(10) + 0.2)
        if bk > 0:  # nube de pensamiento con el frasco
            s = back_out(bk, 1.6)
            c.save()
            c.translate(780, 720)
            c.scale(s, s)
            for (bx, by, rr) in ((-80, 160, 18), (-50, 110, 26)):
                oval(c, bx, by, rr, rr, P("#ffffff"))
            for (bx, by, rr) in ((0, 0, 110), (-90, 20, 80), (90, 20, 80), (0, -60, 90)):
                oval(c, bx, by, rr, rr, P("#ffffff"))
            bottle(c, 1, 0, 30, 0.55, 8 * math.sin(k.t * 2), 0.5)
            c.restore()
        italic(c, "y ya no te lo sacás de la cabeza…", prog(lt, T(14), T(15)), y=1380)


def scene3(c, k):  # lo pedís completo
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    title(c, "LO PEDÍS\nCOMPLETO", prog(lt, T(3) - 0.2, T(3) + 0.1), y=310, size=86)
    hero(c, k, 540, FEET + 120, 0.86, [(0, "neutral"), (T(4), "pulgar")])
    click = clamp(1 - abs(lt - T(4) - 0.2) / 0.25)
    laptop(c, 540, 1400, 1.0, k.t, click)
    sticker(c, "Q500", 860, 820, prog(lt, T(5) - 0.1, T(5) + 0.2), bg_col="#b8862a", size=70, rot=10)


def scene4(c, k):  # llega, abrís la caja, en la mañana ¡qué rico!
    lt, T = k.lt, k.w
    morning = prog(lt, T(11) - 0.3, T(11) + 0.2)
    if morning < 1:
        bg(c, k.t, "cream")
    if morning > 0:
        c.saveLayerAlpha(None, int(255 * morning))
        bg(c, k.t, "gold")
        c.restore()
    if lt < T(8) - 0.2:  # puerta + caja
        title(c, "¡POR FIN LLEGA!", prog(lt, 0.05, 0.3), size=84)
        open_k = prog(lt, T(3), T(5))
        box(c, 540, 1300, 1.2 * lerp(0.6, 1.0, ease_out(prog(lt, 0, 0.5))), open_k, prog(lt, T(3) - 0.3, T(3)))
        if open_k > 0.3:
            bottle(c, 1, 540, lerp(1300, 900, ease_out(prog(lt, T(5), T(7)))), 1.0, 0, 0.8 * open_k)
        sticker(c, "RRRIIIP", 820, 760, prog(lt, T(3) - 0.2, T(3) + 0.1) * (1 - prog(lt, T(5), T(5) + 0.3)), bg_col="#ffffff", fg=INK, size=38, rot=8, border=INK)
    else:
        hero(c, k, 540, FEET, S0, [(0, "sostiene"), (T(12), "enamorado")],
             hold_fn=lambda cc, x, y: bottle(cc, 1, x, y - 60, 0.45, -10))
        mist(c, 660, 860, T(8) - 0.1, lt)
        mist(c, 660, 860, T(9) + 0.1, lt)
        title(c, "9:00 AM", morning, size=110)
        sticker(c, "¡QUÉ RICO!", 830, 720, prog(lt, T(13) - 0.1, T(13) + 0.2), bg_col="#2fbf71", size=48, rot=-5)
        for i in range(3):  # todos te preguntan
            kk = prog(lt, T(15) + i * 0.25, T(15) + i * 0.25 + 0.3)
            if kk > 0:
                x = (170, 910, 200)[i]
                y = (1100, 1050, 1350)[i]
                sticker(c, "¿Qué usás?", x, y, kk, bg_col="#ffffff", fg=INK, size=30, rot=(-6, 6, 4)[i], border=INK)


def scene5(c, k):  # a las tres de la tarde… cambia
    lt, T = k.lt, k.w
    g = prog(lt, T(3) - 0.2, T(6))
    bg(c, k.t, "gold")
    if g > 0:
        c.saveLayerAlpha(None, int(255 * g))
        bg(c, k.t, "gray")
        c.restore()
    hours = lerp(9, 15, ease_in_out(prog(lt, 0.1, T(6))))
    clock(c, 820, 760, 140, hours)
    title(c, "3:00 PM", prog(lt, T(6) - 0.2, T(6) + 0.1), size=110)
    hero(c, k, 430, FEET, S0, [(0, "enamorado"), (T(7), "neutral"), (T(9) - 0.2, "piensa")])
    italic(c, "y el perfume cambia…", prog(lt, T(9), T(10)), y=1380)


def scene6(c, k):  # notas de salida se van, queda el fondo, empalaga, marea
    lt, T = k.lt, k.w
    pink = prog(lt, T(18) - 0.2, T(18) + 0.1) * (1 - prog(lt, T(19) - 0.15, T(19)))
    green = prog(lt, T(19) - 0.15, T(19) + 0.1)
    bg(c, k.t, "gray")
    for mood, a in (("pink", pink), ("green", green)):
        if a > 0:
            c.saveLayerAlpha(None, int(255 * a))
            bg(c, k.t, mood)
            c.restore()
    # notas de salida subiendo y desapareciendo
    r = rng(5)
    for i in range(14):
        kind = i % 3
        x = 140 + r.random() * 800
        u = (lt - r.random() * 1.4) / 2.2
        if 0 < u < 1 and lt < T(7) + 0.5:
            note_icon(c, kind, x, lerp(1300, 520, u), 1.2, (1 - u))
    # el fondo pesado rodeándolo
    fk = prog(lt, T(7), T(9) + 0.3)
    if fk > 0:
        for i in range(10):
            a = k.t * 1.5 + i * 0.63
            note_icon(c, 3, 540 + math.cos(a) * 260, 1050 + math.sin(a) * 200, 1.2, fk * (1 - green * 0.5))
    pose_keys = [(0, "neutral"), (T(10), "encoge"), (T(18) - 0.15, "asco"), (T(19) - 0.1, "mareado")]
    hero(c, k, 540, FEET, S0, pose_keys)
    title(c, "LAS NOTAS DE SALIDA\nSE EVAPORAN", prog(lt, 0.05, 0.35) * (1 - prog(lt, T(9) - 0.2, T(9))), y=300, size=70)
    title(c, "QUEDA EL FONDO…", prog(lt, T(9) - 0.1, T(9) + 0.2) * (1 - prog(lt, T(17) - 0.3, T(17) - 0.1)), size=80)
    sticker(c, "EMPALAGOSO", 540, 330, pink, bg_col="#ff5a9a", size=60, rot=-4)
    sticker(c, "MAREO", 540, 330, green, bg_col="#2f8f3a", size=66, rot=4)


def scene7(c, k):  # el frasco de Q500 que ni querés usar
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    rrect(c, 120, 900, 520, 930, 6, P("#a87a4a"))  # repisa
    bottle(c, 1, 320, 800, 0.7, 0)
    r = rng(8)
    for i in range(30):  # polvo
        oval(c, 220 + r.random() * 200, 640 + r.random() * 250 + 6 * math.sin(k.t + i), 3, 3, P("#9a8a7a", alpha=0.6))
    sk = prog(lt, T(6) - 0.1, T(6) + 0.2)
    sticker(c, "Q500", 420, 640, sk, bg_col="#b8862a", size=56, rot=8)
    xk = prog(lt, T(7), T(8))
    if xk > 0:
        c.drawLine(350, 660, lerp(350, 500, xk), lerp(660, 610, xk), P("#e0203a", "stroke", 12))
    hero(c, k, 760, FEET, S0, [(0, "neutral"), (T(2), "triste")])
    italic(c, "y ahora ni lo querés usar…", prog(lt, T(7), T(8)), y=430, size=56)


def scene8(c, k):  # el error
    lt, T = k.lt, k.w
    bg(c, k.t, "white", room=False)
    title(c, "EL ERROR NO FUE\nEL PERFUME", prog(lt, T(0) - 0.1, T(0) + 0.2) * (1 - prog(lt, T(6) - 0.3, T(6) - 0.1)), y=300, size=76)
    ek = prog(lt, T(6) - 0.1, T(6) + 0.2)
    if ek > 0:
        title(c, "OLER", ek, y=290, size=100)
        text_center(c, "≠", 540, 400, F(R.RES.xbold, 90), P(GOLDD, alpha=ek))
        title(c, "PROBARLO\nTODO EL DÍA", prog(lt, T(8), T(9)), y=500, size=76, col=GOLDD)
    hero(c, k, 540, FEET + 40, 0.8, [(0, "piensa"), (T(6), "señala")], talk=True)


def scene9(c, k):  # Otto Aleman Perfumes: decants, 1 mes, 120 atomizaciones
    lt, T = k.lt, k.w
    bg(c, k.t, "gold")
    lk = prog(lt, T(3) - 0.2, T(3) + 0.3) * (1 - prog(lt, T(11) - 0.3, T(11)))
    if lk > 0:
        img = M.logo()
        s = back_out(lk, 1.6)
        w = 300 * s
        h = w * img.height() / img.width()
        glow(c, R.RES.glow_warm, 540, 360, 320, 0.6 * lk)
        c.drawImageRect(img, RECT(540 - w / 2, 360 - h / 2, 540 + w / 2, 360 + h / 2), R.SAMP, skia.Paint())
        text_center(c, "OTTO ALEMAN PERFUMES", 540, 540, F(R.RES.xbold, 46), P(INK, alpha=lk))
    dk = prog(lt, T(8) - 0.2, T(8) + 0.3)
    if dk > 0:
        decant(c, 790, lerp(1900, 1000, back_out(dk, 1.3)), 520, 8 * math.sin(k.t * 1.5), k.t, 0.9)
        sticker(c, "DECANT 5 ML", 790, 1330, prog(lt, T(8), T(8) + 0.3), bg_col=INK, size=38, rot=-4)
    hero(c, k, 300, FEET, 0.78, [(0, "celebra"), (T(9), "señala")], talk=True)
    mk = prog(lt, T(12), T(15))
    if mk > 0:  # calendario 1 mes
        c.save()
        c.translate(540, 470)
        mk2 = clamp(mk * 2) * (1 - prog(lt, T(16) - 0.3, T(16)))
        c.scale(back_out(mk2, 1.6), back_out(mk2, 1.6))
        rrect(c, -110, -110, 110, 110, 16, P("#ffffff"))
        rrect(c, -110, -110, 110, -50, 16, P("#e0203a"))
        c.drawRect(RECT(-110, -70, 110, -50), P("#e0203a"))
        text_center(c, "1", 0, 50, F(R.RES.xbold, 100), P(INK))
        text_center(c, "MES", 0, -66, F(R.RES.xbold, 34), P("#ffffff"))
        c.restore()
    ck = prog(lt, T(16), T(19) + 0.3)
    if ck > 0:  # contador de atomizaciones
        n = int(120 * ease_out(ck))
        title(c, f"{n}", 1.0, y=500, size=170, col=GOLDD)
        text_center(c, "ATOMIZACIONES", 540, 580, F(R.RES.xbold, 46), P(INK, alpha=ck))
        for j in range(3):
            mist(c, 720, 760, T(16) + j * 0.5, lt, n=16, dirx=-1)


def scene10(c, k):  # ¿te encantó? frasco completo / ¿no? probá otra
    lt, T = k.lt, k.w
    sw = T(6) - 0.15
    c.save()
    c.clipRect(RECT(0, 0, W / 2, H))
    bg(c, k.t, "gold", room=False)
    c.translate(-270, 0)
    hero(c, k, 540, FEET, 0.75, [(0, "pulgar")])
    bottle(c, 1, 830, 1180, 0.7, -8, 0.6)
    c.restore()
    c.save()
    c.clipRect(RECT(W / 2, 0, W, H))
    bg(c, k.t, "cream", room=False)
    if lt > sw:
        c.translate(270, 0)
        hero(c, k, 540, FEET, 0.75, [(0, "encoge")])
        for i in range(2):
            decant(c, 300 + i * 70, 1150, 200, -10 + i * 20, k.t)
    c.restore()
    c.drawLine(540, 600, 540, 1600, P(INK, "stroke", 6))
    sticker(c, "¿TE ENCANTÓ?", 270, 420, prog(lt, T(0), T(0) + 0.3), bg_col="#2fbf71", size=40, rot=-4)
    sticker(c, "FRASCO COMPLETO", 270, 520, prog(lt, T(4), T(4) + 0.3), bg_col=INK, size=32, rot=3)
    sticker(c, "¿NO?", 810, 420, prog(lt, T(6) - 0.1, T(6) + 0.2), bg_col="#e0203a", size=44, rot=4)
    sticker(c, "PROBÁ OTRA", 810, 520, prog(lt, T(7), T(7) + 0.3), bg_col=INK, size=36, rot=-3)


def scene11(c, k):  # 1 frasco Q500 = hasta 6 decants
    lt, T = k.lt, k.w
    bg(c, k.t, "cream", room=False)
    n = int(6 * ease_in_out(prog(lt, T(11) - 0.2, T(12) + 0.6)) + 0.001)
    tilt = lerp(-12, 0, ease_out(prog(lt, T(11), T(13))))

    def left(c2):
        bottle(c2, 1, 0, -40, 0.55, 0)
        sticker(c2, "Q500", 0, 70, prog(lt, T(8) - 0.1, T(8) + 0.2), bg_col="#b8862a", size=34, rot=0)

    def right(c2):
        for i in range(n):
            decant(c2, -90 + (i % 3) * 90, -70 - (i // 3) * 40 + (i // 3) * 0, 120, (-8, 0, 8)[i % 3], k.t)
    scale_balance(c, 540, 1180, tilt, left, right)
    title(c, "1 FRASCO", prog(lt, T(5) - 0.1, T(5) + 0.2), y=300, size=80)
    title(c, "= HASTA 6 FRAGANCIAS", prog(lt, T(11) - 0.1, T(11) + 0.2), y=400, size=64, col=GOLDD)
    sticker(c, "DECANTS DE 5 ML", 540, 1420, prog(lt, T(15), T(15) + 0.3), bg_col=INK, size=40, rot=-3)


def scene12(c, k):  # tarjeta de sellos digital: 6 sellos → decant gratis
    lt, T = k.lt, k.w
    free = prog(lt, T(19) - 0.1, T(19) + 0.2)
    bg(c, k.t, "gold" if free > 0 else "cream", room=False)
    title(c, "TARJETA DE\nSELLOS DIGITAL", prog(lt, T(3) - 0.1, T(3) + 0.2), y=300, size=74)
    n = int(6 * prog(lt, T(8) - 0.6, T(10) + 0.2) + 0.0001)
    stamp_card(c, 360, 1000, 1.2, n, k.t, free)
    hero(c, k, 900, FEET, 0.58, [(0, "señala"), (T(19) - 0.1, "celebra")])
    dk = prog(lt, T(14) - 0.2, T(14) + 0.3)
    if dk > 0:
        decant(c, 700, lerp(1900, 820, back_out(dk, 1.3)), 300, 8 * math.sin(k.t * 2), k.t, 0.8)
        sticker(c, "Q70", 800, 650, prog(lt, T(18) - 0.1, T(18) + 0.2), bg_col="#b8862a", size=40, rot=10)
        xk = prog(lt, T(19) - 0.2, T(19))
        if xk > 0:
            c.drawLine(750, 660, lerp(750, 850, xk), lerp(660, 630, xk), P("#e0203a", "stroke", 10))
    if free > 0:
        sticker(c, "¡GRATIS!", 540, 560, free, bg_col="#2fbf71", size=70, rot=-5)
        r = rng(3)
        for i in range(60):  # confeti
            x = r.random() * W
            y = -50 + ((lt - T(19)) * (400 + 400 * r.random()) + r.random() * 200)
            if y > H:
                continue
            c.save()
            c.translate(x, y)
            c.rotate(k.t * 200 + i * 30)
            c.drawRect(RECT(-9, -5, 9, 5), P(["#d6a24a", "#ff3d6a", "#2fbf71", "#2f6bff", "#ffffff"][i % 5]))
            c.restore()


def scene13(c, k):  # ¿con qué perfume te pasó eso?
    lt, T = k.lt, k.w
    bg(c, k.t, "cream", room=False)
    title(c, "¿CON QUÉ PERFUME\nTE PASÓ ESO?", prog(lt, T(2) - 0.1, T(2) + 0.2), y=300, size=74)
    hero(c, k, 300, FEET, 0.8, [(0, "piensa"), (T(8) - 0.2, "señala")], talk=True)
    bk = ease_out(prog(lt, T(8) - 0.1, T(8) + 0.3))
    if bk > 0:
        c.save()
        c.translate(700, 980)
        c.scale(bk, bk)
        rrect(c, -300, -60, 300, 60, 60, P("#ffffff"))
        rrect(c, -300, -60, 300, 60, 60, P(INK, "stroke", 4))
        oval(c, -244, 0, 30, 30, P(GOLDD))
        msg = "Me pasó con…"
        typed = msg[: int(len(msg) * prog(lt, T(8), T(11) + 0.3))]
        c.drawString(typed, -196, 14, F(R.RES.semi, 40), P(INK))
        c.restore()
    msgs = ["a mí con uno dulce 😩", "con uno amaderado", "me pasó con uno árabe", "jajaja a mí también", "con uno de vainilla"]
    r = rng(11)
    for i in range(10):
        u = (lt - (T(9) + i * 0.3)) / 2.6
        if u <= 0 or u >= 1:
            continue
        x = 700 + (r.random() - 0.5) * 300
        y = lerp(1450, 1120, u)
        a = math.sin(math.pi * u)
        tx = msgs[i % len(msgs)].replace(" 😩", "")
        f = F(R.RES.semi, 28)
        w = f.measureText(tx) + 70
        c.save()
        c.translate(x, y)
        rrect(c, -w / 2, -30, w / 2, 30, 30, P("#ffffff", alpha=0.95 * a))
        oval(c, -w / 2 + 30, 0, 16, 16, P(["#b8862a", "#2f6bff", "#ff3d6a", "#2fbf71"][i % 4], alpha=a))
        c.drawString(tx, -w / 2 + 56, 10, f, P(INK, alpha=a))
        c.restore()


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10, scene11, scene12, scene13]


# ----------------------------------------------------------------------------
# subtítulos abajo (pastilla blanca) y marca
# ----------------------------------------------------------------------------


def draw_subs(c, t, phr):
    f = F(R.RES.bold, 44)
    for p in phr:
        if not (p["s"] <= t < p["e"]):
            continue
        words = p["words"]
        lines, line, wsum = [], [], 0
        for w in words:
            ww = f.measureText(w["w"] + " ")
            if wsum + ww > 860 and line:
                lines.append(line)
                line, wsum = [], 0
            line.append(w)
            wsum += ww
        lines.append(line)
        lh = 58
        top = 1590 - (len(lines) - 1) * lh / 2
        maxw = max(sum(f.measureText(w["w"] + " ") for w in ln) for ln in lines)
        rrect(c, 540 - maxw / 2 - 26, top - 46, 540 + maxw / 2 + 20, top + (len(lines) - 1) * lh + 22, 22, P("#ffffff", alpha=0.94))
        for li, ln in enumerate(lines):
            lw = sum(f.measureText(w["w"] + " ") for w in ln)
            x = 540 - lw / 2
            y = top + li * lh
            for w in ln:
                cur = w["s"] - 0.03 <= t < w["e"] + 0.05
                said = t >= w["s"] - 0.03
                col = GOLDD if cur else (INK if said else "#b8b0a8")
                c.drawString(w["w"], x, y, f, P(col))
                x += f.measureText(w["w"] + " ")


def draw_watermark(c):
    f = F(R.RES.semi, 28)
    txt = "@ottoaleman.perfumesgt"
    w = f.measureText(txt)
    c.drawString(txt, 540 - w / 2, 1760, f, P("#6a4a2a", alpha=0.75))


def render_frame(c, t, vo, phr, total):
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(R.hexc(CREAM))
    k = R.Ctx(vo, si, t)
    lt = k.lt
    if 0 < si and lt < 0.18:  # corte con pequeño empuje
        q = 1 - ease_out(lt / 0.18)
        c.save()
        c.translate(540, 960)
        c.scale(1 + 0.06 * q, 1 + 0.06 * q)
        c.translate(-540, -960)
        SCENES[si](c, k)
        c.restore()
    else:
        SCENES[si](c, k)
    fade = clamp(t / 0.2) * clamp((total - t) / 0.4)
    if fade < 1:
        c.drawRect(RECT(0, 0, W, H), P("#000000", alpha=1 - fade))
    draw_subs(c, t, phr)
    draw_watermark(c)


def install():
    R.SCENES = SCENES
    R.render_frame = render_frame
    R.draw_subs = draw_subs
    R.draw_watermark = draw_watermark


if __name__ == "__main__":
    install()
    R.main()
