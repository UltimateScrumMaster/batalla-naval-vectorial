"""
=============================================================================
SUITE DE PRUEBAS: test_vector2d.py
=============================================================================
Verifica la corrección matemática de todas las operaciones vectoriales:
- Suma y resta
- Multiplicación por escalar
- Magnitud y Teorema de Pitágoras
- Distancia euclidiana
- Producto punto
- Proyección vectorial ortogonal
- Formatos de desglose paso a paso (debugging)
=============================================================================
"""

import unittest
import math
from juego_naval.dominio.vector2d import Vector2D


class TestVector2D(unittest.TestCase):

    def test_creacion_y_componentes(self):
        v = Vector2D(3, 4)
        self.assertEqual(v.x, 3)
        self.assertEqual(v.y, 4)
        self.assertEqual(str(v), "(3, 4)")

    def test_suma_vectores(self):
        v1 = Vector2D(2, 5)
        v2 = Vector2D(3, -2)
        suma = v1 + v2
        self.assertEqual(suma, Vector2D(5, 3))

    def test_resta_vectores(self):
        v1 = Vector2D(10, 8)
        v2 = Vector2D(4, 3)
        resta = v1 - v2
        self.assertEqual(resta, Vector2D(6, 5))

    def test_multiplicacion_escalar(self):
        v = Vector2D(3, -4)
        self.assertEqual(v * 2, Vector2D(6, -8))
        self.assertEqual(3 * v, Vector2D(9, -12))
        self.assertEqual(v * 0, Vector2D(0, 0))

    def test_magnitud_pitagoras(self):
        # Triángulo sagrado 3-4-5
        v = Vector2D(3, 4)
        self.assertAlmostEqual(v.magnitud(), 5.0)
        self.assertEqual(v.magnitud_cuadrada(), 25)

    def test_distancia_euclidiana(self):
        p1 = Vector2D(1, 1)
        p2 = Vector2D(4, 5)
        # Distancia = sqrt((4-1)^2 + (5-1)^2) = sqrt(9 + 16) = 5
        self.assertAlmostEqual(p1.distancia_a(p2), 5.0)

    def test_producto_punto(self):
        v1 = Vector2D(2, 3)
        v2 = Vector2D(4, -1)
        # v1 · v2 = (2 * 4) + (3 * -1) = 8 - 3 = 5
        self.assertEqual(v1.producto_punto(v2), 5)

        # Vectores ortogonales (perpendiculares) -> producto punto = 0
        u = Vector2D(1, 0)
        w = Vector2D(0, 1)
        self.assertEqual(u.producto_punto(w), 0)

    def test_proyeccion_ortogonal(self):
        # Proyectar v = (3, 4) sobre el eje horizontal u = (2, 0)
        v = Vector2D(3, 4)
        u = Vector2D(2, 0)
        proy = v.proyeccion_sobre(u)
        # proj_u(v) debe ser (3, 0)
        self.assertEqual(proy, Vector2D(3, 0))

        # Proyectar sobre diagonal (1, 1)
        v2 = Vector2D(4, 0)
        u2 = Vector2D(2, 2)
        # v2 · u2 = 8. ||u2||^2 = 8. Factor = 1. proj = 1 * (2, 2) = (2, 2)
        proy2 = v2.proyeccion_sobre(u2)
        self.assertEqual(proy2, Vector2D(2, 2))

    def test_desglose_explicativo(self):
        v1 = Vector2D(2, 3)
        v2 = Vector2D(4, 5)
        info_suma = v1.explicar_suma(v2)
        self.assertIn("operacion", info_suma)
        self.assertIn("pasos", info_suma)
        self.assertEqual(len(info_suma["pasos"]), 3)

        info_dist = v1.explicar_distancia(v2)
        self.assertIn("distancia", info_dist)

        info_proy = v1.explicar_proyeccion(v2)
        self.assertIn("factor", info_proy)


if __name__ == "__main__":
    unittest.main()
