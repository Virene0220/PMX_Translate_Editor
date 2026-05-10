# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys


python_root = Path(sys.base_prefix)
dll_dir = python_root / "DLLs"
lib_dir = python_root / "Lib"
tcl_dir = python_root / "tcl"
project_dir = Path.cwd()
icon_ico = project_dir / "app_icon.ico"
icon_png = project_dir / "app_icon.png"
asset_datas = []
if icon_ico.exists():
    asset_datas.append((str(icon_ico), "."))
if icon_png.exists():
    asset_datas.append((str(icon_png), "."))


a = Analysis(
    ["pmx_translate_tool.py"],
    pathex=[],
    binaries=[
        (str(dll_dir / "_tkinter.pyd"), "."),
        (str(dll_dir / "tcl86t.dll"), "."),
        (str(dll_dir / "tk86t.dll"), "."),
    ],
    datas=[
        (str(lib_dir / "tkinter"), "tkinter"),
        (str(tcl_dir / "tcl8.6"), "tcl\\tcl8.6"),
        (str(tcl_dir / "tk8.6"), "tcl\\tk8.6"),
    ]
    + asset_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["pyi_runtime_tk.py"],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PMXTranslateEditor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_ico) if icon_ico.exists() else None,
)
