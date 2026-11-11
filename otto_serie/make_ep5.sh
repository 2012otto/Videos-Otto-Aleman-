#!/usr/bin/env bash
# Serie Otto Aleman Perfumes — "La lámpara de las mil y una noches" (anuncio inesperado): voz -> audio -> animación -> MP4 + SRT
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/otto_serie/build_ep5" VO_TRIM=0.3
mkdir -p otto_serie/output
[ -f otto_serie/build_ep5/voice.json ] || VIDEO_SCRIPT=otto_serie/guion_ep5.json python3 src/voice.py
python3 otto_serie/src/audio_ep5.py
python3 otto_serie/src/render_ep5.py --out otto_serie/build_ep5/video_mudo.mp4
ffmpeg -v error -y -i otto_serie/build_ep5/video_mudo.mp4 -i otto_serie/build_ep5/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart otto_serie/output/OttoAleman_LaLampara.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('otto_serie/output/OttoAleman_LaLampara.srt', timeline.phrases(vo))"
