"""
=================================================================================
PANTALLA: pantalla_tutorial.py - Tutorial Guiado por Misiones (migrado)
=================================================================================
Migración de `juego.ejecutar_tutorial_guiado` (TUI Rich) al patrón de pantallas.
Reutiliza el contenido pedagógico puro de juego_naval/juego/tutorial.py
(MISIONES y evaluar_intento_tutorial) y las explicaciones paso a paso de
`Vector2D.explicar_suma`. Esta pantalla solo muestra la misión, captura la
respuesta y da retroalimentación.
=================================================================================
"""

import math
import tkinter as tk
from tkinter import ttk, Text, END
from typing import Any, Dict, List, Optional, Tuple

from juego_naval.ui.pantalla_base import PantallaBase
from juego_naval.juego.tutorial import (
    MISIONES,
    es_mision_vectorial,
    evaluar_intento_tutorial,
)
from vector2d import Vector2D

COLOR_ORIGEN = "#27ae60"
COLOR_OBJETIVO = "#c0392b"
COLOR_TRAYECTORIA = "#f1c40f"
COLOR_SOLUCION = "#1f6f2f"
COLOR_ERROR = "#c0392b"
COLOR_TEXTO = "#1f2a36"


class PantallaTutorial(PantallaBase):
    """Tutorial guiado: misiones de álgebra vectorial con verificación."""

    ANCHO, ALTO = 10, 10
    CELDA = 40
    MARGEN = 30

    def __init__(self, maestro, gestor, **kwargs):
        self._indice_mision = 0
        self._intentos = 0
        self._mision: Optional[Dict[str, Any]] = None
        self._completada = False
        super().__init__(maestro, gestor, **kwargs)

    # ------------------------------------------------------------ UI ---------
    def _construir_ui(self) -> None:
        barra = ttk.Frame(self)
        barra.pack(fill="x", padx=8, pady=6)
        self.var_titulo = tk.StringVar(value="")
        ttk.Label(barra, textvariable=self.var_titulo,
                  font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Button(barra, text="Volver al menú", command=self.volver).pack(side="right")

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True, padx=8)

        col_info = ttk.Frame(cuerpo, width=430)
        col_info.pack(side="left", fill="y", padx=(0, 8))
        col_info.pack_propagate(False)

        ttk.Label(col_info, text="MISIÓN", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.var_mision = tk.StringVar(value="")
        ttk.Label(col_info, textvariable=self.var_mision, wraplength=410,
                  font=("Segoe UI", 12, "bold"), justify="left").pack(anchor="w", pady=(0, 8))

        self.var_historia = tk.StringVar(value="")
        ttk.Label(col_info, textvariable=self.var_historia, wraplength=410,
                  justify="left").pack(anchor="w", pady=(0, 8))

        self.var_datos = tk.StringVar(value="")
        ttk.Label(col_info, textvariable=self.var_datos, wraplength=410,
                  justify="left", foreground="#2c3e50").pack(anchor="w", pady=(0, 8))

        self.var_pista = tk.StringVar(value="")
        ttk.Label(col_info, textvariable=self.var_pista, wraplength=410,
                  justify="left", foreground="#7f8c8d", font=("Segoe UI", 9, "italic")).pack(anchor="w")

        ttk.Label(col_info, text="\nDESGLOSE MATEMÁTICO", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 2))
        self.desglose = Text(col_info, height=8, wrap="word",
                             font=("Consolas", 9), state="disabled", bg="#f7f9fb")
        self.desglose.pack(fill="both", expand=True)

        col_grafico = ttk.Frame(cuerpo)
        col_grafico.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(
            col_grafico, width=self.ANCHO * self.CELDA + 2 * self.MARGEN,
            height=self.ALTO * self.CELDA + 2 * self.MARGEN, bg="white")
        self.canvas.pack()
        ttk.Label(col_grafico, text="Plano de la misión: ◆ origen · + trayectoria · ◎ objetivo",
                  font=("Segoe UI", 9)).pack(pady=(4, 0))

        # --- Área de respuesta ---
        respuesta = ttk.LabelFrame(self, text="Tu respuesta")
        respuesta.pack(fill="x", padx=8, pady=8)

        self.var_respuesta_x = tk.IntVar(value=0)
        self.var_respuesta_y = tk.IntVar(value=0)
        self.var_respuesta_k = tk.IntVar(value=1)
        self.etiqueta_respuesta = ttk.Label(respuesta, text="Vector de disparo (X, Y):",
                                            font=("Segoe UI", 10, "bold"))
        self.etiqueta_respuesta.pack(side="left", padx=6)
        ttk.Label(respuesta, text="X:").pack(side="left")
        self.entry_x = ttk.Entry(respuesta, textvariable=self.var_respuesta_x, width=5)
        self.entry_x.pack(side="left", padx=3)
        ttk.Label(respuesta, text="Y:").pack(side="left")
        self.entry_y = ttk.Entry(respuesta, textvariable=self.var_respuesta_y, width=5)
        self.entry_y.pack(side="left", padx=3)
        ttk.Label(respuesta, text="k:").pack(side="left")
        self.entry_k = ttk.Entry(respuesta, textvariable=self.var_respuesta_k, width=5)
        self.entry_k.pack(side="left", padx=3)

        self.boton_comprobar = ttk.Button(respuesta, text="Comprobar", command=self._comprobar)
        self.boton_comprobar.pack(side="left", padx=10)
        self.boton_siguiente = ttk.Button(respuesta, text="Siguiente misión",
                                          command=self._siguiente_mision, state="disabled")
        self.boton_siguiente.pack(side="left", padx=4)

        self.var_retro = tk.StringVar(value="")
        self.etiqueta_retro = ttk.Label(self, textvariable=self.var_retro,
                                        foreground=COLOR_ERROR,
                                        font=("Segoe UI", 10, "bold"),
                                        wraplength=1180, justify="center")
        self.etiqueta_retro.pack(fill="x", pady=2)

        self._cargar_mision()

    # ------------------------------------------------------- misiones ---------
    def _cargar_mision(self) -> None:
        self._mision = MISIONES[self._indice_mision]
        self._intentos = 0
        self._completada = False
        m = self._mision

        self.var_titulo.set(f"TUTORIAL GUIADO — MISIÓN {self._indice_mision + 1} de {len(MISIONES)}")
        self.var_mision.set(m["titulo"])
        self.var_historia.set(m["historia"])
        datos = (f"Punto de Origen P: {m['origen']}\n"
                 f"Objetivo Deseado T: {m['objetivo']}")
        if "viento" in m:
            datos += f"\nViento V_viento: {m['viento']}"
        self.var_datos.set(datos)
        self.var_pista.set(f"Pista pedagógica:\n{m['pista']}")

        vectorial = es_mision_vectorial(m)
        self.etiqueta_respuesta.config(
            text="Vector de disparo (X, Y):" if vectorial else "Multiplicador escalar k:")
        self.entry_x.state(["!disabled"] if vectorial else ["disabled"])
        self.entry_y.state(["!disabled"] if vectorial else ["disabled"])
        self.entry_k.state(["disabled"] if vectorial else ["!disabled"])

        self.var_respuesta_x.set(0)
        self.var_respuesta_y.set(0)
        self.var_respuesta_k.set(1)
        self.var_retro.set("")
        self._limpiar_desglose()
        self.boton_comprobar.config(state="normal")
        self.boton_siguiente.config(state="disabled")

        self._dibujar_mision()

    def _siguiente_mision(self) -> None:
        self._indice_mision += 1
        if self._indice_mision >= len(MISIONES):
            self._mostrar_fin()
            return
        self._cargar_mision()

    def _mostrar_fin(self) -> None:
        self._completada = True
        self.var_titulo.set("TUTORIAL GUIADO — COMPLETADO")
        self.var_mision.set("¡FELICITACIONES!")
        self.var_historia.set("Has completado el entrenamiento básico de álgebra vectorial naval. "
                              "Ya puedes enfrentar a la IA en la Batalla Naval.")
        self.var_datos.set("")
        self.var_pista.set("Los vectores: suma (P + V), viento (P + V + V_viento) y "
                           "escalado (P + k·U) ya son parte de tu arsenal.")
        self.var_retro.set("")
        self._limpiar_desglose()
        self._escribir_desglose(["Módulo: ||V|| = sqrt(x² + y²)",
                                 "Producto punto: U · V = Ux·Vx + Uy·Vy",
                                 "Proyección: proj_u(v) = (u·v / u·u) · u"])
        self.boton_comprobar.config(state="disabled")
        self.boton_siguiente.config(state="disabled", text="Volver al menú",
                                    command=self.volver)
        self.canvas.delete("all")

    # ------------------------------------------------------ respuesta ---------
    def _comprobar(self) -> None:
        if self._mision is None or self._completada:
            return
        m = self._mision
        self._intentos += 1

        if es_mision_vectorial(m):
            respuesta = Vector2D(self.var_respuesta_x.get(), self.var_respuesta_y.get())
        else:
            respuesta = self.var_respuesta_k.get()

        acierto, mensaje = evaluar_intento_tutorial(m, respuesta)
        self.var_retro.set(mensaje)
        self.etiqueta_retro.config(foreground=COLOR_SOLUCION if acierto else COLOR_ERROR)

        if acierto:
            self.var_retro.set(f"{mensaje} Intentos: {self._intentos}.")
            self._mostrar_desglose(respuesta)
            self.boton_siguiente.config(state="normal")
            self.boton_comprobar.config(state="disabled")
        elif self._intentos >= 3:
            self.var_retro.set(f"{mensaje}\nSolución: {m['formula']}")
            self._escribir_desglose([m["formula"]])
            self.boton_siguiente.config(state="normal")
            self.boton_comprobar.config(state="disabled")

    def _mostrar_desglose(self, respuesta: Any) -> None:
        m = self._mision
        if es_mision_vectorial(m):
            explicacion = m["origen"].explicar_suma(respuesta, "Pos_Barco", "Tiro_Alumno")
            lineas = [f"Fórmula: {explicacion.get('formula', '')}"]
            lineas += explicacion.get("pasos", [])
            self._escribir_desglose(lineas)
        else:
            self._escribir_desglose([m["formula"]])

    def _escribir_desglose(self, lineas: List[str]) -> None:
        self._limpiar_desglose()
        self.desglose.config(state="normal")
        for linea in lineas:
            self.desglose.insert(END, linea + "\n")
        self.desglose.config(state="disabled")

    def _limpiar_desglose(self) -> None:
        self.desglose.config(state="normal")
        self.desglose.delete("1.0", END)
        self.desglose.config(state="disabled")

    # --------------------------------------------------- plano de misión ------
    def _a_pantalla(self, x: int, y: int) -> Tuple[int, int]:
        px = self.MARGEN + x * self.CELDA
        py = self.MARGEN + (self.ALTO - 1 - y) * self.CELDA
        return px, py

    def _dibujar_mision(self) -> None:
        self.canvas.delete("all")
        m = self._mision
        if m is None:
            return

        for x in range(self.ANCHO):
            self.canvas.create_text(self.MARGEN + x * self.CELDA + self.CELDA // 2, 10,
                                    text=str(x), fill=COLOR_TEXTO, font=("Consolas", 8))
        for y in range(self.ALTO):
            self.canvas.create_text(10, self.MARGEN + (self.ALTO - 1 - y) * self.CELDA + self.CELDA // 2,
                                    text=str(y), fill=COLOR_TEXTO, font=("Consolas", 8))

        for x in range(self.ANCHO):
            for y in range(self.ALTO):
                px, py = self._a_pantalla(x, y)
                self.canvas.create_rectangle(px, py, px + self.CELDA, py + self.CELDA,
                                             fill="#fdfefe", outline="#cfd8dc", width=1)

        origen = m["origen"]
        objetivo = m["objetivo"]

        # Trayectoria interpolada (origen → objetivo)
        dx = objetivo.x - origen.x
        dy = objetivo.y - origen.y
        pasos = max(int(math.hypot(dx, dy) * 2), 2)
        for step in range(1, pasos):
            t = step / pasos
            px = int(round(origen.x + t * dx))
            py = int(round(origen.y + t * dy))
            tupla = (px, py)
            if tupla != origen.a_tupla_grilla() and tupla != objetivo.a_tupla_grilla():
                if 0 <= px < self.ANCHO and 0 <= py < self.ALTO:
                    sx, sy = self._a_pantalla(px, py)
                    self.canvas.create_text(sx + self.CELDA // 2, sy + self.CELDA // 2,
                                            text="+", fill=COLOR_TRAYECTORIA,
                                            font=("Consolas", 12, "bold"))

        # Origen (◆) y objetivo (◎)
        ox, oy = self._a_pantalla(origen.x, origen.y)
        self.canvas.create_text(ox + self.CELDA // 2, oy + self.CELDA // 2,
                                text="◆", fill=COLOR_ORIGEN, font=("Consolas", 14, "bold"))
        tx, ty = self._a_pantalla(objetivo.x, objetivo.y)
        self.canvas.create_text(tx + self.CELDA // 2, ty + self.CELDA // 2,
                                text="◎", fill=COLOR_OBJETIVO, font=("Consolas", 14, "bold"))
