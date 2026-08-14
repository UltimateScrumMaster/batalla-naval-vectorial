"""
=============================================================================
PROYECTO: BATALLA NAVAL VECTORIAL (Álgebra Lineal para Secundaria)
=============================================================================
Punto de entrada principal de la aplicación. Lanza la arquitectura unificada
(tkinter + gestor de pantallas) definida en juego_naval/app.py.

Ejecución: python3 main.py  (requiere tkinter; matplotlib para las pantallas
gráficas. La versión anterior con menú Rich sigue guardada en el historial de
git (tags v1.0-tui / v2.0-hibrido) y en backups/).
=============================================================================
"""

from juego_naval.app import main


if __name__ == "__main__":
    main()
