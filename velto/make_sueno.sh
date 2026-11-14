#!/usr/bin/env bash
# Velto Studio — dato curioso "11 días sin dormir" (anuncio de $5 a la mitad y al final). Voz: clon ElevenLabs.
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/velto/build_sueno" VO_TRIM=0.3
[ -f velto/build_sueno/voice.json ] || VIDEO_SCRIPT=velto/guion_studio_sueno.json python3 src/voice_eleven.py
python3 velto/src/audio_sueno.py
python3 velto/src/render_sueno.py --out velto/build_sueno/video_mudo.mp4
ffmpeg -v error -y -i velto/build_sueno/video_mudo.mp4 -i velto/build_sueno/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart velto/output/VeltoStudio_11DiasSinDormir.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('velto/output/VeltoStudio_11DiasSinDormir.srt', timeline.phrases(vo))"
