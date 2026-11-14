#!/usr/bin/env bash
# Velto — GTA 6 parte 2: "ya habría ganado más de mil millones" + giro a Velto. CTA: Comenta VENTA.
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/velto/build_gta2" VO_TRIM=0.12 VO_GAP=0.15 VO_TAIL=1.2
[ -f velto/build_gta2/voice.json ] || VIDEO_SCRIPT=velto/guion_gta2.json python3 src/voice_eleven.py
python3 velto/src/audio_gta2.py
python3 velto/src/render_gta2.py --out velto/build_gta2/video_mudo.mp4
ffmpeg -v error -y -i velto/build_gta2/video_mudo.mp4 -i velto/build_gta2/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart velto/output/Velto_GTA6_MilMillones.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('velto/output/Velto_GTA6_MilMillones.srt', timeline.phrases(vo))"
