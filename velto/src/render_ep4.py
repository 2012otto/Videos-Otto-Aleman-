"""Velto — Tutorial animado: "Crea tu tienda digital en menos de 5 minutos" (tienda de ejemplo: Sudaderas Diego).

La app de Velto redibujada en vectores (Inicio, Tienda, Productos, Pedidos, Resumen, tienda publicada),
con un dedo que toca los botones, etiqueta de PASO y cronómetro. Ana presenta (voz de Ava).
Uso:
  VIDEO_BUILD=$PWD/velto/build_ep4 VO_TRIM=0.3 python3 velto/src/render_ep4.py --out velto/build_ep4/video_mudo.mp4
"""
import math
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_ep2 as E2  # noqa: E402
from render_velto import (R, P, RECT, ANA, VIO, VIO2, LIME, F, back_out, clamp, ease_in_out, ease_out, glow,  # noqa: E402
                          lerp, lin, rad, oval, prog, rrect, smooth, text_center, draw_kid, rng, neon_bg, phone,
                          client_logo, chat_icon, use, W, H, draw_img)
from render_ep2 import talk, big_text  # noqa: E402

camera = R.camera
BG, CARD, LINE, MUTED = "#0b0a10", "#15131c", "#2c2838", "#9a95a8"
VW = 520  # ancho virtual de la pantalla de la app

PRODUCTS = [("Sudadera Clásica Negra", "250,00 GTQ", "#2a2a33", 24), ("Hoodie Oversize Lila", "275,00 GTQ", "#a66bff", 18),
            ("Sudadera Lima Neón", "260,00 GTQ", "#c6ff1a", 15), ("Hoodie Edición Xela", "300,00 GTQ", "#2f6bff", 10),
            ("Sudadera Gris Básica", "225,00 GTQ", "#9a9aa8", 30), ("Crop Hoodie Rosa", "240,00 GTQ", "#ff7ab8", 12)]
PHONE = (565, 1035, 720, 1090)  # cx, cy, w, h
STATUS = [("Recibido", "#3a7aff"), ("En camino", "#ff9a2e"), ("Entregado", "#2fbf71")]


# ----------------------------------------------------------------------------
# utilidades de la pantalla del teléfono
# ----------------------------------------------------------------------------


def to_screen(vx, vy):
    cx, cy, w, h = PHONE
    m = w * 0.04
    sc = (w - 2 * m) / VW
    return cx - w / 2 + m + vx * sc, cy - h / 2 + m + vy * sc


def app_screen(draw):
    """Envuelve una función que dibuja en coordenadas virtuales (520 de ancho)."""
    def screen(c, x0, y0, x1, y1):
        sc = (x1 - x0) / VW
        c.save()
        c.translate(x0, y0)
        c.scale(sc, sc)
        c.drawRect(RECT(0, 0, VW, 2000), P(BG))
        draw(c)
        c.restore()
    return screen


def txt(c, s, x, y, size, col="#ffffff", tf=None, a=1.0):
    c.drawString(s, x, y, F(tf or R.RES.mb, size), P(col, alpha=a))


def ui_header(c):
    draw_img(c, R.RES.vlogo, 40, 52, 34)
    txt(c, "VELTO", 70, 63, 30, tf=R.RES.mx)
    rrect(c, 452, 34, 492, 74, 10, P("#ffffff", "stroke", 2.5, alpha=0.8))
    c.drawLine(470, 54, 486, 54, P("#ffffff", "stroke", 2.5))


def ui_tabs(c, active, y=100):
    tabs = ["Resumen", "Productos", "Tienda", "Pedidos"]
    x = 14
    f = F(R.RES.ms, 18)
    for i, t in enumerate(tabs):
        w = f.measureText(t) + 46
        on = i == active
        rrect(c, x, y, x + w, y + 40, 20, P(LIME if on else BG))
        rrect(c, x, y, x + w, y + 40, 20, P(LIME if on else LINE, "stroke", 1.5))
        oval(c, x + 18, y + 20, 6, 6, P("#14061f" if on else MUTED, "stroke", 2))
        c.drawString(t, x + 30, y + 26, f, P("#14061f" if on else MUTED))
        x += w + 8
    c.drawLine(0, y + 56, VW, y + 56, P(LINE, "stroke", 1))


def store_logo(c, x, y, r, k=1.0, primary="#2a2a33"):
    if k <= 0:
        return
    s = back_out(k)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, 0, r, r, P("#ffffff"))
    oval(c, 0, 0, r, r, P(primary, "stroke", r * 0.08))
    hoodie(c, 0, r * 0.08, r * 0.013, primary)
    c.restore()


def ui_selector(c, y=172, primary="#2a2a33", logo_k=1.0):
    rrect(c, 20, y, 500, y + 56, 16, P(BG))
    rrect(c, 20, y, 500, y + 56, 16, P(LINE, "stroke", 1.5))
    store_logo(c, 48, y + 28, 18, logo_k, primary)
    txt(c, "Sudaderas Diego", 76, y + 35, 20, tf=R.RES.ms)
    c.drawLine(466, y + 24, 474, y + 32, P("#ffffff", "stroke", 2))
    c.drawLine(474, y + 32, 482, y + 24, P("#ffffff", "stroke", 2))


def hoodie(c, x, y, s, col):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    dark = R.mix_col(col, "#000000", 0.35)
    body = skia.Path()
    body.moveTo(-60, -50)
    body.lineTo(-110, -10)
    body.lineTo(-130, 90)
    body.lineTo(-100, 96)
    body.lineTo(-80, 30)
    body.lineTo(-78, 120)
    body.lineTo(78, 120)
    body.lineTo(80, 30)
    body.lineTo(100, 96)
    body.lineTo(130, 90)
    body.lineTo(110, -10)
    body.lineTo(60, -50)
    body.close()
    c.drawPath(body, P(col))
    hood = skia.Path()
    hood.moveTo(-60, -50)
    hood.quadTo(-62, -110, 0, -112)
    hood.quadTo(62, -110, 60, -50)
    hood.quadTo(0, -20, -60, -50)
    hood.close()
    c.drawPath(hood, P(dark))
    oval(c, 0, -62, 30, 30, P(R.mix_col(col, "#000000", 0.6)))
    c.drawLine(-12, -40, -14, 10, P("#ffffff", "stroke", 4, alpha=0.8))
    c.drawLine(12, -40, 14, 10, P("#ffffff", "stroke", 4, alpha=0.8))
    rrect(c, -50, 50, 50, 96, 10, P(dark))
    c.drawRect(RECT(-78, 108, 78, 120), P(dark))
    c.restore()


def input_box(c, x, y, w, h, text, k=1.0, label=None, cursor=False, t=0.0):
    if label:
        txt(c, label, x, y - 12, 18, tf=R.RES.ms)
    rrect(c, x, y, x + w, y + h, 16, P(BG))
    rrect(c, x, y, x + w, y + h, 16, P(LINE, "stroke", 1.5))
    n = int(len(text) * clamp(k))
    f = F(R.RES.ms, 20)
    c.drawString(text[:n], x + 18, y + h / 2 + 8, f, P("#ffffff"))
    if cursor and k < 1 and (t * 2) % 1 < 0.5:
        cx = x + 20 + f.measureText(text[:n])
        c.drawLine(cx, y + 14, cx, y + h - 14, P(LIME, "stroke", 2))


def lime_button(c, x, y, w, h, label, press=0.0, arrow=True, size=20):
    s = 1 - 0.06 * math.sin(math.pi * clamp(press))
    c.save()
    c.translate(x + w / 2, y + h / 2)
    c.scale(s, s)
    glow(c, R.RES.g_lime, 0, 0, w * 0.6, 0.35)
    rrect(c, -w / 2, -h / 2, w / 2, h / 2, h / 2, P(LIME))
    f = F(R.RES.mb, size)
    tw = f.measureText(label) + (28 if arrow else 0)
    c.drawString(label, -tw / 2, size * 0.36, f, P("#14061f"))
    if arrow:
        ax = tw / 2 - 12
        c.drawLine(ax - 10, 0, ax + 8, 0, P("#14061f", "stroke", 2.5))
        c.drawLine(ax + 1, -7, ax + 8, 0, P("#14061f", "stroke", 2.5))
        c.drawLine(ax + 1, 7, ax + 8, 0, P("#14061f", "stroke", 2.5))
    c.restore()


def check(c, x, y, r, on=True):
    oval(c, x, y, r, r, P(LIME if on else MUTED, "stroke", 2.5))
    if on:
        m = skia.Path()
        m.moveTo(x - r * 0.45, y)
        m.lineTo(x - r * 0.1, y + r * 0.35)
        m.lineTo(x + r * 0.45, y - r * 0.35)
        c.drawPath(m, P(LIME, "stroke", 2.5))


# ----------------------------------------------------------------------------
# pantallas de la app
# ----------------------------------------------------------------------------


def screen_landing(press):
    def d(c):
        ui_header(c)
        c.drawRect(RECT(0, 96, VW, 900), P(BG, shader=rad(260, 300, 500, ["#3a1a6a", BG])))
        for i in range(6):
            c.drawLine(i * 104, 96, i * 104, 900, P("#9b5cff", "stroke", 1, alpha=0.08))
        txt(c, "TIENDAS DIGITALES · PEDIDOS", 22, 190, 15, LIME, R.RES.ms)
        txt(c, "POR WHATSAPP", 22, 212, 15, LIME, R.RES.ms)
        txt(c, "Tu negocio,", 22, 290, 52, "#ffffff", R.RES.mx)
        txt(c, "en", 340, 290, 52, VIO2, R.RES.mx)
        f = F(R.RES.mx, 52)
        c.drawString("versión digital.", 22, 350, f, P(VIO, shader=lin(22, 0, 420, 0, [VIO2, "#b8a0ff", "#a8f0a0"])))
        for i, ln in enumerate(("Crea tu tienda, sube tu catálogo y", "recibe pedidos ordenados en tu", "celular. Sin código.")):
            txt(c, ln, 22, 410 + i * 30, 19, "#b8b2c8", R.RES.ms)
        lime_button(c, 22, 530, 476, 62, "Crear mi tienda gratis", press)
        rrect(c, 22, 610, 498, 672, 31, P(LINE, "stroke", 1.5))
        text_center(c, "Ver cómo funciona", 260, 648, F(R.RES.mb, 20), P("#ffffff"))
        txt(c, "¿Ya tienes cuenta?", 22, 720, 17, MUTED, R.RES.ms)
        txt(c, "Inicia sesión", 190, 720, 17, LIME, R.RES.mb)
    return d


def screen_tienda(lt, T):
    logo_k = prog(lt, T(4) - 0.3, T(4) + 0.1)
    name_k = prog(lt, T(6) - 0.2, T(9))
    desc_k = prog(lt, T(9) - 0.1, T(10))
    cols = ["#000000", "#2f6bff", "#ff7a1a", "#a66bff"]
    ci = 0 if lt < T(13) else min(3, 1 + int((lt - T(13)) / 0.9))
    primary = cols[ci]

    def d(c):
        ui_header(c)
        ui_tabs(c, 2)
        txt(c, "Logo", 30, 200, 18, tf=R.RES.ms)
        rrect(c, 30, 214, 150, 334, 18, P("#ffffff" if logo_k > 0 else BG))
        if logo_k <= 0:
            dash = P(MUTED, "stroke", 2)
            dash.setPathEffect(skia.DashPathEffect.Make([8, 6], 0))
            c.drawRRect(skia.RRect.MakeRectXY(RECT(30, 214, 150, 334), 18, 18), dash)
            text_center(c, "+", 90, 286, F(R.RES.mx, 40), P(MUTED))
        else:
            store_logo(c, 90, 274, 48, logo_k, primary)
        txt(c, "Portada", 180, 200, 18, tf=R.RES.ms)
        dash = P(MUTED, "stroke", 2)
        dash.setPathEffect(skia.DashPathEffect.Make([8, 6], 0))
        c.drawRRect(skia.RRect.MakeRectXY(RECT(180, 214, 490, 300), 18, 18), dash)
        text_center(c, "Subir portada", 335, 264, F(R.RES.ms, 17), P(MUTED))
        input_box(c, 30, 384, 460, 56, "Sudaderas Diego", name_k, "Nombre del negocio", cursor=True, t=lt)
        input_box(c, 30, 484, 460, 56, "Sudaderas y hoodies en Xela", desc_k, "Descripción", cursor=True, t=lt)
        txt(c, "Color principal", 30, 584, 18, tf=R.RES.ms)
        rrect(c, 30, 596, 490, 650, 16, P(LINE, "stroke", 1.5))
        rrect(c, 44, 606, 84, 640, 8, P(primary))
        txt(c, primary.upper(), 100, 630, 20, tf=R.RES.ms)
        txt(c, "Color de acento", 30, 690, 18, tf=R.RES.ms)
        rrect(c, 30, 702, 490, 756, 16, P(LINE, "stroke", 1.5))
        rrect(c, 44, 712, 84, 746, 8, P("#ffffff"))
        txt(c, "#FFFFFF", 100, 736, 20, tf=R.RES.ms)
        # vista previa en vivo
        rrect(c, 30, 780, 490, 880, 18, P(CARD))
        rrect(c, 30, 780, 490, 830, 18, P(primary))
        c.drawRect(RECT(30, 810, 490, 830), P(primary))
        store_logo(c, 70, 830, 26, logo_k, primary)
        txt(c, "Sudaderas Diego"[: max(0, int(15 * name_k))], 106, 864, 20, tf=R.RES.mx)
        txt(c, "VISTA PREVIA", 370, 864, 13, MUTED, R.RES.ms)
    return d, primary


def product_card(c, y, i, k, tallas=0.0):
    if k <= 0:
        return
    name, price, col, stock = PRODUCTS[i]
    s = back_out(k)
    c.save()
    c.translate(260, y + 50)
    c.scale(s, s)
    c.translate(-260, -50)
    rrect(c, 20, 0, 500, 100, 20, P(CARD))
    rrect(c, 20, 0, 500, 100, 20, P(LINE, "stroke", 1.5))
    rrect(c, 32, 12, 108, 88, 14, P("#f4f2f8"))
    hoodie(c, 70, 52, 0.27, col)
    txt(c, name, 124, 38, 19, tf=R.RES.mb)
    txt(c, price, 124, 64, 19, LIME, R.RES.ms)
    txt(c, f"{stock} en stock · 4 variantes", 124, 88, 15, MUTED, R.RES.ms)
    c.drawLine(462, 24, 476, 38, P("#ffffff", "stroke", 2.2))
    rrect(c, 464, 58, 476, 76, 2, P("#ffffff", "stroke", 2))
    if tallas > 0:
        for j, tl in enumerate(("S", "M", "L", "XL")):
            kk = back_out(clamp(tallas * 4 - j))
            if kk > 0:
                c.save()
                c.translate(330 + j * 40, 64)
                c.scale(kk, kk)
                rrect(c, -16, -14, 16, 14, 8, P(VIO))
                text_center(c, tl, 0, 6, F(R.RES.mx, 14), P("#ffffff"))
                c.restore()
    c.restore()


def screen_productos(lt, T, k):
    adds = [prog(lt, T(2) - 0.2 + i * 0.55, T(2) + 0.15 + i * 0.55) for i in range(6)]
    n_vis = sum(a > 0 for a in adds)
    scroll = max(0, (n_vis - 4)) * 112 * 1.0
    scroll = lerp(0, scroll, 1)
    tallas = prog(lt, T(8) - 0.2, T(8) + 0.5)

    def d(c):
        ui_header(c)
        ui_tabs(c, 1)
        ui_selector(c)
        c.save()
        c.clipRect(RECT(0, 240, VW, 900))
        c.translate(0, -scroll)
        txt(c, "Productos", 22, 292, 36, tf=R.RES.mx)
        txt(c, "Tu catálogo con fotos, precios, variantes y stock.", 22, 320, 15, MUTED, R.RES.ms)
        lime_button(c, 22, 340, 230, 52, "+ Nuevo producto", press=prog(lt, T(2) - 0.6, T(2) - 0.2), arrow=False, size=19)
        rrect(c, 20, 410, 500, 460, 16, P(LINE, "stroke", 1.5))
        oval(c, 46, 434, 9, 9, P(MUTED, "stroke", 2))
        txt(c, "Buscar productos", 66, 441, 18, MUTED, R.RES.ms)
        for i in range(6):
            product_card(c, 478 + i * 112, i, adds[i], tallas=tallas if i == 1 else 0.0)
        c.restore()
    return d


def screen_pedidos(lt, T):
    st_i = 0 if lt < T(11) - 0.1 else (1 if lt < T(13) - 0.1 else 2)
    open_dd = (T(9) - 0.2 < lt < T(13) + 0.2)
    arrive = back_out(prog(lt, T(4) - 0.2, T(4) + 0.2))
    contact = prog(lt, T(15) - 0.2, T(15) + 0.3)

    def d(c):
        ui_header(c)
        ui_tabs(c, 3)
        ui_selector(c)
        txt(c, "Pedidos", 22, 292, 36, tf=R.RES.mx)
        txt(c, "Pedidos recibidos desde tu tienda.", 22, 320, 15, MUTED, R.RES.ms)
        if arrive <= 0:
            return
        c.save()
        c.translate(260, 520)
        c.scale(arrive, arrive)
        c.translate(-260, -520)
        rrect(c, 20, 350, 500, 760, 24, P(CARD))
        rrect(c, 20, 350, 500, 760, 24, P(LIME if lt < T(6) else LINE, "stroke", 2))
        txt(c, "#1 · María López", 44, 396, 24, tf=R.RES.mx)
        txt(c, "+502 5555-0123 · 13 nov 2026, 10:24", 44, 422, 14, MUTED, R.RES.ms)
        name, col = STATUS[st_i]
        f = F(R.RES.mb, 16)
        bw = f.measureText(name) + 28
        rrect(c, 44, 444, 44 + bw, 476, 16, P(col, alpha=0.25))
        c.drawString(name, 58, 466, f, P(col))
        rrect(c, 60 + bw, 440, 300 + bw * 0.2, 480, 14, P(BG))
        rrect(c, 60 + bw, 440, 300 + bw * 0.2, 480, 14, P(LINE, "stroke", 1.5))
        txt(c, name, 76 + bw, 467, 17, tf=R.RES.ms)
        txt(c, "2 × Hoodie Oversize Lila (M)", 44, 520, 17, "#c8c2d8", R.RES.ms)
        txt(c, "550,00 GTQ", 384, 520, 17, "#c8c2d8", R.RES.ms)
        rrect(c, 44, 540, 476, 580, 14, P("#1c1a24"))
        txt(c, "Notas: Entregar en la tarde, por favor", 60, 566, 15, "#c8c2d8", R.RES.ms)
        c.drawLine(44, 600, 476, 600, P(LINE, "stroke", 1.5))
        txt(c, "550,00 GTQ", 44, 640, 24, tf=R.RES.mx)
        chat_icon(c, 286, 632, 11, LIME)
        txt(c, "Contactar al cliente", 304, 640, 17, LIME, R.RES.mb)
        if contact > 0:
            glow(c, R.RES.g_lime, 380, 632, 120, 0.5 * (1 - contact))
        # camioneta en camino
        if st_i >= 1:
            u = clamp((lt - (T(11) - 0.1)) / 1.6)
            tx = lerp(60, 400, u) if st_i == 1 else 400
            c.drawLine(44, 708, 476, 708, P(LINE, "stroke", 3))
            rrect(c, tx, 672, tx + 54, 702, 6, P(STATUS[st_i][1]))
            rrect(c, tx + 54, 682, tx + 74, 702, 4, P(STATUS[st_i][1]))
            oval(c, tx + 14, 704, 7, 7, P("#ffffff"))
            oval(c, tx + 58, 704, 7, 7, P("#ffffff"))
            if st_i == 2:
                check(c, 452, 690, 14)
        c.restore()
        if open_dd:
            dk = ease_out(prog(lt, T(9) - 0.2, T(9) + 0.1))
            x0 = 60 + bw
            rrect(c, x0, 486, x0 + 240, 486 + 150 * dk, 14, P("#1c1a24"))
            rrect(c, x0, 486, x0 + 240, 486 + 150 * dk, 14, P(LINE, "stroke", 1.5))
            if dk > 0.8:
                for j, (nm, cl) in enumerate(STATUS):
                    yy = 500 + j * 46
                    if j == st_i:
                        rrect(c, x0 + 6, yy - 4, x0 + 234, yy + 36, 10, P(cl, alpha=0.25))
                    oval(c, x0 + 26, yy + 16, 6, 6, P(cl))
                    txt(c, nm, x0 + 42, yy + 23, 18, tf=R.RES.ms)
    return d, st_i


def screen_resumen(lt, T, published=0.0):
    ventas = 2450.0 * ease_out(prog(lt, T(6) - 0.3, T(6) + 1.0))
    pedidos = int(8 * ease_out(prog(lt, T(8) - 0.2, T(8) + 0.8)))

    def d(c):
        ui_header(c)
        ui_tabs(c, 0)
        ui_selector(c)
        txt(c, "Hola, Sudaderas", 22, 296, 36, tf=R.RES.mx)
        txt(c, "Diego", 22, 338, 36, tf=R.RES.mx)
        txt(c, "Esto es lo que pasa en tu negocio.", 22, 366, 16, MUTED, R.RES.ms)
        lime_button(c, 22, 384, 220, 54, "Publicar tienda", press=published, size=19)
        rrect(c, 20, 456, 500, 650, 22, P(CARD))
        rrect(c, 20, 456, 500, 650, 22, P(LINE, "stroke", 1.5))
        txt(c, "P R I M E R O S   P A S O S", 44, 490, 15, LIME, R.RES.ms)
        steps = [("Sube tu logo", True), ("Agrega tu primer producto", True), ("Publica tu tienda", published >= 1)]
        for i, (lab, on) in enumerate(steps):
            yy = 506 + i * 46
            rrect(c, 40, yy, 480, yy + 38, 12, P(LINE, "stroke", 1.2))
            check(c, 62, yy + 19, 10, on)
            c.drawString(lab, 84, yy + 25, F(R.RES.ms, 17), P(MUTED if on else "#ffffff"))
            if on:
                c.drawLine(84, yy + 19, 84 + F(R.RES.ms, 17).measureText(lab), yy + 19, P(MUTED, "stroke", 1.5))
        for j, (lab, val) in enumerate((("VENTAS", f"{ventas:,.2f} GTQ".replace(",", "X").replace(".", ",").replace("X", ".")),
                                        ("PEDIDOS NUEVOS", str(pedidos)))):
            x0 = 20 + j * 246
            rrect(c, x0, 670, x0 + 234, 800, 22, P(CARD))
            rrect(c, x0, 670, x0 + 234, 800, 22, P(LINE, "stroke", 1.5))
            txt(c, lab, x0 + 20, 706, 15, MUTED, R.RES.ms)
            txt(c, val, x0 + 20, 764, 28 if j == 0 else 40, tf=R.RES.mx)
    return d


def screen_public(lt, k):
    primary = "#a66bff"

    def d(c):
        c.drawRect(RECT(0, 0, VW, 900), P("#f6f3fb"))
        c.drawRect(RECT(0, 0, VW, 200), P(primary, shader=lin(0, 0, VW, 200, ["#7a3ae0", "#c08aff"])))
        store_logo(c, 80, 200, 50, 1.0, "#7a3ae0")
        txt(c, "Sudaderas Diego", 150, 196, 28, "#ffffff", R.RES.mx)
        txt(c, "Sudaderas y hoodies en Xela", 150, 230, 16, "#4a3a6a", R.RES.ms)
        rrect(c, 330, 30, 500, 68, 19, P("#ffffff", alpha=0.25))
        txt(c, "velto/t/sudaderas-diego", 342, 55, 12, "#ffffff", R.RES.ms)
        for i in range(6):
            col_, row = i % 2, i // 2
            x0, y0 = 22 + col_ * 246, 270 + row * 205
            kk = back_out(clamp(k * 3 - i * 0.25))
            if kk <= 0:
                continue
            c.save()
            c.translate(x0 + 117, y0 + 95)
            c.scale(kk, kk)
            c.translate(-(x0 + 117), -(y0 + 95))
            rrect(c, x0, y0, x0 + 234, y0 + 190, 18, P("#ffffff"))
            rrect(c, x0 + 10, y0 + 10, x0 + 224, y0 + 110, 12, P("#efeaf8"))
            hoodie(c, x0 + 117, y0 + 62, 0.32, PRODUCTS[i][2])
            txt(c, PRODUCTS[i][0][:20], x0 + 12, y0 + 134, 14, "#14061f", R.RES.mb)
            txt(c, PRODUCTS[i][1], x0 + 12, y0 + 158, 15, "#7a3ae0", R.RES.mx)
            rrect(c, x0 + 150, y0 + 140, x0 + 224, y0 + 176, 18, P(LIME))
            text_center(c, "Pedir", x0 + 187, y0 + 164, F(R.RES.mb, 15), P("#14061f"))
            c.restore()
    return d


# ----------------------------------------------------------------------------
# dedo, etiqueta de paso, cronómetro
# ----------------------------------------------------------------------------


def finger(c, vx, vy, press, a=1.0):
    if a <= 0:
        return
    x, y = to_screen(vx, vy)
    x += 18
    y += 26 + (0 if press > 0 else 10)
    c.save()
    c.translate(x, y)
    c.rotate(-20)
    sk = P("#f6c09a", shader=lin(-30, 0, 30, 0, ["#e8a880", "#ffe2c8", "#e8a880"]), alpha=a)
    rrect(c, -22, -10, 22, 150, 22, sk)
    rrect(c, -24, 90, 60, 220, 40, sk)
    oval(c, 0, 4, 14, 10, P("#ffd8e0", alpha=0.8 * a))
    c.restore()
    if 0 < press < 1:
        tx, ty = to_screen(vx, vy)
        oval(c, tx, ty, 20 + 60 * press, 20 + 60 * press, P(LIME, "stroke", 5, alpha=(1 - press) * a))


def finger_path(lt, keys):
    """keys = [(tiempo, vx, vy, tap)] -> posición, presión."""
    if not keys:
        return None
    for (t, x, y, tap) in keys:  # los toques tienen prioridad
        if tap and t <= lt < t + 0.35:
            return x, y, (lt - t) / 0.35
    if lt <= keys[0][0]:
        k0 = keys[0]
        return k0[1], k0[2], 0.0
    for (t0, x0, y0, _), (t1, x1, y1, tap1) in zip(keys, keys[1:]):
        if t0 <= lt < t1:
            u = ease_in_out((lt - t0) / max(t1 - t0, 1e-3) * 1.4)
            return lerp(x0, x1, u), lerp(y0, y1, u), 0.0
    for (t, x, y, tap) in keys:
        if tap and t <= lt < t + 0.35:
            return x, y, (lt - t) / 0.35
    k1 = keys[-1]
    return k1[1], k1[2], 0.0


def step_tag(c, n, title, k):
    if k <= 0:
        return
    s = back_out(k)
    c.save()
    c.translate(330, 492)
    c.scale(s, s)
    f1, f2 = F(R.RES.mx, 30), F(R.RES.mb, 30)
    w1 = f1.measureText(f"PASO {n}/5") + 36
    w2 = f2.measureText(title) + 40
    glow(c, R.RES.g_lime, 0, 0, (w1 + w2) * 0.6, 0.35)
    x0 = -(w1 + w2) / 2
    rrect(c, x0, -30, x0 + w1, 30, 30, P(LIME))
    c.drawString(f"PASO {n}/5", x0 + 18, 11, f1, P("#14061f"))
    rrect(c, x0 + w1 - 18, -30, x0 + w1 + w2, 30, 30, P("#14061f"))
    c.drawRect(RECT(x0 + w1 - 18, -30, x0 + w1, 30), P(LIME))
    c.drawString(title, x0 + w1 + 14, 11, f2, P("#ffffff"))
    c.restore()


def stopwatch(c, t, vo, x=990, y=492):
    t0 = vo[1]["start"]
    t1 = vo[6]["start"] + 3.0
    if t < t0 - 0.2:
        return
    u = clamp((t - t0) / (t1 - t0))
    secs = int(272 * u)  # 4:32 al publicar
    oval(c, x, y, 62, 62, P("#14061f", alpha=0.92))
    oval(c, x, y, 62, 62, P(LIME, "stroke", 4))
    arc = skia.Path()
    arc.addArc(RECT(x - 52, y - 52, x + 52, y + 52), -90, 360 * secs / 300)
    c.drawPath(arc, P(VIO2, "stroke", 8))
    text_center(c, f"{secs // 60}:{secs % 60:02d}", x, y + 12, F(R.RES.mx, 32), P("#ffffff"))
    rrect(c, x - 10, y - 82, x + 10, y - 66, 4, P(LIME))


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------
VO = None


def base(c, k):
    camera(c, 1.0, 540, 960, k.t)
    neon_bg(c, k.t, grid=0.12, wy=1640)


def ana_side(c, k, pose="point"):
    hands = {"R": (170, -470), "L": (-110, -220)} if pose == "point" else {"R": (120, -260), "L": (-120, -260)}
    draw_kid(c, 150, 1700, 0.56, k.t, "happy", look=(0.8, -0.4), style=ANA, hands=hands, talk=talk(k.t))


def scene1(c, k):  # gancho
    lt = k.lt
    base(c, k)
    punch = 1 + 0.07 * (1 - ease_out(prog(lt, 0, 0.35)))
    c.save()
    c.translate(540, 640)
    c.scale(punch, punch)
    rrect(c, -500, -150, 500, 250, 40, P("#14061f", alpha=0.8))
    rrect(c, -500, -150, 500, 250, 40, P(LIME, "stroke", 3, alpha=0.8))
    big_text(c, [("TU TIENDA DIGITAL", "#ffffff"), ("EN MENOS DE", "#ffffff"), ("5 MINUTOS", LIME)], 0, -40, 92, 104)
    c.restore()
    phone(c, 760, 1260, 330, 560, app_screen(screen_landing(0.0)), rot=6 + 2 * math.sin(k.t), glow_a=0.7)
    draw_kid(c, 300, 1740, 0.72, k.t, "happy", look=(0.6, -0.4), style=ANA,
             hands={"R": (180, -480), "L": (-110, -220)}, talk=talk(k.t))
    sk = back_out(prog(lt, k.w(7) - 0.2, k.w(7) + 0.2))
    if sk > 0:
        c.save()
        c.translate(220, 950)
        c.scale(sk, sk)
        oval(c, 0, 0, 80, 80, P("#14061f"))
        oval(c, 0, 0, 80, 80, P(LIME, "stroke", 6))
        text_center(c, "5:00", 0, 14, F(R.RES.mx, 40), P("#ffffff"))
        c.restore()


def scene2(c, k):  # paso 1
    lt = k.lt
    T = k.w
    base(c, k)
    tap_t = T(7) - 0.1
    press = clamp((lt - tap_t) / 0.35) if lt >= tap_t else 0.0
    phone(c, *PHONE[:2], PHONE[2], PHONE[3], app_screen(screen_landing(press)), glow_a=0.6)
    pos = finger_path(lt, [(0.0, 380, 820, False), (tap_t - 0.6, 260, 561, False), (tap_t, 260, 561, True)])
    finger(c, *pos)
    step_tag(c, 1, "Crea tu cuenta", prog(lt, 0.0, 0.3))
    ana_side(c, k)
    stopwatch(c, k.t, VO)


def scene3(c, k):  # paso 2: tu marca
    lt = k.lt
    T = k.w
    base(c, k)
    d, primary = screen_tienda(lt, T)
    phone(c, *PHONE[:2], PHONE[2], PHONE[3], app_screen(d), glow_a=0.6)
    keys = [(0.0, 300, 300, False), (T(4) - 0.6, 90, 274, False), (T(4) - 0.3, 90, 274, True),
            (T(6) - 0.5, 260, 412, False), (T(6) - 0.2, 260, 412, True), (T(9) - 0.4, 260, 512, False),
            (T(9) - 0.1, 260, 512, True), (T(13) - 0.4, 64, 623, False), (T(13), 64, 623, True),
            (T(13) + 0.9, 64, 623, True), (T(13) + 1.8, 64, 623, True), (T(13) + 2.7, 64, 623, True)]
    finger(c, *finger_path(lt, keys))
    step_tag(c, 2, "Tu marca", prog(lt, 0.0, 0.3))
    ana_side(c, k)
    stopwatch(c, k.t, VO)


def scene4(c, k):  # paso 3: productos
    lt = k.lt
    T = k.w
    base(c, k)
    phone(c, *PHONE[:2], PHONE[2], PHONE[3], app_screen(screen_productos(lt, T, k)), glow_a=0.6)
    keys = [(0.0, 300, 300, False), (T(2) - 0.9, 137, 366, False), (T(2) - 0.6, 137, 366, True)]
    finger(c, *finger_path(lt, keys), a=1 - prog(lt, T(4), T(5)))
    step_tag(c, 3, "Tus productos", prog(lt, 0.0, 0.3))
    ana_side(c, k)
    stopwatch(c, k.t, VO)


def scene5(c, k):  # paso 4: pedidos
    lt = k.lt
    T = k.w
    base(c, k)
    d, st_i = screen_pedidos(lt, T)
    phone(c, *PHONE[:2], PHONE[2], PHONE[3], app_screen(d), glow_a=0.6)
    keys = [(0.0, 380, 300, False), (T(9) - 0.6, 200, 460, False), (T(9) - 0.3, 200, 460, True),
            (T(11) - 0.5, 200, 562, False), (T(11) - 0.2, 200, 562, True), (T(13) - 0.5, 200, 608, False),
            (T(13) - 0.2, 200, 608, True), (T(15) - 0.6, 380, 632, False), (T(15) - 0.3, 380, 632, True)]
    finger(c, *finger_path(lt, keys))
    step_tag(c, 4, "Tus pedidos", prog(lt, 0.0, 0.3))
    if lt > T(4) - 0.2 and lt < T(6) + 0.5:
        nk = back_out(prog(lt, T(4) - 0.2, T(4) + 0.1))
        c.save()
        c.translate(760, 600)
        c.scale(nk, nk)
        rrect(c, -170, -40, 170, 40, 40, P(LIME))
        text_center(c, "¡Nuevo pedido!", 0, 12, F(R.RES.mx, 32), P("#14061f"))
        c.restore()
    ana_side(c, k)
    stopwatch(c, k.t, VO)


def scene6(c, k):  # resumen
    lt = k.lt
    T = k.w
    base(c, k)
    phone(c, *PHONE[:2], PHONE[2], PHONE[3], app_screen(screen_resumen(lt, T)), glow_a=0.6)
    rk = back_out(prog(lt, 0.0, 0.3))
    if rk > 0:
        c.save()
        c.translate(330, 492)
        c.scale(rk, rk)
        rrect(c, -180, -30, 180, 30, 30, P("#14061f"))
        rrect(c, -180, -30, 180, 30, 30, P(LIME, "stroke", 3))
        text_center(c, "BONUS · Tu resumen", 0, 11, F(R.RES.mx, 28), P(LIME))
        c.restore()
    ana_side(c, k)
    stopwatch(c, k.t, VO)


def scene7(c, k):  # paso 5: publicar
    lt = k.lt
    T = k.w
    base(c, k)
    tap_t = T(3) - 0.1
    press = clamp((lt - tap_t) / 0.35) if lt >= tap_t else 0.0
    pub = prog(lt, tap_t + 0.3, tap_t + 1.0)
    if pub < 1:
        phone(c, *PHONE[:2], PHONE[2], PHONE[3], app_screen(screen_resumen(lt + 10, lambda i: -100, press)), glow_a=0.6)
        pos = finger_path(lt, [(0.0, 380, 700, False), (tap_t - 0.6, 132, 411, False), (tap_t, 132, 411, True)])
        finger(c, *pos, a=1 - pub)
    if pub > 0:
        c.saveLayerAlpha(None, int(255 * smooth(pub)))
        phone(c, *PHONE[:2], PHONE[2], PHONE[3], app_screen(screen_public(lt, prog(lt, tap_t + 0.6, tap_t + 2.2))), glow_a=1.0)
        c.restore()
        use("lime")
        R.burst(c, 600, 900, lt - tap_t - 0.3, dur=1.4, n=70, radius=560, seed=8, intensity=0.9)
    ok = prog(lt, T(6) - 0.2, T(6) + 0.2)
    if ok > 0:
        s = back_out(ok)
        c.save()
        c.translate(565, 1470)
        c.scale(s, s)
        rrect(c, -300, -46, 300, 46, 46, P(LIME))
        text_center(c, "¡Tu tienda está en línea!", 0, 14, F(R.RES.mx, 34), P("#14061f"))
        c.restore()
    step_tag(c, 5, "Publica", prog(lt, 0.0, 0.3))
    ana_side(c, k)
    stopwatch(c, k.t, VO)


def scene8(c, k):  # CTA
    lt = k.lt
    T = k.w
    base(c, k)
    word = "TIENDA"
    r = rng(23)
    for i in range(22):
        side = -1 if i % 2 == 0 else 1
        x = 540 + side * (400 + r.random() * 80)
        u = (lt - (T(1) + i * 0.15)) / 2.6
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
    client_logo(c, 540, 620, 700, a=ease_out(prog(lt, 0, 0.4)))
    bk = ease_out(prog(lt, 0.1, 0.4))
    c.save()
    c.translate(540, 870)
    rrect(c, -360, -56, 360, 56, 56, P("#ffffff", alpha=bk))
    oval(c, -300, 0, 34, 34, P(VIO, alpha=bk))
    typed = word[: int(len(word) * prog(lt, T(1) - 0.45, T(1) + 0.1))]
    if typed:
        c.drawString(typed, -245, 18, F(R.RES.mx, 50), P("#14061f", alpha=bk))
    else:
        c.drawString("Agrega un comentario...", -245, 14, F(R.RES.ms, 34), P("#8a7aa8", alpha=bk))
    oval(c, 300, 0, 38, 38, P(LIME if lt > T(1) + 0.2 else "#d9d0ea", alpha=bk))
    ar = skia.Path()
    ar.moveTo(285, -16)
    ar.lineTo(318, 0)
    ar.lineTo(285, 16)
    ar.close()
    c.drawPath(ar, P("#14061f", alpha=bk))
    c.restore()
    gk = prog(lt, T(4) - 0.2, T(4) + 0.25)
    if gk > 0:
        use("lime")
        R.burst(c, 540, 1110, lt - T(13) + 0.1, dur=1.1, n=50, radius=460, seed=7, intensity=0.6)
        s = back_out(gk)
        c.save()
        c.translate(540, 1110)
        c.scale(s, s)
        glow(c, R.RES.g_lime, 0, 0, 440, 0.5)
        rrect(c, -400, -120, 400, 120, 46, P(LIME))
        text_center(c, "Te creamos tu tienda", 0, -42, F(R.RES.mx, 50), P("#14061f"))
        text_center(c, "sin que hagas nada", 0, 10, F(R.RES.mb, 40), P("#14061f"))
        text_center(c, "100% GRATIS", 0, 80, F(R.RES.mx, 66), P("#14061f"))
        c.restore()
    draw_kid(c, 170, 1660, 0.62, k.t, "happy", look=(0.6, -0.4), style=ANA,
             hands={"R": (170, -480 + 30 * math.sin(lt * 9)), "L": (-120, -220)}, talk=talk(k.t))


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8]


def install():
    global VO
    E2.install()
    R.SCENES = SCENES
    VO, _ = R.timeline.load()


if __name__ == "__main__":
    install()
    R.main()
