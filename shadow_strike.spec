# -*- mode: python ; coding: utf-8 -*-
# PyInstaller build recipe for Shadow Strike.
#   pyinstaller --noconfirm --clean shadow_strike.spec
# Output: dist/ShadowStrike/ShadowStrike(.exe)   (folder build, fast startup)

a = Analysis(
    ["main.py"],
    pathex=["."],
    datas=[("assets", "assets")],
    hiddenimports=["scipy.ndimage"],
    # Don't exclude scipy submodules: scipy.ndimage pulls in scipy.special,
    # which needs scipy.linalg etc. Trimming them breaks the sprite loader.
    excludes=["tkinter", "matplotlib", "pandas", "IPython", "pytest", "cv2", "PIL"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ShadowStrike",
    console=False,          # no black console window
    upx=False,              # UPX triggers antivirus false-positives
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    upx=False,
    name="ShadowStrike",
)
