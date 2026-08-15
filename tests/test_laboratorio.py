"""
=================================================================================
TEST: test_laboratorio.py
Pruebas unitarias de la matemática del Laboratorio de Vectores
(juego_naval/juego/laboratorio.py). Solo funciones puras, sin ventana.
Migrado desde test_interfaz_grafica.py.
=================================================================================
"""

import unittest

from juego_naval.dominio.vector2d import Vector2D
from juego_naval.logica.laboratorio import (
    calcular_resultado_laboratorio,
    calcular_preview_disparo,
    OPCIONES_LABORATORIO,
)


class TestCalculoLaboratorio(unittest.TestCase):
    """Verifica el resultado algebraico de cada operación del laboratorio."""

    def test_suma(self):
        res = calcular_resultado_laboratorio("suma", Vector2D(2, 3), Vector2D(1, 4))
        self.assertEqual(res["tipo"], "vector")
        self.assertEqual(res["resultado"], Vector2D(3, 7))
        self.assertIn("3", " ".join(res["pasos"]))

    def test_resta(self):
        res = calcular_resultado_laboratorio("resta", Vector2D(5, 8), Vector2D(2, 3))
        self.assertEqual(res["tipo"], "vector")
        self.assertEqual(res["resultado"], Vector2D(3, 5))

    def test_escalar(self):
        res = calcular_resultado_laboratorio("escalar", Vector2D(0, 0), Vector2D(1, 2), k=3)
        self.assertEqual(res["tipo"], "vector")
        self.assertEqual(res["resultado"], Vector2D(3, 6))

    def test_escalar_negativo(self):
        res = calcular_resultado_laboratorio("escalar", Vector2D(0, 0), Vector2D(2, -1), k=-2)
        self.assertEqual(res["resultado"], Vector2D(-4, 2))

    def test_modulo(self):
        res = calcular_resultado_laboratorio("modulo", Vector2D(0, 0), Vector2D(3, 4))
        self.assertEqual(res["tipo"], "escalar")
        self.assertAlmostEqual(res["resultado"], 5.0, places=6)

    def test_distancia(self):
        res = calcular_resultado_laboratorio("distancia", Vector2D(0, 0), Vector2D(3, 4))
        self.assertEqual(res["tipo"], "escalar")
        self.assertAlmostEqual(res["resultado"], 5.0, places=6)

    def test_producto_punto(self):
        res = calcular_resultado_laboratorio("punto", Vector2D(1, 2), Vector2D(3, 4))
        self.assertEqual(res["tipo"], "escalar")
        self.assertEqual(res["resultado"], 11)

    def test_proyeccion(self):
        res = calcular_resultado_laboratorio("proyeccion", Vector2D(1, 0), Vector2D(3, 4))
        self.assertEqual(res["tipo"], "vector")
        self.assertEqual(res["resultado"], Vector2D(3, 0))

    def test_proyeccion_base_nula(self):
        res = calcular_resultado_laboratorio("proyeccion", Vector2D(0, 0), Vector2D(3, 4))
        self.assertTrue(res.get("error", False))

    def test_opcion_desconocida(self):
        with self.assertRaises(ValueError):
            calcular_resultado_laboratorio("no_existe", Vector2D(1, 1), Vector2D(1, 1))

    def test_opciones_registradas(self):
        self.assertEqual(len(OPCIONES_LABORATORIO), 7)
        self.assertIn("suma", OPCIONES_LABORATORIO)
        self.assertIn("proyeccion", OPCIONES_LABORATORIO)


class TestPreviewDisparo(unittest.TestCase):
    """Verifica la predicción de impacto dentro/fuera del tablero."""

    def test_impacto_dentro(self):
        preview = calcular_preview_disparo(Vector2D(2, 3), Vector2D(3, 4))
        self.assertTrue(preview["dentro"])
        self.assertEqual(preview["destino"], Vector2D(5, 7))

    def test_impacto_fuera_por_x(self):
        preview = calcular_preview_disparo(Vector2D(8, 3), Vector2D(3, 1))
        self.assertFalse(preview["dentro"])
        self.assertEqual(preview["destino"], Vector2D(11, 4))

    def test_impacto_fuera_por_negativo(self):
        preview = calcular_preview_disparo(Vector2D(2, 2), Vector2D(-4, 1))
        self.assertFalse(preview["dentro"])

    def test_tablero_personalizado(self):
        preview = calcular_preview_disparo(Vector2D(3, 3), Vector2D(3, 3),
                                           ancho=20, alto=20)
        self.assertTrue(preview["dentro"])

    def test_borde_inferior_izquierdo(self):
        preview = calcular_preview_disparo(Vector2D(0, 0), Vector2D(0, 0))
        self.assertTrue(preview["dentro"])


if __name__ == "__main__":
    unittest.main()
