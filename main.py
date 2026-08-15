"""
=============================================================================
PROYECTO: BATALLA NAVAL VECTORIAL (Álgebra Lineal para Secundaria)
=============================================================================
Punto de entrada principal de la aplicación. Lanza la arquitectura unificada
(tkinter + gestor de pantallas) definida en juego_naval/app.py.

Ejecución:
    ./.venv/bin/python main.py        # intérprete del entorno virtual (recomendado)
    python3 main.py                  # intérprete del sistema: se relanza solo
                                     # con el venv si este tiene las dependencias
=============================================================================
"""

import os
import subprocess
import sys


def _relanzar_con_venv() -> None:
    """Si el intérprete actual (p. ej. el python3 del sistema) no tiene las
    dependencias del juego pero el proyecto tiene un `.venv` que sí las tiene,
    relanza la aplicación con ese intérprete. Así `python3 main.py` funciona
    aunque matplotlib solo esté instalado en el entorno virtual."""
    proyecto = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(proyecto, ".venv")
    candidatos = (
        os.path.join(venv_dir, "bin", "python"),
        os.path.join(venv_dir, "Scripts", "python.exe"),
    )
    python_venv = next((p for p in candidatos if os.path.exists(p)), None)
    if python_venv is None:
        return
    # Ya estamos corriendo desde el venv del proyecto: no hacer nada.
    if os.path.realpath(sys.prefix) == os.path.realpath(venv_dir):
        return
    prueba = subprocess.run(
        [python_venv, "-c", "import tkinter, matplotlib"],
        capture_output=True)
    if prueba.returncode != 0:
        return
    print(f"[main] Se relanza con el entorno virtual del proyecto: {python_venv}",
          flush=True)
    print("[main] Si no quieres este comportamiento, usa la ruta del venv al lanzar.",
          flush=True)
    os.execv(python_venv, [python_venv, *sys.argv])


if __name__ == "__main__":
    _relanzar_con_venv()
    from juego_naval.app import main
    main()
