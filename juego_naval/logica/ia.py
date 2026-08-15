"""
=============================================================================
MÓDULO: ia.py - Inteligencia Artificial Enemiga y Cálculos Vectoriales
=============================================================================
El oponente virtual también utiliza álgebra vectorial para planificar sus
ataques. Implementa una estrategia didáctica:
1. Modo Exploración (Patrullaje): Busca coordenadas usando sumas vectoriales.
2. Modo Cacería (Ataque Dirigido): Cuando impacta un barco, suma vectores
   unitarios (+X, -X, +Y, -Y) para rastrear el resto del navío.
3. Uso de Habilidades: Usa sónar y torpedos escalares según su nivel de energía.
=============================================================================
"""

from __future__ import annotations
import random
from typing import List, Tuple, Optional, Dict, Any
from juego_naval.dominio.vector2d import Vector2D
from juego_naval.dominio.tablero import Tablero
from juego_naval.logica.habilidades import DisparoBasicoSuma, TorpedoEscalar, SonarDistanciaEuclidiana


class IAEnemiga:
    """Controlador de la flota enemiga con lógica vectorial de toma de decisiones"""

    def __init__(self, nombre: str = "Almirante Vector", nivel: str = "normal"):
        self.nombre = nombre
        self.nivel = nivel
        self.cola_caceria: List[Vector2D] = []
        self.impactos_conocidos: List[Vector2D] = []
        self.energia: int = 2

    def decidir_turno(self, mi_tablero: Tablero, tablero_jugador: Tablero, viento: Vector2D) -> Dict[str, Any]:
        """
        Decide y ejecuta el movimiento de la IA, retornando la información matemática del turno.
        """
        # Incrementar energía por turno (máximo 6)
        self.energia = min(6, self.energia + 1)

        # Barcos vivos propios para elegir origen de tiro
        barcos_propios = [b for b in mi_tablero.barcos if not b.esta_hundido()]
        barco_emisor = random.choice(barcos_propios) if barcos_propios else mi_tablero.barcos[0]
        origen = barco_emisor.origen

        # Decidir habilidad: Torpedo Escalar si hay energía suficiente y estamos cazando
        if self.energia >= 3 and self.cola_caceria and random.random() < 0.35:
            self.energia -= 2
            objetivo = self.cola_caceria.pop(0)
            diff = objetivo - origen
            # Descomponer en dirección y escalar si es posible
            dir_base = Vector2D(1 if diff.x > 0 else (-1 if diff.x < 0 else 0),
                                1 if diff.y > 0 else (-1 if diff.y < 0 else 0))
            escalar = max(abs(diff.x), abs(diff.y), 1)
            resultado = TorpedoEscalar.ejecutar(origen, dir_base, escalar, tablero_jugador)
            self._procesar_resultado_ia(resultado["resultado_tablero"][0], tablero_jugador)
            return resultado

        # Si tenemos cola de cacería (impactos previos)
        while self.cola_caceria:
            posible_obj = self.cola_caceria.pop(0)
            tupla = posible_obj.a_tupla_grilla()
            if (tablero_jugador.es_posicion_valida(posible_obj) and
                    tupla not in tablero_jugador.disparos_agua and
                    tupla not in tablero_jugador.disparos_acierto):
                # Vector de tiro necesario: V_tiro = Objetivo - Origen
                vector_tiro = posible_obj - origen
                resultado = DisparoBasicoSuma.ejecutar(origen, vector_tiro, tablero_jugador)
                self._procesar_resultado_ia(resultado["resultado_tablero"][0], tablero_jugador)
                return resultado

        # Modo Exploración: Elegir coordenada válida no explorada
        candidatos = []
        for x in range(tablero_jugador.ancho):
            for y in range(tablero_jugador.alto):
                tupla = (x, y)
                if tupla not in tablero_jugador.disparos_agua and tupla not in tablero_jugador.disparos_acierto:
                    candidatos.append(Vector2D(x, y))

        if candidatos:
            # Estrategia de tablero de ajedrez (pares/impares) para mayor eficiencia
            candidatos_par = [c for c in candidatos if (c.x + c.y) % 2 == 0]
            elegido = random.choice(candidatos_par) if candidatos_par else random.choice(candidatos)
        else:
            elegido = Vector2D(random.randint(0, tablero_jugador.ancho - 1),
                               random.randint(0, tablero_jugador.alto - 1))

        vector_tiro = elegido - origen
        resultado = DisparoBasicoSuma.ejecutar(origen, vector_tiro, tablero_jugador)
        self._procesar_resultado_ia(resultado["resultado_tablero"][0], tablero_jugador)
        return resultado

    def _procesar_resultado_ia(self, res_disparo, tablero_jugador: Tablero) -> None:
        """Si la IA acertó, agrega vectores adyacentes a la cola de cacería"""
        if res_disparo.impacto and not res_disparo.hundido:
            self.impactos_conocidos.append(res_disparo.coordenada)
            # Agregar los 4 vectores ortogonales adyacentes (+X, -X, +Y, -Y)
            direcciones = [Vector2D(1, 0), Vector2D(-1, 0), Vector2D(0, 1), Vector2D(0, -1)]
            for d in direcciones:
                nueva_pos = res_disparo.coordenada + d
                if tablero_jugador.es_posicion_valida(nueva_pos):
                    self.cola_caceria.append(nueva_pos)
        elif res_disparo.hundido:
            # Si se hundió el barco, limpiamos cacerías redundantes
            self.impactos_conocidos.clear()
