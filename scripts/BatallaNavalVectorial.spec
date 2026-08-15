# -*- mode: python ; coding: utf-8 -*-
# Spec de PyInstaller (onefile). Vive en scripts/ y resuelve la entrada main.py
# de forma absoluta hacia la raíz del proyecto, para que el build funcione
# se invoque desde donde se invoque.

import os

raiz = os.path.abspath(os.path.join(SPECPATH, os.pardir))

a = Analysis(
    [os.path.join(raiz, 'main.py')],
    pathex=[raiz],
    binaries=[],
    datas=[],
    hiddenimports=['matplotlib.backends.backend_tkagg', 'PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    name='BatallaNavalVectorial',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
