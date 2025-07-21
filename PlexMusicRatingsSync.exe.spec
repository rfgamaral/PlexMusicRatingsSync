datas = [
    ("src/plex_music_ratings_sync/config.template.yml", "plex_music_ratings_sync")
]

a = Analysis(
    ['src\\plex_music_ratings_sync\\__main__.py'],
    binaries=[],
    datas=datas,
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
    name='PlexMusicRatingsSync.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
)
