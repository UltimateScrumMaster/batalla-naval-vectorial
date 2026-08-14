"""
=================================================================================
TEST: test_juego_grafico.py
Pruebas de la lógica de la batalla naval gráfica (juego_grafico.py).
Se comprueban la función pura ejecutar_ataque_jugador y los costos, además de
un smoke test que abre la ventana tkinter y la cierra al instante.
=================================================================================
"""

import unittest

from vector2d import Vector2D
from tablero import Tablero
from juego_grafico import (
    COSTOS_HABILIDAD,
    NOMBRES_HABILIDAD,
    ejecutar_ataque_jugador,
)


def _tablero_vacio() -> Tablero:
    tab = Tablero(ancho=10, alto=10, es_oculto=True, titulo="test")
    tab.barcos = []
    return tab


class TestCostosHabilidades(unittest.TestCase):
    """Los costos de energía de cada habilidad deben coincidir con el juego."""

    def test_costos_conocidos(self):
        self.assertEqual(COSTOS_HABILIDAD["suma"], 0)
        self.assertEqual(COSTOS_HABILIDAD["viento"], 1)
        self.assertEqual(COSTOS_HABILIDAD["torpedo"], 2)
        self.assertEqual(COSTOS_HABILIDAD["sonar"], 1)
        self.assertEqual(COSTOS_HABILIDAD["orbital"], 4)

    def test_nombres_no_vacios(self):
        self.assertEqual(len(NOMBRES_HABILIDAD), 5)
        for nombre in NOMBRES_HABILIDAD.values():
            self.assertTrue(nombre.strip())


class TestEjecutarAtaqueJugador(unittest.TestCase):
    """Comprueba que cada habilidad se ejecuta correctamente sobre el tablero."""

    def test_suma_vacio_impacta_en_agua(self):
        tab = _tablero_vacio()
        res, err = ejecutar_ataque_jugador(
            "suma", Vector2D(1, 1), Vector2D(2, 2), Vector2D(0, 0), 1,
            Vector2D(0, 0), tab)
        self.assertIsNone(err)
        self.assertIn("resultado_tablero", res)
        self.assertIn((3, 3), tab.disparos_agua)

    def test_viento_suma_el_viento(self):
        tab = _tablero_vacio()
        _, err = ejecutar_ataque_jugador(
            "viento", Vector2D(1, 1), Vector2D(1, 0), Vector2D(0, 0), 1,
            Vector2D(1, 2), tab)
        self.assertIsNone(err)
        self.assertIn((3, 3), tab.disparos_agua)

    def test_torpedo_usa_k(self):
        tab = _tablero_vacio()
        _, err = ejecutar_ataque_jugador(
            "torpedo", Vector2D(2, 2), Vector2D(1, 1), Vector2D(0, 0), 3,
            Vector2D(0, 0), tab)
        self.assertIsNone(err)
        self.assertIn((5, 5), tab.disparos_agua)

    def test_torpedo_con_direccion_nula_rechazado(self):
        tab = _tablero_vacio()
        res, err = ejecutar_ataque_jugador(
            "torpedo", Vector2D(2, 2), Vector2D(0, 0), Vector2D(0, 0), 3,
            Vector2D(0, 0), tab)
        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertEqual(len(tab.disparos_agua), 0)

    def test_sonar_no_consume_celda(self):
        tab = _tablero_vacio()
        res, err = ejecutar_ataque_jugador(
            "sonar", Vector2D(2, 2), Vector2D(0, 0), Vector2D(0, 0), 1,
            Vector2D(0, 0), tab)
        self.assertIsNone(err)
        self.assertIn("mensaje", res)
        self.assertEqual(len(tab.disparos_agua), 0)

    def test_orbital_con_base_nula_rechazado(self):
        tab = _tablero_vacio()
        res, err = ejecutar_ataque_jugador(
            "orbital", Vector2D(2, 2), Vector2D(1, 1), Vector2D(0, 0), 1,
            Vector2D(0, 0), tab)
        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertEqual(len(tab.disparos_agua), 0)

    def test_habilidad_desconocida(self):
        tab = _tablero_vacio()
        res, err = ejecutar_ataque_jugador(
            "laser", Vector2D(2, 2), Vector2D(1, 1), Vector2D(0, 0), 1,
            Vector2D(0, 0), tab)
        self.assertIsNone(res)
        self.assertIn("desconocida", err)

    def test_orbital_ejecuta_sin_error(self):
        tab = _tablero_vacio()
        res, err = ejecutar_ataque_jugador(
            "orbital", Vector2D(2, 2), Vector2D(3, 0), Vector2D(1, 1), 1,
            Vector2D(0, 0), tab)
        self.assertIsNone(err)
        self.assertIn("resultado_tablero", res)


class TestVentanaSmoke(unittest.TestCase):
    """Abre la ventana gráfica y la cierra de inmediato (solo si hay tkinter)."""

    def test_crear_y_cerrar_ventana(self):
        try:
            from juego_grafico import AplicacionBatallaGrafica
        except Exception:
            self.skipTest("tkinter/matplotlib no disponibles")
        app = AplicacionBatallaGrafica()
        try:
            self.assertIsNotNone(app.origen_seleccionado)
            self.assertEqual(app.barra_energia["value"], 3)
        finally:
            app.raiz.destroy()


if __name__ == "__main__":
    unittest.main()
