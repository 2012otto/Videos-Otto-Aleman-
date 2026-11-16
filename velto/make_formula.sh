#!/usr/bin/env bash
# Velto — "La fórmula de los mil millones" (GTA 6 en 3 pasos → Velto Studio + Claude). Voz: David. CTA: Comenta GTA.
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/velto/build_formula" VO_TRIM=0.12 VO_GAP=0.15 VO_TAIL=1.2
[ -f velto/build_formula/voice.json ] || VIDEO_SCRIPT=velto/guion_formula.json python3 src/voice_eleven.py
python3 velto/src/audio_formula.py
python3 velto/src/render_formula.py --out velto/build_formula/video_mudo.mp4
ffmpeg -v error -y -i velto/build_formula/video_mudo.mp4 -i velto/build_formula/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart velto/output/Velto_GTA6_LaFormula.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('velto/output/Velto_GTA6_LaFormula.srt', timeline.phrases(vo))"
