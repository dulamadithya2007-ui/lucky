# jarvis.spec  — PyInstaller build specification
# Place this file in the same folder as jarvis.py
# Run:  pyinstaller jarvis.spec

block_cipher = None

a = Analysis(
    ['jarvis.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',    # Windows TTS
        'pyttsx3.drivers.nsss',     # macOS TTS
        'pyttsx3.drivers.espeak',   # Linux TTS
        'speech_recognition',
        'wikipedia',
        'wikipedia.exceptions',
        'psutil',
        'PIL',
        'PIL.ImageGrab',
        'PIL.Image',
        'screen_brightness_control',
        'comtypes',
        'comtypes.client',
        'pycaw',
        'pycaw.pycaw',
        'pyaudio',
        'pkg_resources',
        'pkg_resources.py2_warn',
        'tkinter',
        'tkinter.font',
        'webbrowser',
        'threading',
        'platform',
        'subprocess',
        'math',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'cv2',
              'PyQt5', 'PyQt6', 'wx', 'gi'],
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
    name='JARVIS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # compress (requires UPX installed, optional)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # ← NO black terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='jarvis.ico',  # ← uncomment and add your .ico file if you have one
)
