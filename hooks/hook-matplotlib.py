# -*- mode: python; coding: utf-8 -*-
"""
PyInstaller hook for matplotlib on macOS.

This hook prevents matplotlib from being included in the bundle because:
1. PyInstaller has issues bundling matplotlib._c_internal_utils on macOS arm64
2. The Gradio web UI doesn't actually require matplotlib
3. Matplotlib is only used for static plots which Gradio can handle without it

This hook replaces matplotlib with a stub to prevent import errors.
"""

datas = []
binaries = []
hiddenimports = []
excludedimports = ["matplotlib", "matplotlib.cbook", "matplotlib.pyplot"]
