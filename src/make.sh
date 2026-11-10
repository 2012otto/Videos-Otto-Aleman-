#!/usr/bin/env bash
# Genera el video completo: animación + audio + subtítulos .srt
set -e
cd "$(dirname "$0")/.."
python3 src/render.py --out build/video_mudo.mp4
ffmpeg -v error -y -i build/video_mudo.mp4 -i build/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart output/OttoAleman_Decants_Reel.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('output/OttoAleman_Decants_Reel.srt', timeline.phrases(vo))"
