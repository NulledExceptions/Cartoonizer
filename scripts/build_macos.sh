#!/bin/bash
# build_macos.sh - Build Cartoonizer.app using PyInstaller
#
# Usage:
#   ./scripts/build_macos.sh [--one-file] [--no-dmg]
#
# Options:
#   --one-file    Create a single-file .app (slower startup, but easier to distribute)
#   --no-dmg      Skip DMG generation
#
# Output:
#   dist/Cartoonizer.app          (the app bundle)
#   dist/Cartoonizer-<version>.dmg (drag-and-drop installer, if --no-dmg not set)

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPEC_FILE="$REPO_ROOT/packaging/macos/cartoonizer.spec"
BUILD_DIR="$REPO_ROOT/build"
DIST_DIR="$REPO_ROOT/dist"
APP_NAME="Cartoonizer"
VERSION="1.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[*]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect if we're in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    PYTHON="$VIRTUAL_ENV/bin/python3"
    log_info "Using venv Python: $PYTHON"
else
    PYTHON="python3"
fi

# Parse arguments
ONE_FILE=0
NO_DMG=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --one-file) ONE_FILE=1 ;;
        --no-dmg) NO_DMG=1 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

# Check prerequisites
log_info "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    log_error "python3 not found. Please install Python 3.9+."
    exit 1
fi

# Check if required dependencies are installed
$PYTHON -c "import torch" 2>/dev/null || {
    log_error "Required dependencies not installed."
    log_info "Please run:"
    log_info "  source venv/bin/activate  # if using venv"
    log_info "  pip install -r source/requirements.txt"
    exit 1
}

if ! $PYTHON -m pip list | grep -q "pyinstaller"; then
    log_warn "PyInstaller not installed. Installing..."
    $PYTHON -m pip install pyinstaller
fi

# Check if spec file exists
if [ ! -f "$SPEC_FILE" ]; then
    log_error "Spec file not found: $SPEC_FILE"
    exit 1
fi

log_info "Building ${APP_NAME}.app..."
log_info "  Repo root: $REPO_ROOT"
log_info "  Spec file: $SPEC_FILE"
log_info "  Build dir: $BUILD_DIR"
log_info "  Dist dir: $DIST_DIR"

# Clean previous builds
log_info "Cleaning previous build artifacts..."
rm -rf "$BUILD_DIR" "$DIST_DIR"

# Build with PyInstaller
log_info "Running PyInstaller..."
PYINSTALLER_ARGS=(
    "$SPEC_FILE"
    "--distpath=$DIST_DIR"
    "--workpath=$BUILD_DIR"
    "-y"  # Overwrite without asking
)

if [ $ONE_FILE -eq 1 ]; then
    log_info "Building one-file bundle (slower startup, single executable)..."
    # Note: one-file bundles with PyInstaller on macOS create a temporary directory
    # at runtime, which can be slower. The default is generally better.
    PYINSTALLER_ARGS+=("--onefile")
else
    log_info "Building one-folder bundle (faster startup)..."
fi

$PYTHON -m PyInstaller "${PYINSTALLER_ARGS[@]}" || {
    log_error "PyInstaller build failed"
    exit 1
}

APP_PATH="$DIST_DIR/${APP_NAME}.app"
if [ ! -d "$APP_PATH" ]; then
    log_error "App bundle not created: $APP_PATH"
    exit 1
fi

log_info "✓ App created: $APP_PATH"

# Check app structure
if [ ! -f "$APP_PATH/Contents/MacOS/cartoonizer" ]; then
    log_error "App executable not found in expected location"
    exit 1
fi

log_info "✓ App structure is valid"

# Make executable
chmod +x "$APP_PATH/Contents/MacOS/cartoonizer"

# Copy icon to app bundle
ICON_SOURCE="$REPO_ROOT/source/assets/Cartoonizer.icns"
if [ -f "$ICON_SOURCE" ]; then
    ICON_DEST="$APP_PATH/Contents/Resources/Cartoonizer.icns"
    cp "$ICON_SOURCE" "$ICON_DEST"
    log_info "✓ Icon installed to app bundle"
fi

# Create DMG (optional)
if [ $NO_DMG -eq 0 ]; then
    log_info "Creating DMG installer..."
    
    DMG_NAME="${APP_NAME}-${VERSION}.dmg"
    DMG_PATH="$DIST_DIR/$DMG_NAME"
    DMG_TEMP_DIR="$DIST_DIR/.dmg_temp"
    
    # Create temporary DMG directory structure
    mkdir -p "$DMG_TEMP_DIR"
    
    # Copy app to temp directory
    cp -r "$APP_PATH" "$DMG_TEMP_DIR/"
    
    # Create Applications symlink
    ln -s /Applications "$DMG_TEMP_DIR/Applications"
    
    # Add a background image (optional, would need to be created)
    # For now, skip it
    
    # Create the DMG
    hdiutil create \
        -volname "$APP_NAME" \
        -srcfolder "$DMG_TEMP_DIR" \
        -ov \
        -format UDZO \
        "$DMG_PATH" || {
        log_warn "DMG creation failed, but app bundle is ready"
    }
    
    # Cleanup temp directory
    rm -rf "$DMG_TEMP_DIR"
    
    if [ -f "$DMG_PATH" ]; then
        log_info "✓ DMG created: $DMG_PATH"
        log_info ""
        log_info "Distribution ready:"
        log_info "  - Drag $APP_NAME.app from the DMG to /Applications"
        log_info "  - Or double-click the DMG to mount it"
    fi
fi

log_info ""
log_info "========================================="
log_info "Build complete!"
log_info "========================================="
log_info ""
log_info "Run the app:"
log_info "  open '$APP_PATH'"
log_info ""
log_info "Or double-click from Finder:"
log_info "  $APP_PATH"
log_info ""
