#!/usr/bin/env bash
# Otto Aleman Perfumes — "Te enamoró en la mañana… y en la tarde ya no" (decants). Personaje A, voz David.
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/otto_serie/build_decant" VO_TRIM=0.15 VO_GAP=0.3 VO_TAIL=2.0
[ -f otto_serie/build_decant/voice.json ] || VIDEO_SCRIPT=otto_serie/guion_decant_tarde.json python3 src/voice_eleven.py
python3 otto_serie/src/audio_decant_tarde.py
python3 otto_serie/src/render_decant_tarde.py --out otto_serie/build_decant/video_mudo.mp4
ffmpeg -v error -y -i otto_serie/build_decant/video_mudo.mp4 -i otto_serie/build_decant/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart otto_serie/output/OttoAleman_DecantEnLaTarde.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('otto_serie/output/OttoAleman_DecantEnLaTarde.srt', timeline.phrases(vo))"
