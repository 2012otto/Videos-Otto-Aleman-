"""Otto Aleman Perfumes — "¿Cómo saber si tu Asad Bourbon es original?" (en bucle).

Chepe (cliente, voz Sebastián) compra un Asad Bourbon a mitad de precio y se le va el olor; aparece el
vendedor (personaje A, voz David) con un foco de luz: "¿Vos sos Dios?" → "No, ya te dije que no soy Dios.
Soy el que te vende los perfumes." Cinco pasos, tabla ¿ES ORIGINAL?, cierre Otto Aleman (decants 5/10 ml,
tarjeta de sellos) y vuelta al primer cuadro para que el video quede en bucle.
Uso:
  VIDEO_BUILD=$PWD/otto_serie/build_asad VO_TRIM=0.15 VO_GAP=0.25 VO_TAIL=0.8 \
    python3 otto_serie/src/render_asad.py --out otto_serie/build_asad/video_mudo.mp4
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
import render_elixir as EX  # noqa: E402
from render_decant_tarde import (R, P, lin, rad, oval, rrect, clamp, lerp, smooth, ease_out, ease_in_out, back_out,  # noqa: E402
                                 prog, rng, glow, text_center, W, H, RECT, F, M, INK, GOLDD, OVER, sticker, decant,
                                 Cam)

CHEPE = M.STYLES["CHEPE"]
VEND = M.STYLES["A"]
SPEAKER = ["N", "C", "C", "C", "V", "C", "V", "C", "V", "V", "V", "V", "V", "V", "C", "V", "V", "V", "V", "C"]
FEET = 1560
BROWN = ["#4a2414", "#8a4a2a", "#a8603a", "#7a3e22", "#3a1a0c"]
GOLDC = ["#a8782a", "#ffe08a", "#c8902a", "#ffe08a", "#a8782a"]
BRONZE = ["#4a3020", "#c8a080", "#7a5a40", "#e8c8a0", "#4a3020"]


# ----------------------------------------------------------------------------
# frasco y caja del Asad Bourbon
# ----------------------------------------------------------------------------


def lion_seal(c, r, col_bg="#2a1a10", col_line="#c8a26a"):
    oval(c, 0, 0, r, r, P(col_bg, shader=rad(-r * 0.3, -r * 0.3, r * 1.4, ["#6a4a30", col_bg])))
    oval(c, 0, 0, r * 0.94, r * 0.94, P(col_line, "stroke", r * 0.05))
    for i in range(24):  # greca alrededor
        a = i * math.pi / 12
        x0, y0 = math.cos(a) * r * 0.8, math.sin(a) * r * 0.8
        c.drawRect(RECT(x0 - r * 0.05, y0 - r * 0.05, x0 + r * 0.05, y0 + r * 0.05), P(col_line, alpha=0.8))
    oval(c, 0, 0, r * 0.62, r * 0.62, P(col_line, "stroke", r * 0.04))
    # cara de león estilizada
    for i in range(10):
        a = i * math.pi / 5
        mp = skia.Path()
        mp.moveTo(math.cos(a) * r * 0.2, math.sin(a) * r * 0.2)
        mp.quadTo(math.cos(a + 0.3) * r * 0.55, math.sin(a + 0.3) * r * 0.55, math.cos(a + 0.5) * r * 0.5, math.sin(a + 0.5) * r * 0.5)
        c.drawPath(mp, P(col_line, "stroke", r * 0.04))
    oval(c, -r * 0.12, -r * 0.08, r * 0.05, r * 0.04, P(col_line))
    oval(c, r * 0.12, -r * 0.08, r * 0.05, r * 0.04, P(col_line))
    c.drawLine(0, 0, 0, r * 0.15, P(col_line, "stroke", r * 0.035))


def calligraphy(c, x, y, s, col_shader):
    """Trazo dorado inspirado en la caligrafía del frasco (no es texto)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    p = skia.Path()
    p.moveTo(70, -40)
    p.lineTo(70, 30)
    p.quadTo(40, 50, 0, 30)
    p.quadTo(-30, 10, -60, 30)
    p.quadTo(-80, 40, -70, 10)
    c.drawPath(p, P("#e0b84a", "stroke", 12, shader=col_shader))
    p2 = skia.Path()
    p2.moveTo(40, 0)
    p2.quadTo(20, -20, 0, 0)
    c.drawPath(p2, P("#e0b84a", "stroke", 10, shader=col_shader))
    oval(c, 66, -62, 8, 8, P("#e0b84a"))
    c.restore()


def asad(c, x, y, s, t, fake=False, glow_a=0.0, rot=0.0, cap=True, liquid_view=False):
    """Lattafa Asad Bourbon: cilindro café mate, tapa con aros metálicos, bandas cruzadas con medallón."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if glow_a > 0:
        glow(c, R.RES.glow_warm, 0, -260, 420, 0.6 * glow_a)
    oval(c, 0, 8, 150, 22, P("#000000", alpha=0.35))
    body = skia.Path()
    body.moveTo(-130, -470)
    body.lineTo(130, -470)
    body.lineTo(130, -60)
    body.quadTo(120, 0, 60, 0)
    body.lineTo(-60, 0)
    body.quadTo(-120, 0, -130, -60)
    body.close()
    shade = BROWN if not fake else ["#5a3a2a", "#9a6a4a", "#b07a5a", "#8a5a3a", "#4a2a1a"]
    c.drawPath(body, P(shade[1], shader=lin(-130, 0, 130, 0, shade, [0, .3, .5, .75, 1])))
    if liquid_view:  # contraluz: se ve el color del líquido
        c.save()
        c.clipPath(body, True)
        c.drawRect(RECT(-130, -380, 130, 0), P("#8a4a14", alpha=0.75, shader=lin(0, -380, 0, 0, ["#c87a2a", "#6a2a08"])))
        c.restore()
    c.drawRect(RECT(-130, -478, 130, -462), P("#c8a080", shader=lin(-130, 0, 130, 0, BRONZE)))
    # bandas cruzadas
    for sd in (-1, 1):
        b = skia.Path()
        b.moveTo(-145, -330 + sd * 40)
        b.quadTo(0, -250 - sd * 40, 145, -330 + sd * 40)
        c.drawPath(b, P("#c8a080", "stroke", 26, shader=lin(-145, 0, 145, 0, BRONZE)))
    oval(c, 0, -290, 62, 62, P("#c8a080", shader=lin(-62, 0, 62, 0, BRONZE)))
    c.save()
    c.translate(0, -290)
    lion_seal(c, 52)
    c.restore()
    calligraphy(c, 6, -380, 0.95, lin(-80, 0, 80, 0, GOLDC))
    f1 = F(R.RES.semi, 34 if not fake else 30)
    text_center(c, "ASAD", 0, -170, f1, P("#e8c890"))
    text_center(c, "BOURBON" if not fake else "B0URBON", 0, -126, F(R.RES.semi, 22), P("#e8c890"))
    text_center(c, "Lattafa" if not fake else "Latafa", 0, -88, F(R.RES.medium, 26), P("#e8c890"))
    if cap:
        c.drawRect(RECT(-130, -560, 130, -490), P(shade[1], shader=lin(-130, 0, 130, 0, shade, [0, .3, .5, .75, 1])))
        c.drawRect(RECT(-130, -500, 130, -484), P("#c8a080", shader=lin(-130, 0, 130, 0, BRONZE)))
        c.drawRect(RECT(-130, -574, 130, -560), P("#c8a080", shader=lin(-130, 0, 130, 0, BRONZE)))
        c.drawRect(RECT(-130, -690, 130, -574), P(shade[1], shader=lin(-130, 0, 130, 0, shade, [0, .3, .5, .75, 1])))
    c.restore()


def asad_box(c, x, y, s, base_code=None):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -230, -620, 230, 0, 6, P("#8a4a2a", shader=lin(-230, 0, 230, 0, ["#6a341c", "#9a5634", "#7a3e22"])))
    text_center(c, "EAU DE PARFUM", 0, -570, F(R.RES.medium, 22), P("#e8c890"))
    text_center(c, "BOURBON", 0, -520, F(R.RES.semi, 30), P("#e8c890"))
    c.save()
    c.translate(0, -360)
    lion_seal(c, 130)
    c.restore()
    calligraphy(c, 10, -150, 1.0, lin(-80, 0, 80, 0, GOLDC))
    text_center(c, "ASAD", 0, -70, F(R.RES.semi, 44), P("#e8c890"))
    text_center(c, "Lattafa", 0, -26, F(R.RES.medium, 30), P("#e8c890"))
    c.restore()


def code_label(c, x, y, txt, k, ok=True):
    if k <= 0:
        return
    s = back_out(clamp(k), 1.6)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -150, -40, 150, 40, 10, P("#ffffff"))
    rrect(c, -150, -40, 150, 40, 10, P(INK, "stroke", 3))
    text_center(c, txt, 0, 14, F(R.RES.xbold, 40), P(INK))
    c.restore()


def check(c, x, y, r, ok, k=1.0):
    if k <= 0:
        return
    s = back_out(clamp(k), 2)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, 0, r, r, P("#2fbf71" if ok else "#e0203a"))
    p = skia.Path()
    if ok:
        p.moveTo(-r * 0.45, 0)
        p.lineTo(-r * 0.1, r * 0.35)
        p.lineTo(r * 0.5, -r * 0.35)
    else:
        p.moveTo(-r * 0.4, -r * 0.4)
        p.lineTo(r * 0.4, r * 0.4)
        p.moveTo(r * 0.4, -r * 0.4)
        p.lineTo(-r * 0.4, r * 0.4)
    c.drawPath(p, P("#ffffff", "stroke", r * 0.22))
    c.restore()


# ----------------------------------------------------------------------------
# escenario y personajes
# ----------------------------------------------------------------------------


def room(c, t, purple=0.0):
    top = M.mix("#1a1a3a", "#3a1a4a", purple)
    c.drawRect(RECT(-300, -300, W + 300, H + 300), P(top, shader=lin(0, 0, 0, H, [top, M.mix("#2a2a5a", "#5a2a6a", purple), "#0e0e1e"])))
    rrect(c, 560, 560, 860, 760, 8, P("#0a0a1e"))  # ventana de noche
    oval(c, 790, 610, 26, 26, P("#f4f0d8"))
    oval(c, 800, 603, 24, 24, P("#0a0a1e"))
    r = rng(3)
    for i in range(12):
        oval(c, 570 + r.random() * 280, 570 + r.random() * 180, 2, 2, P("#ffffff", alpha=0.7))
    rrect(c, 560, 560, 860, 760, 8, P("#c8a26a", "stroke", 10))
    c.drawLine(710, 560, 710, 760, P("#c8a26a", "stroke", 6))
    # espejo de cuerpo entero con marco dorado
    rrect(c, 760, 760, 1000, 1540, 120, P("#2a3a7a", shader=lin(760, 0, 1000, 0, ["#1a2a5a", "#4a5aa8", "#1a2a5a"])))
    rrect(c, 760, 760, 1000, 1540, 120, P("#d6a24a", "stroke", 14))
    c.drawLine(800, 900, 860, 820, P("#ffffff", "stroke", 6, alpha=0.4))
    c.drawRect(RECT(-300, 1540, W + 300, H + 300), P("#2a1e3a", shader=lin(0, 1540, 0, H, ["#3a2a4a", "#140e1e"])))
    D.clock(c, 150, 680, 80, 22 + (t * 0.02) % 1)


def chepe(c, k, x, y, s, keys, hold_fn=None):
    p = D.track(k.lt, keys)
    tk = M.talk_amount(k.t, k.s["tokens"]) if SPEAKER[VI] == "C" else 0.0
    M.draw(c, x, y, s, k.t, p, style=CHEPE, talk=tk, hold_fn=hold_fn)


def vendor(c, k, x, y, s, keys, hold_fn=None):
    p = D.track(k.lt, keys)
    tk = M.talk_amount(k.t, k.s["tokens"]) if SPEAKER[VI] == "V" else 0.0
    M.draw(c, x, y, s, k.t, p, style=VEND, talk=tk, hold_fn=hold_fn)


def hold_asad(t, s=0.32):
    return lambda c, x, y: asad(c, x, y + 20, s, t, fake=True)


def spotlight(c, t, a=1.0, x=330):
    if a <= 0:
        return
    p = skia.Path()
    p.moveTo(x - 60, -100)
    p.lineTo(x + 60, -100)
    p.lineTo(x + 300, FEET + 40)
    p.lineTo(x - 300, FEET + 40)
    p.close()
    c.drawPath(p, P("#fff4d0", alpha=0.25 * a, shader=lin(0, 0, 0, FEET, [R.hexc("#fff4d0", 0.5), R.hexc("#fff4d0", 0.15)])))
    oval(c, x, FEET + 20, 300, 50, P("#fff4d0", alpha=0.3 * a))
    r = rng(int(t * 2) % 50)
    for i in range(16):
        oval(c, x - 220 + r.random() * 440, 400 + r.random() * 1100, 4, 4, P("#ffffff", alpha=0.6 * a * r.random()))


def halo(c, x, y, k, t):
    if k <= 0:
        return
    s = back_out(clamp(k), 2)
    c.save()
    c.translate(x, y + 6 * math.sin(t * 3))
    c.scale(s, s)
    glow(c, R.RES.glow_warm, 0, 0, 160, 0.5)
    c.drawPath(skia.Path().addOval(RECT(-110, -26, 110, 26)), P("#ffe04a", "stroke", 16))
    c.restore()


def dark(c, t):
    c.drawRect(RECT(-300, -300, W + 300, H + 300), P("#0a0a18", shader=rad(540, 900, 1400, ["#1a1a3a", "#05050c"])))
    r = rng(5)
    for i in range(30):
        x, y = r.random() * W, r.random() * H
        tw = 0.5 + 0.5 * math.sin(t * 2 + i)
        oval(c, x, y, 2 + 3 * r.random(), 2 + 3 * r.random(), P("#d6a24a", alpha=0.4 * tw))


def step_header(n, name, k):
    if k <= 0:
        return

    def d(cc):
        a = clamp(k * 3)
        cc.save()
        cc.translate(-60 * (1 - ease_out(clamp(k))), 0)
        f = F(R.RES.xbold, 130)
        cc.drawString(f"0{n}", 80, 640, f, P(GOLDD, alpha=a))
        cc.drawString("PASO", 290, 560, F(R.RES.bold, 32), P("#d8d8e0", alpha=a))
        cc.drawString(name, 290, 630, F(R.RES.xbold, 64), P("#ffffff", alpha=a))
        cc.drawLine(290, 660, 1000, 660, P(GOLDD, "stroke", 4, alpha=a))
        cc.restore()
    OVER.append(d)


def step_dots(n):
    def d(cc):
        for i in range(5):
            x = 340 + i * 100
            oval(cc, x, 520, 16 if i + 1 == n else 10, 16 if i + 1 == n else 10, P(GOLDD if i < n else "#5a5a6a"))
            if i < 4:
                cc.drawLine(x + 18, 520, x + 82, 520, P("#5a5a6a", "stroke", 3))
    OVER.append(d)


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------
VI = 0


def s0(c, k, stamp=True):  # gancho (y cuadro final del bucle)
    lt, T = k.lt, k.w
    dark(c, k.t)
    glow(c, R.RES.glow_warm, 540, 1000, 600, 0.45)
    asad(c, 540, 1580, 1.3, k.t, glow_a=0.8)
    r = rng(9)
    for i in range(10):  # destellos
        x, y = 260 + r.random() * 560, 600 + r.random() * 800
        tw = max(0, math.sin(k.t * 3 + i * 1.7))
        c.drawLine(x - 18 * tw, y, x + 18 * tw, y, P("#ffffff", "stroke", 3, alpha=tw))
        c.drawLine(x, y - 18 * tw, x, y + 18 * tw, P("#ffffff", "stroke", 3, alpha=tw))
    if stamp:
        sk = prog(lt, T(7) - 0.1, T(7) + 0.2)
        if sk > 0:
            def d(cc):
                s_ = lerp(2.0, 1.0, ease_out(sk))
                cc.save()
                cc.translate(540, 1180)
                cc.rotate(-12)
                cc.scale(s_, s_)
                rrect(cc, -250, -70, 250, 70, 14, P("#2fbf71", "stroke", 10, alpha=clamp(sk * 3)))
                text_center(cc, "¿ORIGINAL?", 0, 26, F(R.RES.xbold, 80), P("#2fbf71", alpha=clamp(sk * 3)))
                cc.restore()
            OVER.append(d)


def s1(c, k):  # Chepe compra a mitad de precio
    lt, T = k.lt, k.w
    room(c, k.t)
    chepe(c, k, 420, FEET, 0.92, [(0, "sostiene"), (T(9), "celebra")], hold_fn=hold_asad(k.t))
    tk = prog(lt, T(6) - 0.1, T(6) + 0.2)
    if tk > 0:
        OVER.append(lambda cc: EX.price_tag(cc, 830, 700, "-50%", tk, col="#e0203a", rot=10))
    D.mist(c, 520, 860, T(9), lt, n=30)


def s2(c, k):  # ya no huele a nada
    lt, T = k.lt, k.w
    room(c, k.t, purple=1.0)
    D.clock(c, 160, 690, 100, lerp(22, 23, ease_in_out(prog(lt, 0, T(2)))))
    chepe(c, k, 460, FEET, 0.95, [(0, "piensa"), (T(1), "espera"), (T(8), "encoge")])
    sticker(c, "+1 HORA", 170, 850, prog(lt, 0.1, 0.4), bg_col="#e0203a", size=44, rot=-5)


def s3(c, k):  # mi nariz se acostumbró
    lt, T = k.lt, k.w
    room(c, k.t, purple=1.0)
    chepe(c, k, 540, FEET, 0.98, [(0, "piensa")])


def s4(c, k):  # aparece el vendedor con el foco
    lt, T = k.lt, k.w
    dark(c, k.t)
    a = ease_out(prog(lt, 0, 0.5))
    spotlight(c, k.t, a, x=330)
    vy = lerp(-400, FEET, ease_out(prog(lt, 0.1, 0.6)))
    vendor(c, k, 330, vy, 0.82, [(0, "neutral"), (T(1), "señala")])
    chepe(c, k, 800, FEET, 0.82, [(0, "espera")])


def s5(c, k):  # ¿Vos sos Dios?
    lt, T = k.lt, k.w
    dark(c, k.t)
    spotlight(c, k.t, 1.0, x=330)
    vendor(c, k, 330, FEET, 0.82, [(0, "neutral")])
    halo(c, 330, FEET - 0.82 * 1080, prog(lt, T(2) - 0.1, T(2) + 0.2), k.t)
    chepe(c, k, 800, FEET, 0.82, [(0, "espera"), (T(2), "enamorado")])


def s6(c, k):  # "No, ya te dije que no soy Dios. Soy el que te vende los perfumes."
    lt, T = k.lt, k.w
    dark(c, k.t)
    spotlight(c, k.t, 1.0 - 0.6 * prog(lt, T(8), T(8) + 0.4), x=330)
    sw = prog(lt, T(1), T(3))  # se aparta la aureola de un manotazo
    hx = 330 + 700 * ease_in_out(sw)
    if sw < 1:
        halo(c, hx, FEET - 0.82 * 1080 - 200 * sw, 1.0, k.t)
    vendor(c, k, 330, FEET, 0.82, [(0, "encoge"), (T(1), "saludo"), (T(8), "sostiene")],
           hold_fn=lambda cc, x, y: decant(cc, x, y - 70, 160, -6, k.t, 0.6))
    chepe(c, k, 800, FEET, 0.82, [(0, "enamorado"), (T(3), "neutral")])
    sticker(c, "EL QUE TE VENDE LOS PERFUMES", 540, 620, prog(lt, T(9), T(9) + 0.3), bg_col=GOLDD, size=40, rot=-3)


def s7(c, k):  # "Ah… ¿seguro?"
    lt, T = k.lt, k.w
    dark(c, k.t)
    vendor(c, k, 330, FEET, 0.82, [(0, "neutral")])
    chepe(c, k, 800, FEET, 0.82, [(0, "asco")])


def s8(c, k):  # "Sí." (la aureola vuelve a asomarse)
    lt, T = k.lt, k.w
    dark(c, k.t)
    vendor(c, k, 330, FEET, 0.82, [(0, M.pose(mouth="flat", eyes="squint"))])
    halo(c, 330, FEET - 0.82 * 1080, prog(lt, 0.5, 0.8), k.t)
    chepe(c, k, 800, FEET, 0.82, [(0, "espera")])


def s9(c, k):  # hay un montón de falsos: 5 pasos
    lt, T = k.lt, k.w
    room(c, k.t, purple=0.6)
    r = rng(4)
    for i in range(9):
        x = 120 + r.random() * 840
        y = (r.random() * 1600 + lt * 500) % 1700 - 100
        asad(c, x, y, 0.22, k.t, fake=True, rot=(r.random() - 0.5) * 60)
        check(c, x + 40, y - 120, 22, False)
    chepe(c, k, 540, FEET, 0.92, [(0, "triste")])
    sticker(c, "5 PASOS", 540, 620, prog(lt, T(8), T(9) + 0.2), bg_col=GOLDD, size=80, rot=-4)


def step_vendor(c, k, keys=((0, "señala"),)):
    vendor(c, k, 920, FEET + 120, 0.5, [(T, p) for T, p in keys])


def s10(c, k):  # paso 1: el lote
    lt, T = k.lt, k.w
    dark(c, k.t)
    step_dots(1)
    step_header(1, "EL LOTE", prog(lt, 0, 0.4))
    asad_box(c, 280, 1400, 0.7)
    asad(c, 640, 1400, 0.85, k.t, cap=True)
    code_label(c, 280, 1470, "LOTE 24A07", prog(lt, T(7), T(10)))
    code_label(c, 640, 1470, "LOTE 24A07", prog(lt, T(14), T(14) + 0.3))
    if lt > T(16):
        check(c, 460, 1580, 40, True, prog(lt, T(16), T(17)))
        OVER.append(lambda cc: sticker(cc, "IGUALES", 460, 1680, prog(lt, T(18), T(18) + 0.3), bg_col="#2fbf71", size=56, rot=-3))
    step_vendor(c, k)


def hologram(c, x, y, s, tilt, fake):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if fake:
        rrect(c, -130, -80, 130, 80, 14, P("#a8a8b0"))
        text_center(c, "ORIGINAL", 0, 14, F(R.RES.bold, 40), P("#7a7a84"))
    else:
        cols = ["#ff6aa8", "#ffd04a", "#6aff9a", "#4ac8ff", "#a86aff", "#ff6aa8"]
        sh = lin(-130 + tilt * 200, -80, 130 + tilt * 200, 80, cols)
        rrect(c, -130, -80, 130, 80, 14, P("#ffffff", shader=sh))
        rrect(c, -130, -80, 130, 80, 14, P("#ffffff", "stroke", 4, alpha=0.7))
        text_center(c, "ORIGINAL", 0, 14, F(R.RES.bold, 40), P("#ffffff", alpha=0.9))
    c.restore()


def s11(c, k):  # paso 2: el holograma
    lt, T = k.lt, k.w
    dark(c, k.t)
    step_dots(2)
    step_header(2, "EL HOLOGRAMA", prog(lt, 0, 0.4))
    tilt = math.sin(lt * 2.5)
    c.save()
    c.translate(330, 1100)
    c.rotate(tilt * 12)
    c.translate(-330, -1100)
    hologram(c, 330, 1100, 1.3, tilt, False)
    c.restore()
    check(c, 330, 1300, 40, True, prog(lt, T(6), T(7)))
    fk = prog(lt, T(13) - 0.2, T(13) + 0.2)
    if fk > 0:
        hologram(c, 740, 1100, 1.1 * back_out(fk, 1.4), 0, True)
        check(c, 740, 1300, 40, False, prog(lt, T(15), T(15) + 0.3))
    step_vendor(c, k)


def s12(c, k):  # paso 3: el QR
    lt, T = k.lt, k.w
    dark(c, k.t)
    step_dots(3)
    step_header(3, "EL QR", prog(lt, 0, 0.4))
    c.save()  # código QR en la caja
    c.translate(300, 1120)
    rrect(c, -150, -150, 150, 150, 10, P("#ffffff"))
    r = rng(12)
    for i in range(12):
        for j in range(12):
            if r.random() < 0.5:
                c.drawRect(RECT(-120 + i * 20, -120 + j * 20, -100 + i * 20, -100 + j * 20), P("#111111"))
    for (ox, oy) in ((-120, -120), (60, -120), (-120, 60)):
        c.drawRect(RECT(ox, oy, ox + 60, oy + 60), P("#111111"))
        c.drawRect(RECT(ox + 12, oy + 12, ox + 48, oy + 48), P("#ffffff"))
        c.drawRect(RECT(ox + 22, oy + 22, ox + 38, oy + 38), P("#111111"))
    c.restore()
    sk = prog(lt, T(4) - 0.3, T(4))

    def screen(cc):
        cc.drawRect(RECT(-140, -290, 140, 290), P("#f4ece2"))
        if lt < T(9) - 0.2:
            u = (lt * 1.5) % 1
            cc.drawLine(-110, -200 + u * 400, 110, -200 + u * 400, P("#e0203a", "stroke", 4))
            text_center(cc, "Escaneando…", 0, 240, F(R.RES.semi, 26), P(INK))
        else:
            text_center(cc, "lattafa", 0, -120, F(R.RES.xbold, 56), P(INK))
            text_center(cc, "sitio oficial", 0, -70, F(R.RES.semi, 28), P("#6a6a74"))
            check(cc, 0, 60, 70, True)
    if sk > 0:
        D.phone(c, lerp(1200, 760, ease_out(sk)), 1060, 0.9, screen, rot=-6)
    step_vendor(c, k)


def s13(c, k):  # paso 4: la tapa
    lt, T = k.lt, k.w
    dark(c, k.t)
    step_dots(4)
    step_header(4, "LA TAPA", prog(lt, 0, 0.4))
    tilt = lerp(0, 14, ease_out(prog(lt, T(6) - 0.2, T(6) + 0.4)))
    c.save()
    c.translate(540, 1100)
    c.drawRect(RECT(-14, 0, 14, 400), P("#8a6a4a"))
    rrect(c, -120, 390, 120, 420, 10, P("#6a4a2a"))
    c.rotate(tilt)
    c.drawRect(RECT(-380, -10, 380, 10), P("#d6a24a"))
    for sd, fake in ((-1, False), (1, True)):
        px = sd * 340
        c.drawLine(px, 0, px - 80, 160, P("#8a6a4a", "stroke", 4))
        c.drawLine(px, 0, px + 80, 160, P("#8a6a4a", "stroke", 4))
        c.save()
        c.translate(px, 160)
        c.rotate(-tilt)
        pan = skia.Path()
        pan.addArc(RECT(-110, -40, 110, 40), 0, 180)
        c.drawPath(pan, P("#d6a24a"))
        sh = BROWN if not fake else ["#7a5a4a", "#b08a6a", "#c89a7a", "#a07a5a", "#6a4a3a"]
        c.drawRect(RECT(-90, -120, 90, 0), P(sh[1], shader=lin(-90, 0, 90, 0, sh, [0, .3, .5, .75, 1])))
        c.drawRect(RECT(-90, -70, 90, -58), P("#c8a080", shader=lin(-90, 0, 90, 0, BRONZE)))
        c.restore()
    c.restore()
    text_center(c, "ORIGINAL", 200, 1440, F(R.RES.xbold, 40), P("#2fbf71", alpha=prog(lt, T(6), T(7))))
    text_center(c, "FALSA", 880, 1300, F(R.RES.xbold, 40), P("#e0203a", alpha=prog(lt, T(10), T(11))))
    step_vendor(c, k)


def s14(c, k):  # chiste: pesa menos que mi sueldo
    lt, T = k.lt, k.w
    dark(c, k.t)
    chepe(c, k, 540, FEET, 0.95, [(0, M.pose(arm_r=(60, 100, "hold"), mouth="open", eyes="wide"))],
          hold_fn=lambda cc, x, y: (cc.drawRect(RECT(x - 50, y - 120, x + 50, y - 40), P("#b08a6a")),
                                   cc.drawRect(RECT(x - 50, y - 86, x + 50, y - 76), P("#c8a080"))))
    r = rng(2)
    for i in range(3):  # moneditas cayendo
        u = (lt * 0.8 + i / 3) % 1
        oval(c, 300 + i * 220, lerp(500, 1500, u), 30, 30, P("#ffd04a", alpha=1 - u))
        text_center(c, "Q", 300 + i * 220, lerp(500, 1500, u) + 12, F(R.RES.xbold, 32), P("#a8782a", alpha=1 - u))
    del r


def s15(c, k):  # paso 5: impresión y líquido
    lt, T = k.lt, k.w
    dark(c, k.t)
    step_dots(5)
    step_header(5, "LETRAS Y LÍQUIDO", prog(lt, 0, 0.4))
    sw = T(6) - 0.2
    if lt < sw:
        asad(c, 500, 1620, 1.2, k.t)
        mx, my = lerp(380, 620, (math.sin(lt * 1.6) + 1) / 2), 1440
        c.drawPath(skia.Path().addCircle(mx, my, 120), P("#ffffff", "stroke", 14))
        oval(c, mx, my, 116, 116, P("#ffffff", alpha=0.12))
        c.drawLine(mx + 85, my + 85, mx + 190, my + 190, P("#3a2a1a", "stroke", 26))
        check(c, 780, 1000, 44, True, prog(lt, T(4), T(5)))
    else:
        glow(c, R.RES.glow_warm, 480, 1250, 500, 0.7)
        asad(c, 480, 1640, 1.15, k.t, cap=False, liquid_view=True)
        sticker(c, "ÁMBAR OSCURO · CASI CAFÉ", 480, 780, prog(lt, T(9), T(9) + 0.3), bg_col="#8a4a14", size=44, rot=-3)
    step_vendor(c, k)


ROWS = ["Lote", "Holograma", "Código QR", "Tapa", "Letras y líquido"]


def s16(c, k):  # tabla
    lt, T = k.lt, k.w
    dark(c, k.t)
    s = back_out(prog(lt, 0, 0.4), 1.4)
    c.save()
    c.translate(540, 1080)
    c.scale(s, s)
    rrect(c, -460, -400, 460, 360, 30, P("#14141e"))
    rrect(c, -460, -400, 460, 360, 30, P(GOLDD, "stroke", 6))
    text_center(c, "¿ES ORIGINAL?", 0, -310, F(R.RES.xbold, 64), P("#ffffff"))
    c.drawString("ORIGINAL", 90, -230, F(R.RES.bold, 26), P("#d8d8e0"))
    c.drawString("EL DE CHEPE", 240, -230, F(R.RES.bold, 26), P("#d8d8e0"))
    for i, row in enumerate(ROWS):
        y = -150 + i * 95
        c.drawString(row, -410, y + 14, F(R.RES.bold, 40), P("#ffffff"))
        check(c, 150, y, 30, True, prog(lt, 0.2 + i * 0.12, 0.4 + i * 0.12))
        check(c, 320, y, 30, False, prog(lt, 0.8 + i * 0.12, 1.0 + i * 0.12))
    c.restore()
    fk = prog(lt, T(4) - 0.1, T(4) + 0.2)
    if fk > 0:
        OVER.append(lambda cc: sticker(cc, "SI FALLA UNO SOLO, NO ES ORIGINAL", 540, 1560, fk, bg_col="#e0203a", size=40, rot=-2))


def s17(c, k):  # Otto Aleman: todo original, decants 5 y 10 ml
    lt, T = k.lt, k.w
    EX.warm_bg(c, k.t, "gold")
    img = M.logo()
    lk = back_out(prog(lt, T(1) - 0.2, T(1) + 0.2), 1.5)
    if lk > 0:
        w = 260 * lk
        h = w * img.height() / img.width()
        c.drawImageRect(img, RECT(540 - w / 2, 640 - h / 2, 540 + w / 2, 640 + h / 2), R.SAMP, skia.Paint())
        text_center(c, "OTTO ALEMAN PERFUMES", 540, 820, F(R.RES.xbold, 50), P("#ffffff", alpha=clamp(lk)))
    sticker(c, "TODO ORIGINAL", 540, 920, prog(lt, T(6), T(6) + 0.3), bg_col="#2fbf71", size=52, rot=-3)
    d5 = prog(lt, T(15) - 0.2, T(15) + 0.2)
    d10 = prog(lt, T(17) - 0.2, T(17) + 0.2)
    if d5 > 0:
        decant(c, 330, lerp(1900, 1280, back_out(d5, 1.3)), 300, -4, k.t, 0.6)
        text_center(c, "5 ML", 330, 1500, F(R.RES.xbold, 50), P("#ffffff", alpha=d5))
    if d10 > 0:
        decant(c, 560, lerp(1900, 1250, back_out(d10, 1.3)), 380, 4, k.t, 0.6)
        text_center(c, "10 ML", 560, 1500, F(R.RES.xbold, 50), P("#ffffff", alpha=d10))
    vendor(c, k, 880, FEET + 100, 0.6, [(0, "celebra"), (T(9), "señala")])


def s18(c, k):  # tarjeta de sellos: 6 → 1 gratis
    lt, T = k.lt, k.w
    EX.warm_bg(c, k.t, "amber")
    n = int(6 * prog(lt, T(6) - 0.6, T(8) + 0.2) + 0.0001)
    free = prog(lt, T(12) - 0.1, T(12) + 0.2)
    D.stamp_card(c, 330, 1060, 1.3, n, k.t, free)
    if free > 0:
        decant(c, 650, lerp(1900, 1100, back_out(free, 1.3)), 320, 8, k.t, 1.0)
        OVER.append(lambda cc: sticker(cc, "¡GRATIS!", 540, 620, free, bg_col="#2fbf71", size=80, rot=-5))
    vendor(c, k, 880, FEET + 100, 0.55, [(0, "señala"), (T(12), "celebra")])
    chepe(c, k, 180, FEET + 160, 0.45, [(0, "neutral"), (T(12), "celebra")])


def s19(c, k):  # "Pero era una oferta…" → vuelve al primer cuadro (bucle)
    lt, T = k.lt, k.w
    room(c, k.t)
    chepe(c, k, 420, FEET, 0.92, [(0, "sostiene"), (T(4), "piensa")], hold_fn=hold_asad(k.t))
    OVER.append(lambda cc: EX.price_tag(cc, 830, 700, "-50%", 1.0, col="#e0203a", rot=10))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19]
CAMS = [
    Cam(1.18, 1.0, drift=10, punches=(4, 7)),
    Cam(1.0, 1.1, punches=(6, 9), focus=((9, 99, 1.25, 460, 900, 0),)),
    Cam(1.0, 1.08, punches=(0, 7), focus=((1, 99, 1.35, 460, 720, 2),)),
    Cam(1.1, 1.2, drift=0, focus=((0, 99, 1.4, 540, 700, 0),)),
    Cam(1.0, 1.05, punches=(1,)),
    Cam(1.0, 1.05, drift=10, punches=(2,), focus=((2, 99, 1.3, 800, 700, 0),)),
    Cam(1.05, 1.0, punches=(1, 7, 9), focus=((0, 4, 1.25, 330, 700, 0),)),
    Cam(1.0, 1.0, drift=5, focus=((0, 99, 1.45, 800, 700, 0),)),
    Cam(1.0, 1.0, drift=5, focus=((0, 99, 1.5, 330, 700, 0),)),
    Cam(1.0, 1.1, punches=(4, 8)),
    Cam(1.0, 1.05, punches=(3, 7, 14, 19)),
    Cam(1.0, 1.08, punches=(3, 6, 15)),
    Cam(1.0, 1.08, punches=(3, 12)),
    Cam(1.0, 1.08, punches=(3, 6, 13)),
    Cam(1.0, 1.0, drift=8, punches=(1, 5), focus=((0, 99, 1.3, 540, 760, 2),)),
    Cam(1.0, 1.05, punches=(2, 9)),
    Cam(1.0, 1.05, punches=(1, 4)),
    Cam(1.0, 1.08, punches=(1, 6, 15, 17)),
    Cam(1.0, 1.08, punches=(8, 12)),
    Cam(1.0, 1.1, punches=(3,)),
]


def render_frame(c, t, vo, phr, total):
    global VI
    D.VO = vo
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(R.hexc("#000000"))
    k = R.Ctx(vo, si, t)
    lt = k.lt
    VI = si
    OVER.clear()
    loop_t = vo[-1]["tokens"][-1]["e"] + 0.15  # al terminar Chepe, vuelve al primer cuadro
    if t >= loop_t:
        k0 = R.Ctx(vo, 0, 0.0)
        VI = 0
        z, fx, fy, rot = CAMS[0].get(k0)
        u = clamp((t - loop_t) / 0.25)
        c.save()
        c.translate(540, 960)
        c.scale(z, z)
        c.translate(-fx, -fy)
        s0(c, k0, stamp=False)
        c.restore()
        if u < 1:
            c.drawRect(RECT(0, 0, W, H), P("#ffffff", alpha=0.5 * (1 - u)))
    else:
        z, fx, fy, rot = CAMS[si].get(k)
        if 0 < si and lt < 0.2:
            z *= 1 + 0.08 * (1 - ease_out(lt / 0.2))
        if si == len(vo) - 1:  # la cámara se mete al frasco antes del corte del bucle
            zz = ease_in_out(prog(t, loop_t - 0.6, loop_t))
            z *= 1 + 1.5 * zz
            fx, fy = lerp(fx, 470, zz), lerp(fy, 1040, zz)
        c.save()
        c.translate(540, 960)
        c.rotate(rot)
        c.scale(z, z)
        c.translate(-fx, -fy)
        SCENES[si](c, k)
        c.restore()
        for fn in OVER:
            fn(c)
    R.vignette(c, 0.35)
    R.draw_subs(c, t, phr)
    EX.draw_watermark(c)


def install():
    import render_sueno as S
    R.SCENES = SCENES
    R.render_frame = render_frame
    R.draw_subs = S.draw_subs
    R.draw_watermark = EX.draw_watermark


if __name__ == "__main__":
    install()
    R.main()
