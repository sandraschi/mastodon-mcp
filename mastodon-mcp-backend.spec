# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — produce mastodon-mcp-backend.exe for Tauri NSIS embedding.
# Usage (from repo root):
#   uv run pyinstaller mastodon-mcp-backend.spec --distpath src-tauri/resources

block_cipher = None

a = Analysis(
    ["src/mastodon_mcp/__main__.py"],
    pathex=["src"],
    binaries=[],
    datas=[],
    hiddenimports=["mastodon_mcp", "mastodon_mcp.server", "uvicorn", "fastapi", "fastmcp"],
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
    name="mastodon-mcp-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
