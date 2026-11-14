#!/usr/bin/env bash
# Velto Studio — dato curioso GTA 6 (anuncios de $5 que pausan el video). Voz: ElevenLabs "David - Energetic".
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/velto/build_gta" VO_TRIM=0.12 VO_GAP=0.12 VO_TAIL=0.4
[ -f velto/build_gta/voice.json ] || VIDEO_SCRIPT=velto/guion_gta.json python3 src/voice_eleven.py
python3 velto/src/tempo_ads.py
python3 velto/src/audio_gta.py
python3 velto/src/render_gta.py --out velto/build_gta/video_mudo.mp4
ffmpeg -v error -y -i velto/build_gta/video_mudo.mp4 -i velto/build_gta/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart velto/output/VeltoStudio_GTA6.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('velto/output/VeltoStudio_GTA6.srt', timeline.phrases(vo))"
