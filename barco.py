"""
=============================================================================
MÓDULO: barco.py - Modelado de Navíos Navales con Vectores
=============================================================================
Cada navío se modela matemáticamente a partir de un vector de posición inicial
P_0 y un vector de dirección u con una longitud k:
    Posiciones = { P_0 + i * u | i en [0, tamaño - 1] }
Esto refuerza el concepto de ecuaciones paramétricas de una recta discreta.
=============================================================================
"""

from __future__ import annotations
from typing import List, Set, Tuple
from vector2d import Vector2D


class Barco:
    """
    Representa un barco en el tablero de batalla.

    Atributos:
        nombre (str): Nombre del navío.
        origen (Vector2D): Vector de posición del punto de anclaje (popa/proa).
        tamano (int): Cantidad de casillas que ocupa el barco.
        direccion (Vector2D): Vector unitario de orientación (1,0 horizontal o 0,1 vertical).
        icono (str): Carácter decorativo para representarlo en la consola.
    """

    def __init__(self, nombre: str, tamano: int, icono: str = "◆"):
        self.nombre = nombre
        self.tamano = tamano
        self.icono = icono
        self.origen: Vector2D = Vector2D(0, 0)
        self.direccion: Vector2D = Vector2D(1, 0)  # Por defecto horizontal hacia +X
        self.celdas: List[Vector2D] = []
        self.impactos: Set[Tuple[int, int]] = set()

    def ubicar(self, origen: Vector2D, direccion: Vector2D) -> None:
        """
        Calcula las coordenadas de todas las celdas del barco usando la ecuación:
        Celda_i = Origen + i * Direccion
        """
        self.origen = origen
        self.direccion = direccion
        self.celdas = []
        self.impactos.clear()

        for i in range(self.tamano):
            # Ecuación vectorial de la posición de cada casilla del barco
            pos = origen + (i * direccion)
            self.celdas.append(pos)

    def ocupa_coordenada(self, punto: Vector2D) -> bool:
        """Verifica si el barco está sobre una coordenada específica"""
        tupla = punto.a_tupla_grilla()
        return any(c.a_tupla_grilla() == tupla for c in self.celdas)

    def recibir_disparo(self, punto: Vector2D) -> bool:
        """
        Procesa un disparo. Si impacta en una casilla del barco, registra el daño.
        Devuelve True si hubo impacto, False en caso contrario.
        """
        tupla = punto.a_tupla_grilla()
        if self.ocupa_coordenada(punto):
            self.impactos.add(tupla)
            return True
        return False

    def esta_hundido(self) -> bool:
        """Devuelve True si todas las casillas del barco sufrieron un impacto"""
        if not self.celdas:
            return False
        return len(self.impactos) >= self.tamano

    def porcentaje_salud(self) -> float:
        """Calcula el porcentaje de salud restante del navío"""
        if self.tamano == 0:
            return 0.0
        vivas = self.tamano - len(self.impactos)
        return (vivas / self.tamano) * 100

    def __str__(self) -> str:
        estado = "[HUNDIDO]" if self.esta_hundido() else f"{self.tamano - len(self.impactos)}/{self.tamano} HP"
        return f"{self.nombre} ({estado})"


def crear_flota_estandar() -> List[Barco]:
    """Crea una flota equilibrada para una partida estándar"""
    return [
        Barco("Portaaviones Orbital", tamano=4, icono="◈"),
        Barco("Acorazado Vectorial", tamano=3, icono="◆"),
        Barco("Destructor Cartesiano", tamano=3, icono="▲"),
        Barco("Submarino de Gauss", tamano=2, icono="▼"),
        Barco("Patrullera Escalar", tamano=2, icono="●"),
    ]
