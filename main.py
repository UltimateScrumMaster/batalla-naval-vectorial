"""
=============================================================================
PROYECTO: BATALLA NAVAL VECTORIAL (Álgebra Lineal para Secundaria)
=============================================================================
Punto de entrada principal de la aplicación.
Ejecución: python3 main.py
=============================================================================
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

from juego import PartidaBatallaNaval, ejecutar_laboratorio_sandbox, ejecutar_tutorial_guiado
from interfaz import mostrar_guia_habilidades
from interfaz_grafica import hay_interfaz_grafica, lanzar_interfaz_grafica
from juego_grafico import lanzar_juego_grafico


def _preparar_consola_windows() -> None:
    """En Windows la consola usa cp1252 por defecto, que no puede codificar
    los caracteres Unicode del banner y los tableros (═, █, ✖, etc.).
    Cambia el codepage a UTF-8 y fuerza la codificación de los flujos."""
    if sys.platform == "win32":
        try:
            os.system("chcp 65001 >nul")
        except Exception:
            pass
        for flujo in (sys.stdout, sys.stderr):
            try:
                flujo.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_preparar_consola_windows()

console = Console()


def mostrar_banner_principal() -> None:
    """Muestra el cartel de bienvenida del juego"""
    banner_texto = """[bold cyan]
  ██████╗  █████╗ ████████╗ █████╗ ██╗     ██╗      █████╗ 
  ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██║     ██║     ██╔══██╗
  ██████╔╝███████║   ██║   ███████║██║     ██║     ███████║
  ██╔══██╗██╔══██║   ██║   ██╔══██║██║     ██║     ██╔══██║
  ██████╔╝██║  ██║   ██║   ██║  ██║███████╗███████╗██║  ██║
  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
             [bold yellow]N A V A L   V E C T O R I A L[/bold yellow]
    [white]Aprende Vectores, Pitágoras y Proyecciones Jugando[/white]
[/bold cyan]"""
    console.print(Panel(banner_texto, box=box.HEAVY, border_style="cyan"))


def menu_principal() -> None:
    """Controlador del Menú Principal del sistema"""
    while True:
        console.clear()
        mostrar_banner_principal()

        console.print("[bold yellow]══════════════ MENÚ PRINCIPAL ══════════════[/bold yellow]")
        console.print("  [bold green]1.[/bold green] Jugar Batalla Naval vs IA (Campaña Táctica)")
        console.print("  [bold green]2.[/bold green] Tutorial Guiado por Misiones (Ideal para Alumnos)")
        console.print("  [bold green]3.[/bold green] Laboratorio Sandbox y Calculadora Vectorial con Debug")
        console.print("  [bold green]4.[/bold green] Manual de Fórmulas y Habilidades")
        console.print("  [bold green]5.[/bold green] Interfaz Gráfica (Laboratorio Vectorial con Matplotlib)")
        console.print("  [bold green]6.[/bold green] Jugar Batalla Naval en Ventana Gráfica (tkinter)")
        console.print("  [bold red]7.[/bold red] Salir del Juego")

        opcion = Prompt.ask("\n[bold yellow]Selecciona una opción (1-7)[/bold yellow]", default="1")

        if opcion == "1":
            partida = PartidaBatallaNaval()
            partida.jugar()
            Prompt.ask("\n[dim yellow]Presiona Enter para volver al Menú Principal...[/dim yellow]")

        elif opcion == "2":
            ejecutar_tutorial_guiado()

        elif opcion == "3":
            ejecutar_laboratorio_sandbox()

        elif opcion == "4":
            console.clear()
            mostrar_guia_habilidades()
            Prompt.ask("\n[dim yellow]Presiona Enter para volver al Menú Principal...[/dim yellow]")

        elif opcion == "5":
            if hay_interfaz_grafica():
                console.print("\n[green]Abriendo la interfaz gráfica de vectores (tkinter + Matplotlib)...[/green]")
                console.print("[dim]Cierra la ventana para volver al menú.[/dim]\n")
                lanzar_interfaz_grafica()
            else:
                console.print("\n[bold yellow]La interfaz gráfica no está disponible en esta máquina.[/bold yellow]")
                console.print("  Requiere: [cyan]pip install matplotlib[/cyan]")
                console.print("           [cyan]sudo apt install python3-tk[/cyan]  (solo Linux)")
                console.print("  El juego sigue funcionando completo en modo texto (opciones 1-4).\n")
                Prompt.ask("\n[dim yellow]Presiona Enter para volver al Menú Principal...[/dim yellow]")

        elif opcion == "6":
            if hay_interfaz_grafica():
                console.print("\n[green]Abriendo la batalla naval en ventana gráfica (tkinter + Matplotlib)...[/green]")
                console.print("[dim]Cierra la ventana para volver al menú.[/dim]\n")
                lanzar_juego_grafico()
            else:
                console.print("\n[bold yellow]El modo gráfico no está disponible en esta máquina.[/bold yellow]")
                console.print("  Requiere: [cyan]pip install matplotlib[/cyan]")
                console.print("           [cyan]sudo apt install python3-tk[/cyan]  (solo Linux)")
                console.print("  Puedes seguir jugando en modo texto con la opción 1.\n")
                Prompt.ask("\n[dim yellow]Presiona Enter para volver al Menú Principal...[/dim yellow]")

        elif opcion == "7":
            console.print("\n[bold cyan]Gracias por jugar a Batalla Naval Vectorial. Hasta pronto, Almirante.[/bold cyan]\n")
            sys.exit(0)


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]Juego interrumpido por el usuario. ¡Hasta la próxima![/bold yellow]")
        sys.exit(0)
