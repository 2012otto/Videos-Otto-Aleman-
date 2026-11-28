#!/usr/bin/env bash
# Otto Aleman Perfumes — "¡Esto SÍ son ofertas!" Black Friday… ¡NAVIDEÑO! 3x2 en decants, en bucle. Voz David.
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/otto_serie/build_bf" VO_TRIM=0.15 VO_GAP=0.22 VO_TAIL=0.6
[ -f otto_serie/build_bf/voice.json ] || VIDEO_SCRIPT=otto_serie/guion_blackfriday.json python3 src/voice_eleven.py
python3 otto_serie/src/audio_blackfriday.py
python3 otto_serie/src/render_blackfriday.py --out otto_serie/build_bf/video_mudo.mp4
ffmpeg -v error -y -i otto_serie/build_bf/video_mudo.mp4 -i otto_serie/build_bf/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart otto_serie/output/OttoAleman_BlackFridayNavideno.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('otto_serie/output/OttoAleman_BlackFridayNavideno.srt', timeline.phrases(vo))"
