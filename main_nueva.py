"""
=============================================================================
MODO NUEVO: main_nueva.py - Entry point de la arquitectura unificada
=============================================================================
Ventana única con Gestor de Pantallas. Por ahora registra el menú principal
y el Laboratorio de Vectores migrado; se suman las demás pantallas conforme
se migren (batalla, tutorial, sandbox, resultado).

Ejecución:
    python3 main_nueva.py
=============================================================================
"""

import tkinter as tk

from juego_naval.ui.gestor_pantallas import GestorPantallas
from juego_naval.ui.pantallas.menu_principal import PantallaMenuPrincipal
from juego_naval.ui.pantallas.laboratorio import PantallaLaboratorio
from juego_naval.ui.pantallas.batalla import PantallaBatalla
from juego_naval.ui.pantallas.tutorial import PantallaTutorial


def main() -> None:
    raiz = tk.Tk()
    raiz.title("Batalla Naval Vectorial - Arquitectura Unificada")
    raiz.geometry("1240x800")
    raiz.minsize(1000, 680)

    gestor = GestorPantallas(raiz)
    gestor.registrar("menu", PantallaMenuPrincipal)
    gestor.registrar("laboratorio", PantallaLaboratorio)
    gestor.registrar("batalla", PantallaBatalla)
    gestor.registrar("tutorial", PantallaTutorial)
    gestor.reemplazar("menu")

    raiz.mainloop()


if __name__ == "__main__":
    main()
