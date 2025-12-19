# Cartoonizer macOS App

Transform photos into cartoons using AI. A native macOS app powered by Stable Diffusion.

## Quick Start (Users)

1. **Download** `Cartoonizer-1.0.dmg` from [Releases](https://github.com/your-repo/releases)
2. **Mount the DMG** by double-clicking it
3. **Drag** `Cartoonizer.app` to `/Applications` folder (or anywhere you prefer)
4. **Launch** by double-clicking `Cartoonizer.app` in Applications
5. **On first run**, wait 1–2 minutes while the app downloads AI models (~7 GB)

That's it! No terminal, no `pip install`, no manual setup. The app handles everything.

### First-Run Experience

- A **loading window** appears showing progress
- The **web UI** opens automatically in your default browser
- You can start uploading images and generating cartoons immediately
- Logs are saved to `~/Library/Logs/Cartoonizer/app.log`

### Troubleshooting

**"App is damaged and cannot be opened"**
- Right-click the app, select "Open", then click "Open" in the confirmation dialog (macOS Gatekeeper)
- Or run: `xattr -d com.apple.quarantine /Applications/Cartoonizer.app`

**"Waiting for models to download..."**
- First run downloads ~7 GB of AI models from Hugging Face
- Internet connection is required
- Check `~/Library/Logs/Cartoonizer/app.log` to monitor progress

**App crashes or browser doesn't open**
- Check logs: `cat ~/Library/Logs/Cartoonizer/app.log`
- Reset cached models: `rm -rf ~/Library/Application\ Support/Cartoonizer/hf_cache/`
- Restart the app

---

## Development & Building

### Prerequisites

- macOS 10.15 or later
- Python 3.9+ (from python.org or via Homebrew)
- PyInstaller
- Git

### Setup for Development

```bash
# Clone the repository
git clone https://github.com/your-repo/Cartoonizer.git
cd Cartoonizer

# Install Python dependencies
pip install -r source/requirements.txt

# Install PyInstaller
pip install pyinstaller
```

### Running from Source

```bash
# Run the GUI
python source/cartoonizer.py --gui

# Or use CLI mode (batch processing)
python source/cartoonizer.py --input input.jpg --output output.png --style anime
```

### Building the macOS App

#### Option 1: Quick Build (Recommended)

```bash
# Build the .app and DMG
bash scripts/build_macos.sh

# Output: dist/Cartoonizer.app
#         dist/Cartoonizer-1.0.dmg
```

Then test it:
```bash
open dist/Cartoonizer.app
```

#### Option 2: Build Without DMG

```bash
bash scripts/build_macos.sh --no-dmg
```

#### Option 3: Manual PyInstaller Build

```bash
# Build using the spec file directly
pyinstaller packaging/macos/cartoonizer.spec

# The app will be in: dist/Cartoonizer.app
```

### Creating a DMG Installer

```bash
# If you already have dist/Cartoonizer.app, create a DMG:
bash scripts/make_dmg.sh

# Or specify custom paths:
bash scripts/make_dmg.sh /path/to/Cartoonizer.app /path/to/output.dmg
```

### Code Structure

```
Cartoonizer/
├── source/
│   ├── cartoonizer.py          # Main app (Gradio GUI + CLI)
│   ├── requirements.txt         # Python dependencies
│   ├── assets/                  # Icons, images
│   │   ├── Cartoonizer.icns    # macOS app icon
│   │   └── cartoonizer_web_icon.png
│   ├── Info.plist              # App metadata (legacy)
│   └── cartoonizer_launcher    # Shell launcher (legacy)
├── packaging/
│   └── macos/
│       └── cartoonizer.spec     # PyInstaller configuration
├── scripts/
│   ├── build_macos.sh           # Build the .app bundle
│   ├── make_dmg.sh              # Create DMG installer
│   └── generate_icon.py         # Generate icons
└── README.md                     # This file
```

### What's Bundled in the App

- **Python runtime** (embedded)
- **All dependencies** (torch, diffusers, gradio, etc.)
- **Cartoonizer code** (cartoonizer.py)
- **App icon** (Cartoonizer.icns)
- **Web favicon** (cartoonizer_web_icon.png)

### Persistent Data Location

The app stores data in `~/Library/Application Support/Cartoonizer/`:
- `hf_cache/` – Downloaded AI models (4–7 GB)
- `app.log` – Application logs

This location is writable even when the app is installed in `/Applications` (read-only).

### Logs and Debugging

Application logs are written to:
```
~/Library/Logs/Cartoonizer/app.log
```

Check this file if the app fails to start:
```bash
tail -f ~/Library/Logs/Cartoonizer/app.log
```

### Build Artifacts

After `bash scripts/build_macos.sh`, you'll find:

```
dist/
├── Cartoonizer.app/        # The macOS app bundle (ready to run)
└── Cartoonizer-1.0.dmg     # DMG installer (drag-and-drop)
```

### Distributing Your Build

1. **Test the app:**
   ```bash
   open dist/Cartoonizer.app
   ```

2. **Create a DMG for distribution:**
   ```bash
   bash scripts/make_dmg.sh dist/Cartoonizer.app dist/Cartoonizer-1.0.dmg
   ```

3. **Upload to GitHub Releases:**
   - Go to your repo's Releases page
   - Create a new release
   - Upload the `.dmg` file
   - Add installation instructions (see "Quick Start" above)

4. **Optional: Notarize the app** (for wider compatibility):
   ```bash
   # Apple requires notarization for distribution outside the App Store
   # This is a more complex process, covered in Apple's documentation
   ```

### Customization

#### Change App Icon

1. Create a 1024×1024 PNG with your logo
2. Convert to ICNS using:
   ```bash
   python source/scripts/generate_icon.py your_image.png
   ```
3. Update the spec file to reference your icon

#### Change App Name/Bundle ID

Edit `packaging/macos/cartoonizer.spec`:
```python
app = BUNDLE(
    coll,
    name="YourApp.app",
    bundle_identifier="com.yourcompany.yourapp",
    ...
)
```

---

## Architecture

### GUI Mode (Default)

When you run `python cartoonizer.py --gui`:

1. App starts the **Gradio web server** on `127.0.0.1:7860` (or next available port)
2. Opens **default browser** automatically
3. Serves web UI with real-time cartoonization
4. Keeps server running until you close the browser or quit the app

### CLI Mode

For batch processing:

```bash
python cartoonizer.py --input photo.jpg --output cartoon.png --style anime
```

### AI Model

- **Base**: Stable Diffusion 1.5 via HuggingFace `Lykon/dreamshaper-8`
- **Inference method**: Image-to-image with style prompts
- **Hardware acceleration**: Apple Metal Performance Shaders (MPS) on Apple Silicon

### Styles

- **Anime** – Clean cel-shaded style
- **Comic** – Bold inks and halftones
- **Pixar** – 3D-rendered look
- **Sketch** – Line art with minimal shading
- **Watercolor** – Soft, painterly appearance

---

## Known Limitations

- **First run is slow**: Model download + GPU memory setup takes 1–2 minutes
- **VRAM requirement**: 6 GB of GPU memory (Macs with <8 GB RAM may be slow)
- **Apple Silicon only**: Optimized for M1/M2/M3. Intel Macs may work but untested
- **Offline model cache**: Once downloaded, models are cached in `~/Library/Application Support/Cartoonizer/`

---

## License

See [LICENSE](LICENSE)

---

## Contributing

This repository contains:
- `/source/` – Main Python app and UI
- `/packaging/` – macOS build configuration
- `/scripts/` – Build automation

Contributions welcome! Please:

1. Test changes with `python source/cartoonizer.py --gui`
2. Build a test `.app` and verify it works
3. Submit a PR with your changes

---

## Version History

### v1.0 (Current)
- Initial release
- Gradio-based web UI
- Stable Diffusion img2img cartoonization
- macOS app bundle via PyInstaller
- DMG installer support
