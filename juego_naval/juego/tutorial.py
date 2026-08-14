"""
=================================================================================
MÓDULO: juego_naval/juego/tutorial.py - Tutorial guiado (misiones pedagógicas)
=================================================================================
Contenido pedagógico puro del Tutorial Guiado, extraído de
`juego.ejecutar_tutorial_guiado`. Solo datos y funciones comprobables; la
presentación (Tkinter) vive en juego_naval/ui/pantallas/tutorial.py.
=================================================================================
"""

from typing import Any, Dict, Tuple

from vector2d import Vector2D

# Misiones del tutorial, con su historia, objetivos y solución pedagógica.
MISIONES: Tuple[Dict[str, Any], ...] = (
    {
        "titulo": "Misión 1: Tu Primer Disparo Vectorial (Suma de Vectores)",
        "historia": "Tu fragata se encuentra en el origen P = (2, 3). El radar detectó una boya enemiga en T = (5, 7).",
        "origen": Vector2D(2, 3),
        "objetivo": Vector2D(5, 7),
        "formula": "V_tiro = Objetivo - Origen = (5 - 2, 7 - 3) = (3, 4)",
        "solucion": Vector2D(3, 4),
        "pista": "Para llegar a (5,7) desde (2,3), calcula cuánto debes moverte en X (5 - 2) y en Y (7 - 3).",
    },
    {
        "titulo": "Misión 2: Artillería y el Viento Marino (Suma Múltiple)",
        "historia": "Tu barco está en P = (1, 1) y deseas impactar en T = (6, 5). El viento sopla con V_viento = (2, -1).",
        "origen": Vector2D(1, 1),
        "objetivo": Vector2D(6, 5),
        "viento": Vector2D(2, -1),
        "formula": "V_tiro = T - P - V_viento = (6, 5) - (1, 1) - (2, -1) = (3, 5)",
        "solucion": Vector2D(3, 5),
        "pista": "El viento sumará (2, -1) al disparo. Debes compensar restando el viento al vector deseado.",
    },
    {
        "titulo": "Misión 3: Torpedo de Propulsión Escalar",
        "historia": "Tu submarino está en P = (0, 0). Apuntas en la dirección unitaria u = (1, 2) y el objetivo está en (3, 6).",
        "origen": Vector2D(0, 0),
        "objetivo": Vector2D(3, 6),
        "formula": "k · (1, 2) = (3, 6)  -->  k = 3",
        "solucion_escalar": 3,
        "pista": "¿Por qué número debes multiplicar (1, 2) para obtener (3, 6)?",
    },
)


def es_mision_vectorial(mision: Dict[str, Any]) -> bool:
    """True si la misión se resuelve con un vector de disparo, False si es escalar."""
    return "solucion" in mision


def evaluar_intento_tutorial(mision: Dict[str, Any], respuesta: Any) -> Tuple[bool, str]:
    """Evalúa la respuesta del alumno contra la solución de la misión.

    Args:
        mision: Una entrada de MISIONES.
        respuesta: Vector2D para misiones vectoriales, int para escalares.

    Returns:
        (acierto, mensaje_de_retroalimentación).
    """
    if es_mision_vectorial(mision):
        solucion = mision["solucion"]
        if respuesta == solucion:
            return True, "Impacto directo confirmado. ¡Bien calculado!"
        return False, (f"Incorrecto. El disparo cayó en {mision['origen'] + respuesta}, "
                       f"no en el objetivo {mision['objetivo']}.")
    # Misión escalar (torpedo)
    try:
        k = int(respuesta)
    except (TypeError, ValueError):
        return False, "Ingresa un número entero válido para k."
    if k == mision["solucion_escalar"]:
        return True, "Multiplicador escalar correcto. ¡Impacto en el objetivo!"
    return False, (f"Incorrecto. Multiplicar por {k} da {Vector2D(1, 2) * k}, "
                   f"no el objetivo {mision['objetivo']}.")
