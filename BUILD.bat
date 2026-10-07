@echo off
setlocal

title JARVIS — VS Code Build Script
color 0B

echo.
echo ================================================
echo   JARVIS v4.0 — VS Code Build Script
echo   Build jarvis.py into JARVIS.exe
echo ================================================
echo.

:: Step 1 - Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not found in PATH.
    echo Open VS Code and select the correct Python interpreter.
    pause
    exit /b 1
)

:: Step 2 - Upgrade pip
echo [1/5] Upgrading pip...
python -m pip install --upgrade pip

:: Step 3 - Install dependencies
echo.
echo [2/5] Installing required packages...

python -m pip install ^
    pyinstaller ^
    pyttsx3 ^
    SpeechRecognition ^
    wikipedia ^
    psutil ^
    Pillow ^
    screen-brightness-control ^
    pycaw ^
    comtypes ^
    pyaudio

if errorlevel 1 (
    echo.
    echo [WARNING] Some dependencies may have failed.
)

:: Step 4 - Clean previous builds
echo.
echo [3/5] Cleaning old files...

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist JARVIS.exe del /q JARVIS.exe

:: Step 5 - Build EXE
echo.
echo [4/5] Building executable...

if exist jarvis.spec (
    python -m PyInstaller jarvis.spec
) else (
    python -m PyInstaller --onefile --windowed --name JARVIS jarvis.py
)

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

:: Step 6 - Finalize
echo.
echo [5/5] Finalizing build...

if exist dist\JARVIS.exe (
    copy /y dist\JARVIS.exe JARVIS.exe >nul
    echo.
    echo ================================================
    echo SUCCESS! JARVIS.exe created successfully.
    echo Location: %CD%\JARVIS.exe
    echo ================================================
) else (
    echo [ERROR] Executable not found in dist folder.
)

echo.
pause