# Otto Aleman Perfumes — video "El perfume que siempre quise"

Video vertical 1080x1920 (Reels/TikTok) que explica qué es un decant, animado en 2D por código.

## Cómo regenerarlo
```bash
pip install edge-tts skia-python numpy scipy pillow   # skia necesita libegl1
python3 src/voice.py          # voz en off (edge-tts, es-GT-AndresNeural) + tiempos por palabra
python3 src/prep_assets.py    # recorta logo y decant
python3 src/audio.py          # música original + efectos + mezcla (-14 LUFS)
python3 src/render.py --start 0 --end 8 --out build/prueba.mp4   # prueba
python3 src/render.py --out build/video_mudo.mp4                 # completo
```
Luego se une video y audio con ffmpeg (ver `src/make.sh`).
