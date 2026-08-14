#!/usr/bin/env bash
# =============================================================================
# build_linux.sh - Genera un ejecutable para Linux con PyInstaller.
# Requisitos: python3, python3-tk (sudo apt install python3-tk), y acceso a pip.
# El ejecutable resultante incluye tkinter + matplotlib, por lo que el juego
# funciona en la máquina destino sin instalar nada más.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv-build ]; then
    python3 -m venv .venv-build
fi
.venv-build/bin/pip install --upgrade pip
.venv-build/bin/pip install matplotlib pyinstaller

# --onefile: un solo ejecutable. Sin --windowed para poder ver errores en
# consola durante el arranque.
.venv-build/bin/pyinstaller --noconfirm --onefile \
    --name BatallaNavalVectorial \
    --hidden-import matplotlib.backends.backend_tkagg \
    --hidden-import PIL._tkinter_finder \
    main.py

echo
echo "Listo. Ejecutable creado en: dist/BatallaNavalVectorial"
