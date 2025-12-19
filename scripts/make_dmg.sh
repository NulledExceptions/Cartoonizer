#!/bin/bash
# make_dmg.sh - Create a drag-and-drop DMG installer for Cartoonizer.app
#
# This script creates a professional DMG (disk image) with:
#   - Cartoonizer.app bundle
#   - Applications folder symlink (for easy installation)
#   - Custom background and layout (optional)
#
# Usage:
#   ./scripts/make_dmg.sh [APP_PATH] [OUTPUT_DMG]
#
# Examples:
#   ./scripts/make_dmg.sh                          # Uses dist/Cartoonizer.app
#   ./scripts/make_dmg.sh dist/Cartoonizer.app dist/Cartoonizer-1.0.dmg

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Parse arguments
APP_PATH="${1:-$REPO_ROOT/dist/Cartoonizer.app}"
OUTPUT_DMG="${2:-$REPO_ROOT/dist/Cartoonizer-1.0.dmg}"
VERSION="1.0"
APP_NAME="Cartoonizer"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[*]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verify app exists
if [ ! -d "$APP_PATH" ]; then
    log_error "App not found at: $APP_PATH"
    exit 1
fi

log_info "Creating DMG for: $APP_PATH"
log_info "Output: $OUTPUT_DMG"

# Create temporary directory for DMG contents
TEMP_DMG_DIR=$(mktemp -d)
trap "rm -rf '$TEMP_DMG_DIR'" EXIT

log_info "Creating DMG structure in: $TEMP_DMG_DIR"

# Copy the app
cp -r "$APP_PATH" "$TEMP_DMG_DIR/"

# Create Applications symlink
ln -s /Applications "$TEMP_DMG_DIR/Applications"

# Create a .background directory for optional background image
mkdir -p "$TEMP_DMG_DIR/.background"

# Create a simple README
cat > "$TEMP_DMG_DIR/README.txt" << 'EOF'
Cartoonizer - Transform photos into cartoons using AI

1. Drag Cartoonizer.app to the Applications folder
2. Double-click Applications > Cartoonizer.app to launch
3. Or simply double-click Cartoonizer.app from the DMG

First run may take 1-2 minutes to download AI models.
EOF

# Remove any existing DMG
rm -f "$OUTPUT_DMG"

# Create the DMG
log_info "Building DMG image..."
hdiutil create \
    -volname "$APP_NAME" \
    -srcfolder "$TEMP_DMG_DIR" \
    -ov \
    -format UDZO \
    -imagekey zlib-level=9 \
    "$OUTPUT_DMG"

# Verify DMG was created
if [ ! -f "$OUTPUT_DMG" ]; then
    log_error "Failed to create DMG"
    exit 1
fi

# Get file size
DMG_SIZE=$(du -h "$OUTPUT_DMG" | cut -f1)

log_info ""
log_info "========================================="
log_info "DMG created successfully!"
log_info "========================================="
log_info "File: $OUTPUT_DMG"
log_info "Size: $DMG_SIZE"
log_info ""
log_info "To distribute:"
log_info "  1. Upload $OUTPUT_DMG to your website/GitHub"
log_info "  2. Users download and double-click to mount"
log_info "  3. Users drag Cartoonizer.app to Applications"
log_info ""
