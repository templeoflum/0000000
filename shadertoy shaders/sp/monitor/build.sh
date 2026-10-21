#!/bin/zsh
set -eu
cd "$(dirname "$0")"
frameworks="$(cd ../preview/.venv/lib/python3.12/site-packages/syphon/libs && pwd)"
mkdir -p 'Heart.app/Contents/MacOS' 'Heart.app/Contents/Resources'
cp navigation.js Heart.app/Contents/Resources/navigation.js
cp pointer.js Heart.app/Contents/Resources/pointer.js
if [[ -f art/Heart.icns ]]; then cp art/Heart.icns Heart.app/Contents/Resources/Heart.icns; fi
clang -fobjc-arc -O2 -fmodules -fmodules-cache-path=/tmp/heart-clang-modules -framework Cocoa -framework Metal -framework MetalKit -framework WebKit -framework IOKit -framework CoreGraphics -framework CoreMIDI -framework GameController -F "$frameworks" -framework Syphon -Wl,-rpath,"$frameworks" Heart.m -o Heart.app/Contents/MacOS/Heart
cat > Heart.app/Contents/Info.plist <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>CFBundleExecutable</key><string>Heart</string><key>CFBundleIdentifier</key><string>local.heart.monitor</string><key>CFBundleName</key><string>Heart</string><key>CFBundleIconFile</key><string>Heart</string><key>NSHighResolutionCapable</key><true/><key>NSAppTransportSecurity</key><dict><key>NSAllowsLocalNetworking</key><true/></dict></dict></plist>
PLIST
