#!/usr/bin/env bash
# Chocobananos Blanqui's — anuncio animado. Voz: ElevenLabs "David - Energetic" (la del video GTA 6).
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/blanquis/build" VO_TRIM=0.2 VO_GAP=0.4 VO_TAIL=1.5
[ -f blanquis/build/voice.json ] || VIDEO_SCRIPT=blanquis/guion.json python3 src/voice_eleven.py
python3 blanquis/src/audio_blanquis.py
python3 blanquis/src/render_blanquis.py --out blanquis/build/video_mudo.mp4
ffmpeg -v error -y -i blanquis/build/video_mudo.mp4 -i blanquis/build/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart blanquis/output/ChocobananosBlanquis.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('blanquis/output/ChocobananosBlanquis.srt', timeline.phrases(vo))"
