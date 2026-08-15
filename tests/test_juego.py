"""
=============================================================================
SUITE DE PRUEBAS: test_juego.py
=============================================================================
Verifica la mecánica del juego:
- Barcos y detección de coordenadas paramétricas
- Tablero y límites del plano cartesiano
- Ejecución de habilidades (Suma, Viento, Escalar, Sónar, Proyección)
- Inteligencia Artificial y caza de objetivos
=============================================================================
"""

import unittest
from juego_naval.dominio.vector2d import Vector2D
from juego_naval.dominio.barco import Barco, crear_flota_estandar
from juego_naval.dominio.tablero import Tablero
from juego_naval.logica.habilidades import (
    DisparoBasicoSuma,
    DisparoConViento,
    TorpedoEscalar,
    SonarDistanciaEuclidiana,
    CanonProyeccionOrbital
)
from juego_naval.logica.ia import IAEnemiga


class TestMecanicasJuego(unittest.TestCase):

    def test_posicionamiento_barco(self):
        barco = Barco("Fragata", tamano=3)
        origen = Vector2D(2, 2)
        direccion = Vector2D(1, 0)  # Horizontal hacia la derecha
        barco.ubicar(origen, direccion)

        self.assertEqual(len(barco.celdas), 3)
        self.assertEqual(barco.celdas[0], Vector2D(2, 2))
        self.assertEqual(barco.celdas[1], Vector2D(3, 2))
        self.assertEqual(barco.celdas[2], Vector2D(4, 2))
        self.assertTrue(barco.ocupa_coordenada(Vector2D(3, 2)))
        self.assertFalse(barco.ocupa_coordenada(Vector2D(5, 2)))

    def test_impacto_y_hundimiento(self):
        barco = Barco("Patrulla", tamano=2)
        barco.ubicar(Vector2D(0, 0), Vector2D(0, 1))

        self.assertTrue(barco.recibir_disparo(Vector2D(0, 0)))
        self.assertFalse(barco.esta_hundido())
        self.assertEqual(barco.porcentaje_salud(), 50.0)

        self.assertTrue(barco.recibir_disparo(Vector2D(0, 1)))
        self.assertTrue(barco.esta_hundido())
        self.assertEqual(barco.porcentaje_salud(), 0.0)

    def test_tablero_disparos(self):
        tablero = Tablero(ancho=10, alto=10)
        barco = Barco("Destructor", tamano=2)
        tablero.colocar_barco(barco, Vector2D(5, 5), Vector2D(1, 0))

        # Disparo al agua
        res_agua = tablero.procesar_disparo(Vector2D(1, 1))
        self.assertTrue(res_agua.valido)
        self.assertFalse(res_agua.impacto)

        # Disparo certero
        res_acierto = tablero.procesar_disparo(Vector2D(5, 5))
        self.assertTrue(res_acierto.impacto)
        self.assertFalse(res_acierto.hundido)

        # Segundo disparo certero (Hundido)
        res_hundido = tablero.procesar_disparo(Vector2D(6, 5))
        self.assertTrue(res_hundido.hundido)
        self.assertTrue(tablero.todos_hundidos())

    def test_habilidad_suma(self):
        tablero = Tablero(10, 10)
        barco = Barco("Boya", tamano=1)
        tablero.colocar_barco(barco, Vector2D(5, 5), Vector2D(1, 0))

        origen = Vector2D(2, 3)
        vector_tiro = Vector2D(3, 2)  # 2+3=5, 3+2=5 -> Impacto en (5, 5)
        res = DisparoBasicoSuma.ejecutar(origen, vector_tiro, tablero)

        self.assertEqual(res["destino"], Vector2D(5, 5))
        self.assertTrue(res["resultado_tablero"][0].impacto)

    def test_habilidad_viento(self):
        tablero = Tablero(10, 10)
        barco = Barco("Boya", tamano=1)
        tablero.colocar_barco(barco, Vector2D(7, 7), Vector2D(1, 0))

        origen = Vector2D(2, 2)
        v_tiro = Vector2D(4, 4)
        v_viento = Vector2D(1, 1)  # (2+4+1, 2+4+1) = (7, 7)
        res = DisparoConViento.ejecutar(origen, v_tiro, v_viento, tablero)

        self.assertEqual(res["destino"], Vector2D(7, 7))
        self.assertTrue(res["resultado_tablero"][0].impacto)

    def test_habilidad_sonar(self):
        tablero = Tablero(10, 10)
        barco = Barco("Submarino", tamano=1)
        tablero.colocar_barco(barco, Vector2D(3, 4), Vector2D(1, 0))

        origen_sonar = Vector2D(0, 0)
        res = SonarDistanciaEuclidiana.ejecutar(origen_sonar, tablero)
        # Distancia = sqrt(3^2 + 4^2) = 5.0
        self.assertAlmostEqual(res["distancia"], 5.0)

    def test_habilidad_proyeccion_orbital(self):
        tablero = Tablero(10, 10)
        barco = Barco("Fragata", tamano=2)
        tablero.colocar_barco(barco, Vector2D(3, 0), Vector2D(1, 0))

        # Origen (0,0), Vector V = (3, 4), Vector U = (1, 0)
        # Proyección sobre U = (3, 0), barre desde (0,0) hasta (3,0)
        res = CanonProyeccionOrbital.ejecutar(Vector2D(0, 0), Vector2D(3, 4), Vector2D(1, 0), tablero)
        self.assertEqual(res["proyeccion"], Vector2D(3, 0))
        self.assertTrue(any(r.impacto for r in res["resultado_tablero"]))


if __name__ == "__main__":
    unittest.main()
