"""Exporta el logo Velto rehecho (PNG transparente y versión sobre fondo oscuro)."""
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_velto as V  # noqa: E402

V.install()
V.R.RES = V.VeltoRes()
for name, bg in (("Velto_logo_mejorado.png", None), ("Velto_logo_mejorado_fondo_oscuro.png", "#0c0420")):
    surf = skia.Surface(2400, 760)
    c = surf.getCanvas()
    c.clear(skia.ColorTRANSPARENT if bg is None else V.hexc(bg))
    V.full_logo(c, 1200, 360, 1.0, t=0.0, glow_a=0.9 if bg else 0.0)
    out = os.path.join(V.REPO, "velto", "output", name)
    surf.makeImageSnapshot().save(out, skia.kPNG)
    print(out)
