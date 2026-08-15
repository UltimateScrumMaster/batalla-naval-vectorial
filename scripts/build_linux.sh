#!/usr/bin/env bash
# =============================================================================
# build_linux.sh - Genera un ejecutable para Linux con PyInstaller.
# Requisitos: python3, python3-tk (sudo apt install python3-tk), y acceso a pip.
# El ejecutable resultante incluye tkinter + matplotlib, por lo que el juego
# funciona en la máquina destino sin instalar nada más.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."   # scripts/ -> raíz del proyecto

if [ ! -d .venv-build ]; then
    python3 -m venv .venv-build
fi
.venv-build/bin/pip install --upgrade pip
.venv-build/bin/pip install -r scripts/requirements-build.txt

# Onefile y console están definidos en el spec (scripts/BatallaNavalVectorial.spec).
.venv-build/bin/pyinstaller --noconfirm scripts/BatallaNavalVectorial.spec

echo
echo "Listo. Ejecutable creado en: dist/BatallaNavalVectorial"
