"""
=============================================================================
PANTALLA: menu_principal.py - Menú principal (migración de main.py)
=============================================================================
Reemplaza el menú de consola (Rich) por una pantalla Tkinter con el mismo
contenido: opciones de juego que navegan a las pantallas correspondientes.
=============================================================================
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from juego_naval.ui.pantalla_base import PantallaBase

# (clave de pantalla, etiqueta del botón). Se irán agregando los modos
# migrados (batalla, tutorial, sandbox) a medida que se migren.
_OPCIONES = (
    ("batalla", "Batalla Naval vs IA"),
    ("laboratorio", "Laboratorio de Vectores (Sandbox)"),
)


class PantallaMenuPrincipal(PantallaBase):
    def _construir_ui(self) -> None:
        ttk.Label(self, text="BATALLA NAVAL VECTORIAL",
                  font=("Segoe UI", 22, "bold")).pack(pady=(70, 4))
        ttk.Label(self, text="Aprende Vectores, Pitágoras y Proyecciones Jugando",
                  font=("Segoe UI", 12)).pack(pady=(0, 34))

        for clave, etiqueta in _OPCIONES:
            ttk.Button(self, text=etiqueta, width=36,
                       command=lambda c=clave: self.ir_a(c)).pack(pady=6)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=120, pady=16)
        ttk.Button(self, text="Salir", width=36,
                   command=self.gestor.raiz.destroy).pack(pady=6)
