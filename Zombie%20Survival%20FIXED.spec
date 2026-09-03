# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

pygame_datas, pygame_binaries, pygame_hidden = collect_all("pygame")

a = Analysis(
    ["zombie.py"],
    pathex=["."],
    binaries=pygame_binaries,
    datas=pygame_datas + [
        ("zombie_game_assets", "zombie_game_assets"),
        ("zombie_accounts.json", "."),
        ("zombie_leaderboard.json", "."),
    ],
    hiddenimports=pygame_hidden + [
        "pygame",
        "pygame._sdl2",
        "pygame._sdl2.video",
        "pygame._sdl2.audio",
    ],
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
    name="Zombie Survival",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="Zombie Survival",
)
