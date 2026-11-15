"""Velto — GTA 6 "mil millones" en el estilo nuevo: Vice City con cámara 3D en perspectiva.

Mismo guion y voz aprobados (velto/guion_gta2.json, David). Escenas:
 1 vuelo bajando sobre Ocean Drive + lluvia de dinero y contador   2 globo con compras (11 millones)
 3 trofeo frente a la calle desenfocada                            4 calle al atardecer: deportivo rebasa, compras desde las ventanas
 5 la pareja original: ella saca el teléfono                       6 la cámara entra al teléfono: página en Velto
 7 la cámara sale: Comenta VENTA
Uso:
  VIDEO_BUILD=$PWD/velto/build_gta3 VO_TRIM=0.12 VO_GAP=0.15 VO_TAIL=1.2 \
    python3 velto/src/render_gta3.py --out velto/build_gta3/video_mudo.mp4
"""
import math
import os
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_velto as V  # noqa: E402
import render_sueno as S  # noqa: E402
import render_gta as G  # noqa: E402
import render_gta2 as G2  # noqa: E402
import render_ep4 as E4  # noqa: E402
import test_vice3d as T3  # noqa: E402
from render_velto import (R, P, RECT, VIO, VIO2, LIME, F, back_out, clamp, ease_in_out, ease_out, glow, lerp,  # noqa: E402
                          lin, oval, prog, rrect, smooth, rng, use, W, H, draw_img)

Cam = T3.Cam


def blur_layer(c, sx, sy=None):
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(max(sx, 0.01), max(sx if sy is None else sy, 0.01), skia.TileMode.kClamp))
    c.saveLayer(None, p)


# ----------------------------------------------------------------------------
# 1. vuelo sobre Ocean Drive + mil millones
# ----------------------------------------------------------------------------


def scene1(c, k):
    lt, T = k.lt, k.w
    u = ease_in_out(prog(lt, 0, 3.0))
    v = ease_in_out(prog(lt, 3.0, k.D + 0.3))
    cam = Cam(lerp(30, 1.5, u) - 2 * v, lerp(110, 5.0, u) - 2.5 * v, lerp(-160, 50, u) + 60 * v,
              yaw=lerp(-8, 3, u) + 4 * math.sin(lt * 0.9), pitch=lerp(-42, -4, u) + 3 * v)
    T3.world(c, cam, k.t)
    haze = clamp(1 - prog(lt, 0.0, 0.9))
    if haze > 0:  # entra entre nubes rosadas
        c.drawRect(RECT(0, 0, W, H), P("#ffd0e0", alpha=haze))
        G.clouds3d(c, 1.3 + 3 * haze, k.t)
    g = prog(lt, T(0) - 0.1, T(1) + 0.2)
    out = prog(lt, T(7) - 0.2, T(8))
    if g > 0 and out < 1:
        c.save()
        c.translate(540, 1050)
        c.scale(1 + 0.8 * out, 1 + 0.8 * out)
        c.saveLayerAlpha(None, int(255 * (1 - out)))
        G.pop_text(c, "GTA 6", 0, 0, 210, g, rot=-4, shader=G.sunset_text_shader(-150, 0))
        G.tag(c, "AÚN NO SALE", 0, 120, prog(lt, T(3) - 0.1, T(3) + 0.2), bg="#14061f", size=44, rot=3)
        c.restore()
        c.restore()
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
        G.pop_text(c, G2.money_text(n), 540 + sh[0], 1040 + sh[1], 112, mk, shader=lin(0, 960, 0, 1040, ["#d4ff4a", "#4fbf6a"]))
        G.pop_text(c, "DÓLARES", 540, 1160, 80, prog(lt, T(14) - 0.1, T(14) + 0.2))


# ----------------------------------------------------------------------------
# 3. récord: trofeo frente a la calle
# ----------------------------------------------------------------------------


def scene3(c, k):
    lt, T = k.lt, k.w
    hit = T(4) - 0.1
    imp = max(0, 1 - (lt - hit) / 0.35) if lt >= hit else 0
    sh = G.shake(k.t, 24 * imp)
    blur_layer(c, 12)
    cam = Cam(1.0 + lt * 0.6, 1.2, 70 + lt * 4, yaw=-25 + lt * 10, pitch=8)
    T3.world(c, cam, k.t)
    c.restore()
    c.drawRect(RECT(0, 0, W, H), P("#2a0a3a", alpha=0.35))
    c.save()
    c.translate(540 + sh[0], 1060 + sh[1])
    c.rotate(6 * math.sin(lt * 1.2))
    c.translate(-540, -1060)
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
        G2.trophy(c, 540, lerp(-500, 1080, ease_in_out(dk)), 1.1 + 0.03 * math.sin(lt * 3))
    c.restore()
    if imp > 0:
        c.drawRect(RECT(0, 0, W, H), P("#ffffff", alpha=0.5 * imp ** 2))
    use("vio")
    R.burst(c, 540, 1000, lt - hit, dur=1.0, n=50, radius=520, seed=12, intensity=0.9)
    G.tag(c, "RÉCORD DE PREVENTAS", 540, 1440, prog(lt, T(7) - 0.1, T(7) + 0.2), bg="#ffcf3a", fg="#14061f", size=48, rot=-3)
    G.tag(c, "PLAYSTATION STORE", 540, 1550, prog(lt, T(13) - 0.1, T(13) + 0.2),
          bg="#2a4ad0", size=40, rot=2)


# ----------------------------------------------------------------------------
# 4. la calle: un deportivo rebasa y la gente compra desde sus ventanas
# ----------------------------------------------------------------------------


def scene4(c, k):
    lt, T = k.lt, k.w
    cz = 150 + lt * 14
    cam = Cam(1.6 + 0.4 * math.sin(lt * 1.5), lerp(1.4, 6.0, ease_in_out(prog(lt, 1.6, k.D))), cz,
              yaw=lerp(2, -14, ease_in_out(prog(lt, 1.4, k.D))), pitch=lerp(-2, 4, ease_in_out(prog(lt, 1.6, k.D))))
    car_z = cz + lerp(2.0, 160, ease_in_out(prog(lt, 0.0, 1.8)) ** 1.6)
    T3.world(c, cam, k.t, car=(2.8, 0.0, car_z) if lt < 2.4 else None)
    if lt < 1.4:
        for i in range(24):  # velocidad
            y = (i * 97) % 1900
            x = (lt * 3000 + i * 300) % 1500 - 200
            c.drawLine(x, y, x + 220, y, P("#ffffff", "stroke", 2, alpha=0.18 * (1 - lt / 1.4)))
    # compras desde las ventanas (ancladas a los edificios en 3D)
    n = 0
    for b in T3.BLD:
        if b.get("off"):
            continue
        zm = b["z0"] - cam.z
        if not (8 < zm < 120):
            continue
        for j in range(2):
            p = cam.proj((-10.0, 4 + j * 6.5, b["z0"] + 4 + j * 6))
            if not p:
                continue
            t0 = 0.4 + ((b["i"] * 3 + j * 5) % 11) * 0.3
            kk = (lt - t0) / 1.3
            if 0 < kk < 1:
                G2.notif(c, clamp(p[0], 200, 880), p[1], "Compra realizada", kk)
                n += 1
    G.tag(c, "0 FILAS", 540, 640, prog(lt, T(5) - 0.1, T(5) + 0.2) * (1 - prog(lt, T(10), T(11))), bg="#ff3d7f", size=52, rot=-4)
    G.tag(c, "3:07 AM", 540, 640, prog(lt, T(13) - 0.1, T(13) + 0.2), bg="#14061f", size=60, rot=3)


# ----------------------------------------------------------------------------
# 5-7. la pareja (original) → teléfono → Velto → CTA
# ----------------------------------------------------------------------------
PH_X = 660  # mano con el teléfono (coordenadas del plano de la pareja)
SKIN_M, SKIN_F = "#c98a62", "#d9a07a"


def phone_y(k):
    return lerp(1500, 1170, ease_out(k))


def phone_in_hand(c, x, y, s, skin, k, lt5):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rotate(lerp(30, 0, ease_out(k)))
    V.phone(c, 0, 0, 100, 196, E4.app_screen(E4.screen_public(lt5, 1.0)), glow_a=0.5 * k)
    for i in range(4):
        rrect(c, -64, -40 + i * 24, -36, -20 + i * 24, 10, P(skin, shader=lin(-64, 0, -36, 0, [T3.shade(skin, 0.3), skin])))
    rrect(c, 36, 0, 62, 36, 12, P(skin))
    c.restore()


def couple_frame(c, k, lt_shot, phk, zoom=0.0, lt5=0.0, dolly=None):
    """Plano de la pareja con fondo 3D desenfocado. zoom 0..1: la cámara entra a la pantalla del teléfono."""
    t = k.t
    cam_bg = Cam(-2 + lt_shot * 0.8, 1.6, 140 + lt_shot * 2, yaw=-38 + lt_shot * 3, pitch=2)
    u = ease_in_out(prog(lt_shot, 0, 3.2)) if dolly is None else dolly
    z = lerp(0.9, 1.08, u)
    dx = lerp(-60, 40, u)
    py_ = phone_y(phk)
    sx = 540 + (PH_X - 540 + dx) * z
    sy = 1250 + (py_ - 1250) * z
    e = ease_in_out(zoom)
    Z = 1 + 4.6 * e ** 1.5
    c.save()
    c.translate(lerp(sx, 540, e), lerp(sy, 1120, e))
    c.scale(Z, Z)
    c.translate(-sx, -sy)
    blur_layer(c, 14)
    T3.world(c, cam_bg, t)
    c.restore()
    r = rng(9)
    for i in range(26):  # bokeh de neón
        x = r.random() * 1300 - 110 - lt_shot * 40
        y = 300 + r.random() * 1000
        rr_ = 30 + r.random() * 70
        col = T3.NEON[i % 4]
        oval(c, x, y, rr_, rr_, P(col, alpha=0.18))
        c.drawPath(skia.Path().addCircle(x, y, rr_), P(col, "stroke", 3, alpha=0.25))
    c.drawRect(RECT(-200, -200, W + 200, H + 200), P("#2a0a3a", alpha=0.18))
    c.save()
    c.translate(540, 1250)
    c.scale(z, z)
    c.translate(-540 + dx, -1250)
    T3.car_side(c, lerp(560, 520, u), 1500, 1.05, "#e8202a", t)
    T3.torso(c, 270, 1150, 1.0, SKIN_M, "#f4f1ea", shirt="#ff8aa8")
    T3.head(c, 270, 960, 1.05, SKIN_M, t, False, look=0.6, smile=0.4)
    T3.long_hair_back(c, 780, 900, 1.0, t)
    T3.torso(c, 780, 1100, 0.92, SKIN_F, "#ffffff", female=True)
    T3.head(c, 780, 920, 1.0, SKIN_F, t, True, look=-0.6 if phk < 0.5 else -0.2, smile=0.7, phone_glow=phk)
    phone_in_hand(c, PH_X, py_, 1.2, SKIN_F, phk, lt5)
    c.restore()
    c.drawRect(RECT(-200, -200, W + 200, H + 200), P("#ff9a5a", blend=skia.BlendMode.kSoftLight, alpha=0.3))
    c.restore()


def scene5(c, k):  # "Tú no eres Rockstar… pero tu negocio también puede vender así."
    lt, T = k.lt, k.w
    phk = prog(lt, T(8) - 0.4, T(9) + 0.1)
    couple_frame(c, k, lt, phk)
    G.tag(c, "TÚ NO ERES ROCKSTAR", 540, 650, prog(lt, T(1) - 0.1, T(1) + 0.2) * (1 - prog(lt, T(4), T(4) + 0.2)), bg="#14061f", size=44, rot=-3)
    G.tag(c, "PERO…", 540, 650, prog(lt, T(4) - 0.1, T(4) + 0.2), bg=LIME, fg="#14061f", size=52, rot=3)


def scene6(c, k):  # dentro del teléfono: su página en Velto
    lt, T = k.lt, k.w
    prev = G2.VO[4]
    lt_shot = k.t - prev["start"]
    zin = prog(lt, 0.0, 0.6)
    if zin < 1:
        couple_frame(c, k, lt_shot, 1.0, zoom=zin, lt5=lt)
        if zin > 0.7:
            c.drawRect(RECT(0, 0, W, H), P("#0b0a10", alpha=(zin - 0.7) / 0.3 * 0.6))
        return
    blur_layer(c, 18)
    T3.world(c, Cam(-2 + lt_shot * 0.8, 1.6, 140 + lt_shot * 2, yaw=-38 + lt_shot * 3, pitch=2), k.t)
    c.restore()
    c.drawRect(RECT(0, 0, W, H), P("#0a0410", alpha=0.4))
    u = lt - 0.6
    c.save()
    c.translate(540, 1120)
    c.rotate(3 * math.sin(lt * 1.1))
    s = lerp(1.15, 1.0, ease_out(clamp(u / 0.5))) * (1 + 0.02 * math.sin(lt * 2))
    c.scale(s, s)
    c.translate(-540, -1120)
    G2.big_phone(c, k, lt, T)
    c.restore()
    for txt, wi, x, y, rot in (("CATÁLOGO", 8, 200, 640, -6), ("PRECIOS", 10, 880, 760, 6), ("PEDIDOS", 13, 190, 1640, -4)):
        G.tag(c, txt, x, y, prog(lt, T(wi) - 0.1, T(wi) + 0.2), bg=LIME, fg="#14061f", size=38, rot=rot)
    vk = prog(lt, T(4) - 0.1, T(4) + 0.2)
    if vk > 0:
        draw_img(c, R.RES.vlogo, 900, 600 + 10 * math.sin(k.t * 2), 120 * back_out(clamp(vk)))


def scene7(c, k):  # la cámara sale del teléfono: Comenta VENTA
    lt, T = k.lt, k.w
    zout = 1 - ease_out(prog(lt, 0.0, 0.7))
    couple_frame(c, k, 3.2 + lt * 0.3, 1.0, zoom=zout * 0.9, lt5=lt + 8, dolly=1.0 - 0.3 * ease_in_out(prog(lt, 0.7, k.D)))
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


def scene2(c, k):
    G2.scene2(c, k)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7]


def install():
    G2.install()
    G2.SCENES[:] = SCENES
    R.SCENES = SCENES


if __name__ == "__main__":
    install()
    R.main()
