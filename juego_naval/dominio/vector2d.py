"""
=============================================================================
MÓDULO: vector2d.py - Clase y Operaciones con Vectores 2D
=============================================================================
Este módulo define la clase `Vector2D` pensada para estudiantes de secundaria
y desarrolladores. Incluye sobrecarga de operadores matemáticos, métodos
didácticos y generadores de explicación paso a paso (modo depuración / debug)
para entender cómo se calcula cada operación vectorial en tiempo real.
=============================================================================
"""

from __future__ import annotations
import math
from typing import Tuple, List, Dict, Any


class Vector2D:
    """
    Representa un vector en el plano cartesiano 2D con componentes (x, y).

    Atributos:
        x (float | int): Componente horizontal (eje X).
        y (float | int): Componente vertical (eje Y).
    """

    def __init__(self, x: float | int = 0, y: float | int = 0):
        # Guardamos x e y. Si son valores enteros exactos, los dejamos como int para prolijidad visual
        self.x: float | int = int(x) if isinstance(x, (int, float)) and x == int(x) else round(x, 2)
        self.y: float | int = int(y) if isinstance(y, (int, float)) and y == int(y) else round(y, 2)

    # -------------------------------------------------------------------------
    # OPERADORES MATEMÁTICOS BÁSICOS
    # -------------------------------------------------------------------------

    def __add__(self, otro: Vector2D) -> Vector2D:
        """
        Suma de dos vectores: v1 + v2 = (x1 + x2, y1 + y2)
        Ejemplo: (2, 3) + (1, 4) = (3, 7)
        """
        if not isinstance(otro, Vector2D):
            raise TypeError(f"No se puede sumar Vector2D con {type(otro).__name__}")
        return Vector2D(self.x + otro.x, self.y + otro.y)

    def __sub__(self, otro: Vector2D) -> Vector2D:
        """
        Resta de dos vectores: v1 - v2 = (x1 - x2, y1 - y2)
        Ejemplo: (5, 8) - (2, 3) = (3, 5)
        """
        if not isinstance(otro, Vector2D):
            raise TypeError(f"No se puede restar Vector2D con {type(otro).__name__}")
        return Vector2D(self.x - otro.x, self.y - otro.y)

    def __mul__(self, escalar: float | int) -> Vector2D:
        """
        Multiplicación por un escalar (número real): k * v = (k * x, k * y)
        Ejemplo: 3 * (2, -1) = (6, -3)
        """
        if not isinstance(escalar, (int, float)):
            raise TypeError(f"El multiplicador debe ser un número (int o float), recibido: {type(escalar).__name__}")
        return Vector2D(self.x * escalar, self.y * escalar)

    def __rmul__(self, escalar: float | int) -> Vector2D:
        """Permite escribir '3 * v' además de 'v * 3'"""
        return self.__mul__(escalar)

    def __neg__(self) -> Vector2D:
        """Vector opuesto (-v): invierte el sentido del vector (-x, -y)"""
        return Vector2D(-self.x, -self.y)

    def __eq__(self, otro: object) -> bool:
        """Compara si dos vectores tienen las mismas componentes (con tolerancia flotante)"""
        if not isinstance(otro, Vector2D):
            return False
        return math.isclose(self.x, otro.x, abs_tol=1e-5) and math.isclose(self.y, otro.y, abs_tol=1e-5)

    def __repr__(self) -> str:
        """Representación textual formal del vector"""
        return f"Vector2D({self.x}, {self.y})"

    def __str__(self) -> str:
        """Representación legible para el usuario: (x, y)"""
        return f"({self.x}, {self.y})"

    # -------------------------------------------------------------------------
    # PROPIEDADES GEOMÉTRICAS Y MÉTODOS AVANZADOS
    # -------------------------------------------------------------------------

    def magnitud(self) -> float:
        """
        Calcula la longitud o módulo del vector usando el Teorema de Pitágoras:
        ||v|| = sqrt(x^2 + y^2)
        """
        return math.hypot(self.x, self.y)

    def magnitud_cuadrada(self) -> float | int:
        """Calcula ||v||^2 = x^2 + y^2 (evita la raíz cuadrada si no es necesaria)"""
        return self.x ** 2 + self.y ** 2

    def distancia_a(self, otro: Vector2D) -> float:
        """
        Calcula la distancia euclidiana entre dos puntos/vectores:
        d = ||v1 - v2|| = sqrt((x2 - x1)^2 + (y2 - y1)^2)
        """
        return (self - otro).magnitud()

    def producto_punto(self, otro: Vector2D) -> float | int:
        """
        Calcula el producto escalar (o producto punto) entre dos vectores:
        v1 · v2 = (x1 * x2) + (y1 * y2)
        """
        if not isinstance(otro, Vector2D):
            raise TypeError(f"El producto punto requiere otro Vector2D, recibido: {type(otro).__name__}")
        return self.x * otro.x + self.y * otro.y

    def es_cero(self) -> bool:
        """Verifica si es el vector nulo (0, 0)"""
        return self.x == 0 and self.y == 0

    def normalizado(self) -> Vector2D:
        """
        Devuelve el vector unitario (magnitud = 1) en la misma dirección:
        u = v / ||v||
        """
        mag = self.magnitud()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def proyeccion_sobre(self, base: Vector2D) -> Vector2D:
        """
        Calcula la proyección ortogonal de 'self' (vector v) sobre el vector 'base' (vector u):
        
        proj_u(v) = [ (v · u) / ||u||^2 ] * u

        Geométricamente representa la "sombra" que arroja el vector v sobre la recta que contiene a u.
        """
        if not isinstance(base, Vector2D):
            raise TypeError("La base de proyección debe ser un Vector2D.")
        if base.es_cero():
            raise ValueError("No se puede proyectar sobre el vector nulo (0, 0).")

        # Factor escalar c = (v · u) / ||u||^2
        producto = self.producto_punto(base)
        mag_cuadrada = base.magnitud_cuadrada()
        factor = producto / mag_cuadrada
        return factor * base

    def a_tupla_grilla(self) -> Tuple[int, int]:
        """Convierte las componentes a enteros redondeados para indexar el tablero (x, y)"""
        return (int(round(self.x)), int(round(self.y)))

    # -------------------------------------------------------------------------
    # MÉTODOS DE DEPURACIÓN / EXPLICACIÓN DIDÁCTICA PASO A PASO
    # -------------------------------------------------------------------------

    def explicar_suma(self, otro: Vector2D, etiqueta_a: str = "A", etiqueta_b: str = "B") -> Dict[str, Any]:
        """Genera el desglose algebraico paso a paso de la suma de vectores"""
        resultado = self + otro
        return {
            "operacion": "Suma de Vectores",
            "formula": f"{etiqueta_a} + {etiqueta_b} = (Ax + Bx, Ay + By)",
            "vectores": {etiqueta_a: str(self), etiqueta_b: str(otro)},
            "pasos": [
                f"1. Coordenada X = {self.x} + {otro.x} = {resultado.x}",
                f"2. Coordenada Y = {self.y} + {otro.y} = {resultado.y}",
                f"3. Vector Resultante = ({resultado.x}, {resultado.y})"
            ],
            "resultado": resultado
        }

    def explicar_escalar(self, k: float | int, etiqueta: str = "v") -> Dict[str, Any]:
        """Genera el desglose paso a paso de la multiplicación por un escalar"""
        resultado = self * k
        return {
            "operacion": "Multiplicación por Escalar",
            "formula": f"k * {etiqueta} = (k * x, k * y)",
            "valores": {"Escalar k": k, "Vector original": str(self)},
            "pasos": [
                f"1. Multiplicamos componente X por {k}: {k} * {self.x} = {resultado.x}",
                f"2. Multiplicamos componente Y por {k}: {k} * {self.y} = {resultado.y}",
                f"3. Vector Escaldo = ({resultado.x}, {resultado.y})"
            ],
            "resultado": resultado
        }

    def explicar_distancia(self, otro: Vector2D, etiqueta_a: str = "Barco", etiqueta_b: str = "Objetivo") -> Dict[str, Any]:
        """Genera el desglose del cálculo de distancia euclidiana (Sónar) usando Pitágoras"""
        dx = otro.x - self.x
        dy = otro.y - self.y
        dx2 = dx ** 2
        dy2 = dy ** 2
        suma_cuad = dx2 + dy2
        distancia = math.sqrt(suma_cuad)

        return {
            "operacion": "Cálculo de Distancia / Módulo Euclidiano",
            "formula": "d = ||Δv|| = sqrt((x2 - x1)² + (y2 - y1)²)",
            "puntos": {etiqueta_a: str(self), etiqueta_b: str(otro)},
            "pasos": [
                f"1. Vector diferencia Δv = ({otro.x} - {self.x}, {otro.y} - {self.y}) = ({dx}, {dy})",
                f"2. Cuadrados de las componentes: ({dx})² = {dx2},  ({dy})² = {dy2}",
                f"3. Suma de cuadrados = {dx2} + {dy2} = {suma_cuad}",
                f"4. Raíz cuadrada: sqrt({suma_cuad}) ≈ {distancia:.2f} unidades de distancia"
            ],
            "distancia": round(distancia, 2)
        }

    def explicar_proyeccion(self, base: Vector2D, etiqueta_v: str = "Ataque", etiqueta_u: str = "Radar") -> Dict[str, Any]:
        """Genera el desglose completo del cálculo de proyección ortogonal"""
        punto = self.producto_punto(base)
        mag_u2 = base.magnitud_cuadrada()
        factor = punto / mag_u2 if mag_u2 != 0 else 0
        proy = factor * base

        return {
            "operacion": "Proyección Vectorial Ortogonal",
            "formula": f"proj_{etiqueta_u}({etiqueta_v}) = [ ({etiqueta_v} · {etiqueta_u}) / ||{etiqueta_u}||² ] * {etiqueta_u}",
            "vectores": {etiqueta_v: str(self), etiqueta_u: str(base)},
            "pasos": [
                f"1. Producto punto ({etiqueta_v} · {etiqueta_u}) = ({self.x} * {base.x}) + ({self.y} * {base.y}) = {punto}",
                f"2. Magnitud al cuadrado de la base ||{etiqueta_u}||² = ({base.x})² + ({base.y})² = {mag_u2}",
                f"3. Coeficiente escalar c = {punto} / {mag_u2} = {factor:.3f}",
                f"4. Proyección resultante = {factor:.3f} * ({base.x}, {base.y}) = ({proy.x:.2f}, {proy.y:.2f})"
            ],
            "resultado": proy,
            "factor": factor
        }
