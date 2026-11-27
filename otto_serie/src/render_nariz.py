"""Otto Aleman Perfumes — "Estás haciendo esto mal con tu perfume" (adaptación olfativa), en bucle.

Gancho acusador → la nariz con venda → cerebro que apaga el interruptor "PERFUME" → reloj de 2 minutos →
alarma de gas → los demás sí te huelen → el error de echarse más → mito del café → lo que sí ayuda →
rotar perfumes → decants Otto Aleman → Black Friday 3x2 → vuelve al primer cuadro.
Transiciones encadenadas (la cámara entra a la nariz y sale del cerebro). Personaje A, voz David.
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
import render_mandarin as MS  # noqa: E402
import render_elixir as EX  # noqa: E402
from render_decant_tarde import (R, P, lin, rad, oval, rrect, clamp, lerp, smooth, ease_out, ease_in_out, back_out,  # noqa: E402
                                 prog, rng, glow, text_center, W, H, RECT, F, M, INK, GOLDD, OVER, bg, title, sticker,
                                 hero, decant, Cam)

FEET = 1500
S0 = 0.92
NOSE = (540 + 4, FEET - 874 * S0 + 26 * S0)   # punta de la nariz del personaje (pose neutral)


def hold_decant(t, a=-8):
    return lambda c, x, y: decant(c, x, y - 80, 190, a, t, 0.7)


def spray_puff(c, x, y, t0, lt, n=30, size=1.0, col="#ffffff", spread=1.0):
    u = lt - t0
    if not (0 < u < 1.6):
        return
    r = rng(int(t0 * 10) % 97)
    for i in range(n):
        a = math.radians(-30 + r.random() * 60) * spread
        d = (80 + r.random() * 260) * ease_out(clamp(u / 1.0)) * size
        oval(c, x - math.cos(a) * d, y + math.sin(a) * d - 30 * u, (8 + 14 * r.random()) * size, (8 + 14 * r.random()) * size,
             P(col, alpha=0.65 * (1 - u / 1.6)))


def blindfold(c, x, y, s, k):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s * back_out(clamp(k), 1.8), s * back_out(clamp(k), 1.8))
    rrect(c, -70, -24, 70, 24, 22, P("#1a1a22"))
    c.drawLine(-70, 0, -150, -10, P("#1a1a22", "stroke", 10))
    c.drawLine(70, 0, 150, -10, P("#1a1a22", "stroke", 10))
    for sd in (-1, 1):  # ojitos cerrados bordados en el antifaz
        p = skia.Path()
        p.moveTo(sd * 34 - 18, 0)
        p.quadTo(sd * 34, 12, sd * 34 + 18, 0)
        c.drawPath(p, P("#ffffff", "stroke", 4))
    c.restore()


def brain(c, x, y, s, t, switch_on=0.0, alarm=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for (bx, by, r) in ((-120, -40, 120), (0, -90, 130), (120, -40, 120), (-80, 60, 110), (80, 60, 110), (0, 20, 120)):
        oval(c, bx, by, r, r * 0.85, P("#f4a8b8", shader=rad(bx - r * 0.3, by - r * 0.3, r * 1.4, ["#ffd0dc", "#e88aa0"])))
    for i in range(7):  # pliegues
        p = skia.Path()
        p.moveTo(-200 + i * 60, -120)
        p.cubicTo(-180 + i * 60, -40, -220 + i * 60, 20, -190 + i * 60, 100)
        c.drawPath(p, P("#c86a80", "stroke", 6, alpha=0.6))
    c.drawPath(skia.Path().addArc(RECT(-260, -260, 260, 120), 200, 140), P("#2a2a34", "stroke", 22))  # audífonos
    for sd in (-1, 1):
        rrect(c, sd * 250 - 34, -110, sd * 250 + 34, 20, 20, P("#3a3a44"))
    c.restore()
    # panel de interruptores
    px, py = x, y + 300 * s
    rrect(c, px - 300, py - 90, px + 300, py + 90, 24, P("#ffffff"))
    rrect(c, px - 300, py - 90, px + 300, py + 90, 24, P(INK, "stroke", 4))
    for i, (lab, on) in enumerate((("PERFUME", switch_on), ("¡GAS!", alarm))):
        sx = px - 150 + i * 300
        rrect(c, sx - 60, py - 34, sx + 60, py + 34, 34, P("#2fbf71" if on > 0.5 else "#c8c8d0"))
        oval(c, sx + lerp(-30, 30, on), py, 28, 28, P("#ffffff"))
        text_center(c, lab, sx, py + 74, F(R.RES.xbold, 30), P("#e0203a" if (i == 1 and alarm > 0.5) else INK))


def alarm_light(c, k, t):
    if k <= 0:
        return
    blink = 0.5 + 0.5 * math.sin(t * 14)
    c.drawRect(RECT(-300, -300, W + 300, H + 300), P("#ff2020", alpha=0.18 * k * blink))
    for sd in (-1, 1):
        oval(c, 540 + sd * 360, 640, 50, 50, P("#ff3030", alpha=k))
        glow(c, R.RES.glow_warm, 540 + sd * 360, 640, 180, 0.6 * k * blink)


def timer(c, x, y, sec, k):
    if k <= 0:
        return
    s = back_out(clamp(k), 1.6)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -220, -90, 220, 90, 30, P(INK))
    m, ss = int(sec // 60), int(sec % 60)
    text_center(c, f"{m}:{ss:02d}", 0, 40, F(R.RES.xbold, 120), P("#ffffff"))
    c.restore()


def smell_bar(c, x, y, w, level, k):
    if k <= 0:
        return
    rrect(c, x - w / 2, y - 30, x + w / 2, y + 30, 30, P("#e0dcd4"))
    rrect(c, x - w / 2, y - 30, x - w / 2 + w * level, y + 30, 30, P(GOLDD if level > 0.6 else "#ff8a2a"))
    text_center(c, f"OLOR QUE SENTÍS: {int(level * 100)}%", x, y + 80, F(R.RES.xbold, 34), P(INK))


def coffee_jar(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -150, -300, 150, 0, 30, P("#ffffff", alpha=0.6))
    r = rng(4)
    for i in range(40):
        bx, by = -120 + r.random() * 240, -270 + r.random() * 250
        c.save()
        c.translate(bx, by)
        c.rotate(r.random() * 180)
        oval(c, 0, 0, 22, 15, P("#4a2a14", shader=rad(-6, -4, 26, ["#7a4a24", "#2a140a"])))
        c.drawLine(-14, 0, 14, 0, P("#1a0a04", "stroke", 3))
        c.restore()
    rrect(c, -160, -340, 160, -296, 12, P("#8a5a32"))
    rrect(c, -150, -300, 150, 0, 30, P(INK, "stroke", 4, alpha=0.4))
    c.restore()


def tip_card(c, x, y, txt, icon, k):
    if k <= 0:
        return
    s = back_out(clamp(k), 1.6)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -380, -90, 380, 90, 30, P("#ffffff"))
    rrect(c, -380, -90, 380, 90, 30, P(INK, "stroke", 3, alpha=0.4))
    MS_check(c, -300, 0, 44)
    c.drawString(txt, -230, 13, F(R.RES.xbold, 36), P(INK))
    icon(c, 320, 0)
    c.restore()


def MS_check(c, x, y, r):
    oval(c, x, y, r, r, P("#2fbf71"))
    p = skia.Path()
    p.moveTo(x - r * 0.45, y)
    p.lineTo(x - r * 0.1, y + r * 0.35)
    p.lineTo(x + r * 0.5, y - r * 0.35)
    c.drawPath(p, P("#ffffff", "stroke", r * 0.22))


def ic_skin(c, x, y):
    oval(c, x, y, 40, 60, P(M.STYLES["A"]["skin"][0]))


def ic_air(c, x, y):
    for i in range(3):
        p = skia.Path()
        p.moveTo(x - 50, y - 30 + i * 30)
        p.quadTo(x, y - 50 + i * 30, x + 40, y - 30 + i * 30)
        p.quadTo(x + 60, y - 10 + i * 30, x + 40, y - 6 + i * 30)
        c.drawPath(p, P("#5ab0e0", "stroke", 8))


def ic_ask(c, x, y):
    rrect(c, x - 50, y - 40, x + 50, y + 30, 20, P("#2f6bff"))
    text_center(c, "?", x, y + 20, F(R.RES.xbold, 60), P("#ffffff"))


DEC_COLS = ["#ffb04a", "#ff6a8a", "#7ad0ff", "#b08aff", "#7ad070", "#e0a060"]


def color_decant(c, x, y, h, col, t, rot=0.0):
    sys.modules["render_ep4"].decant_vec(c, x, y, h, rot, t, 0.7, 0.0)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    rrect(c, -h * 0.1, h * 0.12, h * 0.1, h * 0.36, h * 0.08, P(col, alpha=0.9))
    c.restore()


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def s0(c, k, final=False):  # gancho
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    hero(c, k, 540, FEET, S0, [(0, "sostiene"), (T(3) + 0.1, "piensa")], hold_fn=hold_decant(k.t))
    for j in range(3):
        spray_puff(c, 700, 640, 0.2 + j * 0.45, lt, n=22)
    if not final:
        hk = prog(lt, T(0) - 0.15, T(0) + 0.15)
        if hk > 0:
            def d(cc):
                s_ = lerp(2.2, 1.0, ease_out(hk))
                cc.save()
                cc.translate(540, 600)
                cc.rotate(-6)
                cc.scale(s_, s_)
                rrect(cc, -400, -80, 400, 80, 20, P("#e0203a", alpha=clamp(hk * 3)))
                text_center(cc, "¡LO ESTÁS HACIENDO MAL!", 0, 22, F(R.RES.xbold, 60), P("#ffffff", alpha=clamp(hk * 3)))
                cc.restore()
            OVER.append(d)


def s1(c, k):  # en la mañana… a la hora ya no huele
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    hours = lerp(8, 9, ease_in_out(prog(lt, T(6), T(9))))
    D.clock(c, 830, 760, 150, hours)
    hero(c, k, 400, FEET, S0, [(0, "sostiene"), (T(6), "piensa"), (T(12), "encoge")], hold_fn=hold_decant(k.t))
    spray_puff(c, 560, 640, 0.3, lt, n=26)
    sticker(c, "+1 HORA", 830, 970, prog(lt, T(8), T(8) + 0.3), bg_col="#e0203a", size=46, rot=5)
    sticker(c, "¿YA NO HUELE?", 540, 560, prog(lt, T(12), T(12) + 0.3), bg_col=INK, size=56, rot=-3)


def s2(c, k):  # no se fue: tu nariz te está mintiendo (aparece la venda)
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    hero(c, k, 540, FEET, S0, [(0, "neutral")])
    blindfold(c, NOSE[0], NOSE[1], S0, prog(lt, T(5) - 0.1, T(5) + 0.25))
    sticker(c, "NO SE FUE", 540, 1360, prog(lt, T(2), T(3)), bg_col="#2fbf71", size=56, rot=-3)


def s3(c, k):  # adaptación olfativa: el cerebro apaga el interruptor
    lt, T = k.lt, k.w
    bg(c, k.t, "pink", room=False)
    off = 1 - prog(lt, T(6), T(8))
    brain(c, 540, 860, 1.1, k.t, switch_on=off)
    sticker(c, "ADAPTACIÓN OLFATIVA", 540, 560, prog(lt, T(2), T(3)), bg_col=GOLDD, size=50, rot=-3)
    sticker(c, "APAGADO", 380, 1460, prog(lt, T(8), T(9)), bg_col="#e0203a", size=46, rot=4)


def s4(c, k):  # en pocas respiraciones; la mitad en 2 minutos
    lt, T = k.lt, k.w
    bg(c, k.t, "white", room=False)
    sec = 120 * ease_in_out(prog(lt, T(9) - 0.3, T(17)))
    timer(c, 540, 720, sec, prog(lt, 0, 0.4))
    level = 1 - 0.5 * ease_in_out(prog(lt, T(9) - 0.3, T(17)))
    smell_bar(c, 500, 940, 700, level, prog(lt, 0.2, 0.6))
    hero(c, k, 900, FEET + 220, 0.5, [(0, "piensa"), (T(9), "espera")])
    sticker(c, "POCAS RESPIRACIONES", 360, 1300, prog(lt, T(7), T(8)), bg_col=INK, size=40, rot=-3)


def s5(c, k):  # para protegerte: detectar gas o humo
    lt, T = k.lt, k.w
    bg(c, k.t, "pink", room=False)
    al = prog(lt, T(13) - 0.1, T(13) + 0.1)
    alarm_light(c, al, k.t)
    brain(c, 540, 820, 1.0, k.t, switch_on=0.0, alarm=al)
    if al > 0:
        r = rng(4)
        for i in range(8):  # humo
            u = ((k.t * 0.4 + i / 8) % 1)
            oval(c, 200 + r.random() * 680, 1500 - u * 500, 40 + 60 * u, 40 + 60 * u, P("#8a8a96", alpha=0.35 * (1 - u)))
    sticker(c, "TE PROTEGE", 540, 560, prog(lt, T(5), T(6)), bg_col="#2f6bff", size=56, rot=-3)


def s6(c, k):  # vos no te olés… pero los demás sí
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    hero(c, k, 330, FEET, 0.85, [(0, "encoge")])
    blindfold(c, 330 + 4, FEET - 874 * 0.85 + 26 * 0.85, 0.85, 1.0)
    wk = ease_out(prog(lt, T(5), T(5) + 1.0))
    px = lerp(1250, 800, wk)
    p = M.walk(M.POSES["enamorado"] if lt > T(8) else M.POSES["neutral"], k.t, amp=1 - wk * 0.9)
    M.draw(c, px, FEET, 0.8, k.t, p, style=M.STYLES["C"])
    if lt > T(8):
        for i in range(3):
            u = ((k.t * 0.6 + i / 3) % 1)
            hp = skia.Path()
            hx, hy = px + 60 + 30 * math.sin(u * 6), FEET - 900 - u * 200
            hp.moveTo(hx, hy + 18)
            hp.cubicTo(hx - 30, hy - 2, hx - 15, hy - 26, hx, hy - 9)
            hp.cubicTo(hx + 15, hy - 26, hx + 30, hy - 2, hx, hy + 18)
            c.drawPath(hp, P("#ff3d6a", alpha=1 - u))
        sticker(c, "¿QUÉ PERFUME ES?", 760, 640, prog(lt, T(8), T(8) + 0.3), bg_col="#ffffff", fg=INK, size=40, rot=4, border=INK)


def s7(c, k):  # el error: te echás más y más
    lt, T = k.lt, k.w
    bg(c, k.t, "green")
    hero(c, k, 540, FEET, S0, [(0, "sostiene"), (T(11) + 0.3, "mareado")], hold_fn=hold_decant(k.t))
    for j, wi in enumerate((6, 7, 9, 11)):
        spray_puff(c, 700, 640, T(wi), lt, n=30 + j * 12, size=1 + j * 0.45, col="#fff0d0")
    fog = prog(lt, T(7), T(11) + 0.4)
    if fog > 0:
        c.drawRect(RECT(-300, -300, W + 300, H + 300), P("#f4e8c8", alpha=0.35 * fog))
    for i, (x, st) in enumerate(((150, "B"), (930, "D"))):  # la gente se va tosiendo
        e = prog(lt, T(9), T(11) + 0.6)
        M.draw(c, x + (-1 if i == 0 else 1) * 400 * e, FEET + 120, 0.5, k.t, M.walk(M.POSES["asco"], k.t), style=M.STYLES[st])
    MS.error_stamp(prog(lt, T(4), T(4) + 0.3))


def s8(c, k):  # mito del café
    lt, T = k.lt, k.w
    bg(c, k.t, "cream", room=False)
    coffee_jar(c, 420, 1300, 1.4)
    hero(c, k, 880, FEET + 120, 0.6, [(0, "piensa"), (T(6), "encoge")])
    mk = prog(lt, T(6) - 0.1, T(6) + 0.2)
    if mk > 0:
        def d(cc):
            s_ = lerp(2.2, 1.0, ease_out(mk))
            cc.save()
            cc.translate(420, 900)
            cc.rotate(-12)
            cc.scale(s_, s_)
            rrect(cc, -200, -70, 200, 70, 14, P("#e0203a", "stroke", 12, alpha=clamp(mk * 3)))
            text_center(cc, "MITO", 0, 30, F(R.RES.xbold, 100), P("#e0203a", alpha=clamp(mk * 3)))
            cc.restore()
        OVER.append(d)


def s9(c, k):  # lo que sí ayuda
    lt, T = k.lt, k.w
    bg(c, k.t, "cream", room=False)
    sticker(c, "LO QUE SÍ AYUDA", 500, 560, prog(lt, 0.0, 0.3), bg_col="#2fbf71", size=56, rot=-3)
    tip_card(c, 500, 700, "Oler tu piel sin perfume", ic_skin, prog(lt, T(4) - 0.1, T(4) + 0.3))
    tip_card(c, 500, 920, "Aire fresco", ic_air, prog(lt, T(10) - 0.1, T(10) + 0.3))
    tip_card(c, 500, 1140, "Preguntarle a alguien", ic_ask, prog(lt, T(15) - 0.1, T(15) + 0.3))
    hero(c, k, 930, FEET + 160, 0.4, [(0, "pulgar")])


def s10(c, k):  # rotar perfumes
    lt, T = k.lt, k.w
    bg(c, k.t, "gold", room=False)
    for i in range(6):
        a = (i - 2.5) * 0.9 + lt * 0.6
        x = 540 + math.sin(a) * 360
        depth = math.cos(a)
        if depth < -0.2:
            continue
        color_decant(c, x, 1050 - 20 * depth, 260 + 120 * depth, DEC_COLS[i], k.t)
    sticker(c, "ROTÁ TUS PERFUMES", 540, 620, prog(lt, T(5), T(6)), bg_col=INK, size=54, rot=-3)
    hero(c, k, 880, FEET + 200, 0.5, [(0, "señala")])


def s11(c, k):  # Otto Aleman: decants 5 y 10 ml
    lt, T = k.lt, k.w
    EX.warm_bg(c, k.t, "gold")
    img = M.logo()
    lk = back_out(prog(lt, T(3) - 0.2, T(3) + 0.2), 1.5)
    if lk > 0:
        w = 260 * lk
        h = w * img.height() / img.width()
        c.drawImageRect(img, RECT(540 - w / 2, 640 - h / 2, 540 + w / 2, 640 + h / 2), R.SAMP, skia.Paint())
        text_center(c, "OTTO ALEMAN PERFUMES", 540, 820, F(R.RES.xbold, 50), P("#ffffff", alpha=clamp(lk)))
    d5 = prog(lt, T(9) - 0.2, T(9) + 0.2)
    d10 = prog(lt, T(11) - 0.2, T(11) + 0.2)
    if d5 > 0:
        decant(c, 330, lerp(1900, 1250, back_out(d5, 1.3)), 300, -4, k.t, 0.6)
        text_center(c, "5 ML", 330, 1470, F(R.RES.xbold, 50), P("#ffffff", alpha=d5))
    if d10 > 0:
        decant(c, 580, lerp(1900, 1220, back_out(d10, 1.3)), 380, 4, k.t, 0.6)
        text_center(c, "10 ML", 580, 1470, F(R.RES.xbold, 50), P("#ffffff", alpha=d10))
    hero(c, k, 880, FEET + 140, 0.55, [(0, "celebra"), (T(6), "señala")], talk=True)


def s12(c, k):  # Black Friday 3x2
    lt, T = k.lt, k.w
    EX.warm_bg(c, k.t, "black")
    bk = prog(lt, T(5) - 0.2, T(5) + 0.2)

    def bf(cc):
        if bk <= 0:
            return
        s_ = back_out(bk, 1.8)
        cc.save()
        cc.translate(540, 620)
        cc.scale(s_, s_)
        cc.rotate(-4)
        rrect(cc, -400, -90, 400, 90, 20, P("#000000"))
        rrect(cc, -400, -90, 400, 90, 20, P("#e0203a", "stroke", 8))
        f = F(R.RES.xbold, 110)
        txt = "BLACK FRIDAY"
        w = f.measureText(txt)
        cc.drawString(txt, -w / 2, 38, f, P("#ffffff", shader=lin(0, -40, 0, 40, ["#ffffff", "#ffd04a"])))
        cc.restore()
    OVER.append(bf)
    tk = prog(lt, T(7) - 0.1, T(9) + 0.1)
    if tk > 0:
        s_ = back_out(clamp(tk), 2)
        c.save()
        c.translate(540, 900)
        c.scale(s_, s_)
        glow(c, R.RES.glow_warm, 0, -40, 300, 0.6)
        text_center(c, "3x2", 0, 40, F(R.RES.xbold, 220), P("#ffd04a"))
        c.restore()
    for i in range(2):
        dk = prog(lt, T(11) - 0.2 + i * 0.25, T(11) + 0.2 + i * 0.25)
        if dk > 0:
            color_decant(c, 260 + i * 200, lerp(1900, 1340, back_out(dk, 1.3)), 300, DEC_COLS[i], k.t, (-6, 6)[i])
    fk = prog(lt, T(16) - 0.2, T(17))
    if fk > 0:
        c.drawString("+", 610, 1360, F(R.RES.xbold, 100), P("#2fbf71", alpha=fk))
        color_decant(c, 800, lerp(1900, 1340, back_out(fk, 1.3)), 300, DEC_COLS[2], k.t, 8)
        OVER.append(lambda cc: sticker(cc, "¡GRATIS!", 800, 1130, fk, bg_col="#2fbf71", size=60, rot=4))
    if lt > T(17):
        r = rng(3)
        for i in range(60):
            x = r.random() * W
            y = -50 + ((lt - T(17)) * (400 + 400 * r.random()) + r.random() * 200)
            if y > H:
                continue
            c.save()
            c.translate(x, y)
            c.rotate(k.t * 200 + i * 30)
            c.drawRect(RECT(-11, -6, 11, 6), P(["#d6a24a", "#e0203a", "#2fbf71", "#ffffff"][i % 4]))
            c.restore()


def s13(c, k):  # "no hagas esto con tu perfume" → vuelve al inicio
    lt, T = k.lt, k.w
    bg(c, k.t, "cream")
    hero(c, k, 540, FEET, S0, [(0, "señala"), (T(4), "sostiene")], talk=True, hold_fn=hold_decant(k.t))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13]
CAMS = [
    Cam(1.15, 1.05, punches=(0, 3)),
    Cam(1.0, 1.1, punches=(5, 12), focus=((10, 99, 1.35, 400, 720, 0),)),
    Cam(1.0, 1.0, drift=8, punches=(2, 5), focus=((4, 99, 2.3, NOSE[0], NOSE[1], 0),)),
    Cam(1.6, 1.0, punches=(2, 8)),
    Cam(1.0, 1.08, punches=(4, 9, 16)),
    Cam(1.0, 1.08, punches=(5, 13), rot=1.0),
    Cam(1.0, 1.06, punches=(5, 8)),
    Cam(1.0, 1.15, punches=(4, 6, 9, 11), rot=1.5),
    Cam(1.0, 1.08, punches=(6,)),
    Cam(1.0, 1.06, punches=(4, 10, 15)),
    Cam(1.0, 1.08, punches=(5,)),
    Cam(1.0, 1.08, punches=(3, 9, 11)),
    Cam(1.0, 1.05, punches=(5, 7, 11, 17), rot=1.0),
    Cam(1.0, 1.15, punches=(4,)),
]


def render_frame(c, t, vo, phr, total):
    D.VO = vo
    MS.VO = vo
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(R.hexc("#000000"))
    k = R.Ctx(vo, si, t)
    lt = k.lt
    OVER.clear()
    loop_t = vo[-1]["tokens"][-1]["e"] + 0.2
    if t >= loop_t:  # bucle: vuelve exactamente al primer cuadro
        k0 = R.Ctx(vo, 0, 0.0)
        z, fx, fy, rot = CAMS[0].get(k0)
        u = clamp((t - loop_t) / 0.2)
        c.save()
        c.translate(540, 960)
        c.scale(z, z)
        c.translate(-fx, -fy)
        s0(c, k0, final=True)
        c.restore()
        if u < 1:
            c.drawRect(RECT(0, 0, W, H), P("#ffffff", alpha=0.4 * (1 - u)))
    else:
        z, fx, fy, rot = CAMS[si].get(k)
        if si == 2:  # la cámara entra a la nariz… y sale del cerebro (escena 3)
            e = ease_in_out(prog(lt, k.D - 0.5, k.D))
            z *= 1 + 3.0 * e
            fx, fy = lerp(fx, NOSE[0], e), lerp(fy, NOSE[1], e)
        elif 0 < si and lt < 0.2:
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
        if si == 2 and lt > k.D - 0.25:
            c.drawRect(RECT(0, 0, W, H), P("#f4a8b8", alpha=(lt - (k.D - 0.25)) / 0.25))
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
