#!/usr/bin/env bash
# Video de fan (no oficial): "¿Y si Jexs nunca hubiera existido?". Voz: David (ElevenLabs).
set -e
cd "$(dirname "$0")/.."
export VIDEO_BUILD="$PWD/fan/build_jexs" VO_TRIM=0.15 VO_GAP=0.25 VO_TAIL=1.5
[ -f fan/build_jexs/voice.json ] || VIDEO_SCRIPT=fan/guion_jexs.json python3 src/voice_eleven.py
python3 fan/src/audio_jexs.py
python3 fan/src/render_jexs.py --out fan/build_jexs/video_mudo.mp4
ffmpeg -v error -y -i fan/build_jexs/video_mudo.mp4 -i fan/build_jexs/audio.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart fan/output/YSiJexsNuncaHubieraExistido.mp4
python3 -c "import sys; sys.path.insert(0,'src'); import timeline; vo,_=timeline.load(); timeline.write_srt('fan/output/YSiJexsNuncaHubieraExistido.srt', timeline.phrases(vo))"
