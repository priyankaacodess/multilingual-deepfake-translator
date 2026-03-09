#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <input_video.mp4> <output_gif.gif> [width]"
  echo "Example: $0 storage/outputs/demo.mp4 assets/demo.gif 960"
  exit 1
fi

INPUT_VIDEO="$1"
OUTPUT_GIF="$2"
WIDTH="${3:-960}"
FPS="10"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg is required but not found."
  exit 1
fi

PALETTE_FILE="$(mktemp /tmp/palette.XXXXXX.png)"

ffmpeg -y -i "$INPUT_VIDEO" \
  -vf "fps=${FPS},scale=${WIDTH}:-1:flags=lanczos,palettegen=stats_mode=diff" \
  "$PALETTE_FILE"

ffmpeg -y -i "$INPUT_VIDEO" -i "$PALETTE_FILE" \
  -lavfi "fps=${FPS},scale=${WIDTH}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" \
  "$OUTPUT_GIF"

rm -f "$PALETTE_FILE"

echo "GIF generated at: $OUTPUT_GIF"
