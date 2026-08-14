"""
=============================================================================
MÓDULO: juego.py - Lógica de Juego, Campaña, Sandbox y Tutoriales
=============================================================================
Contiene el bucle principal del juego, gestión de turnos, modo Sandbox
interactivo para docentes/alumnos y el tutorial guiado de aprendizaje.
=============================================================================
"""

from __future__ import annotations
import random
import time
from typing import Optional, Tuple, List
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich import box

from vector2d import Vector2D
from barco import Barco, crear_flota_estandar
from tablero import Tablero
from habilidades import (
    DisparoBasicoSuma,
    DisparoConViento,
    TorpedoEscalar,
    SonarDistanciaEuclidiana,
    CanonProyeccionOrbital
)
from ia import IAEnemiga
from interfaz import (
    console,
    mostrar_tableros_lado_a_lado,
    renderizar_panel_depuracion,
    mostrar_guia_habilidades,
    mostrar_resumen_flota,
    crear_cuadricula_cartesiana,
    trazar_vector_en_tablero,
    mostrar_pantalla_mision_guiada
)


def pedir_vector(mensaje: str = "Ingresa las componentes del vector") -> Vector2D:
    """Solicita al usuario los valores X e Y de forma amigable y robusta"""
    console.print(f"[bold cyan]{mensaje}:[/bold cyan]")
    while True:
        try:
            x_str = Prompt.ask("  [yellow]Componente X (horizontal)[/yellow]", default="0")
            y_str = Prompt.ask("  [yellow]Componente Y (vertical)[/yellow]", default="0")
            return Vector2D(float(x_str), float(y_str))
        except ValueError:
            console.print("[bold red]Por favor ingresa números válidos.[/bold red]")


def pedir_vector_con_previsualizacion(origen: Vector2D, tablero_enemigo: Tablero,
                                      mensaje: str = "Ingresa tu Vector de Disparo",
                                      etiqueta_tabla: str = "PREVISUALIZACIÓN TÁCTICA DEL DISPARO",
                                      extra: Optional[Vector2D] = None) -> Vector2D:
    """
    Pseudo-GUI interactiva: pide el vector componente a componente y muestra
    en tiempo real la flecha visual trazada en el tablero, indicando si el
    disparo caerá dentro o fuera de la zona de combate.
    """
    while True:
        console.print(f"\n[bold cyan]{mensaje}:[/bold cyan]")
        try:
            x_str = Prompt.ask("  [yellow]Componente X (horizontal)[/yellow]", default="0")
            y_str = Prompt.ask("  [yellow]Componente Y (vertical)[/yellow]", default="0")
            v = Vector2D(float(x_str), float(y_str))
        except ValueError:
            console.print("[bold red]Por favor ingresa números válidos.[/bold red]")
            continue

        # Calcular destino final considerando el vector extra (viento)
        destino = origen + v
        if extra is not None:
            destino = destino + extra

        # Dibujar la flecha sobre el tablero
        trazar_vector_en_tablero(tablero_enemigo, origen, destino)
        tabla_preview = crear_cuadricula_cartesiana(tablero_enemigo)
        tabla_preview.title = f"[bold cyan]{etiqueta_tabla}[/bold cyan]"

        console.clear()
        console.print(tabla_preview)

        if tablero_enemigo.es_posicion_valida(destino):
            estado = f"[bold green]DISPARO DENTRO DEL ÁREA DE COMBATE: {destino}[/bold green]"
        else:
            estado = (f"[bold red]CUIDADO: el disparo cae FUERA del área de combate "
                      f"(coordenadas válidas 0..{tablero_enemigo.ancho-1}, 0..{tablero_enemigo.alto-1})."
                      f" El destino calculado sería {destino}.[/bold red]")

        console.print(Panel(
            f"{estado}\n\n"
            f"[bold yellow]Pista visual:[/bold yellow] ● = posición del barco, "
            f"[bold yellow]+[/bold yellow] = trayectoria del vector, "
            f"[bold yellow]◎[/bold yellow] = punto de impacto calculado.\n\n"
            f"[bold cyan]Si el disparo NO es válido, elige un vector más corto o diferente.[/bold cyan]",
            title="[bold]PSEUDO-GUI TÁCTICA: PREVISUALIZACIÓN EN TIEMPO REAL[/bold]",
            box=box.DOUBLE
        ))

        confirmacion = Prompt.ask("\n[yellow]¿Confirmar este vector de disparo? (s/n)[/yellow]", default="s").lower()
        if confirmacion in ("s", "si", "y", "yes"):
            return v
        console.print("[dim]Reingresando el vector de disparo...[/dim]")



def seleccionar_barco_origen(barcos: List[Barco]) -> Tuple[Barco, Vector2D]:
    """Permite al jugador seleccionar desde qué barco disparar"""
    barcos_vivos = [b for b in barcos if not b.esta_hundido()]
    if not barcos_vivos:
        return barcos[0], barcos[0].origen

    if len(barcos_vivos) == 1:
        return barcos_vivos[0], barcos_vivos[0].origen

    console.print("\n[bold cyan]Selecciona el navío desde donde lanzarás el ataque:[/bold cyan]")
    for i, b in enumerate(barcos_vivos, 1):
        console.print(f"  [bold green]{i}.[/bold green] {b.icono} {b.nombre} - Posición de origen: [bold yellow]{b.origen}[/bold yellow]")

    while True:
        opc = IntPrompt.ask("Número de barco", default=1)
        if 1 <= opc <= len(barcos_vivos):
            barco = barcos_vivos[opc - 1]
            return barco, barco.origen
        console.print("[bold red]Opción inválida.[/bold red]")


class PartidaBatallaNaval:
    """Controlador de una partida completa de Batalla Naval Vectorial"""

    def __init__(self):
        self.tablero_jugador = Tablero(ancho=10, alto=10, es_oculto=False, titulo="TU FLOTA (Plano Aliado)")
        self.tablero_enemigo = Tablero(ancho=10, alto=10, es_oculto=True, titulo="RADAR ENEMIGO (Niebla de Guerra)")
        self.ia = IAEnemiga("Almirante Vector", nivel="normal")

        # Generar flotas
        self.tablero_jugador.colocar_flota_aleatoria()
        self.tablero_enemigo.colocar_flota_aleatoria()

        self.turno: int = 1
        self.energia_jugador: int = 2
        self.viento: Vector2D = Vector2D(0, 0)
        self.actualizar_viento()

    def actualizar_viento(self) -> None:
        """Modifica el vector de corriente marina/viento periódicamente"""
        vx = random.choice([-2, -1, 0, 1, 2])
        vy = random.choice([-2, -1, 0, 1, 2])
        self.viento = Vector2D(vx, vy)

    def turno_jugador(self) -> bool:
        """Ejecuta las acciones del turno del jugador. Retorna True si la partida debe continuar."""
        # Limpiar marcas visuales temporales del turno anterior
        self.tablero_jugador.marcas_temporales.clear()
        self.tablero_enemigo.marcas_temporales.clear()

        # Incrementar energía
        self.energia_jugador = min(6, self.energia_jugador + 1)
        if self.turno % 3 == 0:
            self.actualizar_viento()

        mostrar_tableros_lado_a_lado(
            self.tablero_jugador, self.tablero_enemigo,
            self.turno, self.energia_jugador, self.viento
        )

        console.print("\n[bold yellow]═══ MENÚ DE ACCIÓN TÁCTICA ═══[/bold yellow]")
        console.print("  [bold cyan]1.[/bold cyan] Disparo Vectorial Simple (Costo: [green]0[/green]) - Suma P + V")
        console.print("  [bold cyan]2.[/bold cyan] Artillería con Viento (Costo: [green]1[/green]) - Suma triple P + V + Viento")
        console.print("  [bold cyan]3.[/bold cyan] Torpedo Escalar (Costo: [green]2[/green]) - Multiplicación P + (k · u)")
        console.print("  [bold cyan]4.[/bold cyan] Sónar Acústico de Gauss (Costo: [green]1[/green]) - Distancia euclidiana ||Δv||")
        console.print("  [bold cyan]5.[/bold cyan] Cañón Orbital de Proyección (Costo: [bold red]4[/bold red]) - [bold magenta]SUPERPODER[/bold magenta] proj_u(v)")
        console.print("  [bold cyan]6.[/bold cyan] Ver Estado de Flotas")
        console.print("  [bold cyan]7.[/bold cyan] Ver Ayuda y Fórmulas Vectoriales")

        while True:
            opcion = Prompt.ask("\n[bold yellow]Elige una acción (1-7)[/bold yellow]", default="1")

            if opcion == "1":
                # DISPARO BÁSICO
                barco, pos_origen = seleccionar_barco_origen(self.tablero_jugador.barcos)
                console.print(f"\n[cyan]Disparando desde {barco.nombre} en {pos_origen}...[/cyan]")
                v_tiro = pedir_vector_con_previsualizacion(
                    pos_origen, self.tablero_enemigo,
                    mensaje="Ingresa el Vector de Tiro (Vx, Vy)",
                    etiqueta_tabla="VISTA TÁCTICA: PREDICCIÓN DE IMPACTO (TU DISPARO)",
                    extra=None
                )
                res = DisparoBasicoSuma.ejecutar(pos_origen, v_tiro, self.tablero_enemigo)
                renderizar_panel_depuracion(res["explicacion"], autor="JUGADOR")
                console.print(f"\n{res['resultado_tablero'][0].mensaje}\n")
                break

            elif opcion == "2":
                # ARTILLERÍA CON VIENTO
                if self.energia_jugador < 1:
                    console.print("[bold red]No tienes suficiente energía táctica (Requiere 1).[/bold red]")
                    continue
                self.energia_jugador -= 1
                barco, pos_origen = seleccionar_barco_origen(self.tablero_jugador.barcos)
                console.print(f"\n[cyan]Disparando con Viento activo {self.viento} desde {pos_origen}...[/cyan]")
                console.print("[dim white]Recuerda: P_final = P_origen + V_tiro + V_viento[/dim white]")
                v_tiro = pedir_vector_con_previsualizacion(
                    pos_origen, self.tablero_enemigo,
                    mensaje="Ingresa tu Vector de Tiro V_tiro (el viento se sumará solo)",
                    etiqueta_tabla="VISTA TÁCTICA: PREDICCIÓN CON VIENTO (P + V + Viento)",
                    extra=self.viento
                )
                res = DisparoConViento.ejecutar(pos_origen, v_tiro, self.viento, self.tablero_enemigo)
                renderizar_panel_depuracion(res["explicacion"], autor="JUGADOR")
                console.print(f"\n{res['resultado_tablero'][0].mensaje}\n")
                break

            elif opcion == "3":
                # TORPEDO ESCALAR
                if self.energia_jugador < 2:
                    console.print("[bold red]No tienes suficiente energía táctica (Requiere 2).[/bold red]")
                    continue
                self.energia_jugador -= 2
                barco, pos_origen = seleccionar_barco_origen(self.tablero_jugador.barcos)
                console.print(f"\n[cyan]Armando Torpedo Escalar desde {pos_origen}...[/cyan]")
                dir_base = pedir_vector_con_previsualizacion(
                    pos_origen, self.tablero_enemigo,
                    mensaje="Ingresa el Vector de Dirección Base U (Ux, Uy) ej: (1, 0) o (1, 1)",
                    etiqueta_tabla="VISTA TÁCTICA: DIRECCIÓN BASE DEL TORPEDO",
                    extra=None
                )
                escalar_k = IntPrompt.ask("Ingresa el multiplicador Escalar k (potencia)", default=2)
                # Nueva previsualización con el torpedo escalado final
                trazar_vector_en_tablero(self.tablero_enemigo, pos_origen, pos_origen + (dir_base * escalar_k))
                tabla_torpedo = crear_cuadricula_cartesiana(self.tablero_enemigo)
                tabla_torpedo.title = f"[bold magenta]VISTA TÁCTICA: TORPEDO FINAL k·U = {dir_base} × {escalar_k}[/bold magenta]"
                console.clear()
                console.print(tabla_torpedo)
                res = TorpedoEscalar.ejecutar(pos_origen, dir_base, escalar_k, self.tablero_enemigo)
                renderizar_panel_depuracion(res["explicacion"], autor="JUGADOR")
                console.print(f"\n{res['resultado_tablero'][0].mensaje}\n")
                break

            elif opcion == "4":
                # SÓNAR DE GAUSS
                if self.energia_jugador < 1:
                    console.print("[bold red]No tienes suficiente energía táctica (Requiere 1).[/bold red]")
                    continue
                self.energia_jugador -= 1
                barco, pos_origen = seleccionar_barco_origen(self.tablero_jugador.barcos)
                res = SonarDistanciaEuclidiana.ejecutar(pos_origen, self.tablero_enemigo)
                renderizar_panel_depuracion(res["explicacion"], autor="JUGADOR")

                # Visualizar el ping del sónar en el radar enemigo
                if tablero_enemigo.es_posicion_valida(pos_origen):
                    self.tablero_enemigo.marcas_temporales[pos_origen.a_tupla_grilla()] = ("◉", "bold magenta")
                    tabla_radar = crear_cuadricula_cartesiana(self.tablero_enemigo)
                    tabla_radar.title = "[bold magenta]RADAR ENEMIGO: ONDA DE SÓNAR ACTIVA (Baliza en el origen del barco)[/bold magenta]"
                    console.clear()
                    console.print(tabla_radar)

                console.print(f"\n{res['mensaje']}\n")
                break

            elif opcion == "5":
                # SUPERPODER PROYECCIÓN ORBITAL
                if self.energia_jugador < 4:
                    console.print(f"[bold red]Energía insuficiente: Tienes {self.energia_jugador} y requieres 4.[/bold red]")
                    continue
                self.energia_jugador -= 4
                barco, pos_origen = seleccionar_barco_origen(self.tablero_jugador.barcos)
                console.print("\n[bold magenta]ACTIVANDO SUPERPODER: CAÑÓN DE PROYECCIÓN ORBITAL[/bold magenta]")
                console.print("[dim white]Se calculará la proyección de V sobre el eje U y se barrerán todas las casillas resultantes.[/dim white]")
                v_ataque = pedir_vector("Vector de Ataque Satelital V (Vx, Vy)")
                u_radar = pedir_vector("Vector Base de Radar U (Ux, Uy) - No puede ser (0,0)")
                if u_radar.es_cero():
                    console.print("[bold red]El vector base no puede ser el vector nulo (0,0). Reintentando...[/bold red]")
                    self.energia_jugador += 4
                    continue

                res = CanonProyeccionOrbital.ejecutar(pos_origen, v_ataque, u_radar, self.tablero_enemigo)
                renderizar_panel_depuracion(res["explicacion"], autor="JUGADOR")
                console.print(f"\n{res['mensaje']}\n")
                break

            elif opcion == "6":
                mostrar_resumen_flota(self.tablero_jugador.barcos, "Tu Flota Aliada")
                mostrar_resumen_flota(self.tablero_enemigo.barcos, "Flota Hostil Enemiga")
            elif opcion == "7":
                mostrar_guia_habilidades()

        # Verificar victoria del jugador
        if self.tablero_enemigo.todos_hundidos():
            console.print("\n[bold green]VICTORIA ABSOLUTA: Has destruido toda la flota enemiga con precisión vectorial.[/bold green]\n")
            return False

        return True

    def turno_ia(self) -> bool:
        """Ejecuta el turno de la computadora y muestra el panel matemático de su movimiento"""
        console.print("\n[bold magenta]La Inteligencia Artificial enemiga está calculando su vector de ataque...[/bold magenta]")
        time.sleep(1.0)

        res_ia = self.ia.decidir_turno(self.tablero_enemigo, self.tablero_jugador, self.viento)
        renderizar_panel_depuracion(res_ia["explicacion"], autor="IA")

        for r in res_ia.get("resultado_tablero", []):
            console.print(f"[bold magenta]Impacto IA:[/bold magenta] {r.mensaje}")

        # Verificar derrota del jugador
        if self.tablero_jugador.todos_hundidos():
            console.print("\n[bold red]DERROTA: Tu flota ha sido eliminada por la artillería vectorial enemiga.[/bold red]\n")
            return False

        self.turno += 1
        Prompt.ask("\n[dim yellow]Presiona Enter para continuar al siguiente turno...[/dim yellow]")
        return True

    def jugar(self) -> None:
        """Bucle principal de la batalla naval"""
        console.clear()
        console.print(Panel(
            "[bold cyan]BIENVENIDO A LA BATALLA NAVAL VECTORIAL[/bold cyan]\n"
            "[white]Utiliza operaciones con vectores para localizar y hundir la flota enemiga.[/white]",
            box=box.DOUBLE
        ))

        partida_activa = True
        while partida_activa:
            partida_activa = self.turno_jugador()
            if not partida_activa:
                break
            partida_activa = self.turno_ia()


# =============================================================================
# MODO SANDBOX / LABORATORIO DE VECTORES
# =============================================================================

def ejecutar_laboratorio_sandbox() -> None:
    """
    Laboratorio interactivo para que docentes y alumnos prueben libremente
    cualquier operación con vectores en tiempo real con depuración gráfica.
    """
    tablero_demo = Tablero(ancho=10, alto=10, es_oculto=False, titulo="Plano de Experimentación Vectorial")

    while True:
        console.clear()
        console.print(Panel(
            "[bold yellow]LABORATORIO INTERACTIVO Y CALCULADORA DE VECTORES 2D[/bold yellow]\n"
            "[white]Prueba operaciones, observa el plano cartesiano y analiza el desglose paso a paso.[/white]",
            box=box.ROUNDED
        ))

        console.print(crear_cuadricula_cartesiana(tablero_demo))

        console.print("\n[bold cyan]Selecciona una operación a experimentar:[/bold cyan]")
        console.print("  [bold green]1.[/bold green] Suma de dos vectores (u + v)")
        console.print("  [bold green]2.[/bold green] Resta de dos vectores (u - v)")
        console.print("  [bold green]3.[/bold green] Multiplicación por Escalar (k · v)")
        console.print("  [bold green]4.[/bold green] Módulo / Magnitud y Teorema de Pitágoras (||v||)")
        console.print("  [bold green]5.[/bold green] Distancia Euclidiana entre dos puntos (d = ||u - v||)")
        console.print("  [bold green]6.[/bold green] Producto Punto / Escalar (u · v)")
        console.print("  [bold green]7.[/bold green] Proyección Vectorial Ortogonal (proj_u(v))")
        console.print("  [bold green]8.[/bold green] Limpiar Plano")
        console.print("  [bold red]0.[/bold red] Volver al Menú Principal")
        console.print("[dim cyan]Consejo: la versión GRÁFICA de este laboratorio (con sliders y flechas "
                      "a escala) está en el menú principal, opción 5.[/dim cyan]")

        opc = Prompt.ask("\n[yellow]Opción[/yellow]", default="1")

        if opc == "0":
            break

        elif opc == "1":
            console.print("\n[bold cyan]=== SUMA DE VECTORES ===[/bold cyan]")
            u = pedir_vector("Ingresa Vector U (u_x, u_y)")
            v = pedir_vector("Ingresa Vector V (v_x, v_y)")
            explicacion = u.explicar_suma(v, "U", "V")
            renderizar_panel_depuracion(explicacion)
            res = u + v
            # Previsualizar visualmente la suma en el plano (con marcadores U → resultado)
            trazar_vector_en_tablero(tablero_demo, u, res)
            if tablero_demo.es_posicion_valida(res):
                tablero_demo.disparos_acierto.add(res.a_tupla_grilla())
            tabla_preview = crear_cuadricula_cartesiana(tablero_demo)
            tabla_preview.title = "[bold green]VISTA GRÁFICA: SUMA U + V = RESULTADO[/bold green]"
            console.clear()
            console.print(tabla_preview)

        elif opc == "2":
            console.print("\n[bold cyan]=== RESTA DE VECTORES ===[/bold cyan]")
            u = pedir_vector("Ingresa Vector U (u_x, u_y)")
            v = pedir_vector("Ingresa Vector V (v_x, v_y)")
            res = u - v
            pasos = [
                f"1. Coordenada X = {u.x} - ({v.x}) = {res.x}",
                f"2. Coordenada Y = {u.y} - ({v.y}) = {res.y}",
                f"3. Vector Resta = ({res.x}, {res.y})"
            ]
            renderizar_panel_depuracion({
                "operacion": "Resta de Vectores",
                "formula": "U - V = (Ux - Vx, Uy - Vy)",
                "pasos": pasos,
                "resultado": res
            })
            trazar_vector_en_tablero(tablero_demo, u, res)
            if tablero_demo.es_posicion_valida(res):
                tablero_demo.disparos_acierto.add(res.a_tupla_grilla())
            tabla_preview = crear_cuadricula_cartesiana(tablero_demo)
            tabla_preview.title = "[bold green]VISTA GRÁFICA: RESTA U - V = RESULTADO[/bold green]"
            console.clear()
            console.print(tabla_preview)

        elif opc == "3":
            console.print("\n[bold cyan]=== MULTIPLICACIÓN POR ESCALAR ===[/bold cyan]")
            v = pedir_vector("Ingresa Vector V (x, y)")
            k = float(Prompt.ask("Ingresa el número Escalar k", default="2"))
            explicacion = v.explicar_escalar(k, "V")
            renderizar_panel_depuracion(explicacion)
            res = v * k
            trazar_vector_en_tablero(tablero_demo, Vector2D(0, 0), res)
            if tablero_demo.es_posicion_valida(res):
                tablero_demo.disparos_acierto.add(res.a_tupla_grilla())
            tabla_preview = crear_cuadricula_cartesiana(tablero_demo)
            tabla_preview.title = f"[bold green]VISTA GRÁFICA: k·V = {k} × {v} = {res}[/bold green]"
            console.clear()
            console.print(tabla_preview)

        elif opc == "4":
            console.print("\n[bold cyan]=== MAGNITUD / MÓDULO (PITÁGORAS) ===[/bold cyan]")
            v = pedir_vector("Ingresa Vector V (x, y)")
            mag = v.magnitud()
            pasos = [
                f"1. Componentes: x = {v.x}, y = {v.y}",
                f"2. Cuadrados: x² = {v.x**2}, y² = {v.y**2}",
                f"3. Suma de cuadrados: {v.x**2} + {v.y**2} = {v.magnitud_cuadrada()}",
                f"4. Raíz cuadrada: sqrt({v.magnitud_cuadrada()}) ≈ {mag:.4f} unidades"
            ]
            renderizar_panel_depuracion({
                "operacion": "Módulo / Magnitud de un Vector",
                "formula": "||V|| = sqrt(x² + y²)",
                "pasos": pasos,
                "resultado": f"{mag:.4f}"
            })
            trazar_vector_en_tablero(tablero_demo, Vector2D(0, 0), v)
            tabla_preview = crear_cuadricula_cartesiana(tablero_demo)
            tabla_preview.title = "[bold green]VISTA GRÁFICA: VECTOR ANALIZADO Y SU MAGNITUD[/bold green]"
            console.clear()
            console.print(tabla_preview)

        elif opc == "5":
            console.print("\n[bold cyan]=== DISTANCIA EUCLIDIANA ENTRE DOS PUNTOS ===[/bold cyan]")
            p1 = pedir_vector("Ingresa Punto 1 (P1)")
            p2 = pedir_vector("Ingresa Punto 2 (P2)")
            explicacion = p1.explicar_distancia(p2, "P1", "P2")
            renderizar_panel_depuracion(explicacion)
            trazar_vector_en_tablero(tablero_demo, p1, p2)
            tabla_preview = crear_cuadricula_cartesiana(tablero_demo)
            tabla_preview.title = "[bold green]VISTA GRÁFICA: SEGMENTO ENTRE P1 Y P2[/bold green]"
            console.clear()
            console.print(tabla_preview)

        elif opc == "6":
            console.print("\n[bold cyan]=== PRODUCTO PUNTO / ESCALAR ===[/bold cyan]")
            u = pedir_vector("Ingresa Vector U (u_x, u_y)")
            v = pedir_vector("Ingresa Vector V (v_x, v_y)")
            dot = u.producto_punto(v)
            pasos = [
                f"1. Multiplicación en X: {u.x} * {v.x} = {u.x * v.x}",
                f"2. Multiplicación en Y: {u.y} * {v.y} = {u.y * v.y}",
                f"3. Suma de productos: ({u.x * v.x}) + ({u.y * v.y}) = {dot}",
                f"4. Interpretación: Si U·V = 0 los vectores son perpendiculares (ortogonales)."
            ]
            renderizar_panel_depuracion({
                "operacion": "Producto Punto (Escalar)",
                "formula": "U · V = (Ux · Vx) + (Uy · Vy)",
                "pasos": pasos,
                "resultado": str(dot)
            })
            trazar_vector_en_tablero(tablero_demo, Vector2D(0, 0), u)
            tabla_preview = crear_cuadricula_cartesiana(tablero_demo)
            tabla_preview.title = "[bold green]VISTA GRÁFICA: VECTORES DEL PRODUCTO PUNTO[/bold green]"
            console.clear()
            console.print(tabla_preview)

        elif opc == "7":
            console.print("\n[bold cyan]=== PROYECCIÓN VECTORIAL ORTOGONAL ===[/bold cyan]")
            v = pedir_vector("Ingresa Vector V a proyectar (v_x, v_y)")
            u = pedir_vector("Ingresa Vector Base U sobre el cual proyectar (u_x, u_y)")
            if u.es_cero():
                console.print("[bold red]No se puede proyectar sobre el vector nulo (0,0).[/bold red]")
            else:
                explicacion = v.explicar_proyeccion(u, "V", "U")
                renderizar_panel_depuracion(explicacion)
                proy = v.proyeccion_sobre(u)
                trazar_vector_en_tablero(tablero_demo, Vector2D(0, 0), proy)
                if tablero_demo.es_posicion_valida(proy):
                    tablero_demo.rastro_proyeccion.add(proy.a_tupla_grilla())
                tabla_preview = crear_cuadricula_cartesiana(tablero_demo)
                tabla_preview.title = "[bold green]VISTA GRÁFICA: PROYECCIÓN ORTOGONAL proj_u(v)[/bold green]"
                console.clear()
                console.print(tabla_preview)

        elif opc == "8":
            tablero_demo.disparos_acierto.clear()
            tablero_demo.disparos_agua.clear()
            tablero_demo.rastro_proyeccion.clear()
            tablero_demo.marcas_temporales.clear()
            console.print("[bold green]Plano cartesiano limpiado con éxito.[/bold green]")

        Prompt.ask("\n[dim yellow]Presiona Enter para continuar...[/dim yellow]")


# =============================================================================
# MODO TUTORIAL / MISIONES PEDAGÓGICAS GUIADAS
# =============================================================================

def ejecutar_tutorial_guiado() -> None:
    """Modo tutorial por misiones para alumnos de secundaria"""
    misiones = [
        {
            "titulo": "Misión 1: Tu Primer Disparo Vectorial (Suma de Vectores)",
            "historia": "Tu fragata se encuentra en el origen P = (2, 3). El radar detectó una boya enemiga en T = (5, 7).",
            "origen": Vector2D(2, 3),
            "objetivo": Vector2D(5, 7),
            "formula": "V_tiro = Objetivo - Origen = (5 - 2, 7 - 3) = (3, 4)",
            "solucion": Vector2D(3, 4),
            "pista": "Para llegar a (5,7) desde (2,3), calcula cuánto debes moverte en X (5 - 2) y en Y (7 - 3)."
        },
        {
            "titulo": "Misión 2: Artillería y el Viento Marino (Suma Múltiple)",
            "historia": "Tu barco está en P = (1, 1) y deseas impactar en T = (6, 5). El viento sopla con V_viento = (2, -1).",
            "origen": Vector2D(1, 1),
            "objetivo": Vector2D(6, 5),
            "formula": "V_tiro = T - P - V_viento = (6, 5) - (1, 1) - (2, -1) = (3, 5)",
            "solucion": Vector2D(3, 5),
            "pista": "El viento sumará (2, -1) al disparo. Debes compensar restando el viento al vector deseado."
        },
        {
            "titulo": "Misión 3: Torpedo de Propulsión Escalar",
            "historia": "Tu submarino está en P = (0, 0). Apuntas en la dirección unitaria u = (1, 2) y el objetivo está en (3, 6).",
            "origen": Vector2D(0, 0),
            "objetivo": Vector2D(3, 6),
            "formula": "k · (1, 2) = (3, 6)  -->  k = 3",
            "solucion_escalar": 3,
            "pista": "¿Por qué número debes multiplicar (1, 2) para obtener (3, 6)?"
        }
    ]

    for i, m in enumerate(misiones, 1):
        console.clear()

        # Construir un tablero de demostración que visualice la misión
        tablero_demo = Tablero(ancho=10, alto=10, es_oculto=False, titulo=f"PLANO DE LA MISIÓN {i}")
        tablero_demo.marcas_temporales.clear()
        origen_demo = m["origen"]
        objetivo_demo = m["objetivo"]

        # Colocar un barco ficticio en el origen para visualizarlo en el plano
        if tablero_demo.es_posicion_valida(origen_demo):
            tablero_demo.marcas_temporales[origen_demo.a_tupla_grilla()] = ("◆", "bold green")
        if tablero_demo.es_posicion_valida(objetivo_demo):
            tablero_demo.marcas_temporales[objetivo_demo.a_tupla_grilla()] = ("◎", "bold red")

        # Trazar el vector de solución sobre el plano para referencia visual
        if "solucion" in m:
            trazar_vector_en_tablero(tablero_demo, origen_demo, objetivo_demo)
        else:
            trazar_vector_en_tablero(tablero_demo, origen_demo, Vector2D(3, 6))

        # Mostrar Dashboard Pseudo-GUI del tutorial
        mostrar_pantalla_mision_guiada(m, tablero_demo)

        if "solucion" in m:
            intentos = 0
            while intentos < 3:
                tiro = pedir_vector_con_previsualizacion(
                    origen_demo, tablero_demo,
                    mensaje=f"[Misión {i}] Introduce el Vector de Disparo que calculaste",
                    etiqueta_tabla=f"PREDICCIÓN DE TU DISPARO (MISIÓN {i})",
                    extra=None
                )
                if tiro == m["solucion"]:
                    console.print("\n[bold green]EXCELENTE: ¡Impacto directo confirmado![/bold green]")
                    explicacion = m["origen"].explicar_suma(tiro, "Pos_Barco", "Tiro_Alumno")
                    renderizar_panel_depuracion(explicacion)
                    break
                else:
                    intentos += 1
                    console.print(f"[bold red]Incorrecto. El disparo cayó en {m['origen'] + tiro}, no en el objetivo {m['objetivo']}. Intento {intentos}/3.[/bold red]")
                    if intentos == 3:
                        console.print(f"\n[bold yellow]Explicación de la solución:[/bold yellow] La respuesta correcta es {m['solucion']}.")
                        console.print(f"Fórmula: {m['formula']}")

        elif "solucion_escalar" in m:
            intentos = 0
            while intentos < 3:
                k = IntPrompt.ask("Introduce el valor del escalar k")
                if k == m["solucion_escalar"]:
                    console.print("\n[bold green]PERFECTO: Has calculado correctamente el multiplicador escalar k = 3.[/bold green]")
                    break
                else:
                    intentos += 1
                    console.print(f"[bold red]Incorrecto. Multiplicar por {k} da {Vector2D(1,2) * k}. Intento {intentos}/3.[/bold red]")
                    if intentos == 3:
                        console.print(f"\n[bold yellow]Solución:[/bold yellow] {m['formula']}")

        Prompt.ask("\n[dim yellow]Presiona Enter para avanzar...[/dim yellow]")

    console.print("\n[bold green]FELICITACIONES: Has completado el entrenamiento básico de álgebra vectorial naval.[/bold green]\n")
    console.print("[dim cyan]Para ver estos mismos vectores DIBUJADOS sobre el eje cartesiano con "
                  "flechas reales, proyección y zoom interactivo, abre la INTERFAZ GRÁFICA "
                  "desde el menú principal (opción 5).[/dim cyan]\n")
    Prompt.ask("[dim yellow]Presiona Enter para volver al menú principal...[/dim yellow]")
