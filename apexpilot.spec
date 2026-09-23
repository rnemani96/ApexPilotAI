# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

added_data = [
    ('core/ocr_runner.ps1', 'core'),
]

hidden_imports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'httpx',
    'httpcore',
    'Pillow',
    'PIL',
    'PIL.Image',
    'PIL.ImageGrab',
    'keyboard',
    'numpy',
    'sounddevice',
    '_cffi_backend'
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_data,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ApexPilotAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ApexPilotAI',
)
