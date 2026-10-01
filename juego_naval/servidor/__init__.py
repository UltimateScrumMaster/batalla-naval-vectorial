"""
Módulo de servidor para Batalla Naval Vectorial.
Proporciona el backend WebSocket para clientes desacoplados (Godot, Web, CLI).
"""

from .ws_server import ServidorJuegoNaval, main_servidor

__all__ = ["ServidorJuegoNaval", "main_servidor"]
