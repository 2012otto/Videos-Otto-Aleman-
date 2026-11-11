#!/usr/bin/env bash
# Velto episodio 2 ("Si no te encuentran... no te compran"): voz -> audio -> animación -> MP4 + SRT
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/velto/build_ep2" VO_TRIM=0.3
[ -f velto/build_ep2/voice.json ] || VIDEO_SCRIPT=velto/guion_ep2.json python3 src/voice.py
python3 velto/src/audio_ep2.py
python3 velto/src/render_ep2.py --out velto/build_ep2/video_mudo.mp4
ffmpeg -v error -y -i velto/build_ep2/video_mudo.mp4 -i velto/build_ep2/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart velto/output/Velto_Ep2_SiNoTeEncuentran.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('velto/output/Velto_Ep2_SiNoTeEncuentran.srt', timeline.phrases(vo))"
