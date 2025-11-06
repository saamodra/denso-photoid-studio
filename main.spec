# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import pathlib
from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT


block_cipher = None

# Collect ONNX Runtime dynamic libraries (DLLs/SOs)
onnx_bins = collect_dynamic_libs('onnxruntime')

# Ensure Python DLL and VC runtimes are explicitly bundled (defensive on some setups)
_bins_extra = []
_base_prefix = pathlib.Path(sys.base_prefix)
_exec_prefix = pathlib.Path(sys.exec_prefix)
_dll_name = f"python{sys.version_info.major}{sys.version_info.minor}.dll"
_candidates = [
    _base_prefix / _dll_name,
    _exec_prefix / _dll_name,
]
for c in _candidates:
    if c.exists():
        _bins_extra.append((str(c), '.'))
        break

# Common VC runtime dlls
for vc in ("vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll"):
    for root in (_base_prefix, _exec_prefix):
        p = root / vc
        if p.exists():
            _bins_extra.append((str(p), '.'))
            break

onnx_bins = onnx_bins + _bins_extra

# Minimal hidden imports (avoid pulling CLI extras like click, onnx quantization)
hiddenimports = ['rembg', 'onnxruntime']

# Build datas list for all files under assets/ recursively
assets_root = pathlib.Path('assets')
assets_datas = []
if assets_root.exists():
    for path in assets_root.rglob('*'):
        if path.is_file():
            rel = path.relative_to(assets_root)
            # Destination must be a directory, not include the filename.
            # Place the file under 'assets/<relative parent dir>'
            rel_parent = rel.parent
            if str(rel_parent) in ('', '.'):
                dest_dir = 'assets'
            else:
                dest_dir = os.path.join('assets', str(rel_parent))
            assets_datas.append((str(path), dest_dir))

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=onnx_bins,
    datas=assets_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='denso-photoid-studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Debug/diagnostic console build to reveal runtime errors in a terminal
exe_console = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='denso-photoid-studio-console',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    exe_console,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='denso-photoid-studio'
)
