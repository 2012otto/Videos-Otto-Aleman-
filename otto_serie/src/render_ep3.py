"""Serie Otto Aleman Perfumes — Ep. 3: Quiz "¿Cuánto sabes de perfumes?" (A verdadero / B falso).

Set de concurso de TV: pantalla con marquesina de focos, reflectores, botones A/B, cuenta regresiva 3-2-1.
Uso (desde la raíz del repo):
  VIDEO_BUILD=$PWD/otto_serie/build_ep3 VO_TRIM=0.3 python3 otto_serie/src/render_ep3.py --out otto_serie/build_ep3/video_mudo.mp4
"""
import math
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_ep1 as O1  # noqa: E402
from render_ep1 import (R, P, RECT, GOLD, back_out, clamp, ease_in_out, ease_out, font, glow, hexc, lerp, lin,  # noqa: E402
                        rad, oval, prog, rrect, smooth, text_center, draw_img, draw_kid, rng, W, H, gold_text, pill_gold,
                        mini_bottle)

camera = R.camera
talk = O1.talk
GREEN, RED = "#2fbf71", "#e8414f"
ANSWERS = ["A", "B", "A"]
QUESTIONS = ["¿Es malo frotarte las muñecas después de echarte perfume?",
             "¿El baño es el mejor lugar para guardar tu perfume?",
             "¿Un Eau de Parfum es más concentrado que un Eau de Toilette?"]


# ----------------------------------------------------------------------------
# set del concurso
# ----------------------------------------------------------------------------


def stage(c, t):
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#0c0a24", shader=rad(540, 800, 1300, ["#2a1a5a", "#120c30", "#06040f"], [0, .5, 1])))
    for side in (-1, 1):  # telones
        x0 = -40 if side < 0 else W - 120
        for i in range(5):
            xx = x0 + i * 32
            c.drawRect(RECT(xx, -100, xx + 30, 1500), P("#8a1428", shader=lin(xx, 0, xx + 30, 0, ["#5a0a18", "#b8203a", "#5a0a18"])))
        awn = skia.Path()
        awn.addRect(RECT(-50, -100, W + 50, 120))
        c.drawRect(RECT(-50, 60, W + 50, 120), P("#b8203a"))
    c.drawRect(RECT(-50, 112, W + 50, 124), P("#d9a441", shader=lin(0, 112, 0, 124, GOLD)))
    for i, base in enumerate((-60, W + 60)):  # reflectores
        ang = 0.35 * math.sin(t * 0.9 + i * 2)
        tx = 540 + math.sin(ang) * 900 * (1 if i else -1) * -1
        beam = skia.Path()
        beam.moveTo(base, 140)
        beam.lineTo(tx - 160, 1500)
        beam.lineTo(tx + 160, 1500)
        beam.close()
        c.drawPath(beam, P("#ffffff", shader=lin(0, 140, 0, 1500, [hexc("#fff3d6", .14), hexc("#fff3d6", 0)])))
    c.drawRect(RECT(-500, 1450, W + 500, H + 500), P("#160c2a", shader=lin(0, 1450, 0, H, ["#2a1648", "#05030b"])))
    for k in range(4):
        rr = 180 + k * 120
        oval(c, 540, 1530, rr, rr * 0.16, P("#d9a441", "stroke", 3, alpha=0.35 - k * 0.07))
    R.dust(c, t, n=24, seed=5, alpha=0.4)


def marquee(c, x0, y0, x1, y1, t):
    rrect(c, x0, y0, x1, y1, 30, P("#140a2a", alpha=0.95))
    rrect(c, x0, y0, x1, y1, 30, P("#d9a441", "stroke", 8, shader=lin(x0, 0, x1, 0, GOLD)))
    per = 2 * ((x1 - x0) + (y1 - y0))
    n = int(per / 46)
    for i in range(n):
        d = i * per / n
        if d < x1 - x0:
            bx, by = x0 + d, y0
        elif d < (x1 - x0) + (y1 - y0):
            bx, by = x1, y0 + d - (x1 - x0)
        elif d < 2 * (x1 - x0) + (y1 - y0):
            bx, by = x1 - (d - (x1 - x0) - (y1 - y0)), y1
        else:
            bx, by = x0, y1 - (d - 2 * (x1 - x0) - (y1 - y0))
        on = (i + int(t * 6)) % 3 == 0
        if on:
            glow(c, R.RES.glow_warm, bx, by, 26, 0.6)
        oval(c, bx, by, 8, 8, P("#fff1c4" if on else "#8a5a17"))


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if f.measureText(test) > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def question_card(c, t, num, text, k=1.0, y0=520, y1=930):
    marquee(c, 70, y0, 1010, y1, t)
    if num:
        pill_gold(c, 540, y0, f"PREGUNTA {num} / 3", 1.0, size=34, bg="#d9a441")
    f = font(R.RES.xbold, 54)
    lines = wrap(text, f, 820)
    lh = 66
    top = (y0 + y1) / 2 - (len(lines) - 1) * lh / 2 + 20
    for i, ln in enumerate(lines):
        text_center(c, ln, 540, top + i * lh, f, P("#ffffff", alpha=k))


def ab_buttons(c, t, y=1340, pulse=0.0, lit=None, a=1.0):
    for i, (letter, lab, col) in enumerate((("A", "VERDADERO", GREEN), ("B", "FALSO", RED))):
        x = 290 + i * 500
        on = lit == letter
        dim = 0.35 if (lit is not None and not on) else 1.0
        s = 1 + 0.05 * pulse * math.sin(t * 10 + i * math.pi) + (0.08 if on else 0)
        c.save()
        c.translate(x, y)
        c.scale(s, s)
        if on or pulse > 0:
            glow(c, R.RES.glow_white if on else R.RES.glow_warm, 0, 0, 260, (0.5 if on else 0.2) * a)
        rrect(c, -220, -86, 220, 86, 44, P(col, shader=lin(0, -86, 0, 86, [R.mix_col(col, "#ffffff", 0.3), col]), alpha=a * dim))
        rrect(c, -220, -86, 220, 86, 44, P("#ffffff", "stroke", 4, alpha=0.6 * a * dim))
        oval(c, -150, 0, 56, 56, P("#ffffff", alpha=a * dim))
        text_center(c, letter, -150, 26, font(R.RES.xbold, 74), P(col, alpha=a * dim))
        text_center(c, lab, 45, 18, font(R.RES.xbold, 46 if letter == "B" else 40), P("#ffffff", alpha=a * dim))
        c.restore()


def countdown(c, x, y, lt, q_end, dur=3.1):
    u = (lt - q_end) / dur
    if u < 0 or u > 1.08:
        return
    n = max(1, 3 - int(u * 3))
    frac = (u * 3) % 1
    pop = 1 + 0.25 * (1 - ease_out(clamp(frac * 4)))
    col = ["#e8414f", "#ffb84a", "#2fbf71"][n - 1]
    glow(c, R.RES.glow_warm, x, y, 260, 0.4)
    oval(c, x, y, 125, 125, P("#0c0818", alpha=0.92))
    arc = skia.Path()
    arc.addArc(RECT(x - 115, y - 115, x + 115, y + 115), -90, 360 * (1 - clamp(u)))
    c.drawPath(arc, P(col, "stroke", 16))
    c.save()
    c.translate(x, y)
    c.scale(pop, pop)
    text_center(c, str(n) if u <= 1 else "0", 0, 52, font(R.RES.xbold, 150), P("#ffffff"))
    c.restore()


def tracker(c, revealed, y=1500, r=50):
    for i in range(3):
        x = 540 + (i - 1) * r * 3.0
        ans = ANSWERS[i]
        if i < revealed:
            col = GREEN if ans == "A" else RED
            oval(c, x, y, r, r, P(col))
            text_center(c, ans, x, y + r * 0.44, font(R.RES.xbold, r * 1.2), P("#ffffff"))
        else:
            oval(c, x, y, r, r, P("#ffffff", "stroke", 4, alpha=0.5))
            text_center(c, "?", x, y + r * 0.4, font(R.RES.xbold, r * 1.08), P("#ffffff", alpha=0.5))
        if r >= 40:
            text_center(c, str(i + 1), x, y - r - 16, font(R.RES.bold, 26), P("#e9d8b8", alpha=0.8))


def mic(cc, out, key="R"):
    hx, hy = out[key]
    c = cc
    c.drawLine(hx, hy, hx + 6, hy + 70, P("#2a2a33", "stroke", 12))
    oval(c, hx - 2, hy - 14, 24, 26, P("#9a9aa8", shader=rad(hx - 8, hy - 20, 30, ["#e0e0ea", "#5a5a66"])))


# ---- ilustraciones -------------------------------------------------------------


def wrists(c, x, y, t, rub=1.0):
    off = math.sin(t * 14) * 40 * rub
    for i, (dx, rot) in enumerate(((-off, -8), (off, 8))):
        c.save()
        c.translate(x + dx, y + (i * 30 - 15))
        c.rotate(rot)
        rrect(c, -230, -34, -40, 34, 30, P("#3a69cf"))
        rrect(c, -60, -30, 170, 30, 28, P("#f6c09a", shader=lin(0, -30, 0, 30, ["#ffe2c8", "#eeb08a"])))
        c.restore()
    for j in range(4):
        wv = skia.Path()
        bx = x - 90 + j * 60
        wv.moveTo(bx, y - 70)
        for q in range(5):
            wv.quadTo(bx + (12 if q % 2 else -12), y - 90 - q * 22, bx, y - 110 - q * 22)
        c.drawPath(wv, P("#ff7a3c", "stroke", 5, alpha=0.6 * rub * (0.6 + 0.4 * math.sin(t * 8 + j))))
    R.aroma(c, x, y - 60, t, n=24, height=300, spread=60, intensity=0.8 * rub, seed=4, speed=0.8)


def bathroom(c, x, y, t, cross=0.0):
    x0, y0, x1, y1 = x - 330, y - 170, x + 330, y + 170
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(RECT(x0, y0, x1, y1), 30, 30), True)
    c.drawRect(RECT(x0, y0, x1, y1), P("#cfe9f4"))
    for i in range(16):
        c.drawLine(x0 + i * 46, y0, x0 + i * 46, y1, P("#a8d0e0", "stroke", 2))
    for j in range(9):
        c.drawLine(x0, y0 + j * 46, x1, y0 + j * 46, P("#a8d0e0", "stroke", 2))
    rrect(c, x - 120, y - 140, x + 120, y + 10, 16, P("#e9f6fb"))
    rrect(c, x - 120, y - 140, x + 120, y + 10, 16, P("#8ab8cc", "stroke", 5))
    c.drawRect(RECT(x - 200, y + 50, x + 200, y + 64), P("#ffffff"))
    mini_bottle(c, x - 60, y + 50, 0.9, 0, "#d9a441")
    mini_bottle(c, x + 50, y + 50, 0.8, 1, "#e0558a")
    for i in range(6):
        u = (t * 0.4 + i / 6) % 1
        oval(c, x - 250 + i * 100 + 20 * math.sin(t + i), y + 160 - u * 330, 70 * (0.6 + u), 40 * (0.6 + u),
             P("#ffffff", alpha=0.5 * math.sin(math.pi * u)))
    c.restore()
    if cross > 0:
        e = ease_out(cross)
        c.drawLine(x0 + 20, y0 + 20, lerp(x0 + 20, x1 - 20, e), lerp(y0 + 20, y1 - 20, e), P(RED, "stroke", 22))
        c.drawLine(x1 - 20, y0 + 20, lerp(x1 - 20, x0 + 20, e), lerp(y0 + 20, y1 - 20, e), P(RED, "stroke", 22))


def edp_edt(c, x, y, t, bars=0.0):
    for i, (lab, lvl, col) in enumerate((("EDP", 0.85, "#c9902f"), ("EDT", 0.5, "#f7d27a"))):
        bx = x - 170 + i * 340
        R.draw_bottle(c, bx, y + 150, 0.62, glow_a=0.4)
        rrect(c, bx - 80, y + 160, bx + 80, y + 216, 20, P("#fff8ea"))
        text_center(c, lab, bx, y + 202, font(R.RES.xbold, 40), P("#2a1608"))
        if bars > 0:
            h = 230 * lvl * ease_out(bars)
            rrect(c, bx + 100, y + 150 - h, bx + 150, y + 150, 12, P(col))
            if bars > 0.6:
                text_center(c, ["15–20%", "5–15%"][i], bx + 125, y + 130 - h, font(R.RES.xbold, 28), P("#fff1c4"))


def check_icon(c, x, y, r, col=GREEN):
    oval(c, x, y, r, r, P(col))
    m = skia.Path()
    m.moveTo(x - r * 0.45, y)
    m.lineTo(x - r * 0.12, y + r * 0.35)
    m.lineTo(x + r * 0.5, y - r * 0.35)
    c.drawPath(m, P("#ffffff", "stroke", r * 0.24))


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def scene_intro(c, k):
    lt = k.lt
    T = k.w
    camera(c, 1.0 + 0.03 * ease_out(prog(lt, 0, k.D)), 540, 960, k.t)
    stage(c, k.t)
    marquee(c, 70, 520, 1010, 900, k.t)
    punch = 1 + 0.08 * (1 - ease_out(prog(lt, 0, 0.35)))
    c.save()
    c.translate(540, 680)
    c.scale(punch, punch)
    gold_text(c, "¿CUÁNTO SABES", 0, 0, 92, white=True)
    gold_text(c, "DE PERFUMES?", 0, 108, 100)
    c.restore()
    pill_gold(c, 540, 900, "3 PREGUNTAS · 3 SEGUNDOS", prog(lt, 0.4, 0.7), size=34, bg="#d9a441")
    lit = "A" if T(4) - 0.1 <= lt < T(7) - 0.1 else ("B" if lt >= T(7) - 0.1 else None)
    ab_buttons(c, k.t, 1300, pulse=0.0, lit=lit, a=ease_out(prog(lt, 0.2, 0.6)))
    draw_kid(c, 540, 1760, 0.6, k.t, "happy", look=(0, -0.2), hands={"R": (150, -470), "L": (-120, -220)},
             talk=talk(k.t), front_props=mic)


def make_question(num):
    def scene(c, k):
        lt = k.lt
        q_end = (k.s["vo_start"] + k.s["dur"]) - k.s["start"]
        cd = clamp((lt - q_end) / 3.1)
        z = 1.0 + 0.04 * ease_in_out(cd)
        camera(c, z, 540, 1000, k.t)
        stage(c, k.t)
        question_card(c, k.t, num, QUESTIONS[num - 1], k=ease_out(prog(lt, 0.1, 0.5)), y0=610, y1=960)
        ill_a = 1 - 0.55 * smooth(prog(lt, q_end - 0.2, q_end + 0.2))
        c.saveLayerAlpha(None, int(255 * ill_a))
        if num == 1:
            wrists(c, 540, 1170, k.t, rub=1.0)
        elif num == 2:
            bathroom(c, 540, 1150, k.t)
        else:
            edp_edt(c, 540, 1060, k.t)
        c.restore()
        countdown(c, 540, 1160, lt, q_end)
        ab_buttons(c, k.t, 1410, pulse=1.0 if lt > q_end else 0.0)
    return scene


def scene_cta(c, k):
    lt = k.lt
    T = k.w
    camera(c, 1.0, 540, 960, k.t)
    stage(c, k.t)
    marquee(c, 70, 520, 1010, 900, k.t)
    text_center(c, "COMENTA TUS RESPUESTAS", 540, 600, font(R.RES.xbold, 50), P("#fff1c4"))
    word = "AAB" if lt < T(6) - 0.2 else "BAB"
    start = T(4) - 0.4 if word == "AAB" else T(6) - 0.4
    typed = word[: int(3 * prog(lt, start, start + 0.35))]
    c.save()
    c.translate(540, 700)
    rrect(c, -380, -56, 380, 56, 56, P("#fff8ea"))
    oval(c, -320, 0, 34, 34, P("#d9a441"))
    if typed:
        c.drawString(typed, -265, 22, font(R.RES.xbold, 60), P("#2a1608"))
    else:
        c.drawString("Agrega un comentario...", -265, 14, font(R.RES.semi, 34), P("#9a8a70"))
    oval(c, 320, 0, 38, 38, P("#d9a441"))
    ar = skia.Path()
    ar.moveTo(305, -16)
    ar.lineTo(338, 0)
    ar.lineTo(305, 16)
    ar.close()
    c.drawPath(ar, P("#2a1608"))
    c.restore()
    gk = prog(lt, T(11) - 0.2, T(11) + 0.25)
    if gk > 0:
        s = back_out(gk)
        c.save()
        c.translate(540, 840)
        c.scale(s * 0.8, s * 0.8)
        rrect(c, -380, -90, 380, 90, 44, P("#d9a441", shader=lin(-380, -90, 380, 90, GOLD)))
        text_center(c, "10%", -190, 42, font(R.RES.xbold, 116), P("#2a1608"))
        c.drawString("DE", 0, -10, font(R.RES.xbold, 46), P("#2a1608"))
        c.drawString("DESCUENTO", -10, 44, font(R.RES.xbold, 50), P("#2a1608"))
        c.restore()
        R.burst(c, 540, 840, lt - T(11) + 0.1, dur=1.1, n=40, radius=380, seed=7, intensity=0.8)
    rk = prog(lt, T(14) - 0.2, T(14) + 0.2)
    if rk > 0:
        s = back_out(rk, 2.2)
        c.save()
        c.translate(540, 1110)
        c.scale(s, s)
        gold_text(c, "LAS RESPUESTAS...", 0, 0, 78)
        c.restore()
    tracker(c, 0, y=1290)
    draw_kid(c, 540, 1800, 0.55, k.t, "happy", look=(0, -0.3), hands={"R": (150, -470), "L": (-120, -220)},
             talk=talk(k.t), front_props=mic)


def make_reveal(num):
    def scene(c, k):
        lt = k.lt
        T = k.w
        camera(c, 1.0, 540, 980, k.t)
        stage(c, k.t)
        ans = ANSWERS[num - 1]
        question_card(c, k.t, num, QUESTIONS[num - 1], y0=600, y1=900)
        sk = prog(lt, T(1) - 0.15, T(1) + 0.15)
        if num == 1:
            wrists(c, 540, 1090, k.t, rub=1.0)
        elif num == 2:
            c.save()
            c.translate(540, 1070)
            c.scale(0.85, 0.85)
            bathroom(c, 0, 0, k.t, cross=prog(lt, T(3) - 0.1, T(3) + 0.3))
            c.restore()
        else:
            edp_edt(c, 540, 990, k.t, bars=prog(lt, T(6) - 0.2, T(9)))
        ab_buttons(c, k.t, 1320, lit=ans if sk > 0 else None)
        if sk > 0:
            col = GREEN if ans == "A" else RED
            s = lerp(2.0, 1.0, ease_out(sk))
            c.save()
            c.translate(540, 1170 if num != 3 else 1205)
            c.rotate(-6)
            c.scale(s, s)
            lab = f"{ans} · {'VERDADERO' if ans == 'A' else 'FALSO'}"
            f = font(R.RES.xbold, 64)
            w = f.measureText(lab) + 70
            rrect(c, -w / 2, -60, w / 2, 44, 18, P("#0c0818", alpha=0.85 * clamp(sk * 3)))
            rrect(c, -w / 2, -60, w / 2, 44, 18, P(col, "stroke", 8, alpha=clamp(sk * 3)))
            text_center(c, lab, 0, 14, f, P(col, alpha=clamp(sk * 3)))
            c.restore()
        tracker(c, num if sk > 0.5 else num - 1, y=1450, r=32)
        if num == 3 and lt > T(9):
            fk = prog(lt, T(9), T(9) + 0.4)
            c.drawRect(RECT(0, 0, W, H), P("#06040f", alpha=0.92 * fk))
            if fk > 0:
                s = back_out(fk)
                c.save()
                c.translate(540, 820)
                c.scale(s, s)
                glow(c, R.RES.glow_warm, 0, 0, 380, 0.5)
                gold_text(c, "RESPUESTAS", 0, -60, 70, white=True)
                gold_text(c, "A · B · A", 0, 70, 140)
                c.restore()
                draw_img(c, R.RES.logo_gold, 540, 1150, 200 * s, alpha=fk)
                text_center(c, "Otto Aleman Perfumes", 540, 1310, font(R.RES.semi, 44), P("#fff1c4", alpha=fk))
                R.burst(c, 540, 820, lt - T(9), dur=1.2, n=60, radius=460, seed=9, intensity=0.9)
    return scene


SCENES = [scene_intro, make_question(1), make_question(2), make_question(3), scene_cta,
          make_reveal(1), make_reveal(2), make_reveal(3)]


def install():
    R.Res = O1.OttoRes
    R.SCENES = SCENES
    R.SCENE_GRADE = {}
    R.FADE_IN = 0.0
    R.SUB_PLATE = True
    O1.ENV = O1.build_env()


if __name__ == "__main__":
    install()
    R.main()
