"""Prepara logo (alfa a partir de la tinta negra) y recorte del decant (fondo blanco -> transparente)."""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

A = "assets/"
# --- logo ---
lg = np.asarray(Image.open(A + "logo_original.jpg").convert("L")).astype(float)
lg[-12:, :] = 255  # quitar la línea negra del borde inferior de la captura
alpha = np.clip((235 - lg) / 180, 0, 1)
ys, xs = np.where(alpha > 0.1)
alpha = alpha[ys.min() - 8:ys.max() + 8, xs.min() - 8:xs.max() + 8]
h, w = alpha.shape
for name, col in {"logo_white.png": (255, 255, 255), "logo_black.png": (10, 10, 10)}.items():
    im = np.zeros((h, w, 4), np.uint8); im[..., :3] = col; im[..., 3] = (alpha * 255).astype(np.uint8)
    Image.fromarray(im).save(A + name)
# dorado con degradado vertical
t = np.linspace(0, 1, h)[:, None, None]
c1, c2, c3 = np.array([255, 232, 160]), np.array([226, 170, 70]), np.array([170, 110, 35])
grad = np.where(t < .5, c1 + (c2 - c1) * (t / .5), c2 + (c3 - c2) * ((t - .5) / .5))
grad = np.broadcast_to(grad, (h, w, 3))
im = np.zeros((h, w, 4), np.uint8); im[..., :3] = grad; im[..., 3] = (alpha * 255).astype(np.uint8)
Image.fromarray(im).save(A + "logo_gold.png")

# --- decant (frasco izquierdo) ---
d = np.asarray(Image.open(A + "decant_original.png").convert("RGB")).astype(float)
d = d[:, :627]
bright = d.min(axis=2) > 236
lab, n = ndimage.label(bright)
border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
bg = np.isin(lab, list(border))
fg = ~bg
fg = ndimage.binary_fill_holes(fg)
fg = ndimage.binary_opening(fg, iterations=2)
a = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
rgba = np.dstack([d.astype(np.uint8), np.asarray(a)])
ys, xs = np.where(fg)
rgba = rgba[ys.min() - 4:ys.max() + 4, xs.min() - 4:xs.max() + 4]
Image.fromarray(rgba).save(A + "decant.png")
print("logo", (w, h), "decant", rgba.shape)
