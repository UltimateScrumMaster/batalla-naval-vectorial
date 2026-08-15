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
    limitar_impacto,
    limite_escalar,
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


class TestLimitesMapa(unittest.TestCase):
    """Verifica el recorte del vector para que el disparo nunca salga del mapa."""

    def test_techo_se_recorta_al_eje_mas_cercano(self):
        # Origen (0,0), vector (9,10) -> impacto (9,10) sale por el techo -> (9,9).
        v = limitar_impacto(Vector2D(0, 0), Vector2D(9, 10))
        self.assertEqual(v, Vector2D(9, 9))

    def test_cambio_de_buque_a_esquina(self):
        # Origen (8,9), vector (3,4) -> impacto (11,13) -> recortado a (1,0)
        # para que el impacto quede en (9,9).
        v = limitar_impacto(Vector2D(8, 9), Vector2D(3, 4))
        self.assertEqual(v, Vector2D(1, 0))
        self.assertEqual(Vector2D(8, 9) + v, Vector2D(9, 9))

    def test_cambio_de_buque_mantiene_sentido(self):
        # Origen (2,6), vector (3,4) -> impacto (5,10) -> debe quedar (5,9),
        # es decir vector (3,3): se acorta solo la componente que desborda.
        v = limitar_impacto(Vector2D(2, 6), Vector2D(3, 4))
        self.assertEqual(v, Vector2D(3, 3))
        self.assertEqual(Vector2D(2, 6) + v, Vector2D(5, 9))

    def test_vector_dentro_del_mapa_no_cambia(self):
        v = limitar_impacto(Vector2D(4, 5), Vector2D(3, 4))
        self.assertEqual(v, Vector2D(3, 4))

    def test_componente_valida_se_conserva(self):
        v = limitar_impacto(Vector2D(0, 0), Vector2D(9, 10))
        self.assertEqual(v.x, 9)
        self.assertEqual(v.y, 9)

    def test_limite_inferior_negativo(self):
        # Origen (1,1), vector (-5, 2) -> impacto (-4, 3): x se recorta a -1.
        v = limitar_impacto(Vector2D(1, 1), Vector2D(-5, 2))
        self.assertEqual(v, Vector2D(-1, 2))
        self.assertEqual(Vector2D(1, 1) + v, Vector2D(0, 3))

    def test_torpedo_con_escalar(self):
        # Origen (2,2), a (4,4), k=2 -> impacto (10,10) -> a (3,3) => (8,8).
        v = limitar_impacto(Vector2D(2, 2), Vector2D(4, 4), k=2)
        self.assertEqual(v, Vector2D(3, 3))

    def test_torpedo_con_escalar_nulo_no_toca(self):
        # Con k=0 el impacto siempre es el origen: el vector queda como está.
        v = limitar_impacto(Vector2D(2, 2), Vector2D(9, 9), k=0)
        self.assertEqual(v, Vector2D(9, 9))

    def test_viento_se_tiene_en_cuenta(self):
        # Viento (1,-1), origen (4,5), a (4,4) -> impacto (9,8): dentro, sin cambios.
        v = limitar_impacto(Vector2D(4, 5), Vector2D(4, 4), viento=Vector2D(1, -1))
        self.assertEqual(v, Vector2D(4, 4))

    def test_viento_que_desborda(self):
        # Viento (2,0), origen (8,8), a (2,2) -> x desborda: impacto final (9,9).
        v = limitar_impacto(Vector2D(8, 8), Vector2D(2, 2), viento=Vector2D(2, 0))
        self.assertEqual(v, Vector2D(-1, 1))
        self.assertEqual(Vector2D(8, 8) + v + Vector2D(2, 0), Vector2D(9, 9))

    def test_limite_escalar_diagonal(self):
        # Origen (2,2), a (3,3): floor(7/3)=2 es el k máximo.
        self.assertEqual(limite_escalar(Vector2D(2, 2), Vector2D(3, 3)), 2)

    def test_limite_escalar_vertical(self):
        # Origen (0,5), a (0,5): el techo ya se alcanza con k=0.
        self.assertEqual(limite_escalar(Vector2D(0, 5), Vector2D(0, 5)), 0)

    def test_limite_escalar_con_tope(self):
        # Origen (0,0), a (1,0): caben 9 pasos, pero el tope del slider es 5.
        self.assertEqual(limite_escalar(Vector2D(0, 0), Vector2D(1, 0)), 5)

    def test_limite_escalar_vector_nulo(self):
        self.assertEqual(limite_escalar(Vector2D(3, 3), Vector2D(0, 0)), 5)


if __name__ == "__main__":
    unittest.main()
