"""
=================================================================================
PANTALLA: pantalla_laboratorio.py - Laboratorio de Vectores (migrado)
=================================================================================
Migración de `AplicacionVectorGrafica` (antes en interfaz_grafica.py) al patrón
de pantallas del gestor. Se reutilizan TAL CUAL las funciones puras de
juego_naval/juego/laboratorio.py (`calcular_resultado_laboratorio`,
`calcular_preview_disparo`) y las de dibujo (`dibujar_laboratorio`,
`dibujar_preview_disparo`); solo cambia quién las llama: antes la clase de
ventana, ahora esta pantalla.

Cambios respecto a la versión original:
  * `FigureCanvasTkAgg` se crea dentro de `_construir_ui()`.
  * `_limpiar()` cierra las figuras de matplotlib (`plt.close`) antes de que
    Tkinter destruya el frame, evitando acumular figuras en memoria al
    entrar/salir repetidas veces del laboratorio.
  * El último vector usado se guarda en `gestor.compartido` y se restaura al
    volver a entrar a la pantalla.
=================================================================================
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, Text, END, filedialog

try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    _MATPLOTLIB_DISPONIBLE = True
except ImportError:
    plt = None
    _MATPLOTLIB_DISPONIBLE = False

from juego_naval.ui.pantalla_base import PantallaBase
from juego_naval.diag import diag
from vector2d import Vector2D
from juego_naval.juego.laboratorio import (
    OPCIONES_LABORATORIO,
    calcular_resultado_laboratorio,
    dibujar_laboratorio,
    calcular_preview_disparo,
    dibujar_preview_disparo,
)


class PantallaLaboratorio(PantallaBase):
    """Dos pestañas: Laboratorio de Vectores y Simulador de Disparo (P + V)."""

    # Valores iniciales que se persisten en gestor.compartido.
    CLAVES_ESTADO = {
        "lab_ux": 2, "lab_uy": 3,
        "lab_vx": 4, "lab_vy": 1,
        "lab_k": 2,
        "lab_px": 2, "lab_py": 3,
        "lab_vx_pre": 3, "lab_vy_pre": 4,
    }

    def _construir_ui(self) -> None:
        barra = ttk.Frame(self)
        barra.pack(fill="x", padx=8, pady=6)
        ttk.Label(barra, text="Laboratorio de Vectores",
                  font=("Segoe UI", 13, "bold")).pack(side="left")
        self.var_mensaje = tk.StringVar(value="")
        ttk.Label(barra, textvariable=self.var_mensaje,
                  foreground="#1f6f2f", font=("Segoe UI", 10)).pack(side="left", padx=12)
        ttk.Button(barra, text="Volver al menú", command=self.volver).pack(side="right")

        if not _MATPLOTLIB_DISPONIBLE:
            self._pantalla_sin_matplotlib()
            return

        for clave, valor in self.CLAVES_ESTADO.items():
            self.gestor.compartido.setdefault(clave, valor)

        self._cuaderno = ttk.Notebook(self)
        self._cuaderno.pack(fill="both", expand=True)
        self._pestana_laboratorio()
        self._pestana_preview()
        diag("laboratorio: UI lista (2 pestanas: vectores y simulador P+V)")

    def _pantalla_sin_matplotlib(self) -> None:
        """Fallback: si falta matplotlib, muestra instrucciones en vez de crashear."""
        diag("laboratorio: matplotlib NO disponible, modo fallback")
        marco = ttk.Frame(self)
        marco.pack(fill="both", expand=True, padx=30, pady=30)
        ttk.Label(marco, text="Matplotlib no está instalado",
                  font=("Segoe UI", 16, "bold"), foreground="#c0392b").pack(pady=10)
        ttk.Label(marco, text=(
            "El Laboratorio de Vectores necesita matplotlib.\n\n"
            "Instálalo con:\n"
            "    .venv/bin/pip install matplotlib\n\n"
            "Y lanza el juego con el entorno virtual del proyecto:\n"
            "    .venv/bin/python main.py\n\n"
            "Puedes volver al menú mientras tanto."),
            justify="center", font=("Segoe UI", 11)).pack(pady=6)
        ttk.Button(marco, text="Volver al menú", command=self.volver).pack(pady=10)

    # ------------------------------------------------------------------ UI ---
    def _crear_slider(self, padre, texto, variable, desde, hasta, comando) -> None:
        frame = tk.LabelFrame(padre, text=texto, padx=10, pady=4)
        slider = tk.Scale(frame, from_=desde, to=hasta, orient="horizontal",
                          resolution=1, length=280, variable=variable,
                          command=comando, highlightthickness=0, troughcolor="#e0e0e0")
        slider.pack(fill="x", padx=6, pady=2)
        frame.pack(fill="x", padx=10, pady=6)
        return frame

    def _pestana_laboratorio(self) -> None:
        pestana = ttk.Frame(self._cuaderno)
        self._cuaderno.add(pestana, text="Laboratorio de Vectores")

        panel_control = ttk.Frame(pestana, width=360)
        panel_control.pack(side="left", fill="y", padx=4, pady=4)

        ttk.Label(panel_control, text="Operación a visualizar:",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 2))

        self.var_opcion = ttk.Combobox(panel_control, state="readonly",
                                       values=list(OPCIONES_LABORATORIO.values()),
                                       width=38)
        self.var_opcion.current(0)
        self.var_opcion.pack(fill="x", padx=10)
        self.var_opcion.bind("<<ComboboxSelected>>", lambda _e: self._actualizar_laboratorio())

        self.var_ux = tk.IntVar(self, self.gestor.compartido["lab_ux"])
        self.var_uy = tk.IntVar(self, self.gestor.compartido["lab_uy"])
        self._crear_slider(panel_control, "Vector U: componente X", self.var_ux, -10, 10, self._on_slider)
        self._crear_slider(panel_control, "Vector U: componente Y", self.var_uy, -10, 10, self._on_slider)

        self.var_vx = tk.IntVar(self, self.gestor.compartido["lab_vx"])
        self.var_vy = tk.IntVar(self, self.gestor.compartido["lab_vy"])
        self._crear_slider(panel_control, "Vector V: componente X", self.var_vx, -10, 10, self._on_slider)
        self._crear_slider(panel_control, "Vector V: componente Y", self.var_vy, -10, 10, self._on_slider)

        self.var_k = tk.IntVar(self, self.gestor.compartido["lab_k"])
        self._crear_slider(panel_control, "Escalar k (solo multiplicación)", self.var_k, 0, 5, self._on_slider)

        botones = ttk.Frame(panel_control)
        botones.pack(fill="x", padx=10, pady=6)
        ttk.Button(botones, text="Restablecer", command=self._restablecer_laboratorio).pack(side="left")
        ttk.Button(botones, text="Guardar imagen PNG", command=self._guardar_imagen).pack(side="right")

        self.texto_explicacion = Text(panel_control, height=14, wrap="word",
                                      font=("Consolas", 10))
        self.texto_explicacion.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        marco_grafico = ttk.Frame(pestana)
        marco_grafico.pack(side="right", fill="both", expand=True, padx=4, pady=4)

        self.figura_lab = Figure(figsize=(7.2, 6.2), dpi=100)
        self.ax_lab = self.figura_lab.add_subplot(111)
        self.canvas_lab = FigureCanvasTkAgg(self.figura_lab, master=marco_grafico)
        self.canvas_lab.get_tk_widget().pack(fill="both", expand=True)
        NavigationToolbar2Tk(self.canvas_lab, self.winfo_toplevel()).update()

        self._actualizar_laboratorio()

    def _pestana_preview(self) -> None:
        pestana = ttk.Frame(self._cuaderno)
        self._cuaderno.add(pestana, text="Simulador de Disparo (P + V)")

        panel_control = ttk.Frame(pestana, width=360)
        panel_control.pack(side="left", fill="y", padx=4, pady=4)

        ttk.Label(panel_control, text="Tablero 10x10 (coordenadas 0..9):",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 2))

        self.var_px = tk.IntVar(self, self.gestor.compartido["lab_px"])
        self.var_py = tk.IntVar(self, self.gestor.compartido["lab_py"])
        self._crear_slider(panel_control, "Posición del barco P: X (0..9)", self.var_px, 0, 9, self._on_slider)
        self._crear_slider(panel_control, "Posición del barco P: Y (0..9)", self.var_py, 0, 9, self._on_slider)

        self.var_vx_pre = tk.IntVar(self, self.gestor.compartido["lab_vx_pre"])
        self.var_vy_pre = tk.IntVar(self, self.gestor.compartido["lab_vy_pre"])
        self._crear_slider(panel_control, "Vector de disparo V: X (-9..9)", self.var_vx_pre, -9, 9, self._on_slider)
        self._crear_slider(panel_control, "Vector de disparo V: Y (-9..9)", self.var_vy_pre, -9, 9, self._on_slider)

        self.var_veredicto = tk.StringVar(value="")
        self.etiqueta_veredicto = ttk.Label(
            panel_control, textvariable=self.var_veredicto,
            font=("Segoe UI", 10, "bold"), wraplength=330, justify="center")
        self.etiqueta_veredicto.pack(fill="x", padx=10, pady=10)

        marco_grafico = ttk.Frame(pestana)
        marco_grafico.pack(side="right", fill="both", expand=True, padx=4, pady=4)

        self.figura_preview = Figure(figsize=(7.2, 6.2), dpi=100)
        self.ax_preview = self.figura_preview.add_subplot(111)
        self.canvas_preview = FigureCanvasTkAgg(self.figura_preview, master=marco_grafico)
        self.canvas_preview.get_tk_widget().pack(fill="both", expand=True)

        self._actualizar_preview()

    # ------------------------------------------------------------ acciones ---
    def _on_slider(self, _valor=None) -> None:
        self._guardar_estado()
        self._actualizar_laboratorio()
        self._actualizar_preview()

    def _opcion_seleccionada(self) -> str:
        etiqueta = self.var_opcion.get()
        for clave, texto in OPCIONES_LABORATORIO.items():
            if texto == etiqueta:
                return clave
        return "suma"

    def _actualizar_laboratorio(self) -> None:
        u = Vector2D(self.var_ux.get(), self.var_uy.get())
        v = Vector2D(self.var_vx.get(), self.var_vy.get())
        k = self.var_k.get()
        res = calcular_resultado_laboratorio(self._opcion_seleccionada(), u, v, k)
        dibujar_laboratorio(self.ax_lab, res["opcion"], u, v, k, res)
        self.canvas_lab.draw_idle()
        self._mostrar_explicacion(res)

    def _actualizar_preview(self) -> None:
        origen = Vector2D(self.var_px.get(), self.var_py.get())
        vector = Vector2D(self.var_vx_pre.get(), self.var_vy_pre.get())
        preview = calcular_preview_disparo(origen, vector)
        dibujar_preview_disparo(self.ax_preview, preview)
        self.canvas_preview.draw_idle()

        if preview["dentro"]:
            self.var_veredicto.set(
                f"El disparo cae DENTRO del tablero en {preview['destino']}.")
            self.etiqueta_veredicto.config(foreground="#2ca02c")
        else:
            self.var_veredicto.set(
                f"El disparo cae FUERA del tablero (válido 0..9): destino "
                f"{preview['destino']}.")
            self.etiqueta_veredicto.config(foreground="#d62728")

    def _mostrar_explicacion(self, res: dict) -> None:
        self.texto_explicacion.config(state="normal")
        self.texto_explicacion.delete("1.0", END)
        lineas = [res["operacion"], "", "Formula: " + res["formula"], ""]
        for paso in res["pasos"]:
            lineas.append(paso)
        self.texto_explicacion.insert(END, "\n".join(lineas))
        self.texto_explicacion.config(state="disabled")

    def _restablecer_laboratorio(self) -> None:
        for clave, valor in self.CLAVES_ESTADO.items():
            self.gestor.compartido[clave] = valor
        self.var_ux.set(self.CLAVES_ESTADO["lab_ux"])
        self.var_uy.set(self.CLAVES_ESTADO["lab_uy"])
        self.var_vx.set(self.CLAVES_ESTADO["lab_vx"])
        self.var_vy.set(self.CLAVES_ESTADO["lab_vy"])
        self.var_k.set(self.CLAVES_ESTADO["lab_k"])
        self.var_px.set(self.CLAVES_ESTADO["lab_px"])
        self.var_py.set(self.CLAVES_ESTADO["lab_py"])
        self.var_vx_pre.set(self.CLAVES_ESTADO["lab_vx_pre"])
        self.var_vy_pre.set(self.CLAVES_ESTADO["lab_vy_pre"])
        self.var_opcion.current(0)
        self._guardar_estado()
        self._actualizar_laboratorio()
        self._actualizar_preview()

    def _guardar_imagen(self) -> None:
        ruta = filedialog.asksaveasfilename(
            defaultextension=".png", initialfile="vector.png",
            filetypes=[("Imagen PNG", "*.png")])
        if ruta:
            self.figura_lab.savefig(ruta, dpi=150)
            self.var_mensaje.set(f"Imagen guardada en: {ruta}")

    # ------------------------------------------------------------- estado ----
    def _guardar_estado(self) -> None:
        c = self.gestor.compartido
        c["lab_ux"] = self.var_ux.get()
        c["lab_uy"] = self.var_uy.get()
        c["lab_vx"] = self.var_vx.get()
        c["lab_vy"] = self.var_vy.get()
        c["lab_k"] = self.var_k.get()
        c["lab_px"] = self.var_px.get()
        c["lab_py"] = self.var_py.get()
        c["lab_vx_pre"] = self.var_vx_pre.get()
        c["lab_vy_pre"] = self.var_vy_pre.get()

    # ----------------------------------------------------------- limpieza ----
    def _limpiar(self) -> None:
        if not _MATPLOTLIB_DISPONIBLE:
            return
        for nombre in ("figura_lab", "figura_preview"):
            figura = getattr(self, nombre, None)
            if figura is not None:
                try:
                    plt.close(figura)
                except Exception:
                    pass
