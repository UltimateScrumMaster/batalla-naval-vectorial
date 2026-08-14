"""
=================================================================================
MÓDULO: juego_naval/app.py - Registro central de pantallas y entrada unificada
=================================================================================
Punto único donde se registran todas las pantallas de la aplicación. Tanto
main.py como main_nueva.py son solo envoltorios de `main()`. Al retirar los
módulos legacy (Rich) solo habrá que borrar los archivos viejos: aquí ya vive
todo lo que la aplicación ejecuta.
=================================================================================
"""

import tkinter as tk

from juego_naval.ui.gestor_pantallas import GestorPantallas
from juego_naval.ui.pantallas.menu_principal import PantallaMenuPrincipal
from juego_naval.ui.pantallas.laboratorio import PantallaLaboratorio
from juego_naval.ui.pantallas.batalla import PantallaBatalla
from juego_naval.ui.pantallas.tutorial import PantallaTutorial
from juego_naval.ui.pantallas.guia import PantallaGuia


def crear_aplicacion(raiz: tk.Tk) -> GestorPantallas:
    """Registra todas las pantallas y muestra el menú principal."""
    gestor = GestorPantallas(raiz)
    gestor.registrar("menu", PantallaMenuPrincipal)
    gestor.registrar("laboratorio", PantallaLaboratorio)
    gestor.registrar("batalla", PantallaBatalla)
    gestor.registrar("tutorial", PantallaTutorial)
    gestor.registrar("guia", PantallaGuia)
    gestor.reemplazar("menu")
    return gestor


def main() -> None:
    """Entrada unificada: ventana única con el gestor de pantallas."""
    raiz = tk.Tk()
    raiz.title("Batalla Naval Vectorial - Arquitectura Unificada")
    raiz.geometry("1240x800")
    raiz.minsize(1000, 680)
    crear_aplicacion(raiz)
    raiz.mainloop()
