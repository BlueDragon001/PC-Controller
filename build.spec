# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Function to get valid datas
def get_datas():
    datas = []
    if os.path.exists('templates'):
        datas.append(('templates', 'templates'))
    if os.path.exists('static'):
        datas.append(('static', 'static'))
    if os.path.exists('users.json'):
        datas.append(('users.json', '.'))
    if os.path.exists('certs'):
        datas.append(('certs', 'certs'))
    
    # Check for nircmd.exe
    if not os.path.exists('nircmd.exe'):
        print("WARNING: nircmd.exe not found. Some features may not work.")
        print("Please download from: https://www.nirsoft.net/utils/nircmd.html")
    else:
        datas.append(('nircmd.exe', '.'))
    return datas

a = Analysis(
    ['pc_controller.py'],
    pathex=[],
    binaries=[],
    datas=get_datas(),
    hiddenimports=['waitress'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PC Controller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
