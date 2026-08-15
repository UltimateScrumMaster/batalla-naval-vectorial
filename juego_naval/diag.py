"""
=================================================================================
MÓDULO: juego_naval/diag.py - Diagnóstico en consola (modo bash)
=================================================================================
Pequeño helper para imprimir en la terminal lo que va pasando en la aplicación
(navegación entre pantallas, turnos de partida, disparos, disponibilidad de
matplotlib...). Sirve para seguir el flujo del juego "en vivo" mientras se
ejecuta desde la terminal o se depura.

Uso:
    from juego_naval.diag import diag
    diag("turno 3 del jugador")

Para silenciar los mensajes: BNV_DIAG=0 (p. ej. en las pruebas unitarias).
=================================================================================
"""

import os


def diag(mensaje: str) -> None:
    """Imprime un mensaje de diagnóstico en la consola (si está activo)."""
    if os.environ.get("BNV_DIAG", "1") != "1":
        return
    print(f"[diag] {mensaje}", flush=True)
