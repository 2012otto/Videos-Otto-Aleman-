#!/usr/bin/env bash
# Velto — GTA 6 "mil millones" en estilo Vice City 3D (misma voz y guion que make_gta2.sh). CTA: Comenta VENTA.
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/velto/build_gta3" VO_TRIM=0.12 VO_GAP=0.15 VO_TAIL=1.2
mkdir -p velto/build_gta3
[ -f velto/build_gta3/voice.json ] || cp velto/build_gta2/voice.json velto/build_gta3/ 2>/dev/null || \
  VIDEO_SCRIPT=velto/guion_gta2.json python3 src/voice_eleven.py
python3 velto/src/audio_gta2.py
python3 velto/src/render_gta3.py --out velto/build_gta3/video_mudo.mp4
ffmpeg -v error -y -i velto/build_gta3/video_mudo.mp4 -i velto/build_gta3/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart velto/output/Velto_GTA6_ViceCity.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('velto/output/Velto_GTA6_ViceCity.srt', timeline.phrases(vo))"
