"""Recorta la V brillante del logo (fondo negro) y la deja con fondo transparente."""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

A = "velto/assets/"
im = np.asarray(Image.open(A + "logo_texto_original.png").convert("RGB")).astype(float)
im = im[:, :760]
mx = im.max(2)
fg = mx > 28
lab, n = ndimage.label(fg)
sizes = ndimage.sum(fg, lab, range(1, n + 1))
fg = lab == (np.argmax(sizes) + 1)
fg = ndimage.binary_fill_holes(fg)
fg = ndimage.binary_opening(fg, structure=ndimage.generate_binary_structure(2, 1), iterations=12)
fg = ndimage.binary_erosion(fg, iterations=2)  # quita el borde con ruido de color
a = np.asarray(Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2)))
ys, xs = np.where(fg)
rgba = np.dstack([im.astype(np.uint8), a])[ys.min() - 4:ys.max() + 4, xs.min() - 4:xs.max() + 4]
Image.fromarray(rgba).save(A + "v_logo.png")
print("v_logo", rgba.shape)
