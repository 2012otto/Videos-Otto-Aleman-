#!/usr/bin/env bash
# Otto Aleman Perfumes — Mandarin Sky Elixir + Black Friday. Personaje A, voz David.
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/otto_serie/build_elixir" VO_TRIM=0.15 VO_GAP=0.3 VO_TAIL=2.2
[ -f otto_serie/build_elixir/voice.json ] || VIDEO_SCRIPT=otto_serie/guion_elixir.json python3 src/voice_eleven.py
python3 otto_serie/src/audio_elixir.py
python3 otto_serie/src/render_elixir.py --out otto_serie/build_elixir/video_mudo.mp4
ffmpeg -v error -y -i otto_serie/build_elixir/video_mudo.mp4 -i otto_serie/build_elixir/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart otto_serie/output/OttoAleman_MandarinSkyElixir_BlackFriday.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('otto_serie/output/OttoAleman_MandarinSkyElixir_BlackFriday.srt', timeline.phrases(vo))"
