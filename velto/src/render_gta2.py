"""Velto — GTA 6 (parte 2): "ya habría ganado más de mil millones" → giro: un personaje del mundo saca su
teléfono, la cámara entra a la pantalla y aparece su página en Velto. CTA: Comenta VENTA (guía en 5 min).

Uso:
  VIDEO_BUILD=$PWD/velto/build_gta2 VO_TRIM=0.12 VO_GAP=0.15 VO_TAIL=1.2 \
    python3 velto/src/render_gta2.py --out velto/build_gta2/video_mudo.mp4
"""
import math
import os
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "blanquis", "src"))
import render_velto as V  # noqa: E402
import render_sueno as S  # noqa: E402
import render_gta as G  # noqa: E402
import render_ep4 as E4  # noqa: E402
import render_ep5 as E5  # noqa: E402
import render_blanquis as B  # noqa: E402
from render_velto import (R, P, RECT, VIO, VIO2, LIME, F, back_out, clamp, ease_in_out, ease_out, glow, lerp,  # noqa: E402
                          lin, rad, oval, prog, rrect, smooth, text_center, rng, use, W, H, draw_img)

VO = None


def blur_layer(c, sx, sy=None):
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(max(sx, 0.01), max(sx if sy is None else sy, 0.01), skia.TileMode.kClamp))
    c.saveLayer(None, p)


def money_text(n):
    return "$" + f"{int(n):,}"


# ----------------------------------------------------------------------------
# 1. caída desde el cielo + lluvia de dinero
# ----------------------------------------------------------------------------


def scene1(c, k):
    lt, T = k.lt, k.w
    u = ease_in_out(prog(lt, 0.0, 2.3))
    if lt < 2.3:
        z = 0.5 * (0.11 / 0.5) ** (1 - u)
    else:
        z = 0.5 * (2.0 / 0.5) ** ease_in_out(prog(lt, 2.3, k.D + 0.3))
    w2 = ease_in_out(prog(lt, 0.5, k.D + 0.3))
    cx, cy = lerp(-100, G.CITY[0], w2), lerp(80, G.CITY[1], w2)
    rot = lerp(60, 0, u) - 10 * smooth(prog(lt, 2.3, k.D))
    c.save()
    G.world_cam(c, cx, cy, z, rot)
    G.draw_map(c, k.t)
    c.restore()
    haze = clamp(1 - prog(lt, 0.2, 1.4))
    if haze > 0:
        c.drawRect(RECT(0, 0, W, H), P("#ffe6ef", shader=lin(0, 0, 0, H, ["#ffd2a8", "#ffe6ef", "#c9b8ff"]), alpha=haze))
    G.clouds3d(c, 1 / z + 0.3, k.t)
    g = prog(lt, T(0) - 0.1, T(1) + 0.2)
    out = prog(lt, T(7) - 0.2, T(8))
    if g > 0 and out < 1:
        c.save()
        c.translate(540, 1050)
        c.scale(1 + 0.8 * out, 1 + 0.8 * out)
        c.saveLayerAlpha(None, int(255 * (1 - out)))
        G.pop_text(c, "GTA 6", 0, 0, 200, g, rot=-4, shader=G.sunset_text_shader(-140, 0))
        G.tag(c, "AÚN NO SALE", 0, 120, prog(lt, T(3) - 0.1, T(3) + 0.2), bg="#14061f", size=44, rot=3)
        c.restore()
        c.restore()
    # lluvia de billetes y contador
    mk = prog(lt, T(8) - 0.2, T(8) + 0.2)
    if mk > 0:
        r = rng(91)
        for i in range(34):
            sp = 700 + r.random() * 700
            x = r.random() * 1200 - 60 + 80 * math.sin(k.t * 1.5 + i)
            y = -200 + ((lt - T(8) + r.random() * 0.8) * sp) % 2300
            G.bill(c, x, y, k.t * (60 + 80 * r.random()) + i * 40, 1.0 + 0.6 * r.random())
        n = 1e9 * ease_out(prog(lt, T(9) - 0.2, T(12) + 0.3))
        sh = G.shake(k.t, 6 * mk)
        G.tag(c, "MÁS DE", 540, 880, prog(lt, T(9) - 0.1, T(9) + 0.2), bg=LIME, fg="#14061f", size=40, rot=-3)
        G.pop_text(c, money_text(n), 540 + sh[0], 1040 + sh[1], 112, mk, shader=lin(0, 960, 0, 1040, ["#d4ff4a", "#4fbf6a"]))
        G.pop_text(c, "DÓLARES", 540, 1160, 80, prog(lt, T(14) - 0.1, T(14) + 0.2))


# ----------------------------------------------------------------------------
# 2. el mundo comprando: globo con compras
# ----------------------------------------------------------------------------
CONT = [(-100, 40, 0.55, 0.45), (-60, -15, 0.35, 0.55), (15, 50, 0.45, 0.3), (20, 5, 0.4, 0.6), (90, 45, 0.8, 0.4),
        (135, -25, 0.35, 0.25), (-90, 15, 0.12, 0.12), (100, 15, 0.25, 0.2)]


def globe(c, x, y, r, rot, t, pings=0.0, seed=4):
    glow(c, R.RES.g_vio, x, y, r * 1.6, 0.5, skia.BlendMode.kScreen)
    oval(c, x, y, r * 1.04, r * 1.04, P("#7fd6ff", alpha=0.35, blur=12))
    oval(c, x, y, r, r, P("#1a6ad0", shader=rad(x - r * 0.35, y - r * 0.35, r * 1.4, ["#4ab0ff", "#1a6ad0", "#0a2a6a"])))
    c.save()
    c.clipPath(skia.Path().addCircle(x, y, r), True)
    for lon, lat, rx, ry in CONT:
        a = math.radians(lon) - rot
        if math.cos(a) <= 0.05:
            continue
        px = x + r * math.sin(a) * math.cos(math.radians(lat))
        py = y - r * math.sin(math.radians(lat))
        p = G.blob(int(lon + 500), r * rx * 0.5 * math.cos(a), r * ry * 0.5)
        c.save()
        c.translate(px, py)
        c.drawPath(p, P("#4fbf6a", shader=lin(0, -r * 0.3, 0, r * 0.3, ["#7fdc5a", "#2f8f4a"])))
        c.restore()
    r_ = rng(seed)
    n = int(60 * pings)
    for i in range(n):  # compras apareciendo por el mundo
        lon, lat = r_.random() * 6.283, (r_.random() - 0.5) * 2.2
        a = lon - rot
        if math.cos(a) <= 0.1:
            continue
        px = x + r * math.sin(a) * math.cos(lat)
        py = y - r * math.sin(lat)
        ph = (t * 1.3 + r_.random()) % 1
        oval(c, px, py, 7, 7, P(LIME))
        oval(c, px, py, 7 + 34 * ph, 7 + 34 * ph, P(LIME, "stroke", 3, alpha=1 - ph))
    c.restore()
    oval(c, x, y, r, r, P("#000000", shader=rad(x + r * 0.5, y + r * 0.4, r * 1.3, [R.hexc("#000000", 0), R.hexc("#000000", 0), R.hexc("#000000", 0.6)], [0, .55, 1])))


def space(c, t):
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#060818", shader=rad(540, 1000, 1400, ["#1a1a4a", "#060818"])))
    r = rng(3)
    for i in range(140):
        x, y = r.random() * 1400 - 160, r.random() * 2300 - 190
        a = 0.4 + 0.6 * abs(math.sin(t * 2 + i))
        oval(c, x, y, 1.5 + 2 * r.random(), 1.5 + 2 * r.random(), P("#ffffff", alpha=a))


def scene2(c, k):
    lt, T = k.lt, k.w
    zo = ease_out(prog(lt, 0, 1.0))
    z = lerp(3.2, 1.0, zo) + 0.05 * math.sin(lt * 1.5)
    c.save()
    c.translate(540, 1080)
    c.rotate(lerp(25, 0, zo) + 4 * math.sin(lt * 0.8))
    c.scale(z, z)
    c.translate(-540, -1080)
    space(c, k.t)
    globe(c, 540, 1000, 370, k.t * 0.6, k.t, pings=prog(lt, 0.4, T(10)))
    c.restore()
    G.tag(c, "ESTIMACIÓN DE SENSOR TOWER", 540, 620, prog(lt, T(1) - 0.1, T(1) + 0.2), bg="#14061f", size=32, rot=-2)
    nk = prog(lt, T(6) - 0.15, T(6) + 0.15)
    if nk > 0:
        n = 11_000_000 * ease_out(prog(lt, T(6) - 0.1, T(7) + 0.4))
        G.pop_text(c, f"+{int(n):,}", 540, 1500, 130, nk, shader=lin(0, 1400, 0, 1500, ["#d4ff4a", "#7fdc5a"]))
        G.tag(c, "COPIAS DIGITALES", 540, 1590, prog(lt, T(10) - 0.1, T(10) + 0.2), bg=LIME, fg="#14061f", size=42, rot=2)


# ----------------------------------------------------------------------------
# 3. récord: trofeo
# ----------------------------------------------------------------------------


def trophy(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    gold = lin(-200, 0, 200, 0, ["#a8740a", "#ffe27a", "#ffc23a", "#c8901a"], [0, .35, .6, 1])
    cup = skia.Path()
    cup.moveTo(-200, -300)
    cup.lineTo(200, -300)
    cup.cubicTo(200, -40, 120, 60, 0, 70)
    cup.cubicTo(-120, 60, -200, -40, -200, -300)
    cup.close()
    for sd in (-1, 1):
        h = skia.Path()
        h.moveTo(sd * 190, -250)
        h.cubicTo(sd * 320, -250, sd * 320, -60, sd * 140, -40)
        c.drawPath(h, P("#ffc23a", "stroke", 34, shader=gold))
    c.drawPath(cup, P("#ffc23a", shader=gold))
    rrect(c, -40, 60, 40, 170, 10, P("#ffc23a", shader=gold))
    rrect(c, -150, 170, 150, 250, 18, P("#ffc23a", shader=gold))
    rrect(c, -170, 240, 170, 300, 14, P("#3a1a6a"))
    text_center(c, "#1", 0, -100, F(R.RES.mx, 150), P("#7a4a0a"))
    c.drawLine(-120, -270, -150, -80, P("#ffffff", "stroke", 16, alpha=0.5))
    c.restore()


def scene3(c, k):
    lt, T = k.lt, k.w
    hit = T(4) - 0.1
    imp = max(0, 1 - (lt - hit) / 0.35) if lt >= hit else 0
    sh = G.shake(k.t, 24 * imp)
    c.save()
    c.translate(540 + sh[0], 1060 + sh[1])
    c.rotate(6 * math.sin(lt * 1.2))
    z = lerp(1.25, 1.0, ease_out(prog(lt, 0, 0.6))) * (1 + 0.08 * imp)
    c.scale(z, z)
    c.translate(-540, -1060)
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#0a1440", shader=rad(540, 1060, 1300, ["#2a4ad0", "#0a1440", "#040818"], [0, .5, 1])))
    c.save()
    c.translate(540, 1060)
    c.rotate(k.t * 15)
    for i in range(18):
        p = skia.Path()
        a0, a1 = math.radians(i * 20), math.radians(i * 20 + 8)
        p.moveTo(0, 0)
        p.lineTo(math.cos(a0) * 1800, math.sin(a0) * 1800)
        p.lineTo(math.cos(a1) * 1800, math.sin(a1) * 1800)
        p.close()
        c.drawPath(p, P("#ffd84a", alpha=0.1))
    c.restore()
    dk = prog(lt, hit - 0.35, hit)
    if dk > 0:
        trophy(c, 540, lerp(-500, 1080, ease_in_out(dk)), 1.1 + 0.03 * math.sin(lt * 3))
    c.restore()
    if imp > 0:
        c.drawRect(RECT(0, 0, W, H), P("#ffffff", alpha=0.5 * imp ** 2))
    R.RES.glow_gold, R.RES.glow_warm = R.RES.g_lime, R.RES.g_mag
    use("vio")
    R.burst(c, 540, 1000, lt - hit, dur=1.0, n=50, radius=520, seed=12, intensity=0.9)
    G.tag(c, "RÉCORD DE PREVENTAS", 540, 1560, prog(lt, T(7) - 0.1, T(7) + 0.2), bg="#ffcf3a", fg="#14061f", size=48, rot=-3)
    G.tag(c, "PLAYSTATION STORE", 540, 1680, prog(lt, T(13) - 0.1, T(13) + 0.2), bg="#2a4ad0", size=40, rot=2)


# ----------------------------------------------------------------------------
# 4. la ciudad de noche: todos compran desde el teléfono
# ----------------------------------------------------------------------------


def window_room(c, x0, y0, w, h, t, i):
    rrect(c, x0, y0, x0 + w, y0 + h, 8, P("#ffb86a", shader=lin(0, y0, 0, y0 + h, ["#ffcf8a", "#e88a4a"])))
    r = rng(i + 3)
    style = i % 3
    bx = x0 + w * 0.5
    by = y0 + h
    if style == 0:  # sofá
        rrect(c, x0 + 20, by - 70, x0 + w - 20, by - 10, 14, P("#6a2a4a"))
    elif style == 1:  # cama
        rrect(c, x0 + 10, by - 50, x0 + w - 10, by, 10, P("#f4ecf8"))
    pc = ["#2a1a3a", "#3a1a2a", "#1a2a3a"][i % 3]
    oval(c, bx, by - 110, 34, 34, P(pc))
    rrect(c, bx - 46, by - 80, bx + 46, by - 10, 30, P(pc))
    glow(c, R.RES.g_vio, bx + 20, by - 90, 60, 0.6 + 0.3 * math.sin(t * 4 + i))
    rrect(c, bx + 10, by - 104, bx + 30, by - 72, 4, P("#bfe8ff"))
    c.drawRect(RECT(x0, y0, x0 + w, y0 + h), P("#000000", alpha=0.0))
    c.drawLine(x0 + w / 2, y0, x0 + w / 2, y0 + h, P("#2a1a3a", "stroke", 6))
    c.drawRect(RECT(x0, y0, x0 + w, y0 + h), P("#2a1a3a", "stroke", 8))
    del r


def notif(c, x, y, txt, k):
    if k <= 0:
        return
    a = clamp(k * 3) * (1 - clamp((k - 0.75) * 4))
    s = back_out(clamp(k * 2.5), 2)
    f = F(R.RES.mb, 26)
    w = f.measureText(txt) + 90
    c.save()
    c.translate(x, y - 60 * k)
    c.scale(s, s)
    rrect(c, -w / 2, -34, w / 2, 34, 18, P("#ffffff", alpha=0.95 * a))
    oval(c, -w / 2 + 34, 0, 18, 18, P("#2fbf71", alpha=a))
    ck = skia.Path()
    ck.moveTo(-w / 2 + 25, 0)
    ck.lineTo(-w / 2 + 32, 8)
    ck.lineTo(-w / 2 + 44, -8)
    c.drawPath(ck, P("#ffffff", "stroke", 4, alpha=a))
    c.drawString(txt, -w / 2 + 64, 9, f, P("#14061f", alpha=a))
    c.restore()


def scene4(c, k):
    lt, T = k.lt, k.w
    camx = lerp(0, 1500, ease_in_out(prog(lt, 0, k.D)))
    camy = 60 * math.sin(lt * 1.2)
    z = 1.05 + 0.08 * math.sin(lt * 0.9)
    c.drawRect(RECT(0, 0, W, H), P("#0a0820", shader=lin(0, 0, 0, H, ["#05040f", "#1a1040", "#3a1a5a"])))
    oval(c, 820, 300, 70, 70, P("#f4f0ff"))
    glow(c, R.RES.glow_white, 820, 300, 220, 0.4)
    c.save()
    c.translate(540, 1000 + camy)
    c.scale(z, z)
    c.translate(-540, -1000)
    c.save()
    c.translate(-camx * 0.3, 0)
    r = rng(5)
    for i in range(24):  # skyline lejano
        x0 = -200 + i * 110
        h = 300 + r.random() * 500
        c.drawRect(RECT(x0, 1300 - h, x0 + 100, 1900), P("#1a1236"))
        for j in range(int(h / 50)):
            if r.random() < 0.4:
                c.drawRect(RECT(x0 + 20, 1320 - h + j * 50, x0 + 40, 1335 - h + j * 50), P("#ffcf6a", alpha=0.6))
    c.restore()
    c.save()
    c.translate(-camx, 0)
    for b in range(6):  # edificios cercanos con ventanas
        bx = -100 + b * 560
        c.drawRect(RECT(bx, 400, bx + 520, 2100), P("#2a1a4a", shader=lin(bx, 0, bx + 520, 0, ["#3a2a5a", "#241640"])))
        for row in range(4):
            for col in range(2):
                i = b * 8 + row * 2 + col
                wx, wy = bx + 40 + col * 240, 520 + row * 330
                window_room(c, wx, wy, 200, 250, k.t, i)
    c.restore()
    c.restore()
    # notificaciones de compra
    for i in range(14):
        t0 = 0.3 + i * 0.3
        kk = (lt - t0) / 1.4
        if 0 < kk < 1:
            notif(c, 220 + (i * 337) % 640, 760 + (i * 211) % 800, "Compra realizada", kk)
    G.tag(c, "0 FILAS", 540, 640, prog(lt, T(5) - 0.1, T(5) + 0.2) * (1 - prog(lt, T(10), T(11))), bg="#ff3d7f", size=52, rot=-4)
    ck = prog(lt, T(13) - 0.1, T(13) + 0.2)
    G.tag(c, "3:07 AM", 540, 640, ck, bg="#14061f", size=60, rot=3)


# ----------------------------------------------------------------------------
# 5-7. el giro: un personaje en Vice City saca el teléfono → Velto
# ----------------------------------------------------------------------------
PX, PY, PS = 540, 2010, 1.55  # cintura del personaje en el mundo, escala
PH = 0.4


def vice_street(c, t):
    c.drawRect(RECT(-800, -800, W + 800, 1500), P("#ff8a62", shader=lin(0, 0, 0, 1400, ["#5a2a8a", "#ff5a8a", "#ffb36a", "#ffd8a0"], [0, .35, .75, 1])))
    glow(c, R.RES.glow_warm, 760, 1100, 600, 0.6, skia.BlendMode.kScreen)
    oval(c, 760, 1120, 120, 120, P("#ffe9b0"))
    cols = ["#ffb3c9", "#bdf2dc", "#ffe28a", "#c9d6ff", "#ff9ac0"]
    for i in range(7):
        x0 = -500 + i * 330
        h = 520 + 160 * math.sin(i * 1.7)
        c.drawRect(RECT(x0, 1400 - h, x0 + 300, 1400), P(cols[i % 5]))
        c.drawRect(RECT(x0, 1400 - h, x0 + 300, 1400 - h + 22), P("#ffffff", alpha=0.7))
        for rr in range(int(h / 90)):
            for cc in range(3):
                c.drawRect(RECT(x0 + 30 + cc * 90, 1400 - h + 50 + rr * 90, x0 + 90 + cc * 90, 1400 - h + 100 + rr * 90), P("#7fd6ff", alpha=0.9))
        if i % 2 == 0:  # letrero neón
            f = F(R.RES.mx, 40)
            txt = ["HOTEL", "OCEAN", "CAFÉ", "BAR"][(i // 2) % 4]
            w = f.measureText(txt)
            glow(c, R.RES.g_mag, x0 + 150, 1400 - h - 40, 160, 0.5 + 0.3 * math.sin(t * 5 + i))
            c.drawString(txt, x0 + 150 - w / 2, 1400 - h - 26, f, P("#ff6fb1"))
    for i in range(5):
        G.palm(c, -300 + i * 420, 1450, 700, t, lean=0.12 * (-1) ** i)
    c.drawRect(RECT(-800, 1400, W + 800, 1520), P("#d8c8b8"))
    c.drawRect(RECT(-800, 1520, W + 800, 2600), P("#4a4a5a", shader=lin(0, 1520, 0, 2200, ["#5a5a6a", "#2a2a36"])))
    for i in range(10):
        c.drawRect(RECT(-600 + i * 260, 1760, -480 + i * 260, 1775), P("#f2e9c8", alpha=0.7))
    cx = (t * 700) % 2600 - 800  # auto que pasa
    rrect(c, cx - 170, 1590, cx + 170, 1670, 30, P("#2fb8c8"))
    rrect(c, cx - 100, 1530, cx + 90, 1600, 30, P("#2fb8c8"))
    rrect(c, cx - 86, 1542, cx + 76, 1592, 14, P("#bfe8ff"))
    for dx in (-110, 110):
        oval(c, cx + dx, 1670, 38, 38, P("#1a1a1a"))


def mini_phone(c, hx, hy, k_lt, glow_a=0.0):
    scr = E4.app_screen(E4.screen_public(k_lt, 1.0))
    V.phone(c, hx + 70, hy - 60, 120, 230, scr, rot=8, glow_a=glow_a)


def phone_world(t):
    hx, hy = lerp(150, 70, 0.75), lerp(-300, -430, 0.75)
    bob = 6 * math.sin(t * 2 + PH)
    return PX + PS * (hx + 70), PY + bob + PS * (hy - 60)


def street_shot(c, k, lift, zoom, look_t):
    """Plano de la calle con el personaje. zoom 0..1 = la cámara entra a la pantalla del teléfono."""
    lt = k.lt
    fx, fy = phone_world(k.t)
    zbase = 1.0 + 0.05 * math.sin(lt * 1.1)
    zz = zbase * (1 + (5.6 - 1) * ease_in_out(zoom) ** 2)
    cx = lerp(540 + 60 * math.sin(lt * 0.7), fx, ease_in_out(zoom))
    cy = lerp(1300, fy, ease_in_out(zoom))
    c.save()
    c.translate(540, lerp(1060, 1080, zoom))
    c.rotate(lerp(2 * math.sin(lt * 0.8), 0, zoom))
    c.scale(zz, zz)
    c.translate(-cx, -cy)
    blur_layer(c, 5)
    vice_street(c, k.t)
    c.restore()
    B.fam_person(c, PX, PY, PS, k.t, "#c98a62", "#1a120a", "man", "#2fb8c8", PH,
                 lambda c2, hx, hy: mini_phone(c2, hx, hy, look_t, 0.0) if lift > 0.3 else None, lift)
    c.restore()


BIG = (540, 1120, 640, 1180)


def big_phone(c, k, lt5, T):
    cx, cy, w, h = BIG
    prodk = prog(lt5, T(8) - 0.3, T(8) + 0.6)

    def d(c2):
        E4.screen_public(lt5, max(prodk, 0.35))(c2)
        pk = prog(lt5, T(10) - 0.1, T(10) + 0.2)
        if pk > 0:  # resalta precios
            for i in range(6):
                col_, row = i % 2, i // 2
                x0, y0 = 22 + col_ * 246, 270 + row * 205
                rrect(c2, x0 + 6, y0 + 140, x0 + 120, y0 + 168, 10, P(LIME, "stroke", 3, alpha=pk * (0.6 + 0.4 * math.sin(k.t * 8))))
        for i in range(4):  # pedidos que llegan
            t0 = T(13) - 0.2 + i * 0.32
            u = lt5 - t0
            if u <= 0:
                continue
            y = 20 + min(1, ease_out(u / 0.3)) * (20 + i * 82)
            a = 1 - clamp((u - 2.2) / 0.3) if i < 3 else 1
            rrect(c2, 16, y, 504, y + 72, 16, P("#ffffff", alpha=0.97 * a))
            rrect(c2, 16, y, 504, y + 72, 16, P(LIME, "stroke", 3, alpha=a))
            oval(c2, 52, y + 36, 22, 22, P("#14061f", alpha=a))
            E5.cart_icon(c2, 52, y + 34, 12, LIME)
            name = ["María", "José", "Andrea", "Luis"][i]
            E4.txt(c2, f"Nuevo pedido · {name}", 86, y + 32, 20, "#14061f", R.RES.mx, a)
            E4.txt(c2, ["Q250.00", "Q275.00", "Q300.00", "Q240.00"][i], 86, y + 58, 17, "#7a3ae0", R.RES.mb, a)
    V.phone(c, cx, cy, w, h, E4.app_screen(d), rot=0, glow_a=0.6)


def scene5(c, k):  # "Tú no eres Rockstar… pero tu negocio también puede vender así."
    lt, T = k.lt, k.w
    lift = ease_in_out(prog(lt, T(8) - 0.4, T(9) + 0.1)) * 0.75
    dolly = ease_out(prog(lt, 0, 1.2))
    c.save()
    c.translate(540, 1100)
    c.scale(lerp(0.78, 1.0, dolly), lerp(0.78, 1.0, dolly))
    c.translate(-540, -1100)
    street_shot(c, k, lift / 0.75 * 0.75, 0.0, 0.0)
    c.restore()
    G.tag(c, "TÚ NO ERES ROCKSTAR", 540, 650, prog(lt, T(1) - 0.1, T(1) + 0.2) * (1 - prog(lt, T(4), T(4) + 0.2)), bg="#14061f", size=44, rot=-3)
    G.tag(c, "PERO…", 540, 650, prog(lt, T(4) - 0.1, T(4) + 0.2), bg=LIME, fg="#14061f", size=52, rot=3)


def scene6(c, k):  # dentro del teléfono: su página en Velto
    lt, T = k.lt, k.w
    zin = prog(lt, 0.0, 0.55)
    if zin < 1:
        street_shot(c, k, 0.75, zin, lt)
        if zin > 0.6:
            c.drawRect(RECT(0, 0, W, H), P("#0b0a10", alpha=(zin - 0.6) / 0.4))
        return
    u = lt - 0.55
    c.drawRect(RECT(-500, -500, W + 500, H + 500), P("#0b0a10"))
    blur_layer(c, 18)
    c.save()
    c.translate(540, 1080)
    c.scale(1.6, 1.6)
    c.translate(-540, -1300)
    vice_street(c, k.t)
    c.restore()
    c.restore()
    c.drawRect(RECT(0, 0, W, H), P("#0a0410", alpha=0.35))
    c.save()
    c.translate(540, 1120)
    c.rotate(3 * math.sin(lt * 1.1))
    s = lerp(1.25, 1.0, ease_out(clamp(u / 0.5))) * (1 + 0.02 * math.sin(lt * 2))
    c.scale(s, s)
    c.translate(-540, -1120)
    big_phone(c, k, lt, T)
    c.restore()
    for j, (txt, wi, x, y, rot) in enumerate((("CATÁLOGO", 8, 200, 640, -6), ("PRECIOS", 10, 880, 760, 6), ("PEDIDOS", 13, 190, 1640, -4))):
        G.tag(c, txt, x, y, prog(lt, T(wi) - 0.1, T(wi) + 0.2), bg=LIME, fg="#14061f", size=38, rot=rot)
    vk = prog(lt, T(4) - 0.1, T(4) + 0.2)
    if vk > 0:
        draw_img(c, R.RES.vlogo, 900, 600 + 10 * math.sin(k.t * 2), 120 * back_out(clamp(vk)))


def scene7(c, k):  # CTA en la calle: Comenta VENTA
    lt, T = k.lt, k.w
    zout = 1 - ease_out(prog(lt, 0.0, 0.6))
    c.save()
    c.translate(540, 1060)
    c.rotate(2 * math.sin(lt * 0.9))
    c.translate(-540, -1060)
    street_shot(c, k, 0.75, zout * 0.85, lt + 8)
    c.restore()
    draw_img(c, R.RES.vlogo, 110, 150, 80)
    bk = ease_out(prog(lt, T(0) - 0.1, T(0) + 0.25))
    if bk > 0:
        c.save()
        c.translate(540, 600)
        c.scale(bk, bk)
        rrect(c, -300, -48, 300, 48, 48, P("#ffffff"))
        oval(c, -250, 0, 28, 28, P(VIO))
        typed = "VENTA"[: int(5 * prog(lt, T(1) - 0.25, T(1) + 0.15))]
        if typed:
            c.drawString(typed, -205, 16, F(R.RES.mx, 44), P("#14061f"))
        else:
            c.drawString("Comenta...", -205, 12, F(R.RES.ms, 30), P("#8a7aa8"))
        c.restore()
    r = rng(29)
    for i in range(16):
        side = -1 if i % 2 == 0 else 1
        x = 540 + side * (390 + r.random() * 70)
        u = (lt - (T(1) + i * 0.16)) / 2.4
        if u <= 0 or u >= 1:
            continue
        yy = lerp(1600, 700, u)
        a = math.sin(math.pi * u)
        tx = ["VENTA", "¡VENTA!", "VENTA!!", "VENTA"][i % 4]
        f = F(R.RES.mx, 26)
        w = f.measureText(tx) + 66
        c.save()
        c.translate(x + 16 * math.sin(lt * 2 + i), yy)
        rrect(c, -w / 2, -28, w / 2, 28, 28, P("#2c2540", alpha=0.92 * a))
        oval(c, -w / 2 + 28, 0, 15, 15, P([VIO2, LIME, "#ff6fb1", "#5ad1ff"][i % 4], alpha=a))
        c.drawString(tx, -w / 2 + 52, 9, f, P("#ffffff", alpha=a))
        c.restore()
    G.tag(c, "GUÍA GRATIS", 540, 1400, prog(lt, T(6) - 0.1, T(6) + 0.2), bg=LIME, fg="#14061f", size=50, rot=-3)
    G.tag(c, "TU PÁGINA EN 5 MIN", 540, 1510, prog(lt, T(12) - 0.1, T(12) + 0.2), bg="#14061f", size=44, rot=2)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7]
WHIP = {1, 2, 3}


def render_frame(c, t, vo, phr, total):
    global VO
    VO = vo
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(R.hexc("#000000"))
    k = R.Ctx(vo, si, t)
    lt = k.lt
    blur, dx = 0.0, 0.0
    if si in WHIP and lt < 0.22:
        q = 1 - ease_out(lt / 0.22)
        blur, dx = 70 * q, 260 * q
    if si == 4 and lt < 0.25:  # disco rayado: frenazo con temblor
        q = 1 - lt / 0.25
        blur, dx = 30 * q, 0
    if blur > 0.3:
        blur_layer(c, blur, blur * (0.08 if si in WHIP else 1))
    c.save()
    c.translate(dx, 0)
    if si == 4 and lt < 0.25:
        c.translate(*G.shake(k.t, 18 * (1 - lt / 0.25)))
    SCENES[si](c, k)
    c.restore()
    if blur > 0.3:
        c.restore()
    R.vignette(c, 0.4)
    fade_out = clamp((total - t) / 0.3)
    if fade_out < 1:
        c.drawRect(RECT(0, 0, W, H), P("#000000", alpha=1 - fade_out))
    R.draw_subs(c, t, phr)
    R.draw_watermark(c)


def install():
    V.install()
    R.SCENES = SCENES
    R.FADE_IN = 0.0
    R.render_frame = render_frame
    R.draw_subs = S.draw_subs
    R.draw_watermark = S.draw_watermark


if __name__ == "__main__":
    install()
    R.main()
