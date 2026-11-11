#!/usr/bin/env bash
# Video Velto completo: voz -> audio -> animación -> MP4 + SRT
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/velto/build" VO_TRIM=0.3
[ -f velto/build/voice.json ] || VIDEO_SCRIPT=velto/guion.json python3 src/voice.py
python3 velto/src/audio_velto.py
python3 velto/src/render_velto.py --out velto/build/video_mudo.mp4
ffmpeg -v error -y -i velto/build/video_mudo.mp4 -i velto/build/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart velto/output/Velto_Reel.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('velto/output/Velto_Reel.srt', timeline.phrases(vo))"
