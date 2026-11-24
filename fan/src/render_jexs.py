"""Video de fan (no oficial): "¿Y si Jexs nunca hubiera existido?" — universo alterno chapín y gracioso.

Animación 2D: universo alterno con filtro VHS (2016), miniaturas de parodia con mala ortografía a propósito,
reproductor genérico (sin logos), personaje genérico (no es la cara de nadie) y regreso al universo real.
Voz: David (ElevenLabs). Uso:
  VIDEO_BUILD=$PWD/fan/build_jexs VO_TRIM=0.15 VO_GAP=0.25 VO_TAIL=1.5 \
    python3 fan/src/render_jexs.py --out fan/build_jexs/video_mudo.mp4
"""
import math
import os
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "velto", "src"))
sys.path.insert(0, os.path.join(REPO, "blanquis", "src"))
import render_velto as V  # noqa: E402
import render_sueno as S  # noqa: E402
import render_gta as G  # noqa: E402
import render_formula as FM  # noqa: E402
import render_blanquis as B  # noqa: E402
from render_velto import (R, P, RECT, VIO, LIME, F, back_out, clamp, ease_in_out, ease_out, glow, lerp,  # noqa: E402
                          lin, rad, oval, prog, rrect, smooth, text_center, rng, use, W, H)

ALT = {0, 1, 2, 3, 4}  # escenas del universo alterno (con VHS); la 0 cambia a mitad
SKIN, HAIR, SHIRT = "#d9a07a", "#1a120a", "#2f6bff"


# ----------------------------------------------------------------------------
# efectos
# ----------------------------------------------------------------------------


def vhs(c, t, a=1.0):
    if a <= 0:
        return
    c.drawRect(RECT(0, 0, W, H), P("#808080", blend=skia.BlendMode.kSaturation, alpha=0.55 * a))
    c.drawRect(RECT(0, 0, W, H), P("#3a8a7a", blend=skia.BlendMode.kSoftLight, alpha=0.35 * a))
    for y in range(0, H, 6):
        c.drawLine(0, y, W, y, P("#000000", "stroke", 2, alpha=0.12 * a))
    r = rng(int(t * 30) % 997)
    for i in range(3):  # bandas de interferencia
        y = (t * 300 + i * 640) % (H + 200) - 100
        c.drawRect(RECT(0, y, W, y + 14 + 10 * r.random()), P("#ffffff", alpha=0.06 * a))
    for i in range(40):
        oval(c, r.random() * W, r.random() * H, 1.5, 1.5, P("#ffffff", alpha=0.25 * a))
    f = F(R.RES.mx, 40)
    if int(t * 2) % 2 == 0:
        oval(c, 70, 515, 12, 12, P("#ff2a2a", alpha=a))
    c.drawString("PLAY", 95, 530, f, P("#ffffff", alpha=0.85 * a))
    c.drawString("2016", W - 190, 530, f, P("#ffffff", alpha=0.85 * a))


def glitch(c, k, t):
    """k 0..1: intensidad del glitch."""
    if k <= 0:
        return
    r = rng(int(t * 60) % 991)
    for i in range(int(14 * k)):
        y = r.random() * H
        h = 10 + r.random() * 80
        col = ["#ff2a6a", "#2af0ff", "#ffffff", "#000000"][i % 4]
        c.drawRect(RECT(0, y, W, y + h), P(col, alpha=0.25 + 0.4 * r.random() * k))
    c.drawRect(RECT(0, 0, W, H), P("#ffffff", alpha=0.25 * k * r.random()))


def headphones(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    arc = skia.Path()
    arc.addArc(RECT(-125, -680, 125, -420), 180, 180)
    c.drawPath(arc, P("#1a1a1a", "stroke", 18))
    for sd in (-1, 1):
        rrect(c, sd * 112 - 22, -560, sd * 112 + 22, -480, 16, P("#ff3d6a"))
    c.restore()


def kid(c, x, y, s, t, hold=None, lift=0.0, ph=0.0):
    B.fam_person(c, x, y, s, t, SKIN, HAIR, "kid", SHIRT, ph, hold or (lambda c2, hx, hy: None), lift)
    headphones(c, x, y + 6 * math.sin(t * 2 + ph), s)


def crt(c, x, y, s, draw_screen):
    """Monitor viejo de 2016 (genérico)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -330, -260, 330, 260, 30, P("#d8cfb8", shader=lin(0, -260, 0, 260, ["#e8e0c8", "#b8ae94"])))
    rrect(c, -290, -220, 290, 200, 18, P("#101418"))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(RECT(-280, -210, 280, 190), 14, 14), True)
    draw_screen(c, -280, -210, 280, 190)
    c.drawRect(RECT(-280, -210, 280, 190), P("#ffffff", shader=rad(-120, -120, 380, [R.hexc("#ffffff", 0.12), R.hexc("#ffffff", 0)])))
    c.restore()
    rrect(c, -120, 260, 120, 300, 8, P("#b8ae94"))
    rrect(c, -200, 300, 200, 330, 10, P("#a89e84"))
    oval(c, 250, 230, 10, 10, P("#2fbf71"))
    c.restore()


def player(c, x0, y0, x1, y1, title, views, t, draw_thumb, prog_k=0.3):
    """Reproductor genérico (sin marcas)."""
    c.drawRect(RECT(x0, y0, x1, y1), P("#f4f4f4"))
    th = (y1 - y0) * 0.62
    c.save()
    c.clipRect(RECT(x0, y0, x1, y0 + th))
    draw_thumb(c, x0, y0, x1, y0 + th)
    c.restore()
    c.drawRect(RECT(x0, y0 + th - 6, x1, y0 + th), P("#cccccc"))
    c.drawRect(RECT(x0, y0 + th - 6, lerp(x0, x1, prog_k), y0 + th), P("#e03030"))
    f = F(R.RES.mb, (x1 - x0) * 0.045)
    words, line, lines = title.split(), "", []
    for w in words:
        if f.measureText(line + " " + w) > (x1 - x0) * 0.9 and line:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    lines.append(line)
    for i, ln in enumerate(lines[:2]):
        c.drawString(ln, x0 + 14, y0 + th + (x1 - x0) * 0.06 * (i + 1), f, P("#111111"))
    c.drawString(views, x0 + 14, y1 - 14, F(R.RES.ms, (x1 - x0) * 0.035), P("#777777"))


# ----------------------------------------------------------------------------
# miniaturas de parodia (mala ortografía a propósito)
# ----------------------------------------------------------------------------
THUMBS = [
    ("JUEGANDO SUVWAY SURFERS EN 2016 (NO CLICKBAIT)", "runner", ["#2fb8ff", "#ffe04a"]),
    ("COMO PASAR EL NIVEL 3 DE CANDY CRUSH ((REAL)) 100% FUNSIONA", "candy", ["#ff6fb1", "#ffb3d9"]),
    ("MI CELULAR SE CALENTO MUSHO :(", "phone", ["#ff8a3d", "#ffd04a"]),
    ("REACSIONANDO A MI PROPIO VIDIO", "react", ["#7a3ae0", "#2fb8ff"]),
]


def arrow(c, x, y, rot, s=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    p = skia.Path()
    p.moveTo(-90, -14)
    p.lineTo(30, -14)
    p.lineTo(30, -40)
    p.lineTo(90, 0)
    p.lineTo(30, 40)
    p.lineTo(30, 14)
    p.lineTo(-90, 14)
    p.close()
    c.drawPath(p, P("#ff1a1a"))
    c.drawPath(p, P("#ffffff", "stroke", 6))
    c.restore()


def thumb_art(kind, cols, t):
    def d(c, x0, y0, x1, y1):
        w, h = x1 - x0, y1 - y0
        c.drawRect(RECT(x0, y0, x1, y1), P(cols[0], shader=lin(x0, y0, x1, y1, cols)))
        cx, cy = x0 + w * 0.68, y0 + h * 0.5
        s = h / 400
        if kind == "runner":
            c.drawRect(RECT(cx - 80 * s, cy - 40 * s, cx + 160 * s, cy + 120 * s), P("#e03030"))
            for i in range(3):
                c.drawRect(RECT(cx - 60 * s + i * 70 * s, cy - 20 * s, cx - 20 * s + i * 70 * s, cy + 20 * s), P("#bfe8ff"))
            oval(c, cx - 150 * s, cy - 60 * s, 30 * s, 30 * s, P("#f2c9a0"))
            c.drawLine(cx - 150 * s, cy - 30 * s, cx - 150 * s, cy + 50 * s, P("#2a2a2a", "stroke", 18 * s))
            c.drawLine(cx - 150 * s, cy + 50 * s, cx - 190 * s, cy + 110 * s + 20 * s * math.sin(t * 12), P("#2a2a2a", "stroke", 16 * s))
            c.drawLine(cx - 150 * s, cy + 50 * s, cx - 110 * s, cy + 110 * s - 20 * s * math.sin(t * 12), P("#2a2a2a", "stroke", 16 * s))
        elif kind == "candy":
            for i in range(9):
                gx, gy = cx - 110 * s + (i % 3) * 110 * s, cy - 110 * s + (i // 3) * 110 * s
                col = ["#ff3d6a", "#ffe04a", "#2fbf71", "#2f6bff", "#ff8a3d"][(i * 2) % 5]
                oval(c, gx, gy, 40 * s, 40 * s, P(col))
                oval(c, gx - 12 * s, gy - 12 * s, 10 * s, 10 * s, P("#ffffff", alpha=0.7))
        elif kind == "phone":
            rrect(c, cx - 70 * s, cy - 130 * s, cx + 70 * s, cy + 130 * s, 20 * s, P("#1a1a1a"))
            rrect(c, cx - 58 * s, cy - 112 * s, cx + 58 * s, cy + 112 * s, 12 * s, P("#2f6bff"))
            for i in range(5):
                fx = cx - 90 * s + i * 45 * s
                fl = skia.Path()
                hh = (70 + 30 * math.sin(t * 9 + i)) * s
                fl.moveTo(fx - 26 * s, cy + 140 * s)
                fl.quadTo(fx - 20 * s, cy + 140 * s - hh * 0.6, fx, cy + 140 * s - hh)
                fl.quadTo(fx + 20 * s, cy + 140 * s - hh * 0.6, fx + 26 * s, cy + 140 * s)
                fl.close()
                c.drawPath(fl, P("#ff3d1a", shader=lin(0, cy + 140 * s - hh, 0, cy + 140 * s, ["#ffe04a", "#ff3d1a"])))
        else:
            rrect(c, cx - 140 * s, cy - 100 * s, cx + 140 * s, cy + 100 * s, 12 * s, P("#101418"))
            rrect(c, cx - 70 * s, cy - 50 * s, cx + 70 * s, cy + 50 * s, 8 * s, P("#f4f4f4"))
            rrect(c, cx - 35 * s, cy - 25 * s, cx + 35 * s, cy + 25 * s, 6 * s, P("#101418"))
            oval(c, cx, cy, 10 * s, 10 * s, P("#f4f4f4"))
        # cara de sorpresa (genérica)
        fx, fy = x0 + w * 0.22, y0 + h * 0.55
        oval(c, fx, fy, 110 * s, 120 * s, P("#e8b78c"))
        c.drawPath(skia.Path().addArc(RECT(fx - 115 * s, fy - 130 * s, fx + 115 * s, fy + 40 * s), 180, 180), P("#1a120a"))
        for sd in (-1, 1):
            oval(c, fx + sd * 40 * s, fy - 10 * s, 22 * s, 26 * s, P("#ffffff"))
            oval(c, fx + sd * 40 * s, fy - 6 * s, 10 * s, 12 * s, P("#1a1a1a"))
        oval(c, fx, fy + 60 * s, 30 * s, 38 * s, P("#5a1a24"))
        arrow(c, x0 + w * 0.47, y0 + h * 0.25, 160, s * 1.2)
    return d


def thumb_title(c, txt, x, y, size, maxw):
    """Texto amarillo con borde rojo, todo en mayúsculas (estilo miniatura vieja)."""
    f = F(R.RES.mx, size)
    words, line, lines = txt.split(), "", []
    for w in words:
        if f.measureText(line + " " + w) > maxw and line:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    lines.append(line)
    for i, ln in enumerate(lines):
        w = f.measureText(ln)
        yy = y + i * size * 1.1
        sp = P("#c80000", "stroke", size * 0.22)
        sp.setStrokeJoin(skia.Paint.kRound_Join)
        c.drawString(ln, x - w / 2, yy, f, sp)
        c.drawString(ln, x - w / 2, yy, f, P("#ffe600"))


# ----------------------------------------------------------------------------
# escenarios
# ----------------------------------------------------------------------------


def room(c, t, warm=0.0, night=0.0):
    top = R.mix_col("#2a2440", "#0a0a1a", night)
    S.bokeh(c, t, V.R.mix_col("#3a2a50", "#ff9a6a", warm) if False else "#3a2a50", "#1a1428",
            ["#8a6aff", "#ffb25a", "#5ab0ff"], seed=4)
    if night > 0:
        c.drawRect(RECT(0, 0, W, H), P("#05040f", alpha=0.6 * night))
    del top
    c.drawRect(RECT(-200, 1400, W + 200, H + 200), P("#6a4a30", shader=lin(0, 1400, 0, H, ["#8a5a3a", "#4a2e1a"])))
    c.drawRect(RECT(-200, 1360, W + 200, 1420), P("#a8723e"))


def scene1(c, k):  # gancho: universo real → glitch → universo alterno
    lt, T = k.lt, k.w
    sw = T(5) - 0.05
    if lt < sw:
        c.drawRect(RECT(0, 0, W, H), P("#ff5aa8", shader=rad(540, 1000, 1200, ["#ffb3d9", "#ff5aa8", "#7a3ae0"])))
        R.RES.glow_gold = R.RES.g_lime
        B.sparkles(c, k.t, n=30, seed=2, a=0.9)
        z = 1 + 0.1 * lt
        c.save()
        c.translate(540, 1100)
        c.scale(z, z)
        c.translate(-540, -1100)
        kid(c, 540, 1950, 1.25, k.t)
        c.restore()
        G.pop_text(c, "?", 860, 820, 260, prog(lt, T(2) - 0.1, T(2) + 0.2), col="#ffe04a", rot=12)
        glitch(c, prog(lt, sw - 0.5, sw), k.t)
        return
    u = lt - sw
    yr = int(lerp(2026, 2016, ease_in_out(clamp(u / 1.6))))
    c.drawRect(RECT(0, 0, W, H), P("#101418"))
    c.save()
    c.translate(540, 1080)
    c.rotate(-u * 300 * (1 - clamp(u / 1.6)))
    for i in range(12):  # reloj rebobinando
        a = i * math.pi / 6
        c.drawLine(math.cos(a) * 300, math.sin(a) * 300, math.cos(a) * 340, math.sin(a) * 340, P("#ffffff", "stroke", 8, alpha=0.5))
    c.restore()
    c.drawPath(skia.Path().addCircle(540, 1080, 360), P("#ffffff", "stroke", 10, alpha=0.6))
    G.pop_text(c, str(yr), 540, 1140, 200, 1.0, col="#ffffff", stroke="#000000")
    for i in range(2):  # ◀◀
        tri = skia.Path()
        x0 = 420 + i * 90
        tri.moveTo(x0 + 70, 760)
        tri.lineTo(x0, 800)
        tri.lineTo(x0 + 70, 840)
        tri.close()
        c.drawPath(tri, P("#ffffff", alpha=0.6 + 0.4 * (int(k.t * 6) % 2)))
    G.pop_text(c, "UNIVERSO ALTERNO", 540, 1580, 96, prog(u, 0.05, 0.35), col="#ff3d6a", rot=-4)
    glitch(c, 1 - clamp(u / 0.4), k.t)


def scene2(c, k):  # 2016: el patojo elige AccionAndroid
    lt, T = k.lt, k.w
    room(c, k.t)
    z = lerp(1.0, 1.25, ease_in_out(prog(lt, 0, k.D)))
    cx = lerp(540, 680, ease_in_out(prog(lt, T(10), k.D)))
    click = T(19) - 0.15
    c.save()
    c.translate(540, 1100)
    c.scale(z, z)
    c.translate(-cx, -1100)
    rrect(c, 300, 1260, 1200, 1300, 10, P("#8a5a32"))  # escritorio

    def screen(c2, x0, y0, x1, y1):
        c2.drawRect(RECT(x0, y0, x1, y1), P("#1a2a4a"))
        text_center(c2, "¿QUÉ VIDEOS SUBO?", (x0 + x1) / 2, y0 + 70, F(R.RES.mx, 40), P("#ffffff"))
        for i, lab in enumerate(("COMEDIA", "JUEGOS ANDROID")):
            bx0, by0 = x0 + 40, y0 + 120 + i * 130
            sel = i == 1 and lt > click
            rrect(c2, bx0, by0, x1 - 40, by0 + 100, 16, P("#2fbf71" if sel else "#2a3a6a"))
            rrect(c2, bx0, by0, x1 - 40, by0 + 100, 16, P("#ffffff", "stroke", 4, alpha=0.6))
            text_center(c2, lab, (x0 + x1) / 2, by0 + 66, F(R.RES.mx, 44), P("#ffffff"))
        cu = ease_in_out(prog(lt, T(14), click))
        mx, my = lerp((x0 + x1) / 2 + 120, (x0 + x1) / 2 + 60, cu), lerp(y0 + 160, y0 + 320, cu)
        cur = skia.Path()
        cur.moveTo(mx, my)
        cur.lineTo(mx, my + 50)
        cur.lineTo(mx + 14, my + 38)
        cur.lineTo(mx + 34, my + 40)
        cur.close()
        c2.drawPath(cur, P("#ffffff"))
        c2.drawPath(cur, P("#000000", "stroke", 3))
    crt(c, 760, 1000, 1.0, screen)
    kid(c, 300, 1900, 1.0, k.t, ph=1.0)
    c.restore()
    G.tag(c, "14 AÑOS", 300, 720, prog(lt, T(5) - 0.1, T(5) + 0.2), bg="#ffe04a", fg="#14061f", size=48, rot=-4)
    G.pop_text(c, "UPS…", 540, 1600, 150, prog(lt, click + 0.25, click + 0.5), col="#ff3d6a", rot=-6)


def scene3(c, k):  # el canal que hubiera sido: miniaturas con mala ortografía
    lt, T = k.lt, k.w
    c.drawRect(RECT(0, 0, W, H), P("#e8e8e8"))
    n = len(THUMBS)
    t0 = T(5) + 0.15
    seg = (k.D - t0 - 0.2) / n
    i = max(0, min(n - 1, int((lt - t0) / seg))) if lt > t0 else -1
    if i < 0:  # entra a la pantalla del monitor
        u = ease_in_out(clamp(lt / max(t0, 0.1)))
        c.save()
        c.translate(540, 1050)
        c.scale(lerp(1.4, 2.6, u), lerp(1.4, 2.6, u))
        c.translate(-540, -1050)
        room(c, k.t)
        crt(c, 540, 1050, 1.0, lambda c2, x0, y0, x1, y1: c2.drawRect(RECT(x0, y0, x1, y1), P("#f4f4f4")))
        c.restore()
        return
    title, kind, cols = THUMBS[i]
    ll = lt - (t0 + i * seg)
    e = back_out(clamp(ll / 0.3), 1.8)
    c.save()
    c.translate(540, 1050)
    c.rotate((-6 if i % 2 else 6) * (1 - clamp(ll / 0.3)) + 1.2 * math.sin(lt * 2))
    c.scale(e * (1 + 0.03 * ll), e * (1 + 0.03 * ll))
    c.translate(-540, -1050)
    x0, y0, x1, y1 = 70, 620, 1010, 1540

    def thumb(c2, a0, b0, a1, b1):
        thumb_art(kind, cols, k.t)(c2, a0, b0, a1, b1)
        thumb_title(c2, title, (a0 + a1) / 2, b0 + 90, 52, a1 - a0 - 60)
    player(c, x0, y0, x1, y1, title, "3 vistas • hace 8 años", k.t, thumb, 0.1 + 0.2 * ll)
    c.restore()
    # comentario de mamá
    ck = prog(ll, 0.35, 0.6)
    if ck > 0:
        s = back_out(ck, 1.8)
        c.save()
        c.translate(540, 1660)
        c.scale(s, s)
        rrect(c, -380, -60, 380, 60, 30, P("#ffffff"))
        oval(c, -320, 0, 34, 34, P("#ff9ac0"))
        text_center(c, "M", -320, 14, F(R.RES.mx, 36), P("#ffffff"))
        c.drawString("Mamá", -270, -10, F(R.RES.mx, 30), P("#111111"))
        c.drawString("bien mijo", -270, 32, F(R.RES.ms, 32), P("#333333"))
        hp = skia.Path()
        hx, hy = 300, 6
        hp.moveTo(hx, hy + 18)
        hp.cubicTo(hx - 40, hy - 10, hx - 20, hy - 40, hx, hy - 20)
        hp.cubicTo(hx + 20, hy - 40, hx + 40, hy - 10, hx, hy + 18)
        c.drawPath(hp, P("#ff3d6a"))
        c.restore()


def scene4(c, k):  # sin burlas a la telenovela + verlo a escondidas
    lt, T = k.lt, k.w
    sw = T(12) - 0.2
    if lt < sw:
        z = lerp(1.0, 1.15, ease_in_out(prog(lt, 0, sw)))
        c.save()
        c.translate(540, 1050)
        c.scale(z, z)
        c.translate(-540, -1050)
        room(c, k.t)
        rrect(c, 140, 640, 940, 1260, 30, P("#2a2a30"))  # tele genérica

        def tv(c2):
            c2.drawRect(RECT(170, 670, 910, 1230), P("#f4dcc8", shader=lin(0, 670, 0, 1230, ["#ffe8d8", "#e8c8b0"])))
            for i in range(3):  # cortina
                c2.drawLine(200 + i * 30, 670, 210 + i * 30 + 20 * math.sin(k.t * 2 + i), 1230, P("#c86a8a", "stroke", 24))
            rrect(c2, 480, 1060, 600, 1200, 14, P("#9ad0e8", alpha=0.8))
            sway = 10 * math.sin(k.t * 3)
            c2.drawLine(540, 1060, 540 + sway, 900, P("#2f8f4a", "stroke", 8))
            for j in range(6):
                a = j * math.pi / 3
                oval(c2, 540 + sway + math.cos(a) * 24, 890 + math.sin(a) * 24, 26, 26, P("#e0203a"))
            oval(c2, 540 + sway, 890, 20, 20, P("#a8102a"))
            for j in range(3):  # "el aire" moviéndola
                y = 860 + j * 40
                x = 640 + ((k.t * 200 + j * 60) % 200)
                c2.drawLine(x, y, x + 60, y, P("#7fa8c8", "stroke", 5, alpha=0.6))
        c.save()
        c.clipRect(RECT(170, 670, 910, 1230))
        tv(c)
        c.restore()
        c.restore()
        G.tag(c, "NADIE SE BURLA  :|", 540, 1500, prog(lt, T(8) - 0.2, T(8) + 0.1), bg="#14061f", size=52, rot=-3)
        return
    u = lt - sw
    door = ease_out(prog(lt, T(18) - 0.2, T(19)))
    hide = prog(lt, T(19), T(19) + 0.3)
    z = lerp(1.0, 1.12, ease_in_out(prog(u, 0, k.D - sw)))
    sh = G.shake(k.t, 10 * max(0, 1 - abs(lt - T(19) - 0.1) / 0.25))
    c.save()
    c.translate(540 + sh[0], 1100 + sh[1])
    c.scale(z, z)
    c.translate(-540, -1100)
    c.drawRect(RECT(-200, -200, W + 200, H + 200), P("#0a0a1a", shader=lin(0, 0, 0, H, ["#141430", "#05050f"])))
    # puerta con luz
    c.drawRect(RECT(780, 500, 1080, 1400), P("#1a1a2a"))
    if door > 0:
        lp = skia.Path()
        lp.moveTo(780, 500)
        lp.lineTo(780 + 120 * door, 500)
        lp.lineTo(780 + 500 * door, 1900)
        lp.lineTo(600, 1900)
        lp.close()
        c.drawPath(lp, P("#ffd88a", alpha=0.35))
        c.drawRect(RECT(780, 500, 780 + 120 * door, 1400), P("#ffe9b0"))
        oval(c, 840, 760, 40 * door, 46, P("#2a1a3a"))  # silueta del papá
        rrect(c, 800, 800, 880, 1100, 30, P("#2a1a3a", alpha=door))
    # cama con el patojo bajo la cobija
    rrect(c, 60, 1250, 900, 1480, 40, P("#3a2a5a"))
    bump = skia.Path()
    bump.moveTo(80, 1300)
    bump.cubicTo(200, 1000 + 60 * hide, 520, 1000 + 60 * hide, 860, 1300)
    bump.close()
    c.drawPath(bump, P("#5a7ad6", shader=lin(0, 1000, 0, 1300, ["#7a9aef", "#3a5ab6"])))
    if hide < 1:  # el teléfono brilla bajo la cobija
        glow(c, R.RES.g_vio, 400, 1150, 280, 0.8 * (1 - hide), skia.BlendMode.kScreen)
        rrect(c, 370, 1110, 430, 1200, 10, P("#bfe8ff", alpha=1 - hide))
        oval(c, 300, 1150 + 40 * hide, 50, 50, P(SKIN, alpha=1 - hide))
        for sd in (-1, 1):
            oval(c, 300 + sd * 18, 1140 + 40 * hide, 6, 7, P("#1a1a1a", alpha=1 - hide))
    c.restore()
    # globo con "expresiones" (censuradas) y la aureola de "bonitas"
    ek = prog(lt, T(24) - 0.2, T(24) + 0.1)
    if ek > 0:
        s = back_out(ek, 1.8)
        c.save()
        c.translate(400, 820)
        c.scale(s, s)
        rrect(c, -260, -90, 260, 90, 50, P("#ffffff"))
        tail = skia.Path()
        tail.moveTo(-40, 80)
        tail.lineTo(0, 170)
        tail.lineTo(40, 80)
        c.drawPath(tail, P("#ffffff"))
        text_center(c, "¡#@$%&!", 0, 26, F(R.RES.mx, 80), P("#e0203a"))
        c.restore()
    bk = prog(lt, T(26) - 0.1, T(26) + 0.2)
    if bk > 0:
        c.save()
        c.translate(400, 690 - 10 * math.sin(k.t * 3))
        c.scale(back_out(bk, 2), back_out(bk, 2))
        c.drawPath(skia.Path().addOval(RECT(-120, -26, 120, 26)), P("#ffe04a", "stroke", 14))
        glow(c, R.RES.glow_white, 0, 0, 160, 0.6)
        c.restore()
        G.tag(c, "TAN… BONITAS", 540, 1560, bk, bg="#ffe04a", fg="#14061f", size=56, rot=-3)
    G.tag(c, "A ESCONDIDAS", 540, 1560, prog(lt, T(18) - 0.1, T(18) + 0.2) * (1 - prog(lt, T(24) - 0.3, T(24))), bg="#14061f", size=52, rot=3)


def scene5(c, k):  # el canal #1 sería un tutorial de atol de elote
    lt, T = k.lt, k.w
    c.drawRect(RECT(0, 0, W, H), P("#e8e8e8"))
    z = lerp(1.0, 1.08, ease_in_out(prog(lt, 0, k.D)))
    c.save()
    c.translate(540, 1080)
    c.scale(z, z)
    c.translate(-540, -1080)

    def thumb(c2, x0, y0, x1, y1):
        c2.drawRect(RECT(x0, y0, x1, y1), P("#f4e2c0", shader=lin(0, y0, 0, y1, ["#fff0d0", "#d8b890"])))
        c2.drawRect(RECT(x0, y1 - 120, x1, y1), P("#8a5a3a"))
        cx, cy = (x0 + x1) / 2 + 120, y1 - 200
        oval(c2, cx, cy, 200, 60, P("#5a5a64"))
        c2.drawRect(RECT(cx - 200, cy, cx + 200, cy + 150), P("#7a7a86", shader=lin(cx - 200, 0, cx + 200, 0, ["#5a5a64", "#9a9aa8", "#5a5a64"])))
        oval(c2, cx, cy, 180, 50, P("#ffd84a"))
        a = k.t * 3
        c2.drawLine(cx + math.cos(a) * 80, cy + math.sin(a) * 20, cx + math.cos(a) * 60 + 120, cy - 220, P("#a8723e", "stroke", 16))
        for i in range(3):  # vapor
            v = (k.t * 0.6 + i / 3) % 1
            c2.drawPath(skia.Path().addOval(RECT(cx - 40 + i * 30, cy - 60 - v * 180, cx + i * 30, cy - 20 - v * 180)),
                        P("#ffffff", alpha=0.5 * (1 - v)))
        for j in range(6):  # elotes
            oval(c2, x0 + 110 + j * 30, y1 - 150, 20, 60, P("#ffd84a"))
        thumb_title(c2, "ATOL DE ELOTE FASIL Y RAPIDO", (x0 + x1) / 2, y0 + 90, 58, x1 - x0 - 80)
    player(c, 70, 620, 1010, 1540, "ATOL DE ELOTE FASIL Y RAPIDO (RESETA DE MI ABUELITA)", "12 suscriptores • 31 vistas", k.t, thumb, 0.05)
    c.restore()
    G.tag(c, "EL CANAL #1 DE GUATEMALA", 540, 560 + 40, prog(lt, T(6) - 0.1, T(6) + 0.2) * 0 + prog(lt, T(2), T(2) + 0.3), bg="#14061f", size=40, rot=-2)
    sk = prog(lt, T(17) - 0.1, T(17) + 0.2)
    if sk > 0:
        G.pop_text(c, "12", 840, 1660, 150, sk, col="#ffe04a", rot=6)
    ck = prog(lt, T(18) + 0.5, T(18) + 0.8)
    if ck > 0:  # grillo
        c.save()
        c.translate(260, 1690)
        oval(c, 0, 0, 50, 22, P("#3a5a2a"))
        oval(c, 50, -6, 18, 16, P("#3a5a2a"))
        c.drawLine(60, -18, 110, -70 + 10 * math.sin(k.t * 20), P("#3a5a2a", "stroke", 3))
        for sd in (-1, 1):
            c.drawLine(-20, 10, -60, 50 + sd * 10, P("#3a5a2a", "stroke", 5))
        c.restore()
        if int(k.t * 3) % 2 == 0:
            c.drawString("cri… cri…", 330, 1700, F(R.RES.ms, 44), P("#555555", alpha=ck))


def confetti(c, t, lt, n=80, seed=5):
    r = rng(seed)
    for i in range(n):
        x = r.random() * W
        sp = 300 + r.random() * 500
        y = -60 + (lt * sp + r.random() * 400) % (H + 120)
        a = t * (3 + 5 * r.random()) + i
        c.save()
        c.translate(x + 30 * math.sin(t * 2 + i), y)
        c.rotate(math.degrees(a))
        c.scale(1, abs(math.cos(a)) + 0.2)
        rrect(c, -10, -6, 10, 6, 2, P(["#ff3d6a", "#ffe04a", "#2fbf71", "#2f6bff", "#ffffff", "#ff8a3d"][i % 6]))
        c.restore()


def crown(c, x, y, s):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    p = skia.Path()
    p.moveTo(-150, 60)
    p.lineTo(-170, -80)
    p.lineTo(-80, 0)
    p.lineTo(0, -110)
    p.lineTo(80, 0)
    p.lineTo(170, -80)
    p.lineTo(150, 60)
    p.close()
    c.drawPath(p, P("#ffc23a", shader=lin(-170, 0, 170, 0, ["#c8901a", "#ffe27a", "#c8901a"])))
    for px, py in ((-170, -80), (0, -110), (170, -80)):
        oval(c, px, py, 18, 18, P("#ff3d6a"))
    c.restore()


def scene6(c, k):  # de vuelta al universo real
    lt, T = k.lt, k.w
    portal = ease_in_out(prog(lt, 0, 0.8))
    c.drawRect(RECT(0, 0, W, H), P("#ff5aa8", shader=rad(540, 1000, 1300, ["#ffe04a", "#ff5aa8", "#7a3ae0"])))
    c.save()
    c.translate(540, 1050)
    c.rotate(k.t * 40)
    for i in range(16):
        p = skia.Path()
        a0, a1 = math.radians(i * 22.5), math.radians(i * 22.5 + 10)
        p.moveTo(0, 0)
        p.lineTo(math.cos(a0) * 1800, math.sin(a0) * 1800)
        p.lineTo(math.cos(a1) * 1800, math.sin(a1) * 1800)
        p.close()
        c.drawPath(p, P("#ffffff", alpha=0.12))
    c.restore()
    if portal < 1:  # el portal se abre desde el universo gris
        c.save()
        clip = skia.Path().addCircle(540, 1050, 1400 * portal)
        c.clipPath(clip, skia.ClipOp.kDifference, True)
        c.drawRect(RECT(0, 0, W, H), P("#3a3a44"))
        c.restore()
        c.drawPath(skia.Path().addCircle(540, 1050, 1400 * portal), P("#ffffff", "stroke", 30 * (1 - portal), alpha=0.9))
    confetti(c, k.t, lt)
    val = 14_000_000 * ease_out(prog(lt, T(4) - 0.2, T(7) + 0.3))
    FM.odometer(c, 540, 1000, val, 80, prog(lt, T(4) - 0.3, T(4)), col="#ffffff")
    G.pop_text(c, "SUSCRIPTORES", 540, 1150, 70, prog(lt, T(7) - 0.1, T(7) + 0.2))
    ck = prog(lt, T(11) - 0.1, T(11) + 0.2)
    if ck > 0:
        crown(c, 540, lerp(400, 760, ease_out(ck)), 1.0)
        G.tag(c, "#1 GUATEMALA", 540, 1330, ck, bg="#ffe04a", fg="#14061f", size=64, rot=-3)
    G.pop_text(c, "¡SIMÓN!", 540, 1580, 140, prog(lt, T(1) - 0.1, T(1) + 0.2) * (1 - prog(lt, T(4) - 0.3, T(4))), col="#ffe04a", rot=-5)


def scene7(c, k):  # gracias + ¿cuál es tu favorito?
    lt, T = k.lt, k.w
    c.drawRect(RECT(0, 0, W, H), P("#ff8ac0", shader=rad(540, 900, 1300, ["#ffd0e8", "#ff8ac0", "#a05ad6"])))
    R.RES.glow_gold = R.RES.g_lime
    B.sparkles(c, k.t, n=24, seed=8, a=0.8)
    z = lerp(1.05, 1.0, ease_out(prog(lt, 0, 1)))
    laugh = 0.5 + 0.5 * math.sin(k.t * 14)
    c.save()
    c.translate(540, 1100 + 8 * laugh)
    c.scale(z, z)
    c.rotate(2 * math.sin(k.t * 7))
    c.translate(-540, -1100)

    def screen(c2, x0, y0, x1, y1):
        c2.drawRect(RECT(x0, y0, x1, y1), P("#ff5aa8", shader=lin(0, y0, 0, y1, ["#ffe04a", "#ff5aa8"])))
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        oval(c2, cx, cy, 60, 60, P("#ffffff"))
        tri = skia.Path()
        tri.moveTo(cx - 18, cy - 30)
        tri.lineTo(cx + 32, cy)
        tri.lineTo(cx - 18, cy + 30)
        tri.close()
        c2.drawPath(tri, P("#ff3d6a"))
    crt(c, 760, 1000, 0.9, screen)
    kid(c, 330, 1900, 1.05, k.t, ph=2.0)
    c.restore()
    for i, txt in enumerate(("JAJAJAJA", "jajaja")):  # risas
        a = prog(lt, 0.2 + i * 0.4, 0.5 + i * 0.4)
        G.pop_text(c, txt, (220, 360)[i], (760, 860)[i], (70, 54)[i], a * (1 - prog(lt, T(11), T(12))), col="#ffe04a", rot=(-10, 8)[i])
    r = rng(31)
    msgs = ["todos xd", "JAJAJAJA", "no puedo elegir uno", "el primero que vi", "me hizo llorar de risa", "todos los de la Rosa"]
    for i in range(12):
        side = -1 if i % 2 == 0 else 1
        x = 540 + side * (330 + r.random() * 60)
        u = (lt - (T(12) + i * 0.22)) / 2.6
        if u <= 0 or u >= 1:
            continue
        yy = lerp(1650, 650, u)
        a = math.sin(math.pi * u)
        tx = msgs[i % len(msgs)]
        f = F(R.RES.mb, 28)
        w = f.measureText(tx) + 70
        c.save()
        c.translate(x + 14 * math.sin(lt * 2 + i), yy)
        rrect(c, -w / 2, -30, w / 2, 30, 30, P("#ffffff", alpha=0.95 * a))
        oval(c, -w / 2 + 30, 0, 16, 16, P(["#ff3d6a", "#2f6bff", "#2fbf71", "#ffe04a"][i % 4], alpha=a))
        c.drawString(tx, -w / 2 + 56, 10, f, P("#111111", alpha=a))
        c.restore()
    fk = prog(lt, T(14) - 0.1, T(14) + 0.2)
    if fk > 0:
        G.tag(c, "¿CUÁL ES TU FAVORITO?", 540, 1480, fk, bg="#14061f", size=52, rot=-3)
        a = 0.5 + 0.5 * math.sin(k.t * 8)
        tri = skia.Path()
        tri.moveTo(500, 1560 + 10 * a)
        tri.lineTo(580, 1560 + 10 * a)
        tri.lineTo(540, 1610 + 10 * a)
        tri.close()
        c.drawPath(tri, P("#ffffff", alpha=fk))


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7]
WHIP = {1, 3, 4, 6}


def render_frame(c, t, vo, phr, total):
    si = max(i for i, s in enumerate(vo) if s["start"] <= t) if t >= 0 else 0
    c.clear(R.hexc("#000000"))
    k = R.Ctx(vo, si, t)
    lt = k.lt
    blur, dx = 0.0, 0.0
    if si in WHIP and lt < 0.2:
        q = 1 - ease_out(lt / 0.2)
        blur, dx = 60 * q, 240 * q
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
    alt = si in ALT and not (si == 0 and lt < k.w(5) - 0.05)
    if alt:
        vhs(c, t, 1.0)
    if si == 5 and lt < 0.5:  # el filtro se va al cruzar el portal
        vhs(c, t, 1 - lt / 0.5)
    R.vignette(c, 0.4)
    fade = clamp(t / 0.2) * clamp((total - t) / 0.4)
    if fade < 1:
        c.drawRect(RECT(0, 0, W, H), P("#000000", alpha=1 - fade))
    R.draw_subs(c, t, phr)
    R.draw_watermark(c)


def watermark(c):
    f = F(R.RES.ms, 24)
    txt = "Video de fan · no oficial"
    w = f.measureText(txt)
    rrect(c, W / 2 - w / 2 - 18, 1700, W / 2 + w / 2 + 18, 1744, 22, P("#000000", alpha=0.4))
    c.drawString(txt, W / 2 - w / 2, 1730, f, P("#ffffff", alpha=0.85))


class JRes(V.VeltoRes):
    def __init__(self):
        super().__init__()
        self.g_gold = R.sprite(255, 214, 90, power=1.6)
        self.cloud = R.sprite(255, 255, 255, n=96, power=1.25)


def install():
    V.install()
    R.Res = JRes
    R.SCENES = SCENES
    R.FADE_IN = 0.0
    R.render_frame = render_frame
    R.draw_subs = S.draw_subs
    R.draw_watermark = watermark


if __name__ == "__main__":
    install()
    R.main()
