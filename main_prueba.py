"""
=============================================================================
MODO PRUEBA: main_prueba.py - Validación del Gestor de Pantallas
=============================================================================
Mini aplicación con dos pantallas "dummy" para confirmar la navegación
(ir / volver / reemplazar) antes de migrar los módulos reales.

Ejecución:
    python3 main_prueba.py
=============================================================================
"""

import tkinter as tk
from tkinter import ttk

from juego_naval.ui.gestor_pantallas import GestorPantallas
from juego_naval.ui.pantalla_base import PantallaBase


class PantallaA(PantallaBase):
    def _construir_ui(self):
        ttk.Label(self, text="PANTALLA A", font=("Segoe UI", 18, "bold")).pack(pady=30)
        ttk.Label(self, text="Pantalla inicial del menú", font=("Segoe UI", 11)).pack()
        ttk.Button(self, text="Ir a Pantalla B",
                   command=lambda: self.ir_a("b")).pack(pady=8)
        ttk.Button(self, text="Reemplazar por B (sin historial)",
                   command=lambda: self.gestor.reemplazar("b")).pack(pady=4)
        ttk.Button(self, text="Salir", command=self.gestor.raiz.destroy).pack(pady=8)


class PantallaB(PantallaBase):
    def _construir_ui(self):
        # El contador vive en el estado compartido del gestor, no en params.
        visitas = self.gestor.compartido.get("visitas_b", 0) + 1
        self.gestor.compartido["visitas_b"] = visitas

        ttk.Label(self, text="PANTALLA B", font=("Segoe UI", 18, "bold")).pack(pady=30)
        self._var_visitas = tk.StringVar(
            value=f"Visitas a esta pantalla: {visitas}")
        ttk.Label(self, textvariable=self._var_visitas, font=("Segoe UI", 11)).pack()
        ttk.Button(self, text="Ir a Pantalla A",
                   command=lambda: self.ir_a("a")).pack(pady=8)
        ttk.Button(self, text="Volver (pantalla anterior)",
                   command=self.volver).pack(pady=4)
        ttk.Button(self, text="Salir", command=self.gestor.raiz.destroy).pack(pady=8)


def main():
    raiz = tk.Tk()
    raiz.title("Prueba del Gestor de Pantallas")
    raiz.geometry("420x360")

    gestor = GestorPantallas(raiz)
    gestor.registrar("a", PantallaA)
    gestor.registrar("b", PantallaB)
    gestor.reemplazar("a")

    raiz.mainloop()


if __name__ == "__main__":
    main()
