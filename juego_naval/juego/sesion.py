"""
=================================================================================
MÓDULO: juego_naval/juego/sesion.py - Sesión de partida (máquina de estados)
=================================================================================
Fuente ÚNICA de la lógica de una partida de Batalla Naval Vectorial, extraída
de los duplicados que existían en juego.py (TUI), juego_grafico.py (GUI) y
sus clases de ventana.

Contiene:
    * EstadoBatalla: enum con los estados por los que pasa la partida.
    * SKILLS / COSTOS_HABILIDAD / NOMBRES_HABILIDAD: registro único de las
      habilidades, derivado de las clases de habilidades.py.
    * ejecutar_habilidad(): función pura que despacha la habilidad contra el
      tablero enemigo (sin tocar estado).
    * SesionBatalla: controlador de una partida completa. Las reglas de
      turno, energía, viento y victoria/derrota viven SOLO aquí; la capa de
      presentación (Tkinter o terminal) solo la consulta y la ejecuta.

El estado de la partida NO pertenece a la ventana: se guarda en
`gestor.compartido["sesion"]` para sobrevivir a los cambios de pantalla.
=================================================================================
"""

import random
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple

from vector2d import Vector2D
from tablero import Tablero
from habilidades import (
    DisparoBasicoSuma,
    DisparoConViento,
    TorpedoEscalar,
    SonarDistanciaEuclidiana,
    CanonProyeccionOrbital,
)
from ia import IAEnemiga


class EstadoBatalla(Enum):
    """Estados por los que pasa la partida."""
    TURNO_JUGADOR = auto()
    TURNO_IA = auto()
    VICTORIA = auto()
    DERROTA = auto()


# --------------------------------------------------------------------------
# Registro único de habilidades: se deriva de las clases para no repetir
# costos ni nombres en ningún otro módulo.
# --------------------------------------------------------------------------
SKILLS: Dict[str, type] = {
    "suma": DisparoBasicoSuma,
    "viento": DisparoConViento,
    "torpedo": TorpedoEscalar,
    "sonar": SonarDistanciaEuclidiana,
    "orbital": CanonProyeccionOrbital,
}

COSTOS_HABILIDAD: Dict[str, int] = {clave: cls.energia_costo for clave, cls in SKILLS.items()}
NOMBRES_HABILIDAD: Dict[str, str] = {clave: cls.nombre for clave, cls in SKILLS.items()}


def ejecutar_habilidad(skill: str, origen: Vector2D, vector_a: Vector2D,
                       vector_b: Vector2D, escalar_k: int,
                       viento: Vector2D, tablero_enemigo: Tablero) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Ejecuta la habilidad seleccionada contra el tablero enemigo.

    Args:
        skill: Clave de COSTOS_HABILIDAD ("suma", "viento", ...).
        origen: Posición del barco desde el que se ataca.
        vector_a: Primer vector (tiro/dirección base/ataque según la habilidad).
        vector_b: Segundo vector (solo "orbital": eje del radar).
        escalar_k: Escalar de potencia (solo "torpedo").
        viento: Vector de viento actual de la partida (solo "viento").
        tablero_enemigo: Tablero objetivo (el radar enemigo).

    Returns:
        (resultado_de_habilidad, None) si la ejecución fue válida, o
        (None, mensaje_de_error) si los parámetros son inválidos.
    """
    skill = skill.lower().strip()

    if skill == "suma":
        return DisparoBasicoSuma.ejecutar(origen, vector_a, tablero_enemigo), None

    if skill == "viento":
        return DisparoConViento.ejecutar(origen, vector_a, viento, tablero_enemigo), None

    if skill == "torpedo":
        if vector_a.es_cero():
            return None, "La dirección base U no puede ser el vector nulo (0, 0)."
        return TorpedoEscalar.ejecutar(origen, vector_a, escalar_k, tablero_enemigo), None

    if skill == "sonar":
        return SonarDistanciaEuclidiana.ejecutar(origen, tablero_enemigo), None

    if skill == "orbital":
        if vector_b.es_cero():
            return None, "El vector base del radar U no puede ser el vector nulo (0, 0)."
        return CanonProyeccionOrbital.ejecutar(origen, vector_a, vector_b, tablero_enemigo), None

    return None, f"Habilidad desconocida: {skill}"


class SesionBatalla:
    """Controlador de una partida completa de Batalla Naval Vectorial.

    Encapsula las reglas del juego (turnos, energía, viento, victoria y
    derrota) que antes estaban duplicadas entre la TUI (juego.PartidaBatallaNaval)
    y la GUI (juego_grafico.AplicacionBatallaGrafica). La presentación solo
    invoca estos métodos y consulta `estado`.
    """

    def __init__(self, semilla: Optional[int] = None):
        if semilla is not None:
            random.seed(semilla)

        self.tablero_jugador = Tablero(ancho=10, alto=10, es_oculto=False, titulo="TU FLOTA (Plano Aliado)")
        self.tablero_enemigo = Tablero(ancho=10, alto=10, es_oculto=True, titulo="RADAR ENEMIGO (Niebla de Guerra)")
        self.ia = IAEnemiga("Almirante Vector", nivel="normal")

        self.tablero_jugador.colocar_flota_aleatoria()
        self.tablero_enemigo.colocar_flota_aleatoria()

        self.turno: int = 1
        self.energia_jugador: int = 2
        self.viento: Vector2D = Vector2D(0, 0)
        self.estado: EstadoBatalla = EstadoBatalla.TURNO_JUGADOR
        self.actualizar_viento()

    # ------------------------------------------------------------ viento ----
    def actualizar_viento(self) -> None:
        """Modifica el vector de corriente marina/viento periódicamente."""
        vx = random.choice([-2, -1, 0, 1, 2])
        vy = random.choice([-2, -1, 0, 1, 2])
        self.viento = Vector2D(vx, vy)

    # ------------------------------------------------------- turno jugador ---
    def comenzar_turno_jugador(self) -> None:
        """Aplica las reglas de inicio de turno del jugador.

        Limpia marcas temporales, suma +1 de energía (tope 6) y renueva el
        viento cada 3 turnos. La presentación se encarga del resto de la UI.
        """
        self.tablero_jugador.marcas_temporales.clear()
        self.tablero_enemigo.marcas_temporales.clear()
        self.energia_jugador = min(6, self.energia_jugador + 1)
        if self.turno % 3 == 0:
            self.actualizar_viento()
        self.estado = EstadoBatalla.TURNO_JUGADOR

    def ejecutar_ataque_jugador(self, skill: str, origen: Vector2D, vector_a: Vector2D,
                                vector_b: Vector2D, escalar_k: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Ejecuta la habilidad, descuenta la energía y verifica la victoria.

        Returns:
            (resultado_de_habilidad, None) si el disparo fue válido, o
            (None, mensaje_de_error) si los parámetros o la energía no alcanzan.
        """
        skill = skill.lower().strip()
        costo = COSTOS_HABILIDAD.get(skill)
        if costo is None:
            return None, f"Habilidad desconocida: {skill}"
        if self.energia_jugador < costo:
            return None, (f"Energía insuficiente: tienes {self.energia_jugador} y "
                          f"{NOMBRES_HABILIDAD[skill]} cuesta {costo}.")

        resultado, error = ejecutar_habilidad(
            skill, origen, vector_a, vector_b, escalar_k,
            self.viento, self.tablero_enemigo)
        if error:
            return None, error

        self.energia_jugador -= costo
        if self.tablero_enemigo.todos_hundidos():
            self.estado = EstadoBatalla.VICTORIA
        return resultado, None

    # ------------------------------------------------------------ turno IA ---
    def ejecutar_turno_ia(self) -> Dict[str, Any]:
        """Ejecuta el turno de la IA y actualiza el estado de la partida.

        Si la flota del jugador queda destruida pasa a DERROTA; en caso
        contrario incrementa el turno y vuelve a TURNO_JUGADOR.

        Returns:
            Dict con el resultado de decidir_turno de la IA.
        """
        self.estado = EstadoBatalla.TURNO_IA
        res = self.ia.decidir_turno(self.tablero_enemigo, self.tablero_jugador, self.viento)

        if self.tablero_jugador.todos_hundidos():
            self.estado = EstadoBatalla.DERROTA
            return res

        self.turno += 1
        self.estado = EstadoBatalla.TURNO_JUGADOR
        return res
