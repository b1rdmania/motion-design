#!/usr/bin/env bash
# Build the timing fixture with ffmpeg alone: three plates, cuts at 1.5 s and 3.5 s,
# a tone near -14 LUFS with a silence from 2.5 to 3.0 s.
# Usage: make_reference.sh OUT.mp4 [--shift FRAMES]
set -euo pipefail
out="$1"; shift || true
shift_frames=0
if [[ "${1:-}" == "--shift" ]]; then shift_frames="$2"; fi

fps=24
c2=$(python3 -c "print(3.5 + $shift_frames / $fps)")
d2=$(python3 -c "print($c2 - 1.5)")
d3=$(python3 -c "print(5.0 - $c2)")

ffmpeg -v error -y \
  -f lavfi -i "color=c=0xe6dfd0:s=640x360:r=$fps:d=1.5" \
  -f lavfi -i "color=c=0x1a1816:s=640x360:r=$fps:d=$d2" \
  -f lavfi -i "color=c=0x2d3748:s=640x360:r=$fps:d=$d3" \
  -f lavfi -i "sine=frequency=440:sample_rate=48000:duration=5" \
  -filter_complex "[0:v][1:v][2:v]concat=n=3:v=1:a=0,format=yuv420p[v];\
[3:a]volume=enable='between(t,2.5,3.0)':volume=0,volume=2.45,aformat=channel_layouts=stereo[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -r $fps -c:a aac -b:a 192k -t 5 "$out"
