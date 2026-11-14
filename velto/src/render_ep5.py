"""Velto — "El balde roto": lanzamiento de VELTO STUDIO (ejemplo: Sudaderas Diego). Voz: ElevenLabs (Fernando).

Uso:
  VIDEO_BUILD=$PWD/velto/build_ep5 VO_TRIM=0.3 python3 velto/src/render_ep5.py --out velto/build_ep5/video_mudo.mp4
"""
import math
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_ep2 as E2  # noqa: E402
import render_ep4 as T4  # noqa: E402
from render_velto import (R, P, RECT, ANA, VIO, VIO2, LIME, F, back_out, clamp, ease_in_out, ease_out, glow,  # noqa: E402
                          lerp, lin, rad, oval, prog, rrect, smooth, text_center, draw_kid, rng, neon_bg, phone,
                          client_logo, chat_icon, use, W, H, draw_img, bubble)
from render_ep2 import big_text  # noqa: E402

camera = R.camera
DIEGO = {"shirt": ("#e2ff7a", "#b8f51a", "#7fb80a"), "hem": "#6f9f08", "collar": "#6f9f08", "arm": "#a8e01a",
         "arm_hl": "#f0ffb0", "pants": ("#2f2856", "#1a1533"), "headwear": "cap", "head_col": ("#a66bff", "#6a22c0"),
         "skin": ("#f5d3b5", "#e0aa82", "#c98f68")}
EQUIPO = {"shirt": ("#7ad8f0", "#2a98c8", "#1a6a9a"), "hem": "#1a6a9a", "collar": "#1a6a9a", "arm": "#2a98c8",
          "arm_hl": "#c0f0ff", "pants": ("#2f2856", "#1a1533"), "glasses": True, "hair_col": ("#4a3424", "#2a1c12")}


# ----------------------------------------------------------------------------
# objetos
# ----------------------------------------------------------------------------


def coin(c, x, y, r, rot=0.0, a=1.0):
    sq = abs(math.cos(rot)) * 0.85 + 0.15
    oval(c, x, y, r * sq, r, P("#c9902f", alpha=a))
    oval(c, x, y, r * sq * 0.82, r * 0.82, P("#f4cf6a", shader=lin(x - r, y, x + r, y, ["#d9a441", "#fff1c4", "#c9902f"]), alpha=a))
    if sq > 0.5:
        text_center(c, "Q", x, y + r * 0.35, F(R.RES.mx, r), P("#8a5a17", alpha=a))


def bucket(c, x, y, s, t, fill=0.0, patched=0.0, leak=1.0):
    """Balde metálico. (x, y) = base. fill: 0..1 nivel de monedas; patched: parche lima en el hoyo."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    body = skia.Path()
    body.moveTo(-170, -330)
    body.lineTo(170, -330)
    body.lineTo(130, 0)
    body.lineTo(-130, 0)
    body.close()
    c.drawPath(body, P("#8a96a8", shader=lin(-170, 0, 170, 0, ["#5a6474", "#c8d2e0", "#e8eef6", "#8a96a8", "#4a5262"],
                                             [0, .3, .45, .75, 1])))
    for yy in (-250, -120):
        w = 170 - (yy + 330) * 40 / 330
        c.drawLine(-w, yy, w, yy, P("#4a5262", "stroke", 6, alpha=0.6))
    oval(c, 0, -330, 170, 34, P("#3a4252"))
    if fill > 0:  # monedas: se asoman por arriba cuando el balde se llena
        oval(c, 0, -330, 160, 30, P("#c9902f", alpha=min(1, fill * 2)))
        mound = skia.Path()
        mh = 90 * clamp((fill - 0.4) / 0.6)
        mound.moveTo(-160, -330)
        mound.quadTo(0, -330 - mh * 2, 160, -330)
        mound.close()
        c.drawPath(mound, P("#f4cf6a", shader=lin(0, -330 - mh, 0, -330, ["#fff1c4", "#d9a441"])))
        r = rng(3)
        for q in range(int(14 * clamp((fill - 0.4) / 0.6))):
            cx = -120 + r.random() * 240
            cy = -330 - mh * (1 - (cx / 160) ** 2) * r.random()
            coin(c, cx, cy, 20, rot=r.random() * 3)
    arc = skia.Path()
    arc.addArc(RECT(-170, -480, 170, -190), 200, 140)
    c.drawPath(arc, P("#4a5262", "stroke", 10))
    # el hoyo
    oval(c, 40, -14, 30, 10, P("#0b0a10"))
    if patched > 0:
        s2 = back_out(patched)
        c.save()
        c.translate(40, -16)
        c.scale(s2, s2)
        rrect(c, -46, -22, 46, 22, 10, P(LIME))
        c.drawLine(-36, -12, 36, 12, P("#14061f", "stroke", 4))
        c.drawLine(-36, 12, 36, -12, P("#14061f", "stroke", 4))
        c.restore()
    c.restore()
    if patched < 0.5 and leak > 0:  # monedas que se escapan por el hoyo
        for i in range(6):
            u = (t * 1.3 + i / 6) % 1
            cx = x + (40 + 60 * u + i * 10) * s
            cy = y + (-6 + 40 * u * u) * s + 60 * u
            coin(c, cx + u * 180, cy, 18 * s, rot=t * 8 + i, a=leak * (1 - u))


def calendar(c, x, y, month, k=1.0):
    if k <= 0:
        return
    s = back_out(k)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -110, -110, 110, 120, 20, P("#fff8ea"))
    rrect(c, -110, -110, 110, -40, 20, P("#e8414f"))
    c.drawRect(RECT(-110, -60, 110, -40), P("#e8414f"))
    for dx in (-50, 50):
        rrect(c, dx - 8, -128, dx + 8, -92, 6, P("#4a5262"))
    text_center(c, "MES", 0, -62, F(R.RES.mx, 30), P("#ffffff"))
    text_center(c, month, 0, 72, F(R.RES.mx, 84), P("#14061f"))
    c.restore()


def eye_icon(c, x, y, r, col):
    p = skia.Path()
    p.moveTo(x - r, y)
    p.quadTo(x, y - r * 0.9, x + r, y)
    p.quadTo(x, y + r * 0.9, x - r, y)
    p.close()
    c.drawPath(p, P(col, "stroke", 4))
    oval(c, x, y, r * 0.32, r * 0.32, P(col))


def cart_icon(c, x, y, r, col):
    c.drawLine(x - r, y - r * 0.6, x - r * 0.6, y - r * 0.6, P(col, "stroke", 4))
    p = skia.Path()
    p.moveTo(x - r * 0.6, y - r * 0.6)
    p.lineTo(x - r * 0.4, y + r * 0.3)
    p.lineTo(x + r * 0.8, y + r * 0.3)
    p.lineTo(x + r, y - r * 0.4)
    p.close()
    c.drawPath(p, P(col, "stroke", 4))
    oval(c, x - r * 0.2, y + r * 0.7, r * 0.14, r * 0.14, P(col))
    oval(c, x + r * 0.6, y + r * 0.7, r * 0.14, r * 0.14, P(col))


def reel_screen(views, sales, promo_press=0.0, show_promo=True):
    def d(c):
        c.drawRect(RECT(0, 0, 520, 900), P("#0b0a10"))
        rrect(c, 20, 40, 500, 640, 24, P("#1d1432"))
        c.drawRect(RECT(20, 40, 500, 640), P("#a66bff", shader=lin(0, 40, 0, 640, ["#3a1a6a", "#1d1432"])))
        T4.hoodie(c, 260, 330, 1.05, "#b8f51a")
        oval(c, 260, 340, 54, 54, P("#000000", alpha=0.45))
        tri = skia.Path()
        tri.moveTo(244, 316)
        tri.lineTo(286, 340)
        tri.lineTo(244, 364)
        tri.close()
        c.drawPath(tri, P("#ffffff"))
        oval(c, 56, 690, 22, 22, P("#b8f51a"))
        c.drawString("sudaderas.diego", 90, 698, F(R.RES.mb, 22), P("#ffffff"))
        eye_icon(c, 60, 760, 22, "#ffffff")
        c.drawString(views, 96, 770, F(R.RES.mx, 30), P("#ffffff"))
        cart_icon(c, 300, 760, 22, "#ff5c7a")
        c.drawString(sales, 336, 770, F(R.RES.mx, 30), P("#ff5c7a"))
        if show_promo:
            T4.lime_button(c, 30, 806, 460, 64, "Promocionar · Q500", press=promo_press, arrow=False, size=24)
    return d


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------


def base(c, k, grid=0.12):
    camera(c, 1.0, 540, 960, k.t)
    neon_bg(c, k.t, grid=grid, wy=1660)


def fmt_k(n):
    return f"{n / 1000:.1f}K" if n >= 1000 else str(int(n))


def scene1(c, k):  # gancho: paga publicidad
    lt = k.lt
    T = k.w
    base(c, k)
    punch = 1 + 0.07 * (1 - ease_out(prog(lt, 0, 0.35)))
    c.save()
    c.translate(540, 640)
    c.scale(punch, punch)
    rrect(c, -510, -150, 510, 150, 40, P("#14061f", alpha=0.85))
    rrect(c, -510, -150, 510, 150, 40, P(LIME, "stroke", 3, alpha=0.8))
    big_text(c, [("¿PAGAS POR VISTAS", "#ffffff"), ("QUE NO VENDEN?", LIME)], 0, -20, 88, 104)
    c.restore()
    tap = T(5) - 0.1
    press = clamp((lt - tap) / 0.35) if lt >= tap else 0.0
    phone(c, 760, 1220, 330, 600, T4.app_screen(reel_screen("1.2K", "0", press)), rot=5, glow_a=0.6)
    if lt > tap:
        u = lt - tap
        r = rng(4)
        for i in range(14):
            st = i * 0.08
            v = u - st
            if v <= 0 or v > 1.6:
                continue
            x = 760 + (r.random() - 0.5) * 200 + v * (r.random() - 0.3) * 500
            y = 1400 - v * 900 + v * v * 150
            coin(c, x, y, 26, rot=k.t * 7 + i, a=clamp(1.6 - v))
    draw_kid(c, 330, 1700, 0.85, k.t, "happy" if lt < T(9) else "worried", look=(0.8, -0.2), style=DIEGO,
             hands={"R": (170, -400), "L": (-110, -230)})
    pk = back_out(prog(lt, T(2) - 0.2, T(2) + 0.2))
    if pk > 0:
        c.save()
        c.translate(330, 980)
        c.scale(pk, pk)
        rrect(c, -150, -36, 150, 36, 36, P(LIME))
        text_center(c, "Diego", 0, 12, F(R.RES.mx, 36), P("#14061f"))
        c.restore()


def scene2(c, k):  # miles de vistas, cero ventas
    lt = k.lt
    T = k.w
    base(c, k)
    views = 12400 * ease_out(prog(lt, 0.1, T(3)))
    phone(c, 600, 1030, 600, 1060, T4.app_screen(reel_screen(fmt_k(views), "0 ventas", show_promo=False)), glow_a=0.6)
    zk = prog(lt, T(4) - 0.2, T(5) + 0.2)
    if zk > 0:
        s = back_out(zk)
        c.save()
        c.translate(780, 640)
        c.rotate(-8)
        c.scale(s, s)
        rrect(c, -150, -60, 150, 60, 24, P("#e8414f"))
        text_center(c, "0 VENTAS", 0, 18, F(R.RES.mx, 52), P("#ffffff"))
        c.restore()
    qk = prog(lt, T(6) - 0.2, T(6) + 0.2)
    if qk > 0:
        s = back_out(qk, 2.2)
        c.save()
        c.translate(300, 700)
        c.scale(s, s)
        glow(c, R.RES.g_mag, 0, 0, 200, 0.4)
        text_center(c, "?", 0, 90, F(R.RES.mx, 260), P("#ff5c7a"))
        c.restore()
    draw_kid(c, 170, 1720, 0.62, k.t, "worried", look=(0.8, -0.4), style=DIEGO, tilt=-6,
             hands={"R": (40, -560), "L": (-110, -230)})


def scene3(c, k):  # el balde con el hoyo
    lt = k.lt
    T = k.w
    base(c, k)
    months = ["ENE", "FEB", "MAR", "ABR", "MAY"]
    mi = min(4, int(lt / 0.75))
    calendar(c, 840, 700, months[mi], prog(lt, 0.0, 0.3))
    bucket(c, 560, 1440, 1.25, k.t, fill=0.15 + 0.05 * math.sin(k.t * 3), patched=0.0)
    pour = 0.5 + 0.5 * math.sin(lt * 3)

    def bag(cc, out):
        hx, hy = out["R"]
        rrect(cc, hx - 50, hy - 40, hx + 50, hy + 60, 30, P("#c9a46a", shader=lin(hx - 50, 0, hx + 50, 0, ["#a8864e", "#e8cf9a", "#a8864e"])))
        text_center(cc, "Q500", hx, hy + 24, F(R.RES.mx, 26), P("#5a3a18"))
    hp = draw_kid(c, 260, 1700, 0.8, k.t, "sad", look=(0.6, 0.4), style=DIEGO, tilt=-4,
                  hands={"R": (200, -470), "L": (-110, -230)}, front_props=bag)
    hx, hy = hp["R"]
    for i in range(5):
        u = (lt * 1.6 + i / 5) % 1
        coin(c, lerp(hx + 30, 560, u), lerp(hy - 10, 1100, u) - 120 * math.sin(math.pi * u), 20, rot=k.t * 6 + i)
    tk = prog(lt, T(4) - 0.2, T(4) + 0.2)
    if tk > 0:
        c.save()
        c.translate(560, 820)
        c.scale(back_out(tk), back_out(tk))
        rrect(c, -230, -44, 230, 44, 44, P("#14061f", alpha=0.9))
        rrect(c, -230, -44, 230, 44, 44, P("#ff5c7a", "stroke", 3))
        text_center(c, "Un balde con un hoyo", 0, 12, F(R.RES.mb, 32), P("#ffffff"))
        c.restore()


def scene4(c, k):  # conoció Velto
    lt = k.lt
    camera(c, lerp(1.08, 1.0, ease_out(prog(lt, 0, 1.0))), 540, 960, k.t)
    light = ease_out(prog(lt, 0.3, 0.9))
    neon_bg(c, k.t, grid=0.04 + 0.12 * light, wy=1640)
    u = ease_in_out(prog(lt, 0.0, 0.6))
    if u < 1:
        pth = skia.Path()
        pth.moveTo(-100, 500)
        pth.cubicTo(300, 560, 500, 1000, 1180, 700)
        meas = skia.PathMeasure(pth, False)
        L = meas.getLength()
        seg = skia.Path()
        meas.getSegment(max(0, u - 0.45) * L, u * L, seg, True)
        c.drawPath(seg, P(VIO, "stroke", 36, shader=lin(0, 0, W, 0, [VIO, "#d06bff", LIME]), blur=16, alpha=0.7))
        c.drawPath(seg, P(VIO, "stroke", 10, shader=lin(0, 0, W, 0, [VIO, "#e2b8ff", LIME])))
    lk = ease_out(prog(lt, 0.4, 0.9))
    if lk > 0:
        client_logo(c, 540, 820, 960 * (0.9 + 0.1 * lk), a=lk)
    draw_kid(c, 540, 1700, 0.7, k.t, "surprised", look=(0, -0.8), style=DIEGO,
             hands={"R": (150, -480), "L": (-150, -480)})


def scene5(c, k):  # el catálogo
    lt = k.lt
    T = k.w
    base(c, k)
    phone(c, 600, 1030, 600, 1060, T4.app_screen(T4.screen_public(lt, prog(lt, 0.1, 1.2))), glow_a=0.7)
    labels = [("Productos", T(6)), ("Precios", T(7)), ("Pedidos", T(9))]
    for i, (lab, tm) in enumerate(labels):
        kk = back_out(prog(lt, tm - 0.2, tm + 0.15))
        if kk > 0:
            c.save()
            c.translate(170, 760 + i * 120)
            c.scale(kk, kk)
            rrect(c, -130, -36, 130, 36, 36, P(LIME))
            text_center(c, lab, 0, 12, F(R.RES.mx, 32), P("#14061f"))
            c.restore()
    nk = prog(lt, T(9), T(9) + 0.3)
    if nk > 0 and lt < k.D:
        c.save()
        c.translate(760, 600)
        c.scale(back_out(nk), back_out(nk))
        rrect(c, -190, -40, 190, 40, 40, P("#14061f"))
        rrect(c, -190, -40, 190, 40, 40, P(LIME, "stroke", 3))
        text_center(c, "¡Nuevo pedido!", 0, 12, F(R.RES.mx, 32), P(LIME))
        c.restore()


def studio_title(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glow(c, R.RES.g_vio, 0, 0, 500, 0.6)
    glow(c, R.RES.g_lime, 160, -20, 300, 0.35)
    f = F(R.RES.mx, 120)
    w = f.measureText("VELTO")
    c.drawString("VELTO", -w / 2, -20, f, P("#ffffff"))
    f2 = F(R.RES.mx, 140)
    w2 = f2.measureText("STUDIO")
    c.drawString("STUDIO", -w2 / 2, 130, f2, P(LIME, shader=lin(-w2 / 2, 0, w2 / 2, 0, [VIO2, "#d06bff", LIME])))
    # claqueta
    c.save()
    c.translate(-330, -150)
    c.rotate(-12 + 8 * math.sin(t * 4))
    rrect(c, -70, -10, 70, 70, 8, P("#14061f"))
    for i in range(4):
        c.drawLine(-60 + i * 36, -10, -40 + i * 36, -40, P("#ffffff", "stroke", 10))
    c.drawRect(RECT(-70, -44, 70, -12), P("#ffffff", alpha=0.0))
    c.restore()
    oval(c, 330, -150, 60, 60, P(LIME, "stroke", 14))
    oval(c, 330, -150, 28, 28, P("#14061f"))
    c.restore()


def trend_board(c, x0, y0, x1, y1, t, k, lt):
    rrect(c, x0, y0, x1, y1, 30, P("#14061f", alpha=0.95))
    rrect(c, x0, y0, x1, y1, 30, P(VIO2, "stroke", 3))
    c.drawString("TENDENCIAS DE HOY", x0 + 34, y0 + 60, F(R.RES.mx, 34), P(LIME))
    oval(c, x1 - 50, y0 + 48, 10, 10, P("#ff3b5c", alpha=0.6 + 0.4 * math.sin(t * 6)))
    c.drawString("EN VIVO", x1 - 160, y0 + 58, F(R.RES.mb, 22), P("#ff5c7a"))
    items = [("Audio en tendencia", "+320%"), ("Formato: antes y después", "+180%"), ("Reto de outfits", "+140%")]
    for i, (lab, pct) in enumerate(items):
        kk = ease_out(clamp(k * 3 - i * 0.6))
        yy = y0 + 110 + i * 78
        c.save()
        c.translate(40 * (1 - kk), 0)
        rrect(c, x0 + 30, yy, x1 - 30, yy + 62, 16, P("#241a3a", alpha=kk))
        c.drawString(lab, x0 + 54, yy + 40, F(R.RES.mb, 26), P("#ffffff", alpha=kk))
        c.drawString(pct, x1 - 150, yy + 40, F(R.RES.mx, 28), P(LIME, alpha=kk))
        ar = skia.Path()
        ar.moveTo(x1 - 56, yy + 42)
        ar.lineTo(x1 - 44, yy + 20)
        ar.lineTo(x1 - 32, yy + 42)
        c.drawPath(ar, P(LIME, "stroke", 4, alpha=kk))
        c.restore()
    by = y1 - 40
    for j in range(8):
        h = (18 + 16 * j) * ease_out(clamp(k * 2 - 0.4)) * (0.9 + 0.1 * math.sin(t * 3 + j))
        bx = x0 + 50 + j * ((x1 - x0 - 100) / 8)
        rrect(c, bx, by - h, bx + 40, by, 8, P(LIME if j > 5 else VIO2))
    for j, lab in enumerate(("Instagram", "TikTok")):
        kk = prog(lt, 0, 1)
        cx = x0 + 120 + j * 230
        rrect(c, cx - 100, y0 - 36, cx + 100, y0 + 8, 22, P("#241a3a"))
        rrect(c, cx - 100, y0 - 36, cx + 100, y0 + 8, 22, P(VIO2, "stroke", 2))
        text_center(c, lab, cx, y0 - 6, F(R.RES.mb, 24), P("#ffffff"))


def scene6(c, k):  # VELTO STUDIO
    lt = k.lt
    T = k.w
    base(c, k, grid=0.16)
    pre = prog(lt, 0.0, T(4) - 0.3) * (1 - prog(lt, T(4) - 0.3, T(4)))
    if pre > 0:  # anticipación antes de la revelación
        glow(c, R.RES.g_vio, 540, 900, 200 + 400 * pre, 0.7 * pre)
        glow(c, R.RES.g_lime, 540, 900, 80 + 200 * pre, 0.6 * pre)
        use("lime")
        R.orbit_sparkles(c, 540, 900, k.t * (1 + 2 * pre), 120 + 200 * pre, 60 + 100 * pre, n=30, seed=4, intensity=pre)
        nk = back_out(prog(lt, 0.0, 0.3))
        c.save()
        c.translate(540, 700)
        c.scale(nk * (1 + 0.05 * math.sin(k.t * 8)), nk * (1 + 0.05 * math.sin(k.t * 8)))
        rrect(c, -130, -44, 130, 44, 44, P(LIME))
        text_center(c, "NUEVO", 0, 16, F(R.RES.mx, 48), P("#14061f"))
        c.restore()
    sk = back_out(prog(lt, T(4) - 0.3, T(4) + 0.2), 1.6)
    move = ease_in_out(prog(lt, T(6) - 0.2, T(7) + 0.3))
    if sk > 0:
        studio_title(c, 540, lerp(900, 600, move), sk * lerp(1.0, 0.62, move), k.t)
        use("lime")
        R.burst(c, 540, 900, lt - T(4) + 0.2, dur=1.2, n=60, radius=520, seed=5, intensity=0.9)
    if move > 0:
        bk = prog(lt, T(8) - 0.2, T(13) + 0.4)
        c.saveLayerAlpha(None, int(255 * move))
        trend_board(c, 120, 820, 960, 1340, k.t, bk, lt)
        c.restore()
        draw_kid(c, 230, 1720, 0.56, k.t, "happy", look=(0.7, -0.6), style=ANA, hands={"R": (170, -470), "L": (-110, -230)})
        draw_kid(c, 860, 1720, 0.58, k.t, "happy", look=(-0.7, -0.6), style=EQUIPO, hands={"L": (-170, -470), "R": (110, -230)})


def deliverable(c, x, y, kind, label, k, t):
    if k <= 0:
        return
    s = back_out(k)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rotate(4 * math.sin(t * 2 + x))
    rrect(c, -110, -150, 110, 150, 22, P("#1d1432"))
    rrect(c, -110, -150, 110, 150, 22, P(LIME if kind == "video" else VIO2, "stroke", 4))
    rrect(c, -96, -136, 96, 90, 14, P("#a66bff", shader=lin(0, -136, 0, 90, ["#5a2ab0", "#2a1050"])))
    T4.hoodie(c, 0, -20, 0.5, "#b8f51a")
    if kind == "video":
        oval(c, 0, -20, 32, 32, P("#000000", alpha=0.5))
        tri = skia.Path()
        tri.moveTo(-10, -34)
        tri.lineTo(16, -20)
        tri.lineTo(-10, -6)
        tri.close()
        c.drawPath(tri, P("#ffffff"))
    else:
        rrect(c, -70, 50, 70, 80, 10, P(LIME))
        text_center(c, "-20%", 0, 72, F(R.RES.mx, 22), P("#14061f"))
    text_center(c, label, 0, 128, F(R.RES.mx, 26), P("#ffffff"))
    c.restore()


def scene7(c, k):  # te crea videos e imágenes -> el balde se llena
    lt = k.lt
    T = k.w
    base(c, k)
    for i, (kind, lab, tm) in enumerate((("video", "VIDEO", T(3)), ("video", "VIDEO", T(3) + 0.25),
                                         ("img", "IMAGEN", T(5)), ("img", "IMAGEN", T(5) + 0.25))):
        deliverable(c, 170 + i * 247, 720, kind, lab, prog(lt, tm - 0.2, tm + 0.15), k.t)
    patched = prog(lt, T(9) - 0.2, T(9) + 0.3)
    fill = ease_out(prog(lt, T(9), k.D))
    bucket(c, 560, 1500, 1.0, k.t, fill=0.15 + 0.85 * fill, patched=patched)
    if patched > 0:
        r = rng(9)
        for i in range(10):
            u = (lt * 1.2 + i / 10) % 1
            coin(c, lerp(200 + r.random() * 700, 560 + (r.random() - .5) * 200, u), lerp(950, 1140, u), 22,
                 rot=k.t * 6 + i, a=fill * (1 - u * 0.3))
    msgs = [("¿Precio?", 120, 1000), ("¡La quiero en M!", 640, 1080), ("¿Envían a Xela?", 110, 1180)]
    for i, (m, bx, by) in enumerate(msgs):
        kk = prog(lt, T(10) + i * 0.3, T(10) + 0.25 + i * 0.3)
        bubble(c, bx, by, m, False, 32, 500, kk, col="#2c2540")
    draw_kid(c, 900, 1720, 0.6, k.t, "joy" if patched > 0.5 else "happy", look=(-0.6, -0.4), style=DIEGO,
             hands={"R": (150, -480), "L": (-150, -480)} if patched > 0.5 else {"R": (110, -230), "L": (-110, -230)})


def scene8(c, k):  # CTA: comenta STUDIO
    lt = k.lt
    T = k.w
    base(c, k)
    word = "STUDIO"
    r = rng(23)
    for i in range(22):
        side = -1 if i % 2 == 0 else 1
        x = 540 + side * (400 + r.random() * 80)
        u = (lt - (T(5) + i * 0.15)) / 2.6
        if u <= 0 or u >= 1:
            continue
        y = lerp(1500, 520, u)
        a = math.sin(math.pi * u)
        tx = [word, "¡" + word + "!", word + "!!", word][i % 4]
        f = F(R.RES.mx, 26)
        w = f.measureText(tx) + 70
        c.save()
        c.translate(x + 20 * math.sin(lt * 2 + i), y)
        rrect(c, -w / 2, -28, w / 2, 28, 28, P("#2c2540", alpha=0.9 * a))
        oval(c, -w / 2 + 28, 0, 16, 16, P([VIO2, LIME, "#ff6fb1", "#5ad1ff"][i % 4], alpha=a))
        c.drawString(tx, -w / 2 + 54, 10, f, P("#ffffff", alpha=a))
        c.restore()
    client_logo(c, 540, 600, 660, a=ease_out(prog(lt, 0, 0.4)))
    studio_title(c, 540, 820, 0.42, k.t)
    bk = ease_out(prog(lt, T(4), T(4) + 0.3))
    c.save()
    c.translate(540, 1060)
    rrect(c, -360, -56, 360, 56, 56, P("#ffffff", alpha=bk))
    oval(c, -300, 0, 34, 34, P(VIO, alpha=bk))
    typed = word[: int(len(word) * prog(lt, T(5) - 0.45, T(5) + 0.1))]
    if typed:
        c.drawString(typed, -245, 18, F(R.RES.mx, 50), P("#14061f", alpha=bk))
    else:
        c.drawString("Agrega un comentario...", -245, 14, F(R.RES.ms, 34), P("#8a7aa8", alpha=bk))
    oval(c, 300, 0, 38, 38, P(LIME if lt > T(5) + 0.2 else "#d9d0ea", alpha=bk))
    ar = skia.Path()
    ar.moveTo(285, -16)
    ar.lineTo(318, 0)
    ar.lineTo(285, 16)
    ar.close()
    c.drawPath(ar, P("#14061f", alpha=bk))
    c.restore()
    gk = prog(lt, T(8) - 0.2, T(8) + 0.25)
    if gk > 0:
        use("lime")
        R.burst(c, 540, 1270, lt - T(8) + 0.1, dur=1.1, n=40, radius=420, seed=7, intensity=0.5)
        s = back_out(gk)
        c.save()
        c.translate(540, 1270)
        c.scale(s, s)
        rrect(c, -380, -70, 380, 70, 40, P(LIME))
        text_center(c, "Te contamos cómo funciona", 0, 16, F(R.RES.mx, 44), P("#14061f"))
        c.restore()
    hk = prog(lt, 0.1, 0.5)
    if hk > 0:
        bucket(c, 900, 1720, 0.45, k.t, fill=1.0, patched=1.0)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8]


def install():
    E2.install()
    R.SCENES = SCENES


if __name__ == "__main__":
    install()
    R.main()
