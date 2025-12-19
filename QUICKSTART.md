# Cartoonizer macOS - Quick Reference Card

## For Users: Install & Run

```
1. Download: Cartoonizer-1.0.dmg
2. Mount:    Double-click the DMG
3. Install:  Drag Cartoonizer.app → /Applications
4. Run:      Double-click /Applications/Cartoonizer.app
5. Wait:     First run takes 1–2 min (downloading AI models)
6. Enjoy:    Upload images, click Generate!
```

**Troubleshooting:**
- "App is damaged?" → `xattr -d com.apple.quarantine /Applications/Cartoonizer.app`
- "Models downloading?" → Check `~/Library/Logs/Cartoonizer/app.log`
- "Browser didn't open?" → Open `http://127.0.0.1:7860` manually

---

## For Developers: Build & Test

### Build the App (One Command)

```bash
cd /path/to/Cartoonizer
pip install -r source/requirements.txt pyinstaller
bash scripts/build_macos.sh
```

**Output:**
- `dist/Cartoonizer.app` – The app (ready to run)
- `dist/Cartoonizer-1.0.dmg` – Installer (ready to distribute)

### Test the Build

```bash
# Run the built app
open dist/Cartoonizer.app

# Or test from source
python source/cartoonizer.py --gui

# Watch logs while testing
tail -f ~/Library/Logs/Cartoonizer/app.log
```

### Build Options

```bash
# Skip DMG creation (faster for testing)
bash scripts/build_macos.sh --no-dmg

# Create one-file bundle (slower startup, easier to distribute)
bash scripts/build_macos.sh --one-file
```

---

## File Map

| Path | Purpose | Status |
|------|---------|--------|
| `source/cartoonizer.py` | Main app (Gradio UI + AI) | ✅ Updated for bundled paths |
| `source/requirements.txt` | Python dependencies | ✅ All pinned versions |
| `packaging/macos/cartoonizer.spec` | PyInstaller config | ✅ New (296 lines) |
| `scripts/build_macos.sh` | Build automation | ✅ New (138 lines) |
| `scripts/make_dmg.sh` | DMG creation | ✅ New (90 lines) |
| `README.md` | User & dev guide | ✅ Completely rewritten |
| `BUILD_GUIDE.md` | Technical build details | ✅ New (455 lines) |
| `DEPLOYMENT.md` | Distribution guidance | ✅ New (430 lines) |
| `IMPLEMENTATION_SUMMARY.md` | This project's summary | ✅ New (410 lines) |

---

## What's New

### Path Handling
```python
# cartoonizer.py now detects bundled vs. source environment
get_app_root()      # Returns correct root (PyInstaller or source)
find_asset(file)    # Locates files in bundle or source
setup_logging()     # Logs to ~/Library/Logs/Cartoonizer/app.log
```

### Build Configuration
- PyInstaller spec with hidden imports, data files, icon
- Automated build script with options (--one-file, --no-dmg)
- DMG creation script with proper structure

### Documentation
- Comprehensive README (281 lines) – user & dev focused
- BUILD_GUIDE.md (455 lines) – technical details, testing, troubleshooting
- DEPLOYMENT.md (430 lines) – distribution, support, marketing
- IMPLEMENTATION_SUMMARY.md (410 lines) – what was done

---

## Distribution Workflow

```
1. Build:
   bash scripts/build_macos.sh

2. Test:
   open dist/Cartoonizer.app

3. Create Release:
   git tag -a v1.0
   git push origin v1.0

4. Upload:
   Go to GitHub Releases
   Create new release from v1.0 tag
   Upload dist/Cartoonizer-1.0.dmg

5. Announce:
   Social media, Reddit, Hacker News, etc.

6. Support:
   Monitor GitHub Issues
   Respond to user feedback
   Fix bugs and release updates
```

---

## Technical Details

### App Bundle Structure (After Build)

```
Cartoonizer.app/
├── Contents/
│   ├── MacOS/
│   │   └── cartoonizer          # Executable (PyInstaller-generated)
│   ├── Resources/
│   │   ├── cartoonizer.py       # Main app code
│   │   ├── assets/              # Images, icons
│   │   ├── requirements.txt      # Dependency reference
│   │   └── [hundreds of .so files, python libs, etc.]
│   └── Info.plist               # App metadata
└── MacOS/...                     # Symlink to Contents/MacOS
```

### Data Locations

| Data | Location | Writable |
|------|----------|----------|
| App bundle | `/Applications/Cartoonizer.app` | ❌ Read-only |
| AI models | `~/Library/Application Support/Cartoonizer/hf_cache/` | ✅ Yes |
| App logs | `~/Library/Logs/Cartoonizer/app.log` | ✅ Yes |
| Config | `~/Library/Application Support/Cartoonizer/` | ✅ Yes |

---

## Common Tasks

### Update Dependencies

```bash
# Edit source/requirements.txt
# Then rebuild
bash scripts/build_macos.sh
```

### Change App Icon

```bash
# Create a 1024×1024 PNG, convert to ICNS
python source/scripts/generate_icon.py my_icon.png

# Update packaging/macos/cartoonizer.spec
# Rebuild
bash scripts/build_macos.sh
```

### Change App Name/Bundle ID

Edit `packaging/macos/cartoonizer.spec`:
```python
app = BUNDLE(
    coll,
    name="MyNewApp.app",  # Change this
    bundle_identifier="com.mycompany.app",  # And this
    ...
)
```

Then rebuild: `bash scripts/build_macos.sh`

### Run CLI Mode (Batch Processing)

```bash
python source/cartoonizer.py \
  --input photo.jpg \
  --output cartoon.png \
  --style anime
```

---

## System Requirements

**For Building:**
- macOS 10.15+
- Python 3.9+
- PyInstaller (installed via pip)
- 2 GB free disk (build output)

**For Running (Users):**
- macOS 10.15+
- 20–30 GB free disk (including AI models)
- 8 GB RAM (16 GB recommended for comfortable use)
- Internet (first run only, to download models)

---

## Troubleshooting

### Build Fails

```bash
# Check Python
python3 --version  # Should be 3.9+

# Check PyInstaller
pip install pyinstaller

# Rebuild
bash scripts/build_macos.sh
```

### App Won't Launch

```bash
# Check logs
cat ~/Library/Logs/Cartoonizer/app.log

# Reset app
rm -rf ~/Library/Application\ Support/Cartoonizer/hf_cache/

# Try again
open dist/Cartoonizer.app
```

### "Gatekeeper" Warning

```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine /Applications/Cartoonizer.app

# Or: Right-click app, select "Open", click "Open" in dialog
```

---

## Key Numbers

| Metric | Value |
|--------|-------|
| App size (bundled) | ~2.5 GB |
| Models (first download) | ~7 GB |
| Build time (first) | 10–30 min |
| Build time (cached) | 5–10 min |
| First-run setup | 1–2 min |
| Single image generation | 20–60 sec |
| Python bundled version | 3.9–3.11 |
| macOS requirement | 10.15+ |

---

## Documentation Files

- **README.md** – Start here (user & dev guide)
- **BUILD_GUIDE.md** – Technical building and testing
- **DEPLOYMENT.md** – Distribution and post-launch
- **IMPLEMENTATION_SUMMARY.md** – What was done (detailed reference)

---

## One-Line Builders

```bash
# Quick build (app + DMG)
bash scripts/build_macos.sh

# Test build (no DMG)
bash scripts/build_macos.sh --no-dmg

# Just DMG (if app already exists)
bash scripts/make_dmg.sh

# Manual PyInstaller (advanced)
pyinstaller packaging/macos/cartoonizer.spec
```

---

## Before You Distribute

- [ ] Build and test on your machine
- [ ] Run: `open dist/Cartoonizer.app` ✓
- [ ] Upload image and generate cartoon ✓
- [ ] Check logs: `cat ~/Library/Logs/Cartoonizer/app.log` ✓
- [ ] DMG mounts and installs correctly ✓
- [ ] Re-installed app works ✓
- [ ] README is clear ✓
- [ ] License file included ✓
- [ ] GitHub release ready ✓

---

## After You Distribute

- [ ] Monitor GitHub Issues
- [ ] Respond to user feedback
- [ ] Fix bugs promptly
- [ ] Release updates regularly
- [ ] Keep dependencies current

---

## Support

- **Installation Help** → See README.md "Quick Start"
- **Build Issues** → See BUILD_GUIDE.md "Troubleshooting"
- **Distribution Questions** → See DEPLOYMENT.md
- **Technical Details** → See IMPLEMENTATION_SUMMARY.md

---

**Created:** December 18, 2024  
**Version:** 1.0  
**Status:** ✅ Ready to Build & Distribute
