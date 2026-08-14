@echo off
REM ===========================================================================
REM build_windows.bat - Genera un ejecutable para Windows con PyInstaller.
REM Requisitos: Python 3 (https://www.python.org/downloads/) con "Add to PATH".
REM   - tkinter ya viene incluido con Python en Windows.
REM   - El ejecutable incluye matplotlib, no necesita instalar nada más.
REM ===========================================================================
cd /d "%~dp0"

if not exist .venv-build (
    py -3 -m venv .venv-build
)
.venv-build\Scripts\pip install --upgrade pip
.venv-build\Scripts\pip install matplotlib pyinstaller

REM --onefile: un solo ejecutable. Sin --windowed para poder ver errores en
REM consola durante el arranque.
.venv-build\Scripts\pyinstaller --noconfirm --onefile ^
    --name BatallaNavalVectorial ^
    --hidden-import matplotlib.backends.backend_tkagg ^
    --hidden-import PIL._tkinter_finder ^
    main.py

echo.
echo Listo. Ejecutable creado en: dist\BatallaNavalVectorial.exe
pause
