# Cartoonizer macOS Build Guide

Complete guide for building, testing, and distributing Cartoonizer as a native macOS app.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Detailed Build Process](#detailed-build-process)
4. [Testing](#testing)
5. [Distribution](#distribution)
6. [Troubleshooting](#troubleshooting)

---

## Overview

**Cartoonizer** is packaged as a native macOS app using:

- **Framework**: Gradio (web UI for image processing)
- **Python Runtime**: PyInstaller bundles Python + all dependencies
- **Distribution**: DMG file with drag-and-drop installer
- **Data Location**: `~/Library/Application Support/Cartoonizer/` (writable, persistent)
- **Logs**: `~/Library/Logs/Cartoonizer/app.log`

The build process is fully automated and produces:
- `dist/Cartoonizer.app` – The runnable application
- `dist/Cartoonizer-1.0.dmg` – Disk image for distribution

---

## Quick Start

### For Developers

```bash
# 1. Clone and enter the repo
git clone https://github.com/your-repo/Cartoonizer.git
cd Cartoonizer

# 2. Install dependencies
pip install -r source/requirements.txt
pip install pyinstaller

# 3. Build the app (one command!)
bash scripts/build_macos.sh

# 4. Test it
open dist/Cartoonizer.app
```

**Done!** The app should launch, open a loading window, and then the web UI in your browser.

### For Users

```bash
# 1. Download Cartoonizer-1.0.dmg
# 2. Double-click to mount the DMG
# 3. Drag Cartoonizer.app to Applications
# 4. Double-click Applications/Cartoonizer.app
```

---

## Detailed Build Process

### Prerequisites

- **macOS**: 10.15 or later (for app compatibility)
- **Python**: 3.9+ (from [python.org](https://www.python.org) or Homebrew)
- **Xcode Command Line Tools**: 
  ```bash
  xcode-select --install
  ```
- **PyInstaller**: Installed via pip

### Step 1: Verify Python Installation

```bash
python3 --version
# Output should be 3.9.x or higher
```

### Step 2: Install Dependencies

```bash
cd /path/to/Cartoonizer

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install project dependencies
pip install -r source/requirements.txt

# Install PyInstaller
pip install pyinstaller
```

### Step 3: Build the App

```bash
# Run the build script
bash scripts/build_macos.sh
```

**What happens:**
1. PyInstaller reads `packaging/macos/cartoonizer.spec`
2. Bundles Python runtime + all dependencies
3. Creates `dist/Cartoonizer.app` (the app bundle)
4. Optionally creates `dist/Cartoonizer-1.0.dmg` (installer)

**Build time**: 10–30 minutes (first time) / 5–10 minutes (subsequent builds)

### Step 4: Build Options

```bash
# Default: Build app AND DMG
bash scripts/build_macos.sh

# Build app without DMG (faster for testing)
bash scripts/build_macos.sh --no-dmg

# Build one-file bundle (slower startup, easier distribution)
bash scripts/build_macos.sh --one-file
```

### Step 5: Create DMG (if skipped)

```bash
# If you built with --no-dmg, create the DMG separately
bash scripts/make_dmg.sh
```

---

## Testing

### Test 1: Run from Source (Before Building)

```bash
python source/cartoonizer.py --gui
```

Expected behavior:
- Loading bar in terminal
- Browser opens to `http://127.0.0.1:7860`
- Upload an image and click "Generate"
- First run downloads ~7 GB of models (this is normal!)

### Test 2: Run the Built App

```bash
open dist/Cartoonizer.app
```

Expected behavior:
- Loading window appears
- After 30–60 seconds, browser opens
- Web UI is identical to source version

### Test 3: Installation Simulation

```bash
# Simulate user drag-and-drop installation
cp -r dist/Cartoonizer.app /tmp/test_app/Applications/Cartoonizer.app
open /tmp/test_app/Applications/Cartoonizer.app
```

### Test 4: First-Run Model Download

```bash
# First app launch should download models
open dist/Cartoonizer.app

# Check logs while it's running
tail -f ~/Library/Logs/Cartoonizer/app.log
```

### Test 5: DMG Installation

```bash
# Mount the DMG
open dist/Cartoonizer-1.0.dmg

# Drag the app to Applications (or just run from DMG)
# Then test it
```

### Test 6: Reset and Retry

```bash
# Clear cached models to simulate fresh user
rm -rf ~/Library/Application\ Support/Cartoonizer/hf_cache/

# Clear logs
rm -f ~/Library/Logs/Cartoonizer/app.log

# Test again
open dist/Cartoonizer.app
```

---

## Distribution

### Step 1: Test Build Thoroughly

```bash
bash scripts/build_macos.sh

# Run comprehensive tests
open dist/Cartoonizer.app
tail -f ~/Library/Logs/Cartoonizer/app.log
```

### Step 2: Create Release Notes

Create a `RELEASE_NOTES.md`:

```markdown
# Cartoonizer v1.0

## What's New
- Initial release
- Gradio-based web UI
- 5 style presets (Anime, Comic, Pixar, Sketch, Watercolor)
- Apple Silicon optimized

## Installation
1. Download `Cartoonizer-1.0.dmg`
2. Double-click to mount
3. Drag `Cartoonizer.app` to Applications
4. Launch from Applications folder

## System Requirements
- macOS 10.15 or later
- 6+ GB disk space (for AI models)
- 8 GB RAM (16 GB recommended)
- Apple Silicon (M1/M2/M3) or Intel (untested)

## Known Issues
- First run takes 1–2 minutes (model download)
- VRAM limited to 8 GB per image

## Support
- Check logs: `cat ~/Library/Logs/Cartoonizer/app.log`
- Reset app: `rm -rf ~/Library/Application\ Support/Cartoonizer/hf_cache/`
```

### Step 3: Create GitHub Release

```bash
# Create a git tag
git tag -a v1.0 -m "Release version 1.0"
git push origin v1.0

# Go to GitHub releases page
# Create new release from v1.0 tag
# Upload dist/Cartoonizer-1.0.dmg
# Paste release notes
```

### Step 4: Optional: Sign & Notarize the App

For distribution outside the App Store, you can sign and notarize the app (recommended for wider compatibility):

```bash
# This is a more involved process, see Apple's Developer documentation:
# https://developer.apple.com/documentation/xcode/notarizing_macos_software_before_distribution
```

---

## Troubleshooting

### Build Fails: "PyInstaller not found"

```bash
pip install pyinstaller
```

### Build Fails: Missing Dependencies

```bash
pip install -r source/requirements.txt
```

### Build Succeeds But App Won't Launch

1. Check logs:
   ```bash
   cat ~/Library/Logs/Cartoonizer/app.log
   ```

2. Common issues:
   - **Python 3.x not found**: Install Python from python.org
   - **Missing model cache**: App downloads on first run (normal, takes 1–2 min)
   - **Port 7860 in use**: App falls back to random port (check logs)

### App Says "Waiting for models..."

This is normal on first launch:
- Models download from Hugging Face (~7 GB)
- Network connection required
- Progress shows in logs

To speed up: 
- If you've built and run from source already, models are cached in `~/.cache/huggingface/`
- Copy them to `~/Library/Application Support/Cartoonizer/hf_cache/` before first app launch

### "App is damaged and cannot be opened"

macOS Gatekeeper blocks unsigned apps. Solution:

```bash
# Option 1: Right-click and "Open" in Finder
# Option 2: Remove quarantine attribute
xattr -d com.apple.quarantine ~/Applications/Cartoonizer.app
```

### App Opens But Browser Doesn't

The app starts the server, but browser auto-open failed. You can:
- Manually open `http://127.0.0.1:7860` (port may differ, check logs)
- Check logs for actual port: `grep "Starting at" ~/Library/Logs/Cartoonizer/app.log`

### App Crashes During Inference

Likely causes:
1. **Out of memory**: Reduce `MAX_IMAGE_SIDE` (default 768)
   ```bash
   export CARTOONIZER_MAX_SIDE=512
   open dist/Cartoonizer.app
   ```
2. **GPU memory issues**: App auto-enables memory-saving features on MPS

Check logs:
```bash
tail -50 ~/Library/Logs/Cartoonizer/app.log
```

---

## File Reference

### Build Configuration

- **[packaging/macos/cartoonizer.spec](packaging/macos/cartoonizer.spec)** – PyInstaller spec (defines what gets bundled)
- **[scripts/build_macos.sh](scripts/build_macos.sh)** – Main build automation script
- **[scripts/make_dmg.sh](scripts/make_dmg.sh)** – DMG creation script

### Source Code

- **[source/cartoonizer.py](source/cartoonizer.py)** – Main app (handles paths, logging, UI)
- **[source/requirements.txt](source/requirements.txt)** – Python dependencies
- **[source/assets/](source/assets/)** – App icon and web favicon

### Output

- **dist/Cartoonizer.app/** – App bundle (run this)
- **dist/Cartoonizer-1.0.dmg** – Installer DMG

---

## Advanced: Customization

### Change App Name

Edit `packaging/macos/cartoonizer.spec`:
```python
app = BUNDLE(
    coll,
    name="MyNewApp.app",  # Change this
    bundle_identifier="com.mycompany.newapp",  # And this
    ...
)
```

Then rebuild:
```bash
bash scripts/build_macos.sh
```

### Change App Icon

1. Create a 1024×1024 PNG
2. Convert to ICNS:
   ```bash
   python source/scripts/generate_icon.py your_icon.png
   ```
3. Update `packaging/macos/cartoonizer.spec` to point to your icon
4. Rebuild

### Add New Dependencies

1. Update `source/requirements.txt`
2. Update `packaging/macos/cartoonizer.spec` → `hidden_imports` list (if PyInstaller doesn't auto-detect)
3. Rebuild the app

---

## CI/CD Integration

To automate builds in GitHub Actions, create `.github/workflows/build-macos.yml`:

```yaml
name: Build macOS App

on:
  release:
    types: [published]

jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r source/requirements.txt pyinstaller
      - run: bash scripts/build_macos.sh
      - uses: softprops/action-gh-release@v1
        with:
          files: dist/Cartoonizer-*.dmg
```

This automatically builds the DMG whenever you create a GitHub release!

---

## Version Management

Update version everywhere when releasing:

1. **README.md** – Top-level version info
2. **packaging/macos/cartoonizer.spec** – DMG filename
3. **Git tag** – `git tag v1.1`
4. **GitHub Release** – Create release page

```bash
VERSION=1.1
sed -i '' "s/Cartoonizer-[0-9.]*\.dmg/Cartoonizer-$VERSION.dmg/" packaging/macos/cartoonizer.spec
git tag -a v$VERSION -m "Release $VERSION"
git push origin v$VERSION
```

---

## Questions?

Check:
1. Build logs: `tail -50 /tmp/cartoonizer_build.log` (if added to build script)
2. App logs: `cat ~/Library/Logs/Cartoonizer/app.log`
3. GitHub Issues: Your repo's issue tracker
