"""
=============================================================================
MÓDULO: gestor_pantallas.py - Gestor de Pantallas (Screen Manager) Tkinter
=============================================================================
Una sola ventana raíz. Cada pantalla es un Frame (subclase de PantallaBase)
que se muestra y se destruye bajo demanda, sin abrir ventanas nuevas.

Navegación:
    gestor.ir(nombre, **kwargs)        -> registra la actual y va a otra
    gestor.reemplazar(nombre, **kw)    -> va a otra sin guardar la actual
    gestor.volver(**kwargs)            -> regresa a la pantalla anterior
=============================================================================
"""

from __future__ import annotations

import tkinter as tk

from juego_naval.diag import diag


class GestorPantallas:
    """Controla qué pantalla es visible sobre la ventana raíz."""

    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self._contenedor = tk.Frame(raiz)
        self._contenedor.pack(fill="both", expand=True)
        self._registro: dict = {}
        self._actual: tk.Frame | None = None
        self._actual_nombre: str | None = None
        self._pila: list = []
        # Estado compartido de la app: sobrevive a los cambios de pantalla.
        self.compartido: dict = {}

    def registrar(self, nombre: str, clase) -> None:
        """Asocia un nombre de pantalla con su clase (subclase de Frame)."""
        self._registro[nombre] = clase

    def ir(self, nombre: str, **kwargs) -> None:
        """Navega a otra pantalla guardando la actual en el historial."""
        if nombre not in self._registro:
            raise KeyError(f"Pantalla no registrada: {nombre}")
        diag(f"ir -> {nombre}")
        if self._actual is not None:
            self._pila.append(self._actual_nombre)
            self._actual.destroy()
        self._actual = self._crear(nombre, kwargs)
        self._actual_nombre = nombre

    def reemplazar(self, nombre: str, **kwargs) -> None:
        """Navega a otra pantalla sin guardar la actual (ej: fin de partida)."""
        if nombre not in self._registro:
            raise KeyError(f"Pantalla no registrada: {nombre}")
        diag(f"reemplazar -> {nombre}")
        if self._actual is not None:
            self._actual.destroy()
        self._pila.clear()
        self._actual = self._crear(nombre, kwargs)
        self._actual_nombre = nombre

    def volver(self, **kwargs) -> None:
        """Regresa a la pantalla anterior del historial, si existe."""
        if not self._pila:
            return
        anterior = self._pila.pop()
        diag(f"volver -> {anterior}")
        if self._actual is not None:
            self._actual.destroy()
        self._actual = self._crear(anterior, kwargs)
        self._actual_nombre = anterior

    def pantalla_actual(self):
        """Devuelve la pantalla visible o None."""
        return self._actual

    def nombre_actual(self) -> str | None:
        """Devuelve el nombre de la pantalla visible o None."""
        return self._actual_nombre

    def _crear(self, nombre: str, kwargs: dict) -> tk.Frame:
        clase = self._registro[nombre]
        pantalla = clase(self._contenedor, gestor=self, **kwargs)
        pantalla.pack(fill="both", expand=True)
        return pantalla
