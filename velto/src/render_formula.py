"""Velto — "La fórmula de los mil millones": GTA 6 en 3 pasos (Gancho, Fecha, Botón) → Velto Studio + Claude.

Estilo maqueta isométrica 3D de Vice City al atardecer (velto/src/iso.py), contadores de rodillos,
objetos héroe por dato, palabras gigantes y cámara orbitando. Voz: David (la de los videos de GTA 6).
Uso:
  VIDEO_BUILD=$PWD/velto/build_formula VO_TRIM=0.12 VO_GAP=0.15 VO_TAIL=1.2 \
    python3 velto/src/render_formula.py --out velto/build_formula/video_mudo.mp4
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
import render_gta2 as G2  # noqa: E402
import render_ep4 as E4  # noqa: E402
import iso  # noqa: E402
from render_velto import (R, P, RECT, VIO, VIO2, LIME, F, back_out, clamp, ease_in_out, ease_out, glow, lerp,  # noqa: E402
                          lin, rad, oval, prog, rrect, smooth, text_center, rng, use, W, H, draw_img)

IsoCam = iso.IsoCam
VO = None

# puntos héroe del mundo
HOTEL = None
SCREEN = (73.0, 26.0)
CAL = (73.0, 48.0)
BUTTON = (73.0, 66.0)
SHOP = (18.0, iso.ROADS_X[0] + 3.2)


def setup_hotel():
    global HOTEL
    b = min(iso.CITY, key=lambda q: (q["x"] + q["w"] / 2 - 40) ** 2 + (q["y"] + q["d"] / 2 - 38) ** 2)
    b["h"] = 27.0
    b["col"] = "#ffb3c9"
    b["neon"] = "#ff3d9a"
    HOTEL = (b["x"] + b["w"] / 2, b["y"] + b["d"] / 2, b["h"] + 2.5)


setup_hotel()


def lerp_cam(a, b, u):
    return IsoCam(*[lerp(x, y, u) for x, y in zip(a, b)])


def warm(c, a=0.25):
    c.drawRect(RECT(0, 0, W, H), P("#ff9a5a", blend=skia.BlendMode.kSoftLight, alpha=a))


def scene_city(c, cam, t, extras=None, dim=0.0, night=0.0, sigma=9.0):
    def draw(cc):
        iso.sky(cc, t, night)
        iso.city(cc, cam, t, extras, dim)
    iso.tilt_shift(c, draw, sigma=sigma)
    warm(c, 0.22 * (1 - night))


# ----------------------------------------------------------------------------
# piezas gráficas
# ----------------------------------------------------------------------------


def odometer(c, x, y, value, size, k=1.0, digits=8, col="#ffffff"):
    """Contador de rodillos con separadores de miles."""
    if k <= 0:
        return
    s = back_out(clamp(k), 1.6)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    f = F(R.RES.mx, size)
    cw, ch = size * 0.78, size * 1.25
    n_sep = (digits - 1) // 3
    total = digits * cw + n_sep * size * 0.28
    xx = -total / 2
    v = max(0.0, value)
    for i in range(digits):
        p = digits - 1 - i
        place = 10 ** p
        d = int(v // place) % 10
        lower = (v % place) / place if p > 0 else (v % 1)
        roll = clamp((lower - 0.9) * 10) if p > 0 else 0.0
        rrect(c, xx + 3, -ch / 2, xx + cw - 3, ch / 2, size * 0.14, P("#14061f", shader=lin(0, -ch / 2, 0, ch / 2, ["#2a1440", "#0a0410", "#2a1440"])))
        c.save()
        c.clipRect(RECT(xx, -ch / 2, xx + cw, ch / 2))
        for j, dd in enumerate((d, (d + 1) % 10)):
            ty = size * 0.36 - roll * ch + j * ch
            tw = f.measureText(str(dd))
            c.drawString(str(dd), xx + cw / 2 - tw / 2, ty, f, P(col))
        c.restore()
        c.drawLine(xx + 3, 0, xx + cw - 3, 0, P("#000000", "stroke", 2, alpha=0.5))
        xx += cw
        if p > 0 and p % 3 == 0:
            c.drawString(",", xx + size * 0.02, size * 0.42, f, P(col))
            xx += size * 0.28
    rrect(c, -total / 2 - 10, -ch / 2 - 10, total / 2 + 10, ch / 2 + 10, size * 0.2, P("#ff3d9a", "stroke", 4))
    glow(c, R.RES.g_mag, 0, 0, total * 0.7, 0.35, skia.BlendMode.kScreen)
    c.restore()


def big_word(c, txt, y, k, shader=None, size=170, col="#ffffff"):
    if k <= 0:
        return
    out = 1.0
    s = back_out(clamp(k), 2.2)
    f = F(R.RES.mx, size)
    w = f.measureText(txt)
    if w > 980:
        size = size * 980 / w
        f = F(R.RES.mx, size)
        w = f.measureText(txt)
    c.save()
    c.translate(540, y)
    c.scale(s, s)
    c.skew(-0.08, 0)
    c.drawString(txt, -w / 2 + 8, 10, f, P("#000000", alpha=0.5 * out, blur=10))
    sp = P("#14061f", "stroke", size * 0.12)
    sp.setStrokeJoin(skia.Paint.kRound_Join)
    c.drawString(txt, -w / 2, 0, f, sp)
    c.drawString(txt, -w / 2, 0, f, P(col, shader=shader))
    c.restore()


def chips(c, lit, k=1.0, y=640):
    if k <= 0:
        return
    for i in range(3):
        kk = clamp(k * 3 - i * 0.6)
        if kk <= 0:
            continue
        s = back_out(kk, 2)
        x = 540 + (i - 1) * 150
        on = i < lit
        c.save()
        c.translate(x, y)
        c.scale(s, s)
        if on:
            glow(c, R.RES.g_lime, 0, 0, 120, 0.55)
        rrect(c, -52, -52, 52, 52, 18, P("#14061f" if not on else LIME))
        rrect(c, -52, -52, 52, 52, 18, P(LIME if not on else "#ffffff", "stroke", 5))
        text_center(c, str(i + 1), 0, 26, F(R.RES.mx, 72), P(LIME if not on else "#14061f"))
        c.restore()


def giant_screen(c, cam, t, val, k_count, play_k=1.0):
    x, y = SCREEN
    sx, sy = cam.p(x, y, 0)
    s = cam.S / 30
    c.save()
    c.translate(sx, sy)
    c.scale(s, s)
    for dx in (-200, 200):
        c.drawRect(RECT(dx - 10, -300, dx + 10, 0), P("#3a2a4a"))
    rrect(c, -330, -720, 330, -290, 22, P("#14061f"))
    rrect(c, -312, -702, 312, -308, 14, P("#ff3d9a", shader=lin(0, -702, 0, -308, ["#ff8a4a", "#c8407a", "#3a1a6a"])))
    pulse = 1 + 0.06 * math.sin(t * 5)
    oval(c, 0, -505, 78 * pulse, 78 * pulse, P("#ffffff", alpha=0.95 * play_k))
    tri = skia.Path()
    tri.moveTo(-22, -540)
    tri.lineTo(40, -505)
    tri.lineTo(-22, -470)
    tri.close()
    c.drawPath(tri, P("#c8407a", alpha=play_k))
    glow(c, R.RES.g_mag, 0, -505, 420, 0.4, skia.BlendMode.kScreen)
    c.restore()
    if k_count > 0:
        odometer(c, sx, sy - 840 * s, val, 70 * max(0.8, s), k_count)


def calendar3d(c, cam, flip, t):
    x, y = CAL
    sx, sy = cam.p(x, y, 0)
    s = cam.S / 30
    c.save()
    c.translate(sx, sy - 470 * s)
    c.scale(s, s)
    glow(c, R.RES.soft_dark, 20, 260, 300, 0.4, skia.BlendMode.kSrcOver)
    rrect(c, -220, -250, 220, 250, 24, P("#fbf6ee"))
    rrect(c, -220, -250, 220, -120, 24, P("#ff3d7f"))
    c.drawRect(RECT(-220, -150, 220, -120), P("#ff3d7f"))
    for dx in (-120, -40, 40, 120):
        oval(c, dx, -250, 12, 22, P("#3a2a4a"))
    a = 0 if flip < 0.5 else 1
    month, day = (("JUNIO", "25"), ("NOVIEMBRE", "19"))[a]
    sq = abs(math.cos(math.pi * flip)) if 0 < flip < 1 else 1.0
    c.save()
    c.scale(1, max(0.05, sq))
    text_center(c, month, 0, -168, F(R.RES.mx, 50), P("#ffffff"))
    text_center(c, day, 0, 140, F(R.RES.mx, 260), P("#1a1a1a"))
    c.restore()
    if a == 1:
        tg = "LANZAMIENTO"
        text_center(c, tg, 0, 220, F(R.RES.mb, 30), P("#c8407a"))
    else:
        text_center(c, "ABRE LA PREVENTA", 0, 220, F(R.RES.mb, 30), P("#7a3ae0"))
    c.restore()


def shop_sign(c, cam, k):
    if k <= 0:
        return
    sx, sy = cam.p(SHOP[0] + 6, iso.ROADS_X[0] + 6.5, 9)
    s = cam.S / 26 * back_out(clamp(k), 1.6)
    c.save()
    c.translate(sx, sy)
    c.scale(s, s)
    rrect(c, -210, -60, 210, 60, 18, P("#14061f"))
    rrect(c, -210, -60, 210, 60, 18, P("#ff3d9a", "stroke", 6))
    glow(c, R.RES.g_mag, 0, 0, 260, 0.5, skia.BlendMode.kScreen)
    text_center(c, "PREVENTA", 0, 22, F(R.RES.mx, 62), P("#ffffff"))
    c.restore()


def crowd(cam, lt, t0, n=18):
    out = []
    for i in range(n):
        tj = t0 + i * 0.12
        u = clamp((lt - tj) / 0.5)
        if u <= 0:
            continue
        x = SHOP[0] + 4 - i * 1.4
        y = iso.ROADS_X[0] + 3.4
        xx = lerp(x - 12, x, ease_out(u))
        col = ["#ff6fa8", "#2ff0ff", "#ffe04a", "#ffffff", "#7a3ae0", "#ff8a4a"][i % 6]
        out.append((xx, y, lambda c, cam, xx=xx, y=y, col=col, i=i: iso.person(c, cam, xx, y, col, t0 + i, i, 1.0 - u * 0.8)))
    return out


def button3d(c, cam, press, t, ring=0.0):
    x, y = BUTTON
    sx, sy = cam.p(x, y, 0)
    s = cam.S / 30
    c.save()
    c.translate(sx, sy)
    c.scale(s, s)
    oval(c, 0, 0, 260, 110, P("#000000", alpha=0.3, blur=10))
    c.drawRect(RECT(-240, -120, 240, 0), P("#3a2a4a"))
    oval(c, 0, 0, 240, 100, P("#2a1a3a"))
    oval(c, 0, -120, 240, 100, P("#4a3a5a"))
    dz = 60 - 45 * press
    c.drawRect(RECT(-190, -120 - dz, 190, -120), P(LIME, shader=lin(-190, 0, 190, 0, ["#7fb80a", "#d4ff4a", "#7fb80a"])))
    oval(c, 0, -120, 190, 78, P("#7fb80a"))
    oval(c, 0, -120 - dz, 190, 78, P(LIME, shader=rad(-40, -150 - dz, 220, ["#eaff9a", LIME])))
    c.save()
    c.scale(1, 0.42)
    text_center(c, "COMPRAR", 0, (-120 - dz) / 0.42 + 30, F(R.RES.mx, 74), P("#14061f"))
    c.restore()
    if 0 < ring < 1:
        oval(c, 0, -120, 190 + 400 * ring, (78 + 170 * ring), P(LIME, "stroke", 14 * (1 - ring), alpha=1 - ring))
    c.restore()


def box_tower(c, cam, n, t):
    bx, by = BUTTON[0] - 1.5, BUTTON[1] + 6.0
    for i in range(int(n)):
        col = ["#ff3d9a", "#ffb37a", "#7a3ae0", "#2ff0ff"][i % 4]
        iso.box(c, cam, bx - 1.6 + 0.3 * math.sin(i * 1.3), by - 1.0, 3.2, 2.0, i * 0.9, 0.85, col)
    return (bx, by, int(n) * 0.9)


def medal(c, x, y, s, k):
    if k <= 0:
        return
    sc = back_out(clamp(k), 2) * s
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    for sd in (-1, 1):
        rb = skia.Path()
        rb.moveTo(sd * 10, -40)
        rb.lineTo(sd * 50, -150)
        rb.lineTo(sd * 20, -150)
        rb.lineTo(sd * -10, -40)
        rb.close()
        c.drawPath(rb, P("#ff3d9a" if sd < 0 else "#2ff0ff"))
    oval(c, 0, 0, 66, 66, P("#ffc23a", shader=rad(-20, -20, 90, ["#ffe27a", "#c8901a"])))
    oval(c, 0, 0, 50, 50, P("#a8740a", "stroke", 5))
    text_center(c, "RÉCORD", 0, 10, F(R.RES.mx, 22), P("#5a3a0a"))
    c.restore()


# ----------------------------------------------------------------------------
# escenas
# ----------------------------------------------------------------------------
CAM_WIDE = (40, 40, 14, 55, 0.47)


def scene1(c, k):  # gancho: contador sobre la azotea del hotel
    lt, T = k.lt, k.w
    u = ease_in_out(prog(lt, 0.3, k.D))
    hx, hy, hz = HOTEL
    a = (hx, hy, 70, 25, 0.42)
    b = (lerp(hx, 40, 0.5), lerp(hy, 40, 0.5), 17, 70, 0.5)
    cam = lerp_cam(a, b, u)
    cam.cz = lerp(hz, 6, u)
    cam.py = lerp(1250, 1150, u)
    scene_city(c, cam, k.t, sigma=lerp(4, 9, u))
    sx, sy = cam.p(hx, hy, hz)
    val = 11_000_000 * ease_in_out(prog(lt, 0.2, T(12) + 0.3))
    odometer(c, sx, sy - 70 * cam.S / 25, val, 64 * clamp(cam.S / 40, 0.7, 1.4), prog(lt, 0.0, 0.3))
    big_word(c, "GTA 6", 1480, prog(lt, T(0) - 0.1, T(1) + 0.2), shader=G.sunset_text_shader(1360, 1480), size=200)
    G.tag(c, "COPIAS · ESTIMACIÓN SENSOR TOWER", 540, 1580, prog(lt, T(14) - 0.2, T(14) + 0.1), bg="#14061f", size=30, rot=-2)


def scene2(c, k):  # no fue suerte: tres pasos
    lt, T = k.lt, k.w
    u = ease_in_out(prog(lt, 0, k.D))
    cam = IsoCam(40, 40, lerp(17, 14, u), lerp(70, 130, u), 0.47, py=1180)
    scene_city(c, cam, k.t)
    big_word(c, "NO FUE SUERTE.", 1500, prog(lt, T(0) - 0.1, T(0) + 0.2) * (1 - prog(lt, T(5) - 0.2, T(5))), size=120)
    big_word(c, "3 PASOS", 1500, prog(lt, T(7) - 0.1, T(7) + 0.2), shader=lin(0, 1380, 0, 1500, ["#d4ff4a", "#7fdc5a"]), size=170)
    chips(c, 0, prog(lt, T(7) - 0.1, T(8) + 0.2))


def scene3(c, k):  # paso 1: gancho
    lt, T = k.lt, k.w
    u = ease_in_out(prog(lt, 0.0, 2.0))
    a = (40, 40, 14, 130, 0.47)
    b = (SCREEN[0] - 4, SCREEN[1], 34, lerp(80, 60, prog(lt, 2, k.D)), 0.42)
    cam = lerp_cam(a, b, u)
    cam.cz = lerp(0, 10, u)
    cam.py = lerp(1180, 1250, u)
    val = 90_421_491 * ease_out(prog(lt, T(13) - 0.2, T(16) + 0.3))
    ext = [(SCREEN[0], SCREEN[1], lambda cc, cm: giant_screen(cc, cm, k.t, val, prog(lt, T(13) - 0.3, T(13))))]
    scene_city(c, cam, k.t, extras=ext)
    chips(c, 1, 1.0 - prog(lt, T(13) - 0.5, T(13) - 0.2))
    big_word(c, "GANCHO.", 1500, prog(lt, T(3) - 0.1, T(3) + 0.2) * (1 - prog(lt, T(12), T(13) - 0.3)), shader=G.sunset_text_shader(1380, 1500))
    for i in range(3):
        medal(c, 300 + i * 240, lerp(-200, 1500, ease_out(prog(lt, T(20) - 0.2 + i * 0.12, T(20) + 0.3 + i * 0.12))), 1.1, prog(lt, T(20) - 0.2 + i * 0.12, T(20) + 0.1 + i * 0.12))


def scene4(c, k):  # paso 2: fecha
    lt, T = k.lt, k.w
    sw = T(14) - 0.3
    if lt < sw:
        u = ease_in_out(prog(lt, 0, 1.2))
        a = (SCREEN[0] - 4, SCREEN[1] + 6, 30, 50, 0.42)
        b = (CAL[0] - 3, CAL[1], 30, lerp(40, 25, prog(lt, 1.2, sw)), 0.4)
        cam = lerp_cam(a, b, u)
        cam.cz = 9
        cam.py = 1250
        flip = prog(lt, T(9) - 0.2, T(13))
        ext = [(CAL[0], CAL[1], lambda cc, cm: calendar3d(cc, cm, flip, k.t))]
        scene_city(c, cam, k.t, extras=ext)
    else:
        u = ease_in_out(prog(lt, sw, sw + 0.8))
        a = (CAL[0] - 10, CAL[1] - 10, 28, 25, 0.42)
        b = (SHOP[0] - 4, iso.ROADS_X[0] + 3, 26, lerp(15, 5, prog(lt, sw + 0.8, k.D)), 0.45)
        cam = lerp_cam(a, b, u)
        cam.cz = 3
        cam.py = 1250
        ext = crowd(cam, lt, sw + 0.3)
        ext.append((SHOP[0] + 6, iso.ROADS_X[0] + 6.5, lambda cc, cm: shop_sign(cc, cm, prog(lt, sw + 0.2, sw + 0.6))))
        scene_city(c, cam, k.t, extras=ext)
        G.tag(c, "MILLONES APARTARON EL SUYO", 540, 1560, prog(lt, T(15) - 0.1, T(15) + 0.2), bg=LIME, fg="#14061f", size=38, rot=-2)
    chips(c, 2, 1.0)
    big_word(c, "FECHA.", 1500, prog(lt, T(3) - 0.1, T(3) + 0.2) * (1 - prog(lt, T(9), T(9) + 0.3)), shader=G.sunset_text_shader(1380, 1500))


def scene5(c, k):  # paso 3: botón
    lt, T = k.lt, k.w
    hit = T(4) - 0.05
    press = clamp(1 - abs(lt - hit - 0.1) / 0.25) if lt > hit - 0.15 else 0
    n = 22 * ease_in_out(prog(lt, T(7), T(19)))
    top_z = n * 0.9
    u = ease_in_out(prog(lt, 0, 1.0))
    a = (CAL[0] - 3, CAL[1], 30, 25, 0.4)
    b = (BUTTON[0] - 2, BUTTON[1] + 3, lerp(32, 16, ease_in_out(prog(lt, T(7), T(19)))), lerp(40, 70, prog(lt, 1, k.D)), 0.42)
    cam = lerp_cam(a, b, u)
    cam.cz = lerp(2, top_z * 0.55, ease_in_out(prog(lt, T(7), T(19))))
    cam.py = 1150
    shake = G.shake(k.t, 14 * press)
    cam.px += shake[0]
    cam.py += shake[1]
    ext = [(BUTTON[0], BUTTON[1], lambda cc, cm: button3d(cc, cm, press, k.t, prog(lt, hit, hit + 0.6))),
           (BUTTON[0] - 1.5, BUTTON[1] + 6.0, lambda cc, cm: box_tower(cc, cm, n, k.t))]
    scene_city(c, cam, k.t, extras=ext)
    tk = prog(lt, T(15) - 0.2, T(15) + 0.2)
    if tk > 0:
        sx, sy = cam.p(BUTTON[0] - 1.5, BUTTON[1] + 6.0, top_z + 1.0)
        G2.trophy(c, sx, lerp(sy - 900, sy - 180 * cam.S / 30, ease_out(tk)), 0.55 * cam.S / 20)
        use("vio")
        R.burst(c, sx, sy - 200, lt - T(15) - 0.1, dur=1.0, n=40, radius=380, seed=7, intensity=0.8)
    chips(c, 3, 1.0)
    big_word(c, "BOTÓN.", 1500, prog(lt, T(4) - 0.1, T(4) + 0.2) * (1 - prog(lt, T(14), T(14) + 0.3)), shader=lin(0, 1380, 0, 1500, ["#d4ff4a", "#7fdc5a"]))
    G.tag(c, "#1 EN PREVENTAS · PLAYSTATION STORE", 540, 1560, prog(lt, T(15), T(15) + 0.3), bg="#2a4ad0", size=32, rot=-2)


def scene6(c, k):  # gancho, fecha, botón (cortes secos) → así se convierten vistas en ventas
    lt, T = k.lt, k.w
    cuts = [T(0) - 0.1, T(1) - 0.1, T(2) - 0.1, T(3) - 0.15]
    words = [("GANCHO.", G.sunset_text_shader(1380, 1500)), ("FECHA.", G.sunset_text_shader(1380, 1500)),
             ("BOTÓN.", lin(0, 1380, 0, 1500, ["#d4ff4a", "#7fdc5a"]))]
    if lt < cuts[3]:
        i = 0 if lt < cuts[1] else (1 if lt < cuts[2] else 2)
        ll = lt - cuts[i] if lt >= cuts[0] else 0
        zoom = 1 + 0.15 * ll
        if i == 0:
            cam = IsoCam(SCREEN[0] - 3, SCREEN[1], 40 * zoom, 70, 0.4, py=1200, cz=12)
            ext = [(SCREEN[0], SCREEN[1], lambda cc, cm: giant_screen(cc, cm, k.t, 90_421_491, 0.0))]
        elif i == 1:
            cam = IsoCam(CAL[0] - 3, CAL[1], 40 * zoom, 25, 0.4, py=1200, cz=11)
            ext = [(CAL[0], CAL[1], lambda cc, cm: calendar3d(cc, cm, 1.0, k.t))]
        else:
            cam = IsoCam(BUTTON[0] - 2, BUTTON[1], 40 * zoom, 55, 0.4, py=1100, cz=3)
            ext = [(BUTTON[0], BUTTON[1], lambda cc, cm: button3d(cc, cm, 0.0, k.t))]
        scene_city(c, cam, k.t, extras=ext, sigma=12)
        if lt >= cuts[0]:
            big_word(c, words[i][0], 1500, clamp(ll / 0.15), shader=words[i][1], size=200)
        if ll < 0.08:
            c.drawRect(RECT(0, 0, W, H), P("#ffffff", alpha=0.4 * (1 - ll / 0.08)))
    else:
        u = ease_in_out(prog(lt, cuts[3], k.D))
        cam = IsoCam(40, 40, lerp(22, 15, u), lerp(20, 70, u), 0.47, py=1180)
        scene_city(c, cam, k.t)
        gray = 1 - prog(lt, T(6) - 0.2, T(8) + 0.2)
        if gray > 0:
            c.drawRect(RECT(0, 0, W, H), P("#808080", blend=skia.BlendMode.kSaturation, alpha=gray))
        big_word(c, "VISTAS → VENTAS", 1500, prog(lt, T(6) - 0.1, T(8) + 0.1), shader=lin(0, 1380, 0, 1500, ["#d4ff4a", "#7fdc5a"]), size=120)


# --- Velto Studio + Claude -----------------------------------------------------


def laptop(c, x, y, s, draw_screen):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    base = skia.Path()
    base.moveTo(-430, 0)
    base.lineTo(430, 0)
    base.lineTo(480, 60)
    base.lineTo(-480, 60)
    base.close()
    c.drawPath(base, P("#b8b4c8", shader=lin(0, 0, 0, 60, ["#d8d4e8", "#8a86a0"])))
    rrect(c, -400, -560, 400, 0, 26, P("#1a1624"))
    c.save()
    c.clipRect(RECT(-376, -536, 376, -20))
    c.drawRect(RECT(-376, -536, 376, -20), P("#f6f3fb"))
    draw_screen(c, -376, -536, 376, -20)
    c.restore()
    c.restore()


def chat_screen(lt, T):
    def d(c, x0, y0, x1, y1):
        c.drawRect(RECT(x0, y0, x1, y0 + 56), P("#ece6f6"))
        c.drawString("Claude · Velto Studio", x0 + 24, y0 + 38, F(R.RES.mb, 24), P("#3a2a4a"))
        msg = "Quiero un video estilo GTA para mi marca"
        n = int(len(msg) * prog(lt, T(14) - 0.3, T(18)))
        if n > 0:
            f = F(R.RES.ms, 24)
            w = min(f.measureText(msg[:n]) + 40, 640)
            rrect(c, x1 - 24 - w, y0 + 90, x1 - 24, y0 + 150, 26, P(VIO))
            c.drawString(msg[:n], x1 - 4 - w, y0 + 128, f, P("#ffffff"))
        rk = prog(lt, T(19) - 0.2, T(19) + 0.2)
        if rk > 0:
            rrect(c, x0 + 24, y0 + 180, x0 + 560, y0 + 330, 22, P("#ffffff"))
            rrect(c, x0 + 24, y0 + 180, x0 + 560, y0 + 330, 22, P("#d8d0e8", "stroke", 2))
            c.drawString("¡Listo! Creando tu video animado…", x0 + 48, y0 + 228, F(R.RES.ms, 24), P("#1a1a1a", alpha=rk))
            pk = prog(lt, T(22), T(30))
            rrect(c, x0 + 48, y0 + 260, x0 + 530, y0 + 284, 12, P("#ece6f6"))
            rrect(c, x0 + 48, y0 + 260, lerp(x0 + 48, x0 + 530, pk), y0 + 284, 12, P(LIME))
            c.drawString(f"{int(pk * 100)}%", x0 + 48, y0 + 318, F(R.RES.mb, 20), P("#7a3ae0"))
    return d


def mini_city(c, x, y, s, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.translate(-540, -1000)
    cam = IsoCam(40, 40, 12, 40 + t * 20, 0.47, py=1000)
    iso.sky(c, t)
    iso.city(c, cam, t)
    c.restore()


def sample_card(c, x, y, s, i, t):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -120, -200, 120, 200, 22, P("#14061f"))
    cols = [["#ff8a4a", "#c8407a"], ["#ffe28a", "#ff9a5a"], ["#7fd6ff", "#2a4ad0"], ["#c08aff", "#7a3ae0"]][i % 4]
    rrect(c, -110, -190, 110, 190, 16, P(cols[0], shader=lin(0, -190, 0, 190, cols)))
    if i % 4 == 0:
        V.perfume(c, 0, 0, 0.9)
    elif i % 4 == 1:
        V.sneaker(c, 0, 10, 0.9)
    elif i % 4 == 2:
        E4.hoodie(c, 0, 0, 0.8, "#ffffff")
    else:
        V.necklace(c, 0, 0, 0.9)
    oval(c, 0, 150, 26, 26, P("#ffffff", alpha=0.9))
    tri = skia.Path()
    tri.moveTo(-8, 138)
    tri.lineTo(14, 150)
    tri.lineTo(-8, 162)
    tri.close()
    c.drawPath(tri, P(VIO))
    c.restore()


def scene7(c, k):  # Velto Studio + Claude
    lt, T = k.lt, k.w
    V.neon_bg(c, k.t, top="#1a0830", bottom="#05020b", grid=0.08, waves=False)
    r = rng(3)
    for i in range(18):
        x, y = r.random() * W, r.random() * H
        oval(c, x, y, 40 + 60 * r.random(), 40 + 60 * r.random(), P(["#ff3d9a", "#7a3ae0", "#2ff0ff"][i % 3], alpha=0.12))
    # el video "anterior" se encoge dentro de un teléfono (este video es un gancho)
    if lt < T(9) - 0.2:
        sh = ease_in_out(prog(lt, 0.0, 1.0))
        c.save()
        s = lerp(1.0, 0.36, sh)
        c.translate(540, lerp(960, 1050, sh))
        c.rotate(lerp(0, -6, sh))
        c.scale(s, s)
        c.translate(-540, -960)
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(RECT(0, 0, W, H), 80 * sh, 80 * sh), True)
        cam = IsoCam(40, 40, 15, 70 + lt * 15, 0.47, py=1180)
        iso.sky(c, k.t)
        iso.city(c, cam, k.t)
        c.restore()
        rrect(c, 0, 0, W, H, 80 * sh, P("#ffffff", "stroke", 18 * sh))
        c.restore()
        G.tag(c, "ESTE VIDEO = UN GANCHO", 540, 1600, prog(lt, T(3), T(3) + 0.3), bg=LIME, fg="#14061f", size=40, rot=-3)
        return
    u = lt - (T(9) - 0.2)
    lk = ease_out(clamp(u / 0.6))
    c.save()
    c.translate(540, 1150)
    c.rotate(lerp(-6, 0, lk) + 1.5 * math.sin(lt))
    c.scale(lerp(0.6, 1.0, lk), lerp(0.6, 1.0, lk))
    c.translate(-540, -1150)
    fly = prog(lt, T(26) - 0.2, T(28) + 0.2)
    lap_x = lerp(540, 380, ease_in_out(fly))
    laptop(c, lap_x, 1300, 0.95, chat_screen(lt, T))
    if fly > 0:  # la maqueta sale volando de la laptop al teléfono
        fx = lerp(lap_x, 820, ease_in_out(fly))
        fy = lerp(1050, 1060, ease_in_out(fly)) - 200 * math.sin(math.pi * fly)
        if fly < 1:
            mini_city(c, fx, fy, lerp(0.15, 0.3, fly), k.t)

        def screen(c2, x0, y0, x1, y1):
            c2.save()
            c2.translate((x0 + x1) / 2, (y0 + y1) / 2)
            s2 = (x1 - x0) / W
            c2.scale(s2, s2)
            c2.translate(-540, -960)
            cam = IsoCam(40, 40, 15, 60 + k.t * 20, 0.47, py=1150)
            iso.sky(c2, k.t)
            iso.city(c2, cam, k.t)
            c2.restore()
        pk = ease_out(prog(lt, T(28) - 0.2, T(29) + 0.2))
        if pk > 0:
            V.phone(c, 820, lerp(1900, 1060, pk), 330, 640, screen, rot=6, glow_a=0.8)
    c.restore()
    draw_img(c, R.RES.vlogo, 110, 150, 80)
    G.tag(c, "VELTO STUDIO", 540, 620, prog(lt, T(12) - 0.1, T(12) + 0.2), bg=LIME, fg="#14061f", size=48, rot=-3)
    G.tag(c, "+ CLAUDE (IA)", 540, 720, prog(lt, T(25) - 0.1, T(25) + 0.2), bg="#ff3d9a", size=40, rot=2)
    ck = prog(lt, T(31) - 0.2, T(31) + 0.3)
    if ck > 0:  # carrusel de videos de ejemplo
        for i in range(5):
            a = (i - 2) + (lt * 0.6) % 1
            x = 540 + a * 260
            sc = 0.75 - 0.08 * abs(a)
            sample_card(c, x, 1650 - 20 * abs(a), sc * back_out(clamp(ck), 1.5), i, k.t)
    G.tag(c, "LISTOS PARA PUBLICAR", 540, 820, prog(lt, T(34) - 0.1, T(34) + 0.2), bg="#14061f", size=40, rot=-2)


def scene8(c, k):  # CTA: Comenta GTA
    lt, T = k.lt, k.w
    cam = IsoCam(40, 40, 16 + lt * 0.6, 100 + lt * 14, 0.47, py=1250)
    scene_city(c, cam, k.t, night=0.7, dim=0.25)
    draw_img(c, R.RES.vlogo, 110, 150, 80)
    big_word(c, "Comenta", 760, prog(lt, T(0) - 0.1, T(0) + 0.2), size=110)
    big_word(c, "GTA", 960, prog(lt, T(1) - 0.1, T(1) + 0.2), shader=G.sunset_text_shader(820, 960), size=280)
    bk = ease_out(prog(lt, T(1), T(1) + 0.3))
    if bk > 0:
        c.save()
        c.translate(540, 1170)
        c.scale(bk, bk)
        rrect(c, -300, -48, 300, 48, 48, P("#ffffff"))
        oval(c, -250, 0, 28, 28, P(VIO))
        typed = "GTA"[: int(3 * prog(lt, T(1), T(1) + 0.4))]
        c.drawString(typed or "Comenta...", -205, 16, F(R.RES.mx if typed else R.RES.ms, 44 if typed else 30), P("#14061f" if typed else "#8a7aa8"))
        c.restore()
    G.tag(c, "TE MANDAMOS EJEMPLOS Y PRECIOS", 540, 1330, prog(lt, T(5) - 0.1, T(5) + 0.2), bg=LIME, fg="#14061f", size=38, rot=-2)
    r = rng(29)
    for i in range(14):
        side = -1 if i % 2 == 0 else 1
        x = 540 + side * (390 + r.random() * 70)
        uu = (lt - (T(1) + i * 0.15)) / 2.4
        if uu <= 0 or uu >= 1:
            continue
        yy = lerp(1600, 700, uu)
        a = math.sin(math.pi * uu)
        tx = ["GTA", "¡GTA!", "GTA!!", "GTA"][i % 4]
        f = F(R.RES.mx, 26)
        w = f.measureText(tx) + 66
        c.save()
        c.translate(x + 16 * math.sin(lt * 2 + i), yy)
        rrect(c, -w / 2, -28, w / 2, 28, 28, P("#2c2540", alpha=0.92 * a))
        oval(c, -w / 2 + 28, 0, 15, 15, P([VIO2, LIME, "#ff6fb1", "#5ad1ff"][i % 4], alpha=a))
        c.drawString(tx, -w / 2 + 52, 9, f, P("#ffffff", alpha=a))
        c.restore()


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8]
WHIP = {1, 2, 3, 4, 6, 7}


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
    if blur > 0.3:
        p = skia.Paint()
        p.setImageFilter(skia.ImageFilters.Blur(blur, blur * 0.08, skia.TileMode.kClamp))
        c.saveLayer(None, p)
    c.save()
    c.translate(dx, 0)
    SCENES[si](c, k)
    c.restore()
    if blur > 0.3:
        c.restore()
    R.vignette(c, 0.4)
    fade = clamp(t / 0.25) * clamp((total - t) / 0.3)
    if fade < 1:
        c.drawRect(RECT(0, 0, W, H), P("#000000", alpha=1 - fade))
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
