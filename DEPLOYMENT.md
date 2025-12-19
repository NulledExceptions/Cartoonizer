# Cartoonizer Deployment & Distribution Guide

How to package, distribute, and support Cartoonizer for macOS users.

---

## Distribution Methods

### Method 1: GitHub Releases (Recommended)

**Pros**: Free, easy version management, built-in download counter
**Cons**: Users must download manually

```bash
# 1. Build the DMG
bash scripts/build_macos.sh

# 2. Create a GitHub release
# Go to: https://github.com/your-repo/releases/new

# 3. Upload the DMG file
# Attach: dist/Cartoonizer-1.0.dmg

# 4. Add installation instructions
```

**Installation instructions for users:**

> 1. Download `Cartoonizer-1.0.dmg` from the Releases page
> 2. Double-click the DMG to mount it
> 3. Drag `Cartoonizer.app` to the `/Applications` folder
> 4. Double-click `Cartoonizer.app` to launch
> 5. On first run, wait for AI models to download (1–2 minutes)

### Method 2: Direct Website Download

1. Upload `dist/Cartoonizer-1.0.dmg` to your website
2. Link to it from your download page
3. Users download and install the same way as GitHub Releases

### Method 3: Homebrew (Advanced)

Package Cartoonizer in Homebrew for one-command installation:

```bash
brew install cartoonizer
```

Requires creating a Homebrew formula (`.rb` file). See [Homebrew documentation](https://docs.brew.sh/Formula-Cookbook).

### Method 4: App Store (Apple Distribution)

Most professional approach, but requires:
- Apple Developer Program membership ($99/year)
- App signing certificate
- Notarization process
- App Review submission

Only recommended for professional/commercial apps.

---

## Installation Experience

### What Users Will See

**1. Download**
- Click download link, get `Cartoonizer-1.0.dmg`

**2. Mount DMG**
- Double-click DMG → a new "Cartoonizer" drive appears in Finder
- (Or does nothing if already mounted)

**3. Drag to Applications**
- Drag `Cartoonizer.app` to the `Applications` folder
- Or run it directly from the DMG (slower, but works)

**4. First Launch**
- Double-click the app in Applications (or Launchpad)
- macOS may ask: "Are you sure?" (Gatekeeper)
  - Click "Open" to proceed
- Loading window appears
- Browser opens to the web UI
- App is ready!

**5. Model Download (First Run Only)**
- First generation takes 1–2 minutes
- ~7 GB of AI models download from Hugging Face
- Progress shown in terminal-like status window
- Happens only once; subsequent generations are fast

### Error Scenarios & Solutions

#### "App is damaged and cannot be opened"

**Cause**: macOS Gatekeeper blocks unsigned apps

**Solution** (send users this):
```bash
# Open Terminal and run:
xattr -d com.apple.quarantine /Applications/Cartoonizer.app

# Or:
# Right-click the app, select "Open", then "Open" in the dialog
```

#### "Waiting for models to download..."

**Cause**: First run, normal behavior

**Solution**:
- Let it run for 1–2 minutes
- Check progress: `cat ~/Library/Logs/Cartoonizer/app.log`
- Ensure internet connection is active

#### "Browser doesn't open automatically"

**Cause**: Webbrowser auto-open failed (headless system, etc.)

**Solution**:
- Check logs for the port: `cat ~/Library/Logs/Cartoonizer/app.log`
- Manually open: `http://127.0.0.1:7860` (or the port shown in logs)

#### "App crashes immediately"

**Cause**: Missing dependencies, Python issues, or out of memory

**Solution**:
1. Check logs: `cat ~/Library/Logs/Cartoonizer/app.log`
2. Reset app data:
   ```bash
   rm -rf ~/Library/Application\ Support/Cartoonizer/hf_cache/
   rm ~/Library/Logs/Cartoonizer/app.log
   ```
3. Relaunch and try again

---

## User Support Resources

### Create a Support Page

Suggested content:

```markdown
# Cartoonizer Support

## Installation
1. Download Cartoonizer-1.0.dmg
2. Double-click to mount
3. Drag Cartoonizer.app to Applications
4. Launch from Applications folder

## Troubleshooting

### "App is damaged"
xattr -d com.apple.quarantine /Applications/Cartoonizer.app

### Slow first run
First launch downloads 7 GB of AI models (one-time only).

### Reset the app
rm -rf ~/Library/Application\ Support/Cartoonizer/hf_cache/

### Check logs
cat ~/Library/Logs/Cartoonizer/app.log

## FAQ

**Q: Does it send images to the cloud?**
A: No, everything runs locally on your Mac.

**Q: How much disk space do I need?**
A: 20–30 GB (including downloaded AI models).

**Q: What about privacy?**
A: All processing happens on your computer. No data leaves your Mac.

**Q: Can I use it offline?**
A: After first run (when models are cached), yes.

**Q: Does it work on M1/M2 Macs?**
A: Yes, fully optimized for Apple Silicon.

## Contact
- Email: support@example.com
- GitHub Issues: github.com/your-repo/issues
```

### Knowledge Base / FAQ

Host on a wiki or documentation site (GitHub Pages, Notion, etc.)

---

## Version Updates

### Releasing a New Version

1. **Update code and test:**
   ```bash
   python source/cartoonizer.py --gui
   # Test thoroughly
   ```

2. **Build the new DMG:**
   ```bash
   bash scripts/build_macos.sh
   ```

3. **Test the new build:**
   ```bash
   open dist/Cartoonizer.app
   ```

4. **Create a GitHub Release:**
   - Go to your repo's Releases
   - Click "Draft a new release"
   - Tag: `v1.1` (increment from v1.0)
   - Release name: "Version 1.1"
   - Upload: `dist/Cartoonizer-1.1.dmg`
   - Write release notes

**Release notes template:**

```markdown
## v1.1 (Date)

### New Features
- Feature 1
- Feature 2

### Bug Fixes
- Fix 1
- Fix 2

### Installation
Download `Cartoonizer-1.1.dmg` and drag to Applications.

### Upgrade Notes
If upgrading from v1.0:
1. Quit the current app
2. Drag new Cartoonizer.app to Applications (confirm replacement)
3. Launch the new version

Your existing settings/models will be preserved.
```

### In-App Update Notifications

(Optional) Add an update check in `cartoonizer.py`:

```python
def check_for_updates():
    """Check GitHub releases for newer version."""
    try:
        import requests
        resp = requests.get(
            "https://api.github.com/repos/your-repo/releases/latest",
            timeout=2
        )
        latest = resp.json().get("tag_name", "v1.0")
        current = "v1.0"
        if latest > current:
            log(f"Update available: {latest}")
            # Optional: show notification to user
    except Exception:
        pass  # Silently fail if GitHub is unreachable
```

---

## Monitoring & Feedback

### User Feedback Channels

1. **GitHub Issues** – Bug reports and feature requests
2. **Email** – Direct support inquiries
3. **Surveys** – Post-launch feedback (optional)

### Crash Reporting (Optional)

Set up crash logs collection:

```python
# In cartoonizer.py
import traceback
import time

def log_crash(exc):
    """Log crash details for debugging."""
    crash_log = Path.home() / "Library/Logs/Cartoonizer/crashes.log"
    crash_log.parent.mkdir(parents=True, exist_ok=True)
    
    with open(crash_log, "a") as f:
        f.write(f"\n=== Crash at {time.ctime()} ===\n")
        f.write(traceback.format_exc())
```

You could ask users to upload `~/Library/Logs/Cartoonizer/crashes.log` when reporting bugs.

---

## Analytics (Privacy-Respecting)

Optional: Track feature usage without compromising privacy:

```python
def record_usage(action):
    """Record anonymized usage event."""
    # Example: Count cartoonizations per day
    usage_log = Path.home() / "Library/Application Support/Cartoonizer/usage.json"
    
    # Record only: action name + timestamp (no image data)
    import json
    event = {"action": action, "timestamp": time.time()}
    
    # Users can see/delete this file anytime
    # Upload is opt-in only
```

**Important**: Always be transparent about what you collect!

---

## Legal & Licensing

### License File

Include a [LICENSE](LICENSE) file in the repo (e.g., MIT, Apache 2.0):

```markdown
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

### Terms of Service (Optional)

If distributing commercially, create a ToS explaining:
- What users can/cannot do with generated images
- Data collection (if any)
- Liability limitations
- AI model licenses (Stable Diffusion has its own license)

### Third-Party Licenses

Document licenses of dependencies:
- PyTorch
- Diffusers
- Gradio
- etc.

Create [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md):

```markdown
# Third-Party Licenses

## PyTorch
Apache License 2.0

## Diffusers
Apache License 2.0

## Gradio
Apache License 2.0

## Stable Diffusion
CreativeML Open RAIL License
```

---

## Marketing & Outreach

### Positioning

"Cartoonizer: Transform photos to cartoons locally, without cloud uploads. Fast, private, powered by AI."

### Social Media Posts

**Twitter/X:**
> 🎨 Cartoonizer is here! Turn any photo into a cartoon using AI on your Mac. No cloud, no data leaves your computer. Download now: [link]

**Reddit/Hacker News:**
> I built a macOS app that turns photos into cartoons using Stable Diffusion. Everything runs locally. [GitHub link]

### Product Hunt (Optional)

If you want broader exposure, submit to Product Hunt:
- https://www.producthunt.com
- Timing: Launch on Tuesday–Thursday for best engagement
- Get upvotes from your audience

### Blog Post

Write a launch post:
- What problem does it solve?
- How it works technically
- Installation instructions
- Example outputs
- Call to action (download link)

---

## Post-Launch Support

### Monitor Issues

1. Check GitHub Issues daily
2. Respond to bug reports within 24 hours
3. Create fixes and release updates frequently

### Community Management

- Thank contributors
- Feature interesting user examples
- Highlight issues that got fixed
- Share usage tips/tricks

### Long-Term Maintenance

- Keep dependencies updated
- Monitor PyInstaller releases
- Test on new macOS versions
- Deprecate old macOS versions as needed

---

## Checklist: Before Distributing

- [ ] Build succeeds: `bash scripts/build_macos.sh`
- [ ] App launches: `open dist/Cartoonizer.app`
- [ ] Browser opens automatically
- [ ] Image processing works
- [ ] Models download on first run
- [ ] Logs are created correctly
- [ ] App can be quit gracefully
- [ ] Reinstall test: Copy app, remove, reinstall from DMG
- [ ] README updated with build/install instructions
- [ ] LICENSE file included
- [ ] Third-party licenses documented
- [ ] GitHub repo is public (if applicable)
- [ ] Release page has download links
- [ ] Support contact info is clear

---

## Checklist: After Distribution

- [ ] Monitor GitHub Issues daily
- [ ] Respond to user feedback
- [ ] Fix critical bugs promptly
- [ ] Release updates regularly
- [ ] Keep dependencies current
- [ ] Test on new macOS versions

---

## Quick Reference: Build & Release Commands

```bash
# Full release workflow
cd /path/to/Cartoonizer
bash scripts/build_macos.sh
open dist/Cartoonizer.app
# Test thoroughly...
git tag -a v1.0 -m "Release 1.0"
git push origin v1.0
# Go to GitHub Releases, create release, upload DMG
```

---

## Questions?

This guide covers the most common distribution scenarios. For questions not addressed, check:

- [BUILD_GUIDE.md](BUILD_GUIDE.md) – Technical build details
- [README.md](README.md) – Installation instructions for users
- PyInstaller docs: https://pyinstaller.org
- macOS app development: https://developer.apple.com/macos/

Happy distributing! 🚀
