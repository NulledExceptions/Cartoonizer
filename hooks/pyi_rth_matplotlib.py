# -*- mode: python; coding: utf-8 -*-
"""
Runtime hook for matplotlib replacement.

This hook replaces matplotlib with a minimal stub module to prevent import errors
when Gradio tries to import it. The Gradio web UI doesn't actually use matplotlib
functionality.
"""

import sys
from types import ModuleType

# Create stub matplotlib module with minimal structure
matplotlib_stub = ModuleType("matplotlib")
matplotlib_stub.__version__ = "3.0.0"
matplotlib_stub.__file__ = __file__

# Add minimal pyplot stub
pyplot_stub = ModuleType("pyplot")
pyplot_stub.savefig = lambda *args, **kwargs: None
pyplot_stub.figure = lambda *args, **kwargs: None
pyplot_stub.close = lambda *args, **kwargs: None
pyplot_stub.plot = lambda *args, **kwargs: None
matplotlib_stub.pyplot = pyplot_stub

# Add minimal backends stub
backends_stub = ModuleType("backends")
backend_agg = ModuleType("backend_agg")
backends_stub.backend_agg = backend_agg
matplotlib_stub.backends = backends_stub

# Add minimal cbook stub
cbook_stub = ModuleType("cbook")
matplotlib_stub.cbook = cbook_stub

# Add _c_internal_utils stub
_c_internal_utils_stub = ModuleType("_c_internal_utils")
matplotlib_stub._c_internal_utils = _c_internal_utils_stub

# Add animation stub
animation_stub = ModuleType("animation")
animation_stub.PillowWriter = type("PillowWriter", (), {})
matplotlib_stub.animation = animation_stub

# Add colors stub
colors_stub = ModuleType("colors")
matplotlib_stub.colors = colors_stub

# Add data path function
def get_data_path():
    return ""

matplotlib_stub.get_data_path = get_data_path

# Install the stub before any matplotlib imports
sys.modules["matplotlib"] = matplotlib_stub
sys.modules["matplotlib.pyplot"] = pyplot_stub
sys.modules["matplotlib.backends"] = backends_stub
sys.modules["matplotlib.backends.backend_agg"] = backend_agg
sys.modules["matplotlib.cbook"] = cbook_stub
sys.modules["matplotlib._c_internal_utils"] = _c_internal_utils_stub
sys.modules["matplotlib.animation"] = animation_stub
sys.modules["matplotlib.colors"] = colors_stub
