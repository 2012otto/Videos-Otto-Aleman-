#!/usr/bin/env bash
# Otto Aleman Perfumes — Estás haciendo esto mal con tu perfume (adaptación olfativa), en bucle. Voz David.
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/otto_serie/build_nariz" VO_TRIM=0.15 VO_GAP=0.25 VO_TAIL=0.8
[ -f otto_serie/build_nariz/voice.json ] || VIDEO_SCRIPT=otto_serie/guion_nariz.json python3 src/voice_eleven.py
python3 otto_serie/src/audio_nariz.py
python3 otto_serie/src/render_nariz.py --out otto_serie/build_nariz/video_mudo.mp4
ffmpeg -v error -y -i otto_serie/build_nariz/video_mudo.mp4 -i otto_serie/build_nariz/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart otto_serie/output/OttoAleman_TuNarizTeMiente.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('otto_serie/output/OttoAleman_TuNarizTeMiente.srt', timeline.phrases(vo))"
