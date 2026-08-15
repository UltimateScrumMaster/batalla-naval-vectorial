"""
=================================================================================
TEST: test_sesion.py
Pruebas de la lógica de la partida: registro de habilidades y máquina de
estados de SesionBatalla (juego_naval/juego/sesion.py), además de un smoke
test de la PantallaBatalla que la usa.
Migrado desde test_juego_grafico.py.
=================================================================================
"""

import os
import unittest

os.environ["BNV_DIAG"] = "0"

from juego_naval.dominio.vector2d import Vector2D
from juego_naval.dominio.tablero import Tablero
from juego_naval.dominio.barco import Barco
from juego_naval.logica.sesion import (
    SesionBatalla,
    EstadoBatalla,
    COSTOS_HABILIDAD,
    NOMBRES_HABILIDAD,
    ejecutar_habilidad,
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


class TestEjecutarHabilidad(unittest.TestCase):
    """Comprueba que cada habilidad se ejecuta correctamente sobre el tablero."""

    def test_suma_vacio_impacta_en_agua(self):
        tab = _tablero_vacio()
        res, err = ejecutar_habilidad(
            "suma", Vector2D(1, 1), Vector2D(2, 2), Vector2D(0, 0), 1,
            Vector2D(0, 0), tab)
        self.assertIsNone(err)
        self.assertIn("resultado_tablero", res)
        self.assertIn((3, 3), tab.disparos_agua)

    def test_viento_suma_el_viento(self):
        tab = _tablero_vacio()
        _, err = ejecutar_habilidad(
            "viento", Vector2D(1, 1), Vector2D(1, 0), Vector2D(0, 0), 1,
            Vector2D(1, 2), tab)
        self.assertIsNone(err)
        self.assertIn((3, 3), tab.disparos_agua)

    def test_torpedo_usa_k(self):
        tab = _tablero_vacio()
        _, err = ejecutar_habilidad(
            "torpedo", Vector2D(2, 2), Vector2D(1, 1), Vector2D(0, 0), 3,
            Vector2D(0, 0), tab)
        self.assertIsNone(err)
        self.assertIn((5, 5), tab.disparos_agua)

    def test_torpedo_con_direccion_nula_rechazado(self):
        tab = _tablero_vacio()
        res, err = ejecutar_habilidad(
            "torpedo", Vector2D(2, 2), Vector2D(0, 0), Vector2D(0, 0), 3,
            Vector2D(0, 0), tab)
        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertEqual(len(tab.disparos_agua), 0)

    def test_sonar_no_consume_celda(self):
        tab = _tablero_vacio()
        res, err = ejecutar_habilidad(
            "sonar", Vector2D(2, 2), Vector2D(0, 0), Vector2D(0, 0), 1,
            Vector2D(0, 0), tab)
        self.assertIsNone(err)
        self.assertIn("mensaje", res)
        self.assertEqual(len(tab.disparos_agua), 0)

    def test_orbital_con_base_nula_rechazado(self):
        tab = _tablero_vacio()
        res, err = ejecutar_habilidad(
            "orbital", Vector2D(2, 2), Vector2D(1, 1), Vector2D(0, 0), 1,
            Vector2D(0, 0), tab)
        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertEqual(len(tab.disparos_agua), 0)

    def test_habilidad_desconocida(self):
        tab = _tablero_vacio()
        res, err = ejecutar_habilidad(
            "laser", Vector2D(2, 2), Vector2D(1, 1), Vector2D(0, 0), 1,
            Vector2D(0, 0), tab)
        self.assertIsNone(res)
        self.assertIn("desconocida", err)

    def test_orbital_ejecuta_sin_error(self):
        tab = _tablero_vacio()
        res, err = ejecutar_habilidad(
            "orbital", Vector2D(2, 2), Vector2D(3, 0), Vector2D(1, 1), 1,
            Vector2D(0, 0), tab)
        self.assertIsNone(err)
        self.assertIn("resultado_tablero", res)


class TestSesionBatalla(unittest.TestCase):
    """Verifica la máquina de estados de una partida completa."""

    def test_estado_inicial(self):
        s = SesionBatalla(semilla=1)
        self.assertEqual(s.estado, EstadoBatalla.TURNO_JUGADOR)
        self.assertEqual(s.turno, 1)
        self.assertEqual(s.energia_jugador, 2)

    def test_comenzar_turno_suma_energia(self):
        s = SesionBatalla(semilla=1)
        s.comenzar_turno_jugador()
        self.assertEqual(s.energia_jugador, 3)
        self.assertEqual(s.estado, EstadoBatalla.TURNO_JUGADOR)

    def test_energia_tope_seis(self):
        s = SesionBatalla(semilla=1)
        s.energia_jugador = 6
        s.comenzar_turno_jugador()
        self.assertEqual(s.energia_jugador, 6)

    def test_viento_siempre_en_rango(self):
        s = SesionBatalla(semilla=3)
        self.assertIn(s.viento.x, (-2, -1, 0, 1, 2))
        self.assertIn(s.viento.y, (-2, -1, 0, 1, 2))

    def test_ataque_suma_gratis_con_cero_energia(self):
        s = SesionBatalla(semilla=1)
        s.energia_jugador = 0
        res, err = s.ejecutar_ataque_jugador(
            "suma", Vector2D(1, 1), Vector2D(1, 1), Vector2D(0, 0), 1)
        self.assertIsNone(err)
        self.assertIsNotNone(res)

    def test_energia_insuficiente_no_ejecuta(self):
        s = SesionBatalla(semilla=1)
        s.energia_jugador = 1
        res, err = s.ejecutar_ataque_jugador(
            "torpedo", Vector2D(2, 2), Vector2D(1, 0), Vector2D(0, 0), 1)
        self.assertIsNone(res)
        self.assertIn("Energía insuficiente", err)

    def test_torpedo_descuenta_energia(self):
        s = SesionBatalla(semilla=1)
        s.energia_jugador = 3
        res, err = s.ejecutar_ataque_jugador(
            "torpedo", Vector2D(2, 2), Vector2D(1, 0), Vector2D(0, 0), 1)
        self.assertIsNone(err)
        self.assertEqual(s.energia_jugador, 1)

    def test_ataque_invalido_no_descuenta_energia(self):
        s = SesionBatalla(semilla=1)
        s.energia_jugador = 3
        res, err = s.ejecutar_ataque_jugador(
            "torpedo", Vector2D(2, 2), Vector2D(0, 0), Vector2D(0, 0), 3)
        self.assertIsNone(res)
        self.assertIsNotNone(err)
        self.assertEqual(s.energia_jugador, 3)

    def test_habilidad_desconocida_en_sesion(self):
        s = SesionBatalla(semilla=1)
        res, err = s.ejecutar_ataque_jugador(
            "laser", Vector2D(0, 0), Vector2D(1, 0), Vector2D(0, 0), 1)
        self.assertIsNone(res)
        self.assertIn("desconocida", err)

    def test_victoria_al_hundir_flota_enemiga(self):
        s = SesionBatalla(semilla=42)
        b = Barco("Lancha", 1)
        b.ubicar(Vector2D(3, 3), Vector2D(1, 0))
        s.tablero_enemigo.barcos = [b]
        s.comenzar_turno_jugador()
        res, err = s.ejecutar_ataque_jugador(
            "suma", Vector2D(0, 0), Vector2D(3, 3), Vector2D(0, 0), 1)
        self.assertIsNone(err)
        self.assertIsNotNone(res)
        self.assertEqual(s.estado, EstadoBatalla.VICTORIA)

    def test_derrota_si_flota_jugador_hundida(self):
        s = SesionBatalla(semilla=42)
        b = Barco("Lancha", 1)
        b.ubicar(Vector2D(5, 5), Vector2D(1, 0))
        s.tablero_jugador.barcos = [b]
        b.recibir_disparo(Vector2D(5, 5))
        s.ejecutar_turno_ia()
        self.assertEqual(s.estado, EstadoBatalla.DERROTA)

    def test_turno_ia_incrementa_turno(self):
        s = SesionBatalla(semilla=42)
        res = s.ejecutar_turno_ia()
        self.assertIsInstance(res, dict)
        self.assertEqual(s.estado, EstadoBatalla.TURNO_JUGADOR)
        self.assertEqual(s.turno, 2)


class TestPantallaBatallaSmoke(unittest.TestCase):
    """Abre la pantalla de batalla y la cierra de inmediato (si hay GUI)."""

    def test_abrir_y_cerrar_pantalla(self):
        try:
            import tkinter
            import matplotlib  # noqa: F401
        except Exception:
            self.skipTest("tkinter/matplotlib no disponibles")
        import tkinter as tk
        from juego_naval.ui.gestor_pantallas import GestorPantallas
        from juego_naval.ui.pantallas.batalla import PantallaBatalla

        raiz = tk.Tk()
        try:
            raiz.withdraw()
            gestor = GestorPantallas(raiz)
            gestor.registrar("batalla", PantallaBatalla)
            gestor.reemplazar("batalla")
            pantalla = gestor.pantalla_actual()
            self.assertEqual(gestor.nombre_actual(), "batalla")
            self.assertIsNotNone(pantalla.origen_seleccionado)
            self.assertEqual(pantalla.barra_energia["value"], 3)
        finally:
            raiz.destroy()


if __name__ == "__main__":
    unittest.main()
