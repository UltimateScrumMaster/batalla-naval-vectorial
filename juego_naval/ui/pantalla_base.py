"""
=============================================================================
MÓDULO: pantalla_base.py - Clase base de una pantalla del juego
=============================================================================
Toda pantalla de la aplicación debe heredar de PantallaBase. Recibe siempre
el gestor para poder navegar y debe implementar `_construir_ui()`.
=============================================================================
"""

from __future__ import annotations

import tkinter as tk


class PantallaBase(tk.Frame):
    """Frame que representa una pantalla; recibe el gestor para navegar."""

    def __init__(self, maestro, gestor, **kwargs):
        super().__init__(maestro)
        self.gestor = gestor
        self.params = dict(kwargs)
        self._construir_ui()

    def _construir_ui(self) -> None:
        """Cada pantalla construye aquí sus widgets. Debe sobreescribirse."""
        raise NotImplementedError

    def ir_a(self, nombre: str, **kwargs) -> None:
        """Atajo para navegar hacia adelante."""
        self.gestor.ir(nombre, **kwargs)

    def volver(self, **kwargs) -> None:
        """Atajo para volver a la pantalla anterior."""
        self.gestor.volver(**kwargs)

    def destroy(self) -> None:
        """Destruye la pantalla. Antes, ejecuta el hook de limpieza `_limpiar()`
        para que cada pantalla libere recursos (ej: figuras de matplotlib)."""
        self._limpiar()
        super().destroy()

    def _limpiar(self) -> None:
        """Hook de limpieza. Sobreescribir en pantallas que posean recursos
        que deban liberarse explícitamente (ej: `plt.close(self.figura)`)."""
        pass
