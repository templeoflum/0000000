#!/bin/zsh
set -eu
cd "$(dirname "$0")"
mkdir -p Heart.iconset
for size in 16 32 128 256 512; do
  sips -z "$size" "$size" heart.png --out "Heart.iconset/icon_${size}x${size}.png" >/dev/null
  sips -z "$((size*2))" "$((size*2))" heart.png --out "Heart.iconset/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns Heart.iconset -o Heart.icns
