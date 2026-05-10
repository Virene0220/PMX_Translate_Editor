# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pmx_translate_tool.py'],
    pathex=[],
    binaries=[('C:\\Users\\MSI\\AppData\\Local\\Programs\\Python\\Python314\\DLLs\\_tkinter.pyd', '.'), ('C:\\Users\\MSI\\AppData\\Local\\Programs\\Python\\Python314\\DLLs\\tcl86t.dll', '.'), ('C:\\Users\\MSI\\AppData\\Local\\Programs\\Python\\Python314\\DLLs\\tk86t.dll', '.')],
    datas=[('C:\\Users\\MSI\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\tkinter', 'tkinter'), ('C:\\Users\\MSI\\AppData\\Local\\Programs\\Python\\Python314\\tcl\\tcl8.6', 'tcl\\tcl8.6'), ('C:\\Users\\MSI\\AppData\\Local\\Programs\\Python\\Python314\\tcl\\tk8.6', 'tcl\\tk8.6')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_runtime_tk.py'],
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
    name='PMXTranslateEditor',
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
)
