#!/bin/bash
# Build Cartoonizer.app from the files in this source/ folder.

set -e

APP_DIR="Cartoonizer.app"
CONTENTS="$APP_DIR/Contents"
MACOS="$CONTENTS/MacOS"
RESOURCES="$CONTENTS/Resources"

mkdir -p "$MACOS"
mkdir -p "$RESOURCES"

cp Info.plist "$CONTENTS/Info.plist"
cp cartoonizer_launcher "$MACOS/cartoonizer_launcher"
chmod +x "$MACOS/cartoonizer_launcher"
cp cartoonizer.py "$RESOURCES/cartoonizer.py"
cp requirements.txt "$RESOURCES/requirements.txt"
if [ -f assets/Cartoonizer.icns ]; then
  cp assets/Cartoonizer.icns "$RESOURCES/Cartoonizer.icns"
fi
if [ -f assets/cartoonizer_web_icon.png ]; then
  cp assets/cartoonizer_web_icon.png "$RESOURCES/cartoonizer_web_icon.png"
fi

echo "Cartoonizer.app built. You can now double-click it in Finder."
