"""
=============================================================================
MÓDULO: interfaz.py - Renderizado Visual TUI / Pseudo-GUI con Rich y Depuración
=============================================================================
Maneja la presentación visual en consola tipo Dashboard / Pseudo-GUI:
- Ejes cartesianos X e Y con colores, íconos y trazado gráfico de vectores.
- Previsualización visual de vectores con flechas directores en el plano.
- Panel de Depuración Matemática en Tiempo Real con fórmulas paso a paso.
- Layouts divididos para misiones del Tutorial y Batalla Principal.
=============================================================================
"""

from __future__ import annotations
import math
from typing import Dict, Any, List, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.layout import Layout
from rich import box

from vector2d import Vector2D
from tablero import Tablero
from barco import Barco

console = Console()


def crear_cuadricula_cartesiana(tablero: Tablero, ancho_celda: int = 2) -> Table:
    """
    Genera una tabla Rich que representa el plano cartesiano.
    El eje Y se dibuja de arriba (alto-1) hacia abajo (0), igual que en matemática.
    El eje X se dibuja de izquierda a derecha (0 a ancho-1).
    """
    tabla = Table(
        title=f"[bold cyan]{tablero.titulo}[/bold cyan]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold yellow",
        padding=(0, 0)
    )

    # Columna para los números del eje Y
    tabla.add_column("Y\\X", justify="center", style="bold yellow", width=4)

    # Columnas para cada coordenada en el eje X
    for x in range(tablero.ancho):
        tabla.add_column(f"{x}", justify="center", width=3)

    # Filas desde Y_maximo bajando hasta 0 (orientación cartesiana estándar)
    for y in range(tablero.alto - 1, -1, -1):
        fila = [f"{y}"]
        for x in range(tablero.ancho):
            simbolo, color = tablero.obtener_simbolo_celda(x, y)
            fila.append(f"[{color}]{simbolo}[/{color}]")
        tabla.add_row(*fila)

    return tabla


def trazar_vector_en_tablero(tablero: Tablero, origen: Vector2D, destino: Vector2D,
                             limpiar_previo: bool = True) -> List[Tuple[int, int]]:
    """
    Dibuja visualmente la flecha/trayectoria vectorial sobre el tablero usando marcas temporales.
    Coloca:
      - ● en el origen
      - + a lo largo de la línea
      - ◎ en la coordenada de impacto esperada
    """
    if limpiar_previo:
        tablero.marcas_temporales.clear()

    orig_tuple = origen.a_tupla_grilla()
    dest_tuple = destino.a_tupla_grilla()

    # Trazar puntos intermedios (interpolación lineal discreta)
    dx = destino.x - origen.x
    dy = destino.y - origen.y
    pasos = max(int(math.hypot(dx, dy) * 2), 2)

    puntos_trazados: List[Tuple[int, int]] = []

    for step in range(1, pasos):
        t = step / pasos
        px = int(round(origen.x + t * dx))
        py = int(round(origen.y + t * dy))
        pt_tuple = (px, py)

        if pt_tuple != orig_tuple and pt_tuple != dest_tuple:
            if tablero.es_posicion_valida(Vector2D(px, py)):
                puntos_trazados.append(pt_tuple)
                tablero.marcas_temporales[pt_tuple] = ("+ ", "bold yellow")

    # Marcar Origen y Destino
    if tablero.es_posicion_valida(origen):
        tablero.marcas_temporales[orig_tuple] = ("●", "bold green")

    if tablero.es_posicion_valida(destino):
        tablero.marcas_temporales[dest_tuple] = ("◎", "bold red")
    else:
        # Si cae fuera de rango, no lo dibuja en la grilla pero guarda para advertencia
        pass

    return puntos_trazados


def mostrar_tableros_lado_a_lado(tablero_jugador: Tablero, tablero_enemigo: Tablero,
                                 turno: int, energia: int, viento: Vector2D) -> None:
    """Muestra ambos tableros simultáneamente junto con el estado del turno y clima"""
    grid_jugador = crear_cuadricula_cartesiana(tablero_jugador)
    grid_enemigo = crear_cuadricula_cartesiana(tablero_enemigo)

    barra_energia = f"[bold green]{'█' * energia}[/bold green][dim]{'░' * (6 - energia)}[/dim]"
    # Panel de estado superior
    info_texto = (
        f"[bold white]Turno:[/bold white] [bold yellow]#{turno}[/bold yellow]  |  "
        f"[bold white]Energía Táctica:[/bold white] {barra_energia} ({energia}/6)  |  "
        f"[bold white]Vector Viento:[/bold white] [bold cyan]{viento}[/bold cyan]  |  "
        f"[dim white]Leyenda: ◆ Barco | ✖ Impacto | ✕ Agua | ◉ Sónar | ▸ Proyección[/dim white]"
    )
    panel_info = Panel(info_texto, style="bold blue", box=box.HORIZONTALS)

    console.print(panel_info)
    console.print(Columns([grid_jugador, grid_enemigo], equal=True))


def renderizar_panel_depuracion(explicacion: Dict[str, Any], autor: str = "JUGADOR") -> None:
    """
    Renderiza el Panel de Depuración Matemática en Tiempo Real.
    Muestra la fórmula empleada, los vectores de entrada y cada paso del cálculo algebraico.
    """
    if not explicacion:
        return

    titulo_operacion = explicacion.get("operacion", "Operación Vectorial")
    formula = explicacion.get("formula", "")
    pasos: List[str] = explicacion.get("pasos", [])
    resultado = explicacion.get("resultado", "")

    estilo_borde = "bold cyan" if autor == "JUGADOR" else "bold magenta"
    etiqueta_autor = "CÁLCULO DEL JUGADOR" if autor == "JUGADOR" else "CÁLCULO DE LA IA"
    color_autor = "bold cyan" if autor == "JUGADOR" else "bold magenta"

    cuerpo = Text()
    cuerpo.append_text(Text.from_markup(f"{etiqueta_autor}\n", style=color_autor))
    cuerpo.append(f"Operación: {titulo_operacion}\n", style="bold yellow")
    if formula:
        cuerpo.append(f"Fórmula teórica: {formula}\n", style="bold green")

    cuerpo.append("\nDesglose paso a paso (modo depuración):\n", style="bold underline white")
    for paso in pasos:
        cuerpo.append(f"   {paso}\n", style="white")

    if resultado != "":
        cuerpo.append(f"\nResultado final: {resultado}\n", style="bold yellow")

    panel = Panel(
        cuerpo,
        title=f"[bold]PANEL DE DEPURACIÓN MATEMÁTICA EN TIEMPO REAL ({titulo_operacion})[/bold]",
        border_style=estilo_borde,
        box=box.DOUBLE
    )
    console.print(panel)


def mostrar_pantalla_mision_guiada(mision_info: Dict[str, Any], tablero_demo: Tablero) -> None:
    """
    Genera un Dashboard Pseudo-GUI dividido para el Tutorial Guiado:
    - Izquierda: Información de la Misión, Historia, Pistas y Fórmulas.
    - Derecha: Plano Cartesiano Gráfico con Barcos y Objetivos marcados.
    """
    layout = Layout()
    layout.split_row(
        Layout(name="info", ratio=1),
        Layout(name="grafico", ratio=1)
    )

    text_info = Text()
    text_info.append(f"{mision_info['titulo']}\n\n", style="bold yellow")
    text_info.append(f"Historia:\n{mision_info['historia']}\n\n", style="white")
    text_info.append(f"Punto de Origen P: {mision_info['origen']}\n", style="bold green")
    text_info.append(f"Objetivo Deseado T: {mision_info['objetivo']}\n\n", style="bold red")
    text_info.append(f"Pista Pedagógica:\n{mision_info['pista']}\n", style="italic cyan")

    if "formula" in mision_info:
        text_info.append(f"\nFórmula sugerida: {mision_info['formula']}", style="bold yellow")

    panel_info = Panel(text_info, title="[bold cyan]PANEL DE MISIONES Y CONSEJOS[/bold cyan]", box=box.ROUNDED)
    grid_tabla = crear_cuadricula_cartesiana(tablero_demo)

    layout["info"].update(panel_info)
    layout["grafico"].update(grid_tabla)

    console.print(layout)


def mostrar_guia_habilidades() -> None:
    """Muestra una tabla con el catálogo de habilidades vectoriales y su fundamento matemático"""

    # --- Diccionario de significados de cada tipo de vector ---
    diccionario = Table(
        title="[bold cyan]DICCIONARIO DE VECTORES: ¿QUÉ SIGNIFICA CADA UNO?[/bold cyan]",
        box=box.HEAVY_HEAD
    )
    diccionario.add_column("Tipo de Vector", style="bold yellow", width=24)
    diccionario.add_column("¿Qué significa?", style="white", width=52)
    diccionario.add_column("Ejemplo", style="bold green", width=28)

    diccionario.add_row("P_barco (Posición del barco)", "Dónde está tu navío. Punto de partida de todos tus disparos.", "(2, 3)")
    diccionario.add_row("V_tiro (Vector de tiro)", "Cuánto y hacia dónde viaja el proyectil. Se SUMA a la posición del barco.", "(3, 2) = 3 a la derecha, 2 arriba")
    diccionario.add_row("P_impacto (Punto de impacto)", "Dónde cae la bala. Resultado de P_barco + V_tiro.", "(2,3) + (3,2) = (5,5)")
    diccionario.add_row("V_viento (Vector de viento)", "Fuerza que empuja y desvía tu proyectil. Debes compensarla.", "(1,-1) sopla derecha y abajo")
    diccionario.add_row("u_dir (Dirección base)", "Orientación pura del torpedo, sin potencia. Generalmente corto.", "(1,0) u (1,1)")
    diccionario.add_row("k (Escalar)", "Número que multiplica la potencia/alcance del vector (no es un vector).", "k = 3 triplica el alcance")
    diccionario.add_row("k·u (Vector escalado)", "El vector original estirado k veces: mismo sentido, más largo.", "3·(1,2) = (3,6)")
    diccionario.add_row("Δv (Vector diferencia)", "Distancia y dirección que separa un punto de otro.", "T - P = (5,7) - (2,3) = (3,4)")
    diccionario.add_row("||v|| (Módulo / Magnitud)", "La longitud de la flecha: cuánto mide el vector (Pitágoras).", "||(3,4)|| = 5")
    diccionario.add_row("V_ataque (Vector satelital)", "Dirección del rayo del Cañón Orbital (superpoder).", "(3,4)")
    diccionario.add_row("U_radar (Vector base)", "Eje de referencia sobre el que se proyecta el rayo orbital.", "(1,0) eje horizontal")
    diccionario.add_row("proj_U(V) (Proyección)", "La 'sombra' del vector de ataque sobre el eje del radar.", "proj_(1,0)((3,4)) = (3,0)")

    console.print(diccionario)
    console.print("[dim]Regla de oro: los vectores con P son PUNTOS (dónde estás / dónde cae). "
                  "Los vectores con V o U son FLECHAS DE MOVIMIENTO (cuánto te mueves y hacia dónde).[/dim]\n")

    # --- Catálogo de habilidades ---
    tabla = Table(title="[bold yellow]Catálogo de Habilidades y Fundamentos Vectoriales[/bold yellow]", box=box.ROUNDED)
    tabla.add_column("Habilidad", style="bold cyan", width=25)
    tabla.add_column("Costo", justify="center", style="bold green", width=8)
    tabla.add_column("Fórmula Matemática", style="bold yellow", width=30)
    tabla.add_column("Concepto Pedagógico", style="white", width=40)

    tabla.add_row(
        "Disparo Simple (Suma)", "0",
        "P_final = P_barco + V_tiro",
        "Suma básica de componentes (x1+x2, y1+y2)."
    )
    tabla.add_row(
        "Artillería con Viento (Suma múltiple)", "1",
        "P_final = P_barco + V_tiro + V_viento",
        "Suma múltiple de 3 vectores. Enseña a compensar fuerzas contrarias."
    )
    tabla.add_row(
        "Torpedo Escalar (Multiplicación)", "2",
        "P_final = P_barco + (k · u_dir)",
        "Multiplicación de un vector por un escalar (magnificación de alcance)."
    )
    tabla.add_row(
        "Sónar de Gauss (Módulo)", "1",
        "d = ||Δv|| = sqrt(Δx² + Δy²)",
        "Módulo del vector diferencia y distancia euclidiana por Pitágoras."
    )
    tabla.add_row(
        "Proyección Orbital (Superpoder)", "4",
        "proj_u(v) = [(v·u)/||u||²] · u",
        "SUPERPODER: Producto punto, proyección ortogonal y barrido lineal de sombra."
    )

    console.print(tabla)
    console.print("[dim cyan]Consejo visual: para ver estas fórmulas DIBUJADAS sobre el plano cartesiano "
                  "(flechas, paralelogramo, sombra de proyección), abre la INTERFAZ GRÁFICA "
                  "desde el menú principal (opción 5).[/dim cyan]\n")


def mostrar_resumen_flota(barcos: List[Barco], titulo: str = "Estado de Flota") -> None:
    """Muestra el estado de salud y coordenadas de una flota"""
    tabla = Table(title=f"[bold]{titulo}[/bold]", box=box.SIMPLE_HEAVY)
    tabla.add_column("Navío", style="bold white", width=22)
    tabla.add_column("Tamaño", justify="center", width=8)
    tabla.add_column("Coordenada Ancla", justify="center", style="yellow", width=16)
    tabla.add_column("Salud", justify="center", width=12)
    tabla.add_column("Estado", justify="center", width=15)

    for b in barcos:
        hp = f"{b.tamano - len(b.impactos)}/{b.tamano}"
        estado = "[bold red]HUNDIDO[/bold red]" if b.esta_hundido() else "[bold green]OPERATIVO[/bold green]"
        pos_str = str(b.origen)
        tabla.add_row(f"{b.icono} {b.nombre}", str(b.tamano), pos_str, hp, estado)

    console.print(tabla)
