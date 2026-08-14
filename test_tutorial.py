"""
=================================================================================
TEST: test_tutorial.py
Pruebas del contenido pedagógico del Tutorial Guiado
(juego_naval/juego/tutorial.py): estructura de las misiones y evaluación de
intentos del alumno. Solo funciones puras.
=================================================================================
"""

import unittest

from vector2d import Vector2D
from juego_naval.juego.tutorial import (
    MISIONES,
    es_mision_vectorial,
    evaluar_intento_tutorial,
)


class TestEstructuraMisiones(unittest.TestCase):
    """Cada misión debe estar bien formada y con su solución."""

    def test_tres_misiones(self):
        self.assertEqual(len(MISIONES), 3)

    def test_campos_esenciales(self):
        for mision in MISIONES:
            self.assertIn("titulo", mision)
            self.assertIn("historia", mision)
            self.assertIn("origen", mision)
            self.assertIn("objetivo", mision)
            self.assertIn("pista", mision)
            self.assertIsInstance(mision["origen"], Vector2D)
            self.assertIsInstance(mision["objetivo"], Vector2D)

    def test_clasificacion_vectorial(self):
        self.assertTrue(es_mision_vectorial(MISIONES[0]))
        self.assertTrue(es_mision_vectorial(MISIONES[1]))
        self.assertFalse(es_mision_vectorial(MISIONES[2]))

    def test_mision_2_tiene_viento(self):
        self.assertIn("viento", MISIONES[1])
        self.assertEqual(MISIONES[1]["viento"], Vector2D(2, -1))


class TestEvaluacionIntentos(unittest.TestCase):
    """La evaluación debe distinguir acierto de error en ambos tipos de misión."""

    def test_vector_correcto(self):
        acierto, mensaje = evaluar_intento_tutorial(MISIONES[0], Vector2D(3, 4))
        self.assertTrue(acierto)
        self.assertTrue(mensaje.strip())

    def test_vector_incorrecto(self):
        acierto, mensaje = evaluar_intento_tutorial(MISIONES[0], Vector2D(0, 0))
        self.assertFalse(acierto)
        self.assertIn("no en el objetivo", mensaje)

    def test_mision_con_viento_exige_compensar(self):
        acierto, _ = evaluar_intento_tutorial(MISIONES[1], Vector2D(3, 5))
        self.assertTrue(acierto)
        acierto, _ = evaluar_intento_tutorial(MISIONES[1], Vector2D(5, 4))
        self.assertFalse(acierto)

    def test_escalar_correcto(self):
        acierto, _ = evaluar_intento_tutorial(MISIONES[2], 3)
        self.assertTrue(acierto)

    def test_escalar_incorrecto(self):
        acierto, _ = evaluar_intento_tutorial(MISIONES[2], 2)
        self.assertFalse(acierto)

    def test_escalar_invalido(self):
        acierto, mensaje = evaluar_intento_tutorial(MISIONES[2], "k")
        self.assertFalse(acierto)
        self.assertIn("número entero", mensaje)


if __name__ == "__main__":
    unittest.main()
