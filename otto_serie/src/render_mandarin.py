"""Otto Aleman Perfumes — "Cómo crear un Mandarin Sky" (formato viral: lo hacés → error → lo arreglás).

Proceso de fábrica simplificado (inyección de frasco y tapa, alcohol, esencias pesadas gota a gota,
tanques de mezcla, maceración, enfriado y filtrado, llenado y tapado). Personaje A reacciona en cada
paso; cámara siempre en movimiento. Pirámide del Odyssey Mandarin Sky EDP (Armaf).
Uso:
  VIDEO_BUILD=$PWD/otto_serie/build_mandarin VO_TRIM=0.15 VO_GAP=0.3 VO_TAIL=2.0 \
    python3 otto_serie/src/render_mandarin.py --out otto_serie/build_mandarin/video_mudo.mp4
"""
import math
import os
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_decant_tarde as D  # noqa: E402
from render_decant_tarde import (R, P, lin, rad, oval, rrect, clamp, lerp, smooth, ease_out, ease_in_out, back_out,  # noqa: E402
                                 prog, rng, glow, text_center, W, H, RECT, F, M, INK, GOLDD, CREAM, OVER,
                                 bg, title, italic, sticker, hero, decant, clock, Cam)

VO = None
TABLE_Y = 1290
BX, BY = 480, 1080   # frasco sobre la mesa


# ----------------------------------------------------------------------------
# el frasco Mandarin Sky (azul con tapa naranja) y su líquido
# ----------------------------------------------------------------------------
LIQ = [  # (escena, palabra, nivel, color)
    (2, 3, 0.55, "#dcecf6"), (4, 29, 0.62, "#ffd08a"), (6, 5, 0.7, "#f2b24a"), (8, 5, 0.78, "#d8862a"),
]


def wt(si, wi):
    s = VO[si]
    tok = s["tokens"][min(wi, len(s["tokens"]) - 1)]
    return tok["s"]


def liquid(t):
    level, col = 0.0, "#dcecf6"
    for si, wi, lv, cc in LIQ:
        t0 = wt(si, wi)
        u = clamp((t - t0) / 1.2)
        if u > 0:
            level = lerp(level, lv, ease_out(u))
            col = M.mix(col, cc, u)
    return level, col


def msky(c, x, y, s, t, level=None, col=None, cap=1.0, glow_a=0.0, rot=0.0):
    """Frasco azul con tapa naranja. (x, y) = base del frasco."""
    if level is None:
        level, col = liquid(t)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if glow_a > 0:
        glow(c, R.RES.glow_warm, 0, -170, 320, 0.6 * glow_a)
    oval(c, 0, 4, 140, 20, P("#000000", alpha=0.2))
    body = skia.RRect.MakeRectXY(RECT(-120, -330, 120, 0), 40, 40)
    c.drawRRect(body, P("#1a4ab8", shader=lin(-120, 0, 120, 0, ["#0e2c7a", "#2f6be0", "#5a9aff", "#1a4ab8", "#0a2260"], [0, .25, .45, .7, 1])))
    if level > 0:
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(RECT(-104, -314, 104, -16), 30, 30), True)
        ly = lerp(-16, -314, level)
        wave = skia.Path()
        wave.moveTo(-110, ly)
        for i in range(6):
            wave.quadTo(-90 + i * 40, ly + 6 * math.sin(t * 4 + i), -70 + i * 40, ly)
        wave.lineTo(110, 0)
        wave.lineTo(-110, 0)
        wave.close()
        c.drawPath(wave, P(col, alpha=0.75))
        c.restore()
    c.drawRRect(body, P("#ffffff", "stroke", 4, alpha=0.4))
    rrect(c, -90, -300, -64, -30, 13, P("#ffffff", alpha=0.25))
    text_center(c, "ODYSSEY", 0, -190, F(R.RES.xbold, 30), P("#ffffff", alpha=0.85))
    text_center(c, "MANDARIN SKY", 0, -150, F(R.RES.bold, 22), P("#ffd08a", alpha=0.9))
    rrect(c, -40, -356, 40, -330, 6, P("#c8c8d0", shader=lin(-40, 0, 40, 0, ["#8a8a96", "#ffffff", "#8a8a96"])))
    if cap > 0:
        cy = -356 - (1 - cap) * 260
        c.save()
        c.translate(0, cy)
        c.rotate((1 - cap) * 90)
        rrect(c, -62, -140, 62, 0, 20, P("#ff7a1a", shader=lin(-62, 0, 62, 0, ["#c84a0a", "#ff8a2a", "#ffb060", "#e05a10"], [0, .35, .5, 1])))
        rrect(c, -46, -130, -30, -10, 8, P("#ffffff", alpha=0.3))
        c.restore()
    c.restore()


# ----------------------------------------------------------------------------
# máquinas y laboratorio
# ----------------------------------------------------------------------------
STEEL = ["#7a7e88", "#e4e6ec", "#a8acb6", "#5a5e68"]


def table(c):
    c.drawRect(RECT(-200, TABLE_Y, W + 200, TABLE_Y + 40), P("#a87a4a", shader=lin(0, TABLE_Y, 0, TABLE_Y + 40, ["#c8945a", "#8a5a30"])))
    c.drawRect(RECT(-200, TABLE_Y + 40, W + 200, H + 200), P("#e6d6bc"))


def injection_machine(c, x, y, s, press):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -220, -200, 220, 200, 20, P("#3a6ad0", shader=lin(-220, 0, 220, 0, ["#2a4aa0", "#4a7ae0", "#2a4aa0"])))
    rrect(c, -180, -160, 180, 60, 10, P("#d8dce4"))
    dz = 50 * press
    rrect(c, -140, -150 + dz, -10, -10, 8, P("#8a8e98", shader=lin(-140, 0, -10, 0, STEEL)))
    rrect(c, 10, -150, 140, -10 - dz * 0.0, 8, P("#8a8e98", shader=lin(10, 0, 140, 0, STEEL)))
    for i in range(3):
        oval(c, -150 + i * 50, 130, 14, 14, P(["#ff3d3d", "#ffd04a", "#2fbf71"][i]))
    text_center(c, "INYECCIÓN", 70, 140, F(R.RES.bold, 26), P("#ffffff"))
    c.restore()


def steel_tank(c, x, y, s, label, fill=0.0, col="#dcecf6", t=0.0, agitate=0.0, window=True):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for sd in (-1, 1):
        c.drawLine(sd * 120, 200, sd * 140, 300, P("#6a6e78", "stroke", 16))
    body = skia.Path()
    body.moveTo(-150, -260)
    body.lineTo(150, -260)
    body.lineTo(150, 160)
    body.quadTo(0, 250, -150, 160)
    body.close()
    c.drawPath(body, P("#a8acb6", shader=lin(-150, 0, 150, 0, STEEL + ["#8a8e98"], [0, .3, .55, .8, 1])))
    oval(c, 0, -260, 150, 34, P("#c8ccd4"))
    oval(c, 0, -260, 150, 34, P("#6a6e78", "stroke", 4))
    if window:
        rrect(c, -50, -170, 50, 120, 30, P("#2a2e38"))
        if fill > 0:
            c.save()
            c.clipRRect(skia.RRect.MakeRectXY(RECT(-50, -170, 50, 120), 30, 30), True)
            ly = lerp(120, -170, fill)
            c.drawRect(RECT(-50, ly, 50, 120), P(col, alpha=0.9))
            if agitate > 0:
                for i in range(5):
                    a = t * 6 * agitate + i * 1.25
                    oval(c, math.cos(a) * 30, ly + 60 + math.sin(a) * 40, 8, 8, P("#ffffff", alpha=0.5 * agitate))
            c.restore()
    if agitate > 0:  # motor del mezclador
        rrect(c, -40, -340, 40, -270, 10, P("#4a4e58"))
        c.drawLine(0, -340, 0, -380, P("#4a4e58", "stroke", 10))
    rrect(c, -110, -230, 110, -190, 10, P("#ffffff", alpha=0.9))
    text_center(c, label, 0, -200, F(R.RES.xbold, 26), P(INK))
    c.restore()


def pipe_stream(c, x0, y0, x1, y1, k, col, t):
    c.drawLine(x0, y0, x0, y0 + 60, P("#8a8e98", "stroke", 26))
    c.drawLine(x0, y0 + 60, x1, y0 + 60, P("#8a8e98", "stroke", 26))
    c.drawLine(x1, y0 + 60, x1, y0 + 90, P("#8a8e98", "stroke", 26))
    oval(c, (x0 + x1) / 2, y0 + 60, 26, 26, P("#e03030"))  # válvula
    if k > 0:
        ln = lerp(y0 + 100, y1, clamp(k * 3))
        c.drawLine(x1, y0 + 100, x1, ln, P(col, "stroke", 14, alpha=0.85))
        for i in range(4):
            dy = ((t * 600 + i * 40) % max(1, ln - y0 - 100))
            oval(c, x1, y0 + 100 + dy, 9, 12, P("#ffffff", alpha=0.6))


def vial(c, x, y, s, label, col, k):
    if k <= 0:
        return
    sc = back_out(clamp(k), 1.8) * s
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    rrect(c, -34, -110, 34, 60, 14, P("#ffffff", alpha=0.6))
    rrect(c, -30, -40, 30, 56, 12, P(col, alpha=0.9))
    rrect(c, -22, -150, 22, -108, 6, P("#3a2a1a"))
    rrect(c, -34, -110, 34, 60, 14, P("#3a2a1a", "stroke", 3, alpha=0.5))
    f = F(R.RES.xbold, 24)
    w = f.measureText(label) + 24
    rrect(c, -w / 2, 70, w / 2, 110, 10, P("#ffffff"))
    rrect(c, -w / 2, 70, w / 2, 110, 10, P(INK, "stroke", 2))
    c.drawString(label, -w / 2 + 12, 99, f, P(INK))
    c.restore()


def falling_drop(c, x, y0, y1, u, col):
    if 0 < u < 1:
        y = lerp(y0, y1, u * u)
        p = skia.Path()
        p.moveTo(x, y - 22)
        p.cubicTo(x + 16, y, x + 16, y + 18, x, y + 18)
        p.cubicTo(x - 16, y + 18, x - 16, y, x, y - 22)
        c.drawPath(p, P(col))


def pipette(c, x, y, s, squeeze):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(RECT(-10, -40, 10, 160), P("#ffffff", alpha=0.7))
    c.drawRect(RECT(-10, -40, 10, 160), P("#8a8e98", "stroke", 2))
    oval(c, 0, -70 + 6 * squeeze, 28, 40 - 10 * squeeze, P("#ff6a3a"))
    c.restore()


def scale_digital(c, x, y, grams):
    rrect(c, x - 200, y, x + 200, y + 50, 12, P("#d8dce4", shader=lin(0, y, 0, y + 50, ["#eef0f4", "#a8acb6"])))
    rrect(c, x - 90, y + 8, x + 90, y + 42, 6, P("#1a2a1a"))
    text_center(c, f"{grams:5.2f} g", x, y + 36, F(R.RES.bold, 28), P("#6aff6a"))


def alembic(c, x, y, s, t, k):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s * back_out(clamp(k), 1.5), s * back_out(clamp(k), 1.5))
    oval(c, 0, 0, 110, 110, P("#c87a3a", shader=rad(-30, -30, 140, ["#ffb070", "#a85a2a"])))
    c.drawLine(0, -110, 0, -200, P("#c87a3a", "stroke", 26))
    p = skia.Path()
    p.moveTo(0, -200)
    p.quadTo(120, -240, 200, -60)
    c.drawPath(p, P("#c87a3a", "stroke", 14))
    for i in range(3):  # fuego
        h = 50 + 20 * math.sin(t * 12 + i)
        fl = skia.Path()
        fl.moveTo(-40 + i * 40, 150)
        fl.quadTo(-30 + i * 40, 150 - h, -20 + i * 40, 150 - h * 1.2)
        fl.quadTo(-10 + i * 40, 150 - h, 0 + i * 40, 150)
        c.drawPath(fl, P("#ff7a1a"))
    u = (t * 1.5) % 1
    falling_drop(c, 200, -40, 60, u, "#ffd08a")
    rrect(c, 160, 70, 240, 150, 10, P("#ffffff", alpha=0.6))
    text_center(c, "DESTILACIÓN", 0, 230, F(R.RES.xbold, 34), P(INK))
    c.restore()


def press(c, x, y, s, t, k):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s * back_out(clamp(k), 1.5), s * back_out(clamp(k), 1.5))
    c.drawRect(RECT(-120, -220, 120, -190), P("#6a6e78"))
    for sd in (-1, 1):
        c.drawRect(RECT(sd * 120 - 12, -220, sd * 120 + 12, 120), P("#6a6e78"))
    dz = 40 + 40 * abs(math.sin(t * 3))
    c.drawRect(RECT(-90, -190 + dz, 90, -160 + dz), P("#a8acb6"))
    c.drawLine(0, -220, 0, -190 + dz, P("#8a8e98", "stroke", 14))
    for i in range(5):  # cáscaras
        oval(c, -70 + i * 35, 60, 22, 12, P("#ff9a2a"))
    for i in range(3):
        falling_drop(c, -40 + i * 40, 80, 130, ((t * 2 + i / 3) % 1), "#ffc04a")
    rrect(c, -110, 120, 110, 150, 8, P("#8a8e98"))
    text_center(c, "PRENSADO", 0, 220, F(R.RES.xbold, 34), P(INK))
    c.restore()


def molecule(c, x, y, s, t, k):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s * back_out(clamp(k), 1.6), s * back_out(clamp(k), 1.6))
    pts = []
    for i in range(10):
        a = i * 0.9 + t * 1.2
        r = 90 + 40 * math.sin(i * 1.7)
        pts.append((math.cos(a) * r, math.sin(a * 0.7 + i) * 70, math.sin(a) * r))
    pts.sort(key=lambda q: q[2])
    for i in range(len(pts) - 1):
        c.drawLine(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], P("#6a6e78", "stroke", 8))
    for i, (px, py, pz) in enumerate(pts):
        rr = 20 + pz * 0.08
        col = "#3a3a44" if i % 3 else "#e03030"
        oval(c, px, py, rr, rr, P(col, shader=rad(px - rr * 0.3, py - rr * 0.3, rr * 1.4, ["#ffffff", col])))
    c.restore()


def calendar_flip(c, x, y, s, n, label):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -120, -120, 120, 120, 16, P("#ffffff"))
    rrect(c, -120, -120, 120, -60, 16, P("#e0203a"))
    c.drawRect(RECT(-120, -80, 120, -60), P("#e0203a"))
    text_center(c, label, 0, -76, F(R.RES.xbold, 30), P("#ffffff"))
    text_center(c, str(n), 0, 70, F(R.RES.xbold, 110), P(INK))
    c.restore()


def chiller(c, x, y, s, t, k):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s * back_out(clamp(k), 1.5), s * back_out(clamp(k), 1.5))
    rrect(c, -150, -180, 150, 180, 20, P("#bfe8ff", shader=lin(-150, 0, 150, 0, ["#9ad0f0", "#e8f8ff", "#9ad0f0"])))
    rrect(c, -150, -180, 150, 180, 20, P("#5a8aaa", "stroke", 5))
    r = rng(3)
    for i in range(14):  # copos
        sx, sy = -120 + r.random() * 240, -150 + ((r.random() * 300 + t * 60) % 300)
        for j in range(3):
            a = j * math.pi / 3
            c.drawLine(sx - math.cos(a) * 12, sy - math.sin(a) * 12, sx + math.cos(a) * 12, sy + math.sin(a) * 12, P("#ffffff", "stroke", 3))
    text_center(c, "ENFRIADO", 0, 240, F(R.RES.xbold, 34), P(INK))
    c.restore()


def funnel(c, x, y, s, t, k, col):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s * back_out(clamp(k), 1.5), s * back_out(clamp(k), 1.5))
    p = skia.Path()
    p.moveTo(-130, -120)
    p.lineTo(130, -120)
    p.lineTo(20, 40)
    p.lineTo(20, 120)
    p.lineTo(-20, 120)
    p.lineTo(-20, 40)
    p.close()
    c.drawPath(p, P("#ffffff", alpha=0.7))
    c.drawPath(p, P("#8a8e98", "stroke", 4))
    c.drawRect(RECT(-110, -110, 110, -80), P(col, alpha=0.8))
    for i in range(3):
        falling_drop(c, 0, 130, 220, ((t * 1.6 + i / 3) % 1), col)
    text_center(c, "FILTRADO", 0, 290, F(R.RES.xbold, 34), P(INK))
    c.restore()


def error_stamp(k):
    if k <= 0:
        return

    def d(c):
        s = lerp(2.2, 1.0, ease_out(clamp(k * 1.6)))
        a = clamp(k * 3)
        c.save()
        c.translate(540, 470)
        c.rotate(-8)
        c.scale(s, s)
        rrect(c, -230, -80, 230, 80, 20, P("#e0203a", alpha=a))
        rrect(c, -230, -80, 230, 80, 20, P("#ffffff", "stroke", 8, alpha=a))
        c.drawLine(-190, -40, -110, 40, P("#ffffff", "stroke", 18, alpha=a))
        c.drawLine(-110, -40, -190, 40, P("#ffffff", "stroke", 18, alpha=a))
        c.drawString("ERROR", -80, 34, F(R.RES.xbold, 96), P("#ffffff", alpha=a))
        c.restore()
    OVER.append(d)


def label_sticker(txt, k, y=470, bg_col="#2fbf71", size=64, rot=-4):
    if k > 0:
        OVER.append(lambda c: sticker(c, txt, 540, y, k, bg_col=bg_col, size=size, rot=rot))


def side_hero(c, k, keys, x=900, s=0.62, talk=False, hold=None):
    hero(c, k, x, D.FEET, s, keys, talk=talk, hold_fn=hold)


def aroma_trail(c, x, y, t, a, col="#ffb060"):
    for i in range(10):
        u = ((t * 0.4 + i / 10) % 1)
        px = x + math.sin(u * 8 + i) * 40 + u * 200
        py = y - u * 400
        oval(c, px, py, 10 + 20 * u, 10 + 20 * u, P(col, alpha=a * (1 - u) * 0.6))


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def s0(c, k):  # frasco + tapa = "perfume"
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    table(c)
    pr = clamp(1 - abs(lt - 0.5) / 0.3) + clamp(1 - abs(lt - T(6)) / 0.3)
    injection_machine(c, 230, 760, 0.85, pr)
    bk = ease_out(prog(lt, 0.6, 1.4))
    capk = ease_out(prog(lt, T(6), T(8)))
    msky(c, lerp(260, BX, bk), lerp(860, TABLE_Y, bk), 0.95, k.t, 0.0, "#dcecf6", cap=capk)
    side_hero(c, k, [(0, "neutral"), (T(9), "celebra")], x=880, s=0.7)
    title(c, "MANDARIN SKY", prog(lt, 0.1, 0.4), y=300, size=96)
    italic(c, "¿cómo se crea?", prog(lt, 0.4, 0.8), y=400, size=58)
    label_sticker("¡YA TENÉS UN PERFUME!", prog(lt, T(9), T(9) + 0.3), y=560, bg_col=GOLDD, size=50)


def s1(c, k):  # le apretás… no sale nada
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    table(c)
    msky(c, BX, TABLE_Y, 0.95, k.t, 0.0, "#dcecf6")
    pk = prog(lt, T(3) - 0.2, T(3) + 0.2)
    if pk > 0:  # telaraña y polvito
        for i in range(8):
            a = i * math.pi / 4
            c.drawLine(BX + 80, 870, BX + 80 + math.cos(a) * 60 * pk, 870 + math.sin(a) * 60 * pk, P("#9a9aa8", "stroke", 2))
        for r_ in (20, 40, 60):
            c.drawPath(skia.Path().addCircle(BX + 80, 870, r_ * pk), P("#9a9aa8", "stroke", 2))
        for i in range(6):
            u = prog(lt, T(3), T(3) + 1.0)
            oval(c, BX + 80 + i * 20 * u, 870 - i * 8 * u, 6, 6, P("#b8b0a8", alpha=1 - u))
    side_hero(c, k, [(0, "señala"), (T(4), "encoge")], x=880, s=0.7)
    error_stamp(prog(lt, T(5) - 0.1, T(5) + 0.3))


def s2(c, k):  # alcohol
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    table(c)
    steel_tank(c, 250, 560, 0.75, "ETANOL", fill=0.8, col="#dcecf6", t=k.t)
    flow = prog(lt, T(3) - 0.2, T(3) + 0.2) * (1 - prog(lt, k.D - 0.6, k.D - 0.2))
    pipe_stream(c, 250, 760, BX, TABLE_Y - 300, flow, "#dcecf6", k.t)
    msky(c, BX, TABLE_Y, 0.95, k.t, cap=1.0 - flow)
    side_hero(c, k, [(0, "piensa"), (T(4), "pulgar")], x=890, s=0.68)
    label_sticker("ALCOHOL DE PERFUMERÍA", prog(lt, T(4), T(4) + 0.3), y=470, bg_col="#2f6bff", size=48)


def s3(c, k):  # solo huele a alcohol
    lt, T = k.lt, k.w
    bg(c, k.t, "green")
    hero(c, k, 540, D.FEET, 0.92, [(0, "neutral"), (T(4), "asco")])
    msky(c, 860, 1300, 0.6, k.t)
    label_sticker("HUELE A FARMACIA", prog(lt, T(5), T(5) + 0.3), y=1380, bg_col=INK, size=48)
    error_stamp(prog(lt, T(7) - 0.1, T(7) + 0.3))


TOP = [("MANDARINA", "#ff9a2a"), ("NARANJA", "#ffb04a"), ("AZAFRÁN", "#c8402a"), ("SALVIA", "#7aa86a")]
HEART = [("CARAMELO", "#c8802a"), ("HABA TONKA", "#6a4020"), ("TAGETE", "#ffb020")]
BASE = [("AMBROXAN", "#e8dcc0"), ("CEDRO", "#a8703a"), ("VETIVER", "#6a7a3a")]


def note_vials(c, lt, T, notes, words, y=650):
    for i, (lab, col) in enumerate(notes):
        k = prog(lt, T(words[i]) - 0.1, T(words[i]) + 0.25)
        vial(c, 200 + i * 225 if len(notes) == 4 else 270 + i * 270, y, 0.9, lab, col, k)


def s4(c, k):  # notas de salida: no es fruta, son aceites (destilación/prensado) pesados gota a gota
    lt, T = k.lt, k.w
    bg(c, k.t, "cream", room=False)
    if lt < T(12) - 0.1:
        table(c)
        note_vials(c, lt, T, TOP, (7, 8, 9, 11))
        msky(c, BX, TABLE_Y, 0.85, k.t)
        side_hero(c, k, [(0, "señala"), (T(7), "pulgar")], x=900, s=0.6)
        label_sticker("NOTAS DE SALIDA", prog(lt, T(5), T(5) + 0.3), y=440, bg_col="#ff9a2a", size=56)
    elif lt < T(19) - 0.2:  # no se echa fruta de verdad
        bg(c, k.t, "white", room=False)
        fk = prog(lt, T(12), T(14))
        oval(c, 540, lerp(400, 900, ease_out(fk)), 150, 140, P("#ff8a1a", shader=rad(490, 840, 220, ["#ffc070", "#ff7a0a"])))
        oval(c, 540, lerp(400, 900, ease_out(fk)) - 140, 30, 14, P("#3a8a3a"))
        xk = prog(lt, T(16), T(18))
        if xk > 0:
            c.drawLine(360, 720, lerp(360, 720, xk), lerp(720, 1080, xk), P("#e0203a", "stroke", 30))
            c.drawLine(720, 720, lerp(720, 360, xk), lerp(720, 1080, xk), P("#e0203a", "stroke", 30))
        side_hero(c, k, [(0, "espera"), (T(16), "encoge")], x=880, s=0.62)
        label_sticker("NO ES FRUTA DE VERDAD", prog(lt, T(16), T(16) + 0.3), y=440, bg_col="#e0203a", size=50)
    elif lt < T(29) - 0.2:  # destilación o prensado
        bg(c, k.t, "cream", room=False)
        alembic(c, 290, 950, 1.0, k.t, prog(lt, T(26) - 0.3, T(26) + 0.1))
        press(c, 790, 980, 1.0, k.t, prog(lt, T(28) - 0.4, T(28)))
        label_sticker("ACEITES ESENCIALES", prog(lt, T(20), T(20) + 0.3), y=440, bg_col=GOLDD, size=54)
    else:  # gota a gota en el laboratorio
        bg(c, k.t, "cream", room=False)
        table(c)
        scale_digital(c, BX, TABLE_Y - 50, 12.4 * prog(lt, T(31), T(37) + 0.3))
        msky(c, BX, TABLE_Y - 50, 0.85, k.t, cap=0.0)
        sq = abs(math.sin(lt * 6))
        pipette(c, BX, 700, 1.0, sq)
        for i in range(4):
            falling_drop(c, BX, 880, 1000, ((lt * 1.8 + i / 4) % 1), "#ffb04a")
        side_hero(c, k, [(0, "piensa")], x=900, s=0.6)
        label_sticker("GOTA A GOTA", prog(lt, T(32), T(32) + 0.3), y=440, bg_col=INK, size=56)


def s5(c, k):  # a los 15 min ya no huele
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    clock(c, 280, 760, 150, lerp(9, 9.25, ease_in_out(prog(lt, 0.2, T(4)))))
    aroma_trail(c, 540, 1000, k.t, 1 - prog(lt, T(4), T(7)))
    hero(c, k, 600, D.FEET, 0.88, [(0, "neutral"), (T(6), "triste")])
    title(c, "15 MIN", prog(lt, T(3) - 0.1, T(3) + 0.2), y=300, size=110)
    error_stamp(prog(lt, T(9) - 0.1, T(9) + 0.3))


def s6(c, k):  # corazón
    lt, T = k.lt, k.w
    bg(c, k.t, "gold", room=False)
    table(c)
    note_vials(c, lt, T, HEART, (5, 7, 9))
    msky(c, BX, TABLE_Y, 0.85, k.t, cap=0.0)
    for i, w in enumerate((5, 7, 9)):
        falling_drop(c, BX, 760, 940, prog(lt, T(w), T(w) + 0.5), HEART[i][1])
    side_hero(c, k, [(0, "neutral"), (T(5), "enamorado")], x=900, s=0.62)
    label_sticker("CORAZÓN", prog(lt, T(4), T(4) + 0.3), y=440, bg_col="#c8802a", size=64)


def s7(c, k):  # en la tarde desaparece
    lt, T = k.lt, k.w
    bg(c, k.t, "gray")
    clock(c, 820, 720, 150, lerp(12, 15, ease_in_out(prog(lt, 0, T(3)))))
    hero(c, k, 400, D.FEET, 0.88, [(0, "neutral"), (T(4), "triste")])
    title(c, "3:00 PM", prog(lt, T(3) - 0.1, T(3) + 0.2), y=300, size=110)
    error_stamp(prog(lt, T(4) + 0.3, T(4) + 0.6))


def s8(c, k):  # base + ambroxan molécula
    lt, T = k.lt, k.w
    bg(c, k.t, "cream", room=False)
    if lt < T(9) - 0.2:
        table(c)
        note_vials(c, lt, T, BASE, (5, 6, 8))
        msky(c, BX, TABLE_Y, 0.85, k.t, cap=0.0)
        for i, w in enumerate((5, 6, 8)):
            falling_drop(c, BX, 760, 940, prog(lt, T(w), T(w) + 0.5), BASE[i][1])
        side_hero(c, k, [(0, "neutral"), (T(5), "pulgar")], x=900, s=0.62)
        label_sticker("FONDO", prog(lt, T(4), T(4) + 0.3), y=440, bg_col="#a8703a", size=70)
    else:
        bg(c, k.t, "white", room=False)
        molecule(c, 540, 900, 2.0, k.t, prog(lt, T(9), T(10)))
        side_hero(c, k, [(0, "piensa"), (T(17), "señala")], x=880, s=0.6)
        label_sticker("AMBROXAN", prog(lt, T(10), T(10) + 0.3), y=440, bg_col=INK, size=64)
        label_sticker("MOLÉCULA DE LABORATORIO", prog(lt, T(13), T(13) + 0.3), y=1380, bg_col=GOLDD, size=42, rot=3)


def s9(c, k):  # tanques de mezcla, luego lo usás de una vez: huele desordenado
    lt, T = k.lt, k.w
    sw = T(8) - 0.15
    if lt < sw:
        bg(c, k.t, "cream", room=False)
        c.drawRect(RECT(-200, 1500, W + 200, H + 200), P("#c8ccd4"))
        level, col = liquid(k.t)
        for i, x in enumerate((220, 540, 860)):
            steel_tank(c, x, 1150, 0.95 if i == 1 else 0.75, "MEZCLA", fill=0.7, col=col, t=k.t, agitate=1.0)
        label_sticker("TANQUES DE ACERO", prog(lt, T(5), T(5) + 0.3), y=440, bg_col=INK, size=56)
    else:
        bg(c, k.t, "green")
        hero(c, k, 540, D.FEET, 0.92, [(0, "sostiene"), (T(15), "mareado")],
             hold_fn=lambda cc, x, y: msky(cc, x, y + 10, 0.3, k.t))
        u = prog(lt, T(12), T(15))
        r = rng(9)
        for i in range(30):  # nube revuelta
            a = r.random() * 6.28 + k.t * 2
            d = 220 * u * r.random()
            oval(c, 700 + math.cos(a) * d, 820 + math.sin(a) * d * 0.6, 16 + 20 * r.random(), 16 + 20 * r.random(),
                 P(["#ff9a2a", "#c8802a", "#7a4a6a", "#6a7a3a"][i % 4], alpha=0.5 * u))
        label_sticker("FUERTE Y DESORDENADO", prog(lt, T(16), T(16) + 0.3), y=1380, bg_col=INK, size=46)
        error_stamp(prog(lt, T(18), T(18) + 0.3))


def s10(c, k):  # maceración, enfriado y filtrado
    lt, T = k.lt, k.w
    bg(c, k.t, "cream", room=False)
    level, col = liquid(k.t)
    if lt < T(12) - 0.2:
        c.drawRect(RECT(-200, 1500, W + 200, H + 200), P("#3a3a44"))
        c.drawRect(RECT(-200, -200, W + 200, 1500), P("#2a2a34", alpha=0.6))
        for x in (200, 540, 880):
            steel_tank(c, x, 1200, 0.7, "REPOSO", fill=0.7, col=col, t=k.t)
        n = 1 + int(prog(lt, T(3), T(8)) * 11)
        calendar_flip(c, 540, 640, 1.1, n, "SEMANA" if n < 5 else "MES")
        label_sticker("MACERACIÓN", prog(lt, T(11) - 0.2, T(11) + 0.1), y=420, bg_col="#7a3ae0", size=64)
    else:
        table(c)
        chiller(c, 280, 1000, 0.9, k.t, prog(lt, T(14) - 0.2, T(14) + 0.2))
        funnel(c, 790, 820, 0.9, k.t, prog(lt, T(17) - 0.2, T(17) + 0.2), col)
        msky(c, 790, TABLE_Y, 0.6, k.t, cap=0.0, glow_a=prog(lt, T(20), T(21)))
        side_hero(c, k, [(0, "piensa"), (T(20), "pulgar")], x=520, s=0.55)
        label_sticker("CRISTALINO", prog(lt, T(21), T(21) + 0.3), y=440, bg_col=GOLDD, size=60)


def s11(c, k):  # llenado y tapado en fábrica: 250,000 piezas al día
    lt, T = k.lt, k.w
    bg(c, k.t, "cream", room=False)
    belt_y = 1260
    c.drawRect(RECT(-200, belt_y, W + 200, belt_y + 60), P("#3a3a44"))
    for i in range(30):
        x = (i * 80 - (k.t * 160) % 80) - 100
        c.drawLine(x, belt_y + 10, x + 30, belt_y + 10, P("#6a6a74", "stroke", 6))
    for i in range(8):  # frascos avanzando
        x = ((k.t * 160 + i * 220) % 1760) - 300
        filled = x > 380
        capped = x > 700
        msky(c, x, belt_y, 0.55, k.t, 0.72 if filled else 0.0, "#d8862a", cap=1.0 if capped else 0.0)
    for nx in (380,):  # boquilla de llenado
        c.drawRect(RECT(nx - 30, 600, nx + 30, 860), P("#8a8e98", shader=lin(nx - 30, 0, nx + 30, 0, STEEL)))
        if prog(lt, T(5), T(5) + 0.2) > 0:
            c.drawLine(nx, 860, nx, 1020, P("#d8862a", "stroke", 10, alpha=0.6 + 0.4 * math.sin(k.t * 20)))
    c.drawRect(RECT(670, 600, 730, 820), P("#8a8e98", shader=lin(670, 0, 730, 0, STEEL)))  # tapadora
    dz = 80 * abs(math.sin(k.t * 3))
    rrect(c, 650, 820 + dz, 750, 860 + dz, 10, P("#ff7a1a"))
    side_hero(c, k, [(0, "neutral"), (T(21), "celebra")], x=900, s=0.5)
    label_sticker("LLENADO Y TAPADO", prog(lt, T(3), T(3) + 0.3) * (1 - prog(lt, T(21) - 0.5, T(21) - 0.3)), y=440, bg_col=INK, size=52)
    ck = prog(lt, T(21) - 0.3, T(22))
    if ck > 0:
        n = int(250000 * ease_out(ck))
        OVER.append(lambda cc: text_center(cc, f"{n:,}", 540, 600, F(R.RES.xbold, 150), P(GOLDD)))
        OVER.append(lambda cc: text_center(cc, "PIEZAS AL DÍA · DUBÁI", 540, 680, F(R.RES.xbold, 44), P(INK)))


def pyramid(c, x, y, s, k):
    if k <= 0:
        return
    layers = [("SALIDA", "mandarina · naranja · azafrán · salvia", "#ffb04a"),
              ("CORAZÓN", "caramelo · haba tonka · tagete", "#e0902a"),
              ("FONDO", "ambroxan · cedro · vetiver", "#a8602a")]
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for i, (name, notes, col) in enumerate(layers):
        kk = clamp(k * 3 - i * 0.6)
        if kk <= 0:
            continue
        w0, w1 = 180 + i * 150, 330 + i * 150
        y0 = i * 130
        p = skia.Path()
        p.moveTo(-w0, y0)
        p.lineTo(w0, y0)
        p.lineTo(w1, y0 + 120)
        p.lineTo(-w1, y0 + 120)
        p.close()
        c.save()
        c.scale(1, back_out(kk, 1.4))
        c.drawPath(p, P(col))
        text_center(c, name, 0, y0 + 56, F(R.RES.xbold, 40), P("#ffffff"))
        text_center(c, notes, 0, y0 + 100, F(R.RES.semi, 28), P("#ffffff"))
        c.restore()
    c.restore()


def s12(c, k):  # y así creaste un Mandarin Sky
    lt, T = k.lt, k.w
    bg(c, k.t, "gold", room=False)
    msky(c, 240, 1300, 0.85, k.t, 0.78, "#d8862a", glow_a=1.0)
    R.RES.glow_gold = R.RES.glow_warm
    R.burst(c, 240, 1050, lt - T(2), dur=1.2, n=50, radius=420, seed=3, intensity=0.9)
    pyramid(c, 600, 560, 0.72, prog(lt, T(1), T(4)))
    side_hero(c, k, [(0, "celebra")], x=880, s=0.45)
    title(c, "¡ASÍ CREASTE UN\nMANDARIN SKY!", prog(lt, T(2) - 0.1, T(2) + 0.2), y=290, size=80)


def s13(c, k):  # pedilo en decant en Otto Aleman Perfumes
    lt, T = k.lt, k.w
    bg(c, k.t, "cream", room=False)
    lk = prog(lt, T(12) - 0.2, T(12) + 0.2)
    if lk > 0:
        img = M.logo()
        s = back_out(lk, 1.6)
        w = 280 * s
        h = w * img.height() / img.width()
        c.drawImageRect(img, RECT(540 - w / 2, 520 - h / 2, 540 + w / 2, 520 + h / 2), R.SAMP, skia.Paint())
        text_center(c, "OTTO ALEMAN PERFUMES", 540, 720, F(R.RES.xbold, 50), P(INK, alpha=lk))
    dk = prog(lt, T(9) - 0.3, T(9))
    if dk > 0:
        decant(c, 300, lerp(1900, 1100, back_out(dk, 1.3)), 420, -6, k.t, 0.8)
        msky(c, 520, 1300, 0.55, k.t, 0.78, "#d8862a")
    side_hero(c, k, [(0, "señala"), (T(15), "pulgar")], x=900, s=0.6, talk=True)
    label_sticker("AHORRATE TODO EL PROCESO", prog(lt, T(3), T(3) + 0.3), y=420, bg_col=GOLDD, size=46)
    label_sticker("ESCRIBINOS · DM O COMENTARIOS", prog(lt, T(15), T(15) + 0.3), y=1390, bg_col=INK, size=40)


def s14(c, k):  # ¿qué perfume querés que creemos ahora?
    lt, T = k.lt, k.w
    bg(c, k.t, "cream", room=False)
    title(c, "¿QUÉ PERFUME\nCREAMOS AHORA?", prog(lt, T(2) - 0.1, T(2) + 0.2), y=290, size=84)
    hero(c, k, 290, D.FEET, 0.9, [(0, "señala")], talk=True)
    bk = ease_out(prog(lt, T(1), T(1) + 0.3))
    if bk > 0:
        c.save()
        c.translate(720, 960)
        c.scale(bk, bk)
        rrect(c, -330, -70, 330, 70, 70, P("#ffffff"))
        rrect(c, -330, -70, 330, 70, 70, P(INK, "stroke", 4))
        oval(c, -266, 0, 34, 34, P(GOLDD))
        msg = "Creen el…"
        c.drawString(msg[: int(len(msg) * prog(lt, T(1), T(5)))], -214, 16, F(R.RES.semi, 48), P(INK))
        c.restore()
    msgs = ["¡el Asad!", "Club de Nuit", "uno de vainilla", "¡el Hawas!", "uno árabe dulce"]
    r = rng(11)
    for i in range(10):
        u = (lt - (T(3) + i * 0.3)) / 2.4
        if u <= 0 or u >= 1:
            continue
        x = 740 + (r.random() - 0.5) * 220
        y = lerp(1460, 1110, u)
        a = math.sin(math.pi * u)
        f = F(R.RES.semi, 34)
        tx = msgs[i % len(msgs)]
        w = f.measureText(tx) + 80
        c.save()
        c.translate(x, y)
        rrect(c, -w / 2, -36, w / 2, 36, 36, P("#ffffff", alpha=0.96 * a))
        rrect(c, -w / 2, -36, w / 2, 36, 36, P(INK, "stroke", 2, alpha=0.3 * a))
        oval(c, -w / 2 + 34, 0, 18, 18, P(["#b8862a", "#2f6bff", "#ff3d6a", "#2fbf71"][i % 4], alpha=a))
        c.drawString(tx, -w / 2 + 64, 12, f, P(INK, alpha=a))
        c.restore()


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14]
CAMS = [
    Cam(1.15, 1.0, punches=(0, 6, 9), focus=((6, 9, 1.3, BX, 1000, 0),)),
    Cam(1.0, 1.05, punches=(5,), focus=((2, 4, 1.6, BX + 60, 900, 0), (4, 99, 1.4, 880, 760, 1))),
    Cam(1.0, 1.1, punches=(3, 4), focus=((3, 6, 1.2, 380, 900, 0),)),
    Cam(1.0, 1.1, punches=(4, 7), focus=((4, 7, 1.5, 540, 700, 2),)),
    Cam(1.0, 1.08, punches=(7, 8, 9, 11, 16, 26, 28, 32), focus=((29, 99, 1.3, BX, 1000, 0),)),
    Cam(1.0, 1.1, punches=(3, 9), focus=((5, 99, 1.45, 600, 720, 0),)),
    Cam(1.0, 1.08, punches=(4, 5, 7, 9), focus=((5, 99, 1.18, 560, 950, 0),)),
    Cam(1.0, 1.1, punches=(3,), focus=((3, 99, 1.45, 400, 720, 0),)),
    Cam(1.0, 1.06, punches=(4, 5, 6, 8, 10)),
    Cam(1.15, 1.0, punches=(5, 18), focus=((12, 99, 1.4, 600, 760, 3),)),
    Cam(1.0, 1.08, punches=(11, 14, 17, 21)),
    Cam(1.0, 1.12, punches=(5, 10, 21), rot=1.0),
    Cam(1.0, 1.15, punches=(2,)),
    Cam(1.0, 1.08, punches=(9, 12, 15)),
    Cam(1.0, 1.1, punches=(2,)),
]


def render_frame(c, t, vo, phr, total):
    global VO
    VO = vo
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(R.hexc(CREAM))
    k = R.Ctx(vo, si, t)
    lt = k.lt
    OVER.clear()
    z, fx, fy, rot = CAMS[si].get(k)
    if 0 < si and lt < 0.2:
        z *= 1 + 0.08 * (1 - ease_out(lt / 0.2))
    c.save()
    c.translate(540, 960)
    c.rotate(rot)
    c.scale(z, z)
    c.translate(-fx, -fy)
    SCENES[si](c, k)
    c.restore()
    for fn in OVER:
        fn(c)
    fade = clamp(t / 0.2) * clamp((total - t) / 0.4)
    if fade < 1:
        c.drawRect(RECT(0, 0, W, H), P("#000000", alpha=1 - fade))
    D.draw_subs(c, t, phr)
    D.draw_watermark(c)


def install():
    R.SCENES = SCENES
    R.render_frame = render_frame
    R.draw_subs = D.draw_subs
    R.draw_watermark = D.draw_watermark


if __name__ == "__main__":
    install()
    R.main()
