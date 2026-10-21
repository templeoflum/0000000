#!/bin/zsh
set -eu
cd "$(dirname "$0")"
clang -fobjc-arc -O2 -fmodules -fmodules-cache-path=/tmp/heart-v2-clang-modules -framework Cocoa -framework WebKit -framework CoreMIDI -framework GameController -framework CoreGraphics Window.m -o 'Heart Surface.app/Contents/MacOS/HeartSurface.next'
mv 'Heart Surface.app/Contents/MacOS/HeartSurface.next' 'Heart Surface.app/Contents/MacOS/HeartSurface'
