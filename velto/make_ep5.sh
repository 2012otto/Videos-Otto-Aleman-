#!/usr/bin/env bash
# Velto — "El balde roto" (lanzamiento de VELTO STUDIO). Voz: ElevenLabs (clave inyectada por el proxy del entorno).
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/velto/build_ep5" VO_TRIM=0.3
[ -f velto/build_ep5/voice.json ] || VIDEO_SCRIPT=velto/guion_ep5.json python3 src/voice_eleven.py
python3 velto/src/audio_ep5.py
python3 velto/src/render_ep5.py --out velto/build_ep5/video_mudo.mp4
ffmpeg -v error -y -i velto/build_ep5/video_mudo.mp4 -i velto/build_ep5/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart velto/output/Velto_Studio_BaldeRoto.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('velto/output/Velto_Studio_BaldeRoto.srt', timeline.phrases(vo))"
