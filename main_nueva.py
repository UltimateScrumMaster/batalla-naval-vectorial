"""
=================================================================================
MODO NUEVO: main_nueva.py - Entry point de la arquitectura unificada
=================================================================================
Envoltorio del punto de entrada único (juego_naval/app.py). Ejecuta la app
completa con todas las pantallas migradas.

Ejecución:
    ./venv/bin/python main_nueva.py   (o python3 con tkinter+matplotlib)
=================================================================================
"""

from juego_naval.app import main


if __name__ == "__main__":
    main()
