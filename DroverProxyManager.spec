# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['bz2', 'lzma', 'multiprocessing', 'pwd', 'grp', 'fcntl', 'posix', '_hashlib', '_ssl', '_ctypes', 'defusedxml', 'uharfbuzz', 'reportlab_settings', 'dis', 'opcode', 'inspect', 'unittest', 'sqlite3', 'pdb', 'doctest', 'cProfile', 'asyncio', 'trace', 'timeit'],
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
    name='DroverProxyManager',
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
