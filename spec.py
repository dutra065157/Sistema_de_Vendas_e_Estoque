from PyInstaller.building.build_main import Analysis, EXE
from PyInstaller.building.datastruct import TOC
from PyInstaller.building.osx import BUNDLE

# Nome do seu script principal
script_name = 'app.py'  # substitua pelo nome do seu arquivo

# Análise das dependências
a = Analysis(
    [script_name],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'flet',
        'sqlite3',
        'datetime',
        'asyncio',
        'traceback',
        'pandas',
        'relatorio',
        'database',
        # Adicione outras dependências se necessário
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Configurações do executável
exe = EXE(
    a.pure,
    a.zipped_data,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Graça_Presentes',  # Nome do executável
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Comprimir o executável (opcional)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Mude para True se quiser ver o console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='compras-online.ico',  # Adicione um ícone se quiser
)
