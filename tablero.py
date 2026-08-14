"""
=============================================================================
MÓDULO: tablero.py - Plano Cartesiano y Gestión de Grillas
=============================================================================
Este módulo maneja el plano cartesiano 2D donde se posicionan las flotas
y se registran los impactos. El sistema de coordenadas está diseñado como
un plano escolar real:
    - Eje X: Horizontal (0 a Ancho - 1, de izquierda a derecha)
    - Eje Y: Vertical (0 a Alto - 1, de abajo hacia arriba)
    - Origen (0, 0): Esquina inferior izquierda.
=============================================================================
"""

from __future__ import annotations
import random
from typing import List, Optional, Tuple, Set, Dict, Any
from vector2d import Vector2D
from barco import Barco, crear_flota_estandar


class ResultadoDisparo:
    """Estructura con los detalles de lo que ocurrió tras un ataque vectorial"""
    def __init__(self, coordenada: Vector2D, valido: bool, impacto: bool,
                 hundido: bool = False, barco: Optional[Barco] = None, repetido: bool = False,
                 mensaje: str = ""):
        self.coordenada = coordenada
        self.valido = valido
        self.impacto = impacto
        self.hundido = hundido
        self.barco = barco
        self.repetido = repetido
        self.mensaje = mensaje


class Tablero:
    """
    Representa el plano cartesiano marítimo.

    Atributos:
        ancho (int): Límite máximo en X (por defecto 10, índices 0..9).
        alto (int): Límite máximo en Y (por defecto 10, índices 0..9).
        es_oculto (bool): Si es True, oculta los barcos no impactados (modo niebla de guerra).
    """

    def __init__(self, ancho: int = 10, alto: int = 10, es_oculto: bool = False, titulo: str = "Tablero"):
        self.ancho = ancho
        self.alto = alto
        self.es_oculto = es_oculto
        self.titulo = titulo
        self.barcos: List[Barco] = []
        self.disparos_agua: Set[Tuple[int, int]] = set()
        self.disparos_acierto: Set[Tuple[int, int]] = set()
        self.historial_sonar: List[Dict[str, Any]] = []
        self.rastro_proyeccion: Set[Tuple[int, int]] = set()
        self.marcas_temporales: Dict[Tuple[int, int], Tuple[str, str]] = {}

    def es_posicion_valida(self, punto: Vector2D) -> bool:
        """Comprueba si un vector (x, y) está contenido dentro de los límites del tablero"""
        x, y = punto.a_tupla_grilla()
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def puede_colocar_barco(self, barco: Barco, origen: Vector2D, direccion: Vector2D) -> bool:
        """Verifica si un barco cabe en el plano sin colisionar con otros navíos"""
        for i in range(barco.tamano):
            pos = origen + (i * direccion)
            if not self.es_posicion_valida(pos):
                return False
            tupla_pos = pos.a_tupla_grilla()
            # Verificar colisión con barcos existentes
            for otro_barco in self.barcos:
                if otro_barco.ocupa_coordenada(pos):
                    return False
        return True

    def colocar_barco(self, barco: Barco, origen: Vector2D, direccion: Vector2D) -> bool:
        """Ubica un barco en el tablero si la posición es legal"""
        if self.puede_colocar_barco(barco, origen, direccion):
            barco.ubicar(origen, direccion)
            self.barcos.append(barco)
            return True
        return False

    def colocar_flota_aleatoria(self, flota: Optional[List[Barco]] = None) -> None:
        """Ubica automáticamente todos los barcos en posiciones válidas al azar"""
        if flota is None:
            flota = crear_flota_estandar()

        self.barcos.clear()
        direcciones_posibles = [
            Vector2D(1, 0),   # Horizontal hacia la derecha (+X)
            Vector2D(0, 1),   # Vertical hacia arriba (+Y)
            Vector2D(-1, 0),  # Horizontal hacia la izquierda (-X)
            Vector2D(0, -1)   # Vertical hacia abajo (-Y)
        ]

        for barco in flota:
            colocado = False
            intentos = 0
            while not colocado and intentos < 200:
                intentos += 1
                rx = random.randint(0, self.ancho - 1)
                ry = random.randint(0, self.alto - 1)
                origen = Vector2D(rx, ry)
                dir_elegida = random.choice(direcciones_posibles)
                if self.colocar_barco(barco, origen, dir_elegida):
                    colocado = True

            if not colocado:
                # Si falló por saturación, reintento limpio
                self.colocar_flota_aleatoria(flota)
                return

    def procesar_disparo(self, objetivo: Vector2D) -> ResultadoDisparo:
        """
        Evalúa el impacto de un vector en las coordenadas del tablero.
        """
        tupla = objetivo.a_tupla_grilla()

        # 1. Comprobar si cayó fuera del plano
        if not self.es_posicion_valida(objetivo):
            return ResultadoDisparo(
                coordenada=objetivo,
                valido=False,
                impacto=False,
                mensaje=f"ADVERTENCIA: El vector {objetivo} cayó fuera del plano de combate (0..{self.ancho-1}, 0..{self.alto-1})."
            )

        # 2. Comprobar si ya se había disparado en este punto
        if tupla in self.disparos_agua or tupla in self.disparos_acierto:
            return ResultadoDisparo(
                coordenada=objetivo,
                valido=True,
                impacto=(tupla in self.disparos_acierto),
                repetido=True,
                mensaje=f"INFO: Ya se había registrado un disparo previo en las coordenadas {objetivo}."
            )

        # 3. Comprobar si impactó en algún barco
        for barco in self.barcos:
            if barco.recibir_disparo(objetivo):
                self.disparos_acierto.add(tupla)
                hundido = barco.esta_hundido()
                mensaje = (f"IMPACTO CRÍTICO en {objetivo}! Has dañado al {barco.nombre}."
                           if not hundido else
                           f"HUNDIDO! El navío {barco.nombre} ha sido destruido en {objetivo}!")
                return ResultadoDisparo(
                    coordenada=objetivo,
                    valido=True,
                    impacto=True,
                    hundido=hundido,
                    barco=barco,
                    mensaje=mensaje
                )

        # 4. Cayó al agua
        self.disparos_agua.add(tupla)
        return ResultadoDisparo(
            coordenada=objetivo,
            valido=True,
            impacto=False,
            mensaje=f"AGUA: El disparo en {objetivo} no encontró ningún objetivo."
        )

    def todos_hundidos(self) -> bool:
        """Verifica si la flota completa fue eliminada"""
        if not self.barcos:
            return False
        return all(barco.esta_hundido() for barco in self.barcos)

    def obtener_simbolo_celda(self, x: int, y: int) -> Tuple[str, str]:
        """
        Devuelve el símbolo y el estilo de color de una celda específica.
        Símbolos:
            · : Agua vacía
            ◈ ◆ ▲ ▼ ● : Barcos aliados (si no está oculto)
            ✖ : Impacto certero
            ✕ : Disparo al agua
            ◉ : Señal de sónar
            ▸ : Traza de proyección orbital
        """
        tupla = (x, y)

        if tupla in self.marcas_temporales:
            return self.marcas_temporales[tupla]

        if tupla in self.disparos_acierto:
            return ("✖", "bold red")
        if tupla in self.disparos_agua:
            return ("✕", "dim cyan")
        if tupla in self.rastro_proyeccion:
            return ("▸", "bold yellow")

        # Buscar si hay un barco visible
        for barco in self.barcos:
            if barco.ocupa_coordenada(Vector2D(x, y)):
                if not self.es_oculto:
                    return (barco.icono, "bold green")
                elif tupla in barco.impactos:
                    return ("✖", "bold red")

        # Verificar si hay sónar registrado
        for scan in self.historial_sonar:
            if (x, y) == scan["centro"].a_tupla_grilla():
                return ("◉", "bold magenta")

        return ("· ", "dim blue")

    def barco_mas_cercano(self, origen: Vector2D) -> Optional[Tuple[Barco, float]]:
        """
        Encuentra el barco vivo más cercano a un punto y calcula la distancia euclidiana mínima.
        Ideal para la mecánica del sónar.
        """
        barcos_vivos = [b for b in self.barcos if not b.esta_hundido()]
        if not barcos_vivos:
            return None

        min_dist = float("inf")
        barco_cercano = None

        for barco in barcos_vivos:
            for celda in barco.celdas:
                if celda.a_tupla_grilla() not in barco.impactos:
                    d = origen.distancia_a(celda)
                    if d < min_dist:
                        min_dist = d
                        barco_cercano = barco

        if barco_cercano is not None:
            return (barco_cercano, min_dist)
        return None
