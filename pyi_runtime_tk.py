"""Runtime Tcl/Tk paths for PyInstaller builds."""

from __future__ import annotations

import os
import sys
from pathlib import Path


base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
tcl_dir = base / "tcl"
if tcl_dir.exists():
    os.environ.setdefault("TCL_LIBRARY", str(tcl_dir / "tcl8.6"))
    os.environ.setdefault("TK_LIBRARY", str(tcl_dir / "tk8.6"))
