# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('gata.png', '.')],
    hiddenimports=[
        'flet',
        'sqlite3',
        'datetime',
        'asyncio',
        'traceback',
        'pandas',
        'relatorio',
        'database',
        'qrcode',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Graça_Presentes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='compras-online.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    a.zipfiles,
    name='Graça_Presentes',
    strip=False,
    upx=True,
    upx_exclude=[],
)