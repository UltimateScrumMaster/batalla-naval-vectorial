@echo off
REM ===========================================================================
REM build_windows.bat - Genera un ejecutable para Windows con PyInstaller.
REM Requisitos: Python 3 (https://www.python.org/downloads/) con "Add to PATH".
REM   - tkinter ya viene incluido con Python en Windows.
REM   - El ejecutable incluye matplotlib, no necesita instalar nada más.
REM ===========================================================================
cd /d "%~dp0.."

if not exist .venv-build (
    py -3 -m venv .venv-build
)
.venv-build\Scripts\pip install --upgrade pip
.venv-build\Scripts\pip install -r scripts\requirements-build.txt

REM Onefile y console están definidos en el spec (scripts\BatallaNavalVectorial.spec).
.venv-build\Scripts\pyinstaller --noconfirm scripts\BatallaNavalVectorial.spec

echo.
echo Listo. Ejecutable creado en: dist\BatallaNavalVectorial.exe
pause
