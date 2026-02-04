# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import collect_submodules
from pathlib import Path

# Collect hidden imports for dynamic imports under models.admindashboard
_hiddenimports = collect_submodules('models.admindashboard')

# Collect all files (py, resources) under src/models/admindashboard and preserve subfolders
_extra_datas = []
for p in Path('src/models/admindashboard').rglob('*'):
    if p.is_file():
        # Place files under the same relative path inside the bundle
        rel = p.relative_to('src/models/admindashboard')
        dest = Path('models/admindashboard') / rel
        _extra_datas.append((str(p), str(dest.parent)))

a = Analysis(
    ['src\\models\\admindashboard\\dashboardadmin.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src\\models\\admindashboard\\logo.gif', 'models/admindashboard')] + _extra_datas,
    hiddenimports=_hiddenimports,
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
    [],
    exclude_binaries=True,
    name='KambaFarmaAdmin',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KambaFarmaAdmin',
)
