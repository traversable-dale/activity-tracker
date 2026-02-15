# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Activity Tracker (Windows)

Build commands:
    # Single file (easier to distribute)
    pyinstaller ActivityTracker-onefile.spec
    
    # Folder mode (faster startup)
    pyinstaller ActivityTracker.spec

Output: dist/Activity Tracker.exe
"""

block_cipher = None

a = Analysis(
    ['activity_tracker.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/bg/background.png', 'assets/bg'),  # Include background image
        ('ref/TDT-logo-white-circle.ico', 'ref'),   # Include icon file
    ],
    hiddenimports=[
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# FOLDER MODE BUILD (faster startup)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Activity Tracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ref/TDT-logo-white-circle.ico',  # Custom icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Activity Tracker',
)
