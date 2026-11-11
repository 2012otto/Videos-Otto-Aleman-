#!/usr/bin/env bash
# Serie Otto Aleman Perfumes — "El mensaje en la botella" (anuncio inesperado): voz -> audio -> animación -> MP4 + SRT
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/otto_serie/build_ep4" VO_TRIM=0.3
mkdir -p otto_serie/output
[ -f otto_serie/build_ep4/voice.json ] || VIDEO_SCRIPT=otto_serie/guion_ep4.json python3 src/voice.py
python3 otto_serie/src/audio_ep4.py
python3 otto_serie/src/render_ep4.py --out otto_serie/build_ep4/video_mudo.mp4
ffmpeg -v error -y -i otto_serie/build_ep4/video_mudo.mp4 -i otto_serie/build_ep4/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart otto_serie/output/OttoAleman_MensajeEnLaBotella.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('otto_serie/output/OttoAleman_MensajeEnLaBotella.srt', timeline.phrases(vo))"
