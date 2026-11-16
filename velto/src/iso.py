"""Motor de maqueta isométrica 3D (estilo diorama): Vice City en miniatura al atardecer.

Cámara isométrica con órbita (theta), elevación (e), zoom (S) y centro. Cajas con 3 caras visibles,
luz que cambia con la órbita, ventanas, neón, palmeras, autos, gente diminuta y desenfoque tipo
"tilt-shift" (arriba y abajo borrosos) para que se vea como una maqueta.
"""
import math

import skia

import render as R
from render import P, lin, rad, oval, rrect, clamp, lerp, rng, glow

W, H = 1080, 1920
RECT = R.R


def hx(col):
    if isinstance(col, int):
        return "#%02x%02x%02x" % (skia.ColorGetR(col), skia.ColorGetG(col), skia.ColorGetB(col))
    return col


def mixc(a, b, t):
    return hx(R.mix_col(hx(a), hx(b), clamp(t)))


class IsoCam:
    def __init__(self, cx, cy, S, theta=45.0, e=0.5, px=540, py=1050, cz=0.0):
        self.cx, self.cy, self.S, self.e = cx, cy, S, e
        self.ct, self.st = math.cos(math.radians(theta)), math.sin(math.radians(theta))
        self.px, self.py, self.cz = px, py, cz
        self.kz = math.sqrt(max(0.0, 1 - e * e)) * 1.15

    def rot(self, x, y):
        dx, dy = x - self.cx, y - self.cy
        return dx * self.ct - dy * self.st, dx * self.st + dy * self.ct

    def p(self, x, y, z=0.0):
        xr, yr = self.rot(x, y)
        return (self.px + (xr - yr) * 0.866 * self.S,
                self.py + (xr + yr) * self.e * self.S - (z - self.cz) * self.S * self.kz)

    def depth(self, x, y, z=0.0):
        xr, yr = self.rot(x, y)
        return xr + yr + z * 0.01

    def facing(self, nx, ny):
        rx = nx * self.ct - ny * self.st
        ry = nx * self.st + ny * self.ct
        return rx + ry


SUN = (-0.55, 0.85)  # dirección de la luz del atardecer (mundo)


def face_paint(col, nx, ny, top=False):
    if top:
        return mixc(col, "#fff4e0", 0.18)
    lam = max(0.0, nx * SUN[0] + ny * SUN[1])
    base = mixc(col, "#3a1440", 0.42 - 0.3 * lam)
    return mixc(base, "#ffb07a", 0.25 * lam)


def quad(c, cam, pts, paint):
    path = skia.Path()
    for i, (x, y, z) in enumerate(pts):
        sx, sy = cam.p(x, y, z)
        (path.moveTo if i == 0 else path.lineTo)(sx, sy)
    path.close()
    c.drawPath(path, paint)
    return path


def box(c, cam, x, y, w, d, z0, h, col, windows=None, neon=None, t=0.0, seed=0):
    """Caja alineada a los ejes: base (x, y)-(x+w, y+d), de z0 a z0+h."""
    x1, y1, z1 = x + w, y + d, z0 + h
    faces = [((1, 0), [(x1, y, z0), (x1, y1, z0), (x1, y1, z1), (x1, y, z1)], (x1, y, 0, 1)),
             ((-1, 0), [(x, y1, z0), (x, y, z0), (x, y, z1), (x, y1, z1)], (x, y1, 0, -1)),
             ((0, 1), [(x1, y1, z0), (x, y1, z0), (x, y1, z1), (x1, y1, z1)], (x1, y1, -1, 0)),
             ((0, -1), [(x, y, z0), (x1, y, z0), (x1, y, z1), (x, y, z1)], (x, y, 1, 0))]
    for (nx, ny), pts, (ox, oy, ux, uy) in faces:
        if cam.facing(nx, ny) <= 0:
            continue
        quad(c, cam, pts, P(face_paint(col, nx, ny)))
        L = abs(w if ux else d)
        if windows and h > 4:
            rows = int((h - 2) / windows[1])
            cols = int((L - 1.2) / windows[0])
            for rr in range(rows):
                for cc in range(cols):
                    u0 = 0.9 + cc * windows[0]
                    v0 = z0 + 1.4 + rr * windows[1]
                    lit = (rr * 7 + cc * 3 + seed * 5 + nx * 5 + ny * 11) % 3 == 0
                    wc = "#ffd88a" if lit else mixc("#7fd6ff", "#3a1440", 0.25 if cam.facing(nx, ny) > 0.8 else 0.5)
                    quad(c, cam, [(ox + ux * u0, oy + uy * u0, v0), (ox + ux * (u0 + windows[0] * 0.55), oy + uy * (u0 + windows[0] * 0.55), v0),
                                  (ox + ux * (u0 + windows[0] * 0.55), oy + uy * (u0 + windows[0] * 0.55), v0 + windows[1] * 0.6),
                                  (ox + ux * u0, oy + uy * u0, v0 + windows[1] * 0.6)], P(wc))
        if neon:  # franja de neón en la parte alta
            a = 0.8 + 0.2 * math.sin(t * 6 + seed)
            p0 = cam.p(ox, oy, z1 - 0.8)
            p1 = cam.p(ox + ux * L, oy + uy * L, z1 - 0.8)
            c.drawLine(*p0, *p1, P(neon, "stroke", max(1.5, 0.35 * cam.S), alpha=a))
            c.drawLine(*p0, *p1, P(neon, "stroke", max(3, 0.9 * cam.S), alpha=0.3 * a, blur=4))
    quad(c, cam, [(x, y, z1), (x1, y, z1), (x1, y1, z1), (x, y1, z1)], P(face_paint(col, 0, 0, top=True)))


def palm(c, cam, x, y, h, t, ph=0.0):
    sx, sy = cam.p(x, y, 0)
    hp = h * cam.S * cam.kz
    top = (sx + hp * 0.12, sy - hp)
    tr = skia.Path()
    tr.moveTo(sx, sy)
    tr.quadTo(sx + hp * 0.02, sy - hp * 0.5, *top)
    c.drawPath(tr, P("#8a5a3a", "stroke", max(1.5, hp * 0.07)))
    for i in range(8):
        a = math.radians(-165 + i * 44 + 8 * math.sin(t * 1.6 + i + ph))
        L = hp * 0.5
        lf = skia.Path()
        lf.moveTo(*top)
        ex, ey = top[0] + math.cos(a) * L, top[1] + math.sin(a) * L * 0.55 + L * 0.3
        lf.quadTo(top[0] + math.cos(a) * L * 0.5, top[1] - L * 0.25, ex, ey)
        c.drawPath(lf, P("#2f8f5a", "stroke", max(1.5, hp * 0.06)))


def person(c, cam, x, y, col, t, ph=0.0, walk=0.0):
    sx, sy = cam.p(x, y, 0)
    s = cam.S
    bob = abs(math.sin(t * 8 + ph)) * 0.15 * s * walk
    oval(c, sx, sy, 0.45 * s, 0.2 * s, P("#000000", alpha=0.25))
    rrect(c, sx - 0.32 * s, sy - 1.5 * s - bob, sx + 0.32 * s, sy - 0.2 * s - bob, 0.3 * s, P(col))
    oval(c, sx, sy - 1.85 * s - bob, 0.3 * s, 0.3 * s, P("#e8b78c"))


def car(c, cam, x, y, along_x, col, t):
    w, d = (4.2, 2.0) if along_x else (2.0, 4.2)
    box(c, cam, x - w / 2, y - d / 2, w, d, 0.2, 1.0, col)
    if along_x:
        box(c, cam, x - 1.1, y - 0.85, 2.0, 1.7, 1.2, 0.7, "#2a1040")
    else:
        box(c, cam, x - 0.85, y - 1.1, 1.7, 2.0, 1.2, 0.7, "#2a1040")


# ----------------------------------------------------------------------------
# la ciudad
# ----------------------------------------------------------------------------
PASTEL = ["#ffb3c9", "#bdf2dc", "#ffe28a", "#c9d6ff", "#ff9ac0", "#ffd0a8", "#a8f0e8", "#f4f1ea"]
NEON = ["#ff3d9a", "#2ff0ff", "#ffe04a", "#b46bff"]
ROADS_X = [22, 52]   # calles a lo largo de x (en y fijo)
ROADS_Y = [26, 56]   # calles a lo largo de y (en x fijo)
RW = 5.0
ISLAND = (0, 0, 80, 80)


def make_city(seed=5):
    r = rng(seed)
    blds = []
    xs = [(2, ROADS_Y[0] - RW / 2 - 1), (ROADS_Y[0] + RW / 2 + 1, ROADS_Y[1] - RW / 2 - 1), (ROADS_Y[1] + RW / 2 + 1, 66)]
    ys = [(2, ROADS_X[0] - RW / 2 - 1), (ROADS_X[0] + RW / 2 + 1, ROADS_X[1] - RW / 2 - 1), (ROADS_X[1] + RW / 2 + 1, 78)]
    i = 0
    for bx0, bx1 in xs:
        for by0, by1 in ys:
            x = bx0
            while x < bx1 - 5:
                w = min(bx1 - x, 7 + r.random() * 6)
                y = by0
                while y < by1 - 5:
                    d = min(by1 - y, 7 + r.random() * 6)
                    h = 6 + r.random() * 16
                    blds.append(dict(x=x, y=y, w=w - 0.8, d=d - 0.8, h=h, col=PASTEL[i % 8], neon=NEON[i % 4] if i % 2 == 0 else None, i=i))
                    i += 1
                    y += d
                x += w
    return blds


CITY = make_city()
PALMS = [(68.5, y) for y in range(4, 80, 6)] + [(ROADS_Y[0] + 3.2, y + 3) for y in range(0, 80, 9)]
HERO = {"hotel": (36.0, 34.0)}  # azotea del hotel del contador


def water(c, cam, t):
    x0, y0, x1, y1 = -40, -40, 120, 120
    pts = [cam.p(x0, y0, -1.2), cam.p(x1, y0, -1.2), cam.p(x1, y1, -1.2), cam.p(x0, y1, -1.2)]
    ys = [q[1] for q in pts]
    path = skia.Path()
    for i, q in enumerate(pts):
        (path.moveTo if i == 0 else path.lineTo)(*q)
    path.close()
    c.drawPath(path, P("#2a7ab8", shader=lin(0, min(ys), 0, max(ys), ["#ff9ab0", "#c85a9a", "#2a7ab8", "#1a4a8a"], [0, .25, .6, 1])))
    c.drawPath(path, P("#ffd0e0", "stroke", max(2, 0.6 * cam.S), alpha=0.5, blur=6))
    r = rng(3)
    for i in range(70):
        x, y = -40 + r.random() * 160, -40 + r.random() * 160
        if 0 < x < 80 and 0 < y < 80:
            continue
        a = 0.5 + 0.5 * math.sin(t * 2 + i)
        p0 = cam.p(x, y, -1.2)
        p1 = cam.p(x + 2, y, -1.2)
        c.drawLine(*p0, *p1, P("#bff7ff", "stroke", max(1, 0.25 * cam.S), alpha=0.5 * a))


def city(c, cam, t, extras=None, dim=0.0):
    """Dibuja la maqueta completa. extras: lista de (x, y, fn(c, cam)) objetos héroe ordenados por profundidad."""
    water(c, cam, t)
    # isla (losa con orilla de arena)
    box(c, cam, -1, -1, 82, 82, -3, 3, "#f3d8b0")
    quad(c, cam, [(0, 0, 0.01), (66, 0, 0.01), (66, 80, 0.01), (0, 80, 0.01)], P(face_paint("#e8c8d8", 0, 0, True)))
    quad(c, cam, [(66, 0, 0.01), (80, 0, 0.01), (80, 80, 0.01), (66, 80, 0.01)], P("#f6e2b8"))
    road = P("#4a3a5a")
    for ry in ROADS_X:
        quad(c, cam, [(0, ry - RW / 2, 0.02), (66, ry - RW / 2, 0.02), (66, ry + RW / 2, 0.02), (0, ry + RW / 2, 0.02)], road)
        for k in range(0, 66, 4):
            quad(c, cam, [(k, ry - 0.12, 0.03), (k + 2, ry - 0.12, 0.03), (k + 2, ry + 0.12, 0.03), (k, ry + 0.12, 0.03)], P("#ffe9a0"))
    for rx in ROADS_Y:
        quad(c, cam, [(rx - RW / 2, 0, 0.02), (rx + RW / 2, 0, 0.02), (rx + RW / 2, 80, 0.02), (rx - RW / 2, 80, 0.02)], road)
        for k in range(0, 80, 4):
            quad(c, cam, [(rx - 0.12, k, 0.03), (rx + 0.12, k, 0.03), (rx + 0.12, k + 2, 0.03), (rx - 0.12, k + 2, 0.03)], P("#ffe9a0"))
    items = []
    for b in CITY:
        items.append((cam.depth(b["x"] + b["w"] / 2, b["y"] + b["d"] / 2), "b", b))
    for x, y in PALMS:
        items.append((cam.depth(x, y), "p", (x, y)))
    for i in range(6):  # autos circulando
        u = (t * 0.06 + i / 6) % 1
        if i % 2 == 0:
            x, y = u * 66, ROADS_X[i % 2 and 1 or 0] + (1.2 if i % 4 == 0 else -1.2)
            items.append((cam.depth(x, y), "c", (x, y, True, ["#e8202a", "#ffe04a", "#2ff0ff"][i % 3])))
        else:
            x, y = ROADS_Y[1] + 1.2, (1 - u) * 80
            items.append((cam.depth(x, y), "c", (x, y, False, ["#ff3d9a", "#ffffff", "#7a3ae0"][i % 3])))
    r = rng(12)
    for i in range(26):  # gente caminando por la acera
        u = (t * 0.02 * (1 + r.random()) + r.random()) % 1
        x, y = (u * 64 + 1, ROADS_X[0] + 3.2) if i % 2 else (ROADS_Y[0] - 3.3, u * 78 + 1)
        items.append((cam.depth(x, y), "h", (x, y, ["#ff6fa8", "#2ff0ff", "#ffe04a", "#ffffff", "#7a3ae0"][i % 5], i)))
    for (x, y, fn) in (extras or []):
        items.append((cam.depth(x, y), "x", fn))
    items.sort(key=lambda q: q[0])
    for _, kind, o in items:
        if kind == "b":
            box(c, cam, o["x"], o["y"], o["w"], o["d"], 0, o["h"], o["col"], windows=(2.4, 3.0), neon=o["neon"], t=t, seed=o["i"])
            if o["h"] > 12:  # remate escalonado art déco
                box(c, cam, o["x"] + o["w"] * 0.25, o["y"] + o["d"] * 0.25, o["w"] * 0.5, o["d"] * 0.5, o["h"], 2.5, o["col"])
        elif kind == "p":
            palm(c, cam, o[0], o[1], 7.5, t, o[1])
        elif kind == "c":
            car(c, cam, o[0], o[1], o[2], o[3], t)
        elif kind == "h":
            person(c, cam, o[0], o[1], o[2], t, o[3], 1.0)
        else:
            o(c, cam)
    if dim > 0:
        c.drawRect(RECT(-200, -200, W + 200, H + 200), P("#1a0820", alpha=dim))


def sky(c, t, night=0.0):
    top = mixc("#3a1060", "#0a0418", night)
    mid = mixc("#c8407a", "#2a0a4a", night)
    bot = mixc("#ffb37a", "#5a1a6a", night)
    c.drawRect(RECT(-200, -200, W + 200, H + 200), P(top, shader=lin(0, 0, 0, H, [top, mid, bot], [0, .55, 1])))
    glow(c, R.RES.g_mag, 820, 420, 700, 0.35 * (1 - night), skia.BlendMode.kScreen)


def tilt_shift(c, draw, sigma=10.0, band=(0.22, 0.8)):
    """Dibuja `draw` nítido en el centro y desenfocado arriba/abajo (efecto maqueta)."""
    surf = skia.Surface(W, H)
    draw(surf.getCanvas())
    img = surf.makeImageSnapshot()
    c.drawImage(img, 0, 0)
    c.saveLayer(None, None)
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(sigma, sigma, skia.TileMode.kClamp))
    c.drawImage(img, 0, 0, R.SAMP, p)
    m = skia.Paint()
    m.setBlendMode(skia.BlendMode.kDstIn)
    a, b = band
    m.setShader(lin(0, 0, 0, H, [R.hexc("#000000", 1), R.hexc("#000000", 0), R.hexc("#000000", 0), R.hexc("#000000", 1)],
                    [0, a, b, 1]))
    c.drawRect(RECT(0, 0, W, H), m)
    c.restore()
