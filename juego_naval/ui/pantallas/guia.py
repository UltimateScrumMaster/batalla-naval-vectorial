"""
=================================================================================
PANTALLA: pantalla_guia.py - Manual de Fórmulas y Habilidades (migrado)
=================================================================================
Migración de `interfaz.mostrar_guia_habilidades` (Rich) al patrón de pantallas.
Muestra el diccionario de vectores y el catálogo de habilidades con sus
fundamentos matemáticos, usando tablas ttk. Los datos puros viven en
juego_naval/juego/guia.py.
=================================================================================
"""

import tkinter as tk
from tkinter import ttk

from juego_naval.ui.pantalla_base import PantallaBase
from juego_naval.juego.guia import (
    DICCIONARIO_VECTORES,
    CATALOGO_HABILIDADES,
    REGLA_DE_ORO,
    CONSEJO_VISUAL,
)


class PantallaGuia(PantallaBase):
    """Manual de fórmulas y habilidades vectoriales."""

    def _construir_ui(self) -> None:
        barra = ttk.Frame(self)
        barra.pack(fill="x", padx=8, pady=6)
        ttk.Label(barra, text="MANUAL DE FÓRMULAS Y HABILIDADES",
                  font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Button(barra, text="Volver al menú", command=self.volver).pack(side="right")

        lienzo = tk.Canvas(self, highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient="vertical", command=lienzo.yview)
        contenido = ttk.Frame(lienzo)
        contenido.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
        lienzo.create_window((0, 0), window=contenido, anchor="nw")
        lienzo.configure(yscrollcommand=scroll.set)
        lienzo.pack(side="left", fill="both", expand=True, padx=(8, 0))
        scroll.pack(side="right", fill="y", pady=6)

        self._seccion_diccionario(contenido)
        ttk.Label(contenido, text=REGLA_DE_ORO, wraplength=1150, justify="center",
                  foreground="#7f8c8d", font=("Segoe UI", 9, "italic")).pack(pady=8)
        self._seccion_catalogo(contenido)
        ttk.Label(contenido, text=CONSEJO_VISUAL, wraplength=1150, justify="center",
                  foreground="#2c3e50", font=("Segoe UI", 10)).pack(pady=12)

    def _seccion_diccionario(self, padre) -> None:
        ttk.Label(padre, text="DICCIONARIO DE VECTORES: ¿QUÉ SIGNIFICA CADA UNO?",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(4, 2))
        tabla = ttk.Treeview(padre, columns=("tipo", "significado", "ejemplo"),
                             show="headings", height=12)
        tabla.heading("tipo", text="Tipo de Vector")
        tabla.heading("significado", text="¿Qué significa?")
        tabla.heading("ejemplo", text="Ejemplo")
        tabla.column("tipo", width=230, anchor="w")
        tabla.column("significado", width=520, anchor="w")
        tabla.column("ejemplo", width=280, anchor="w")
        for fila in DICCIONARIO_VECTORES:
            tabla.insert("", "end", values=fila)
        tabla.pack(fill="x", padx=4)

    def _seccion_catalogo(self, padre) -> None:
        ttk.Label(padre, text="CATÁLOGO DE HABILIDADES Y FUNDAMENTOS VECTORIALES",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(12, 2))
        tabla = ttk.Treeview(padre, columns=("habilidad", "costo", "formula", "concepto"),
                             show="headings", height=6)
        tabla.heading("habilidad", text="Habilidad")
        tabla.heading("costo", text="Costo")
        tabla.heading("formula", text="Fórmula Matemática")
        tabla.heading("concepto", text="Concepto Pedagógico")
        tabla.column("habilidad", width=250, anchor="w")
        tabla.column("costo", width=70, anchor="center")
        tabla.column("formula", width=290, anchor="w")
        tabla.column("concepto", width=430, anchor="w")
        for fila in CATALOGO_HABILIDADES:
            tabla.insert("", "end", values=fila)
        tabla.pack(fill="x", padx=4)
