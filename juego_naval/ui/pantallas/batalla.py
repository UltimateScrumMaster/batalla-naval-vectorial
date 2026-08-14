"""
=================================================================================
MÓDULO: pantalla_batalla.py - Batalla Naval vs IA (migrado)
=================================================================================
Migración de `AplicacionBatallaGrafica` (juego_grafico.py) al patrón de
pantallas de juego_naval/ui.

La lógica de la partida (turnos, energía, viento, victoria/derrota) vive en
`SesionBatalla` (juego_naval/juego/sesion.py), guardada en
`gestor.compartido["sesion"]`. Esta pantalla solo se encarga de:

    * Pintar los tableros en tkinter Canvas.
    * Capturar el origen del disparo (clic sobre un barco propio).
    * Construir el vector con sliders y mostrar la predicción en matplotlib.
    * Mostrar el desglose matemático de cada disparo en el log.

Se reutilizan TAL CUAL las funciones puras de interfaz_grafica.py
(`calcular_preview_disparo`, `dibujar_preview_disparo`) y no se toca ninguna
regla del juego.
=================================================================================
"""

import tkinter as tk
from tkinter import ttk, Text, END, filedialog, messagebox
from typing import Any, Dict, List, Optional, Tuple

try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    _MATPLOTLIB_DISPONIBLE = True
except ImportError:
    plt = None
    _MATPLOTLIB_DISPONIBLE = False

from juego_naval.ui.pantalla_base import PantallaBase
from juego_naval.juego.sesion import SesionBatalla, EstadoBatalla, COSTOS_HABILIDAD, NOMBRES_HABILIDAD
from vector2d import Vector2D
from tablero import Tablero
from interfaz_grafica import calcular_preview_disparo, dibujar_preview_disparo

CLAVE_SESION = "sesion"


class PantallaBatalla(PantallaBase):
    """Pantalla de la batalla naval jugable con tkinter + matplotlib."""

    ANCHO, ALTO = 10, 10
    CELDA = 34
    MARGEN = 18
    COLOR_AGUA = "#b7d4ea"
    COLOR_AGUA_FALLO = "#e8eef3"
    COLOR_BARCO = "#6b7f99"
    COLOR_BARCO_SELECCION = "#f1c40f"
    COLOR_IMPACTO = "#c0392b"
    COLOR_SONAR = "#9b59b6"
    COLOR_PROYECCION = "#e67e22"
    COLOR_TEXTO = "#1f2a36"

    def __init__(self, maestro, gestor, **kwargs):
        self.sesion: Optional[SesionBatalla] = None
        self.habilidad_activa = "suma"
        self.origen_seleccionado: Optional[Vector2D] = None
        self._preview_item_enemigo: List[int] = []
        self._celda_items_enemigo: Dict[Tuple[int, int], int] = {}
        self._en_turno_ia = False
        super().__init__(maestro, gestor, **kwargs)

    # ------------------------------------------------------------ UI ---------
    def _construir_ui(self) -> None:
        if not _MATPLOTLIB_DISPONIBLE:
            self._pantalla_sin_matplotlib()
            return

        self._inicializar_sesion()

        marco_estado = ttk.Frame(self)
        marco_estado.pack(fill="x", padx=8, pady=(8, 4))

        self.var_estado = tk.StringVar(value="")
        self.etiqueta_estado = ttk.Label(
            marco_estado, textvariable=self.var_estado,
            font=("Segoe UI", 11, "bold"), foreground="#1f2a36")
        self.etiqueta_estado.pack(side="left", padx=6)

        self.barra_energia = ttk.Progressbar(
            marco_estado, length=140, maximum=6)
        self.barra_energia.pack(side="right", padx=6)
        self.var_energia = tk.StringVar(value="Energía: 2/6")
        ttk.Label(marco_estado, textvariable=self.var_energia,
                  font=("Consolas", 10)).pack(side="right")

        # --- Tres columnas: tablero jugador, radar enemigo, panel derecho ---
        columnas = ttk.Frame(self)
        columnas.pack(fill="both", expand=True, padx=8)

        col_jugador = ttk.Frame(columnas)
        col_jugador.pack(side="left", fill="both", expand=True, padx=4)
        ttk.Label(col_jugador, text="TU FLOTA (haz clic en un barco para disparar)",
                  font=("Segoe UI", 10, "bold")).pack()
        self.canvas_jugador = tk.Canvas(
            col_jugador, width=self.ANCHO * self.CELDA + 2 * self.MARGEN,
            height=self.ALTO * self.CELDA + 2 * self.MARGEN, bg="white")
        self.canvas_jugador.pack()
        self.canvas_jugador.bind("<Button-1>", self._al_clicar_tablero_jugador)

        col_enemigo = ttk.Frame(columnas)
        col_enemigo.pack(side="left", fill="both", expand=True, padx=4)
        ttk.Label(col_enemigo, text="RADAR ENEMIGO (niebla de guerra)",
                  font=("Segoe UI", 10, "bold")).pack()
        self.canvas_enemigo = tk.Canvas(
            col_enemigo, width=self.ANCHO * self.CELDA + 2 * self.MARGEN,
            height=self.ALTO * self.CELDA + 2 * self.MARGEN, bg="white")
        self.canvas_enemigo.pack()

        col_derecha = ttk.Frame(columnas)
        col_derecha.pack(side="left", fill="both", expand=True, padx=4)

        ttk.Label(col_derecha, text="PREDICCIÓN DEL VECTOR (P + V)",
                  font=("Segoe UI", 10, "bold")).pack()
        self.figura_plano = Figure(figsize=(3.3, 3.3), dpi=100)
        self.ax_plano = self.figura_plano.add_subplot(111)
        self.canvas_plano = FigureCanvasTkAgg(self.figura_plano, master=col_derecha)
        self.canvas_plano.get_tk_widget().pack(fill="both", expand=True)

        ttk.Label(col_derecha, text="Desglose matemático del turno:",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 2))
        self.log = Text(col_derecha, height=9, wrap="word",
                        font=("Consolas", 9), state="disabled", bg="#f7f9fb")
        self.log.pack(fill="both", expand=True)

        # --- Panel de control inferior ---
        control = ttk.Frame(self)
        control.pack(fill="x", padx=8, pady=(4, 8))

        marco_habilidades = ttk.LabelFrame(control, text="Habilidades")
        marco_habilidades.pack(fill="x", padx=4, pady=4)
        self.botones_habilidad: Dict[str, ttk.Button] = {}
        for clave in ("suma", "viento", "torpedo", "sonar", "orbital"):
            etiqueta = f"{clave.upper()[:1]} - {NOMBRES_HABILIDAD[clave]} ({COSTOS_HABILIDAD[clave]})"
            boton = ttk.Button(
                marco_habilidades, text=etiqueta, width=30,
                command=lambda c=clave: self._seleccionar_habilidad(c))
            boton.pack(side="left", padx=4, pady=2)
            self.botones_habilidad[clave] = boton

        marco_sliders = ttk.LabelFrame(control, text="Construye el vector")
        marco_sliders.pack(fill="x", padx=4, pady=4)

        self.var_vax = tk.IntVar(value=3)
        self.var_vay = tk.IntVar(value=4)
        self.var_vbx = tk.IntVar(value=1)
        self.var_vby = tk.IntVar(value=0)
        self.var_k = tk.IntVar(value=2)

        fila_a = ttk.Frame(marco_sliders)
        fila_a.pack(fill="x")
        self.etiqueta_a = ttk.Label(fila_a, text="Vector A: ",
                                    font=("Segoe UI", 9, "bold"), width=18)
        self.etiqueta_a.pack(side="left")
        self._crear_slider(fila_a, "X", self.var_vax, -9, 9)
        self._crear_slider(fila_a, "Y", self.var_vay, -9, 9)

        fila_b = ttk.Frame(marco_sliders)
        fila_b.pack(fill="x")
        self.etiqueta_b = ttk.Label(fila_b, text="Vector B (radar): ",
                                    font=("Segoe UI", 9, "bold"), width=18)
        self.etiqueta_b.pack(side="left")
        self._crear_slider(fila_b, "X", self.var_vbx, -9, 9)
        self._crear_slider(fila_b, "Y", self.var_vby, -9, 9)

        fila_k = ttk.Frame(marco_sliders)
        fila_k.pack(fill="x")
        self.etiqueta_k = ttk.Label(fila_k, text="Escalar k (potencia): ",
                                    font=("Segoe UI", 9, "bold"), width=18)
        self.etiqueta_k.pack(side="left")
        self._crear_slider(fila_k, "k", self.var_k, 0, 5)

        marco_botones = ttk.Frame(control)
        marco_botones.pack(fill="x", padx=4, pady=4)
        self.boton_disparar = ttk.Button(
            marco_botones, text="DISPARAR", command=self._disparar,
            style="Accent.TButton")
        self.boton_disparar.pack(side="left", padx=4)
        self.boton_siguiente = ttk.Button(
            marco_botones, text="Siguiente turno", command=self._siguiente_turno,
            state="disabled")
        self.boton_siguiente.pack(side="left", padx=4)
        ttk.Button(marco_botones, text="Nueva partida",
                   command=self._nueva_partida).pack(side="left", padx=4)
        ttk.Button(marco_botones, text="Guardar imagen del plano",
                   command=self._guardar_imagen).pack(side="left", padx=4)
        ttk.Button(marco_botones, text="Volver al menú",
                   command=self.volver).pack(side="right", padx=4)

        self.var_mensaje = tk.StringVar(value="")
        ttk.Label(control, textvariable=self.var_mensaje,
                  foreground="#c0392b", font=("Segoe UI", 10, "bold"),
                  wraplength=1100, justify="center").pack(fill="x", pady=2)

        self._empezar_turno_jugador()

    def _pantalla_sin_matplotlib(self) -> None:
        """Fallback: si falta matplotlib, muestra instrucciones en vez de crashear."""
        marco = ttk.Frame(self)
        marco.pack(fill="both", expand=True, padx=30, pady=30)
        ttk.Label(marco, text="Matplotlib no está instalado",
                  font=("Segoe UI", 16, "bold"), foreground="#c0392b").pack(pady=10)
        ttk.Label(marco, text=(
            "La Batalla Naval necesita matplotlib para el plano de predicción.\n\n"
            "Instálalo con:\n    pip install matplotlib\n\n"
            "Puedes volver al menú mientras tanto."),
            justify="center", font=("Segoe UI", 11)).pack(pady=6)
        ttk.Button(marco, text="Volver al menú", command=self.volver).pack(pady=10)

    def _inicializar_sesion(self) -> None:
        """Crea la sesión de partida y la guarda en gestor.compartido."""
        self.sesion = SesionBatalla()
        self.gestor.compartido[CLAVE_SESION] = self.sesion

    def _crear_slider(self, padre, nombre, variable, desde, hasta) -> None:
        slider = tk.Scale(
            padre, from_=desde, to=hasta, orient="horizontal", resolution=1,
            length=150, variable=variable, command=lambda _e: self._actualizar_preview(),
            highlightthickness=0, troughcolor="#d9e2ea")
        slider.pack(side="left", padx=6, pady=2)

    # --------------------------------------------------------- turnos ---------
    def _empezar_turno_jugador(self) -> None:
        self.sesion.comenzar_turno_jugador()

        self._en_turno_ia = False
        self._elegir_origen_predeterminado()
        self._seleccionar_habilidad(self.habilidad_activa, reescanear=False)
        self.boton_disparar.config(state="normal")
        for boton in self.botones_habilidad.values():
            boton.config(state="normal")
        self.boton_siguiente.config(state="disabled")
        self._estado(f"TURNO {self.sesion.turno}: elige habilidad, ajusta el vector y dispara. "
                     f"Viento actual: {self.sesion.viento}")
        self._mensaje("")
        self._redibujar_todo()
        self._actualizar_preview()

    def _seleccionar_habilidad(self, clave: str, reescanear: bool = True) -> None:
        self.habilidad_activa = clave
        for k, boton in self.botones_habilidad.items():
            boton.config(style="Accent.TButton" if k == clave else "TButton")

        # Activar/desactivar sliders según la habilidad
        requiere_a = clave in ("suma", "viento", "torpedo", "orbital")
        requiere_b = clave == "orbital"
        requiere_k = clave == "torpedo"
        self._configurar_slider_fila("a", requiere_a, "Vector de tiro V" if clave in ("suma", "viento", "orbital") else "Dirección base U")
        self._configurar_slider_fila("b", requiere_b, "Vector base del radar U")
        self._configurar_slider_fila("k", requiere_k, "Escalar k (potencia)")

        if reescanear:
            self._actualizar_preview()

    def _configurar_slider_fila(self, fila: str, activo: bool, etiqueta: str) -> None:
        etiqueta_widget = getattr(self, f"etiqueta_{fila}")
        etiqueta_widget.config(text=etiqueta + ": " if activo else f"{etiqueta}: (no aplica)")
        for widget in etiqueta_widget.master.winfo_children():
            if isinstance(widget, tk.Scale):
                widget.config(state="normal" if activo else "disabled")

    def _elegir_origen_predeterminado(self) -> None:
        vivos = [b for b in self.sesion.tablero_jugador.barcos if not b.esta_hundido()]
        if vivos:
            self.origen_seleccionado = vivos[0].origen

    def _al_clicar_tablero_jugador(self, evento) -> None:
        if self._en_turno_ia:
            return
        x, y = self._celda_desde_evento(evento, self.canvas_jugador)
        if x is None:
            return
        barco = self._barco_en_celda(x, y)
        if barco is not None and not barco.esta_hundido():
            self.origen_seleccionado = barco.origen
            self._estado(f"Barco emisor seleccionado: {barco.nombre} en {barco.origen}")
            self._redibujar_todo()
            self._actualizar_preview()

    # ----------------------------------------------------- ejecución ---------
    def _vector_efectivo(self) -> Tuple[Vector2D, Vector2D]:
        a = Vector2D(self.var_vax.get(), self.var_vay.get())
        b = Vector2D(self.var_vbx.get(), self.var_vby.get())
        return a, b

    def _actualizar_preview(self) -> None:
        if self.origen_seleccionado is None or self.sesion is None:
            return
        a, _b = self._vector_efectivo()
        clave = self.habilidad_activa
        if clave == "viento":
            vector = a + self.sesion.viento
        elif clave == "torpedo":
            vector = a * self.var_k.get()
        else:
            vector = a

        preview = calcular_preview_disparo(self.origen_seleccionado, vector)
        dibujar_preview_disparo(self.ax_plano, preview)
        self.canvas_plano.draw_idle()
        self._marcar_destino_enemigo(preview)

    def _marcar_destino_enemigo(self, preview: Dict[str, Any]) -> None:
        for item in self._preview_item_enemigo:
            self.canvas_enemigo.delete(item)
        self._preview_item_enemigo = []
        destino = preview["destino"]
        color = self.COLOR_IMPACTO if not preview["dentro"] else "#2ca02c"
        px, py = self._a_pantalla(destino.x, destino.y)
        item = self.canvas_enemigo.create_rectangle(
            px + 3, py + 3, px + self.CELDA - 3, py + self.CELDA - 3,
            outline=color, width=4)
        self._preview_item_enemigo.append(item)

    def _disparar(self) -> None:
        if self._en_turno_ia or self.origen_seleccionado is None:
            return
        clave = self.habilidad_activa
        a, b = self._vector_efectivo()
        resultado, error = self.sesion.ejecutar_ataque_jugador(
            clave, self.origen_seleccionado, a, b, self.var_k.get())

        if error:
            self._mensaje(error)
            return

        self._limpiar_log()
        self._log(f"=== {NOMBRES_HABILIDAD[clave]} ===", "bold")

        if clave == "sonar":
            self._log(resultado["mensaje"])
        else:
            for r in resultado.get("resultado_tablero", []):
                self._log("  " + r.mensaje)
            if "mensaje" in resultado and clave == "orbital":
                self._log("  " + resultado["mensaje"])

        explicacion = resultado.get("explicacion", {})
        self._log("Formulación: " + explicacion.get("formula", ""))
        for paso in explicacion.get("pasos", []):
            self._log("  " + paso)

        self._redibujar_todo()

        if self.sesion.estado == EstadoBatalla.VICTORIA:
            self._mensaje("VICTORIA: destruiste toda la flota enemiga con precisión vectorial.")
            self._deshabilitar_controles()
            messagebox.showinfo("Victoria",
                                "Has hundido toda la flota enemiga con álgebra vectorial.")
            return

        self._turno_ia()

    def _turno_ia(self) -> None:
        self._en_turno_ia = True
        self._deshabilitar_controles()
        self._estado("La IA enemiga está calculando su vector de ataque...")
        self._mensaje("")
        self.after(900, self._ejecutar_turno_ia)

    def _ejecutar_turno_ia(self) -> None:
        res = self.sesion.ejecutar_turno_ia()

        self._log("=== TURNO DE LA IA (Almirante Vector) ===")
        for r in res.get("resultado_tablero", []):
            self._log("  " + r.mensaje)
        explicacion = res.get("explicacion", {})
        for paso in explicacion.get("pasos", []):
            self._log("  " + paso)

        self._redibujar_todo()

        if self.sesion.estado == EstadoBatalla.DERROTA:
            self._mensaje("DERROTA: la IA eliminó tu flota.")
            messagebox.showinfo("Derrota", "Tu flota fue eliminada por la artillería enemiga.")
            return

        self._en_turno_ia = False
        self.boton_siguiente.config(state="normal")
        self._estado(f"La IA disparó. Presiona 'Siguiente turno' para continuar (turno {self.sesion.turno}).")

    def _siguiente_turno(self) -> None:
        self._empezar_turno_jugador()

    def _nueva_partida(self) -> None:
        self._inicializar_sesion()
        self._limpiar_log()
        self._empezar_turno_jugador()

    def _guardar_imagen(self) -> None:
        ruta = filedialog.asksaveasfilename(
            defaultextension=".png", initialfile="vector_tiro.png",
            filetypes=[("Imagen PNG", "*.png")])
        if ruta:
            self.figura_plano.savefig(ruta, dpi=150)
            self._estado(f"Imagen guardada en: {ruta}")

    # -------------------------------------------------- render de tableros ---
    def _a_pantalla(self, x: int, y: int) -> Tuple[int, int]:
        px = self.MARGEN + x * self.CELDA
        py = self.MARGEN + (self.ALTO - 1 - y) * self.CELDA
        return px, py

    def _celda_desde_evento(self, evento, canvas) -> Tuple[Optional[int], Optional[int]]:
        col = (evento.x - self.MARGEN) // self.CELDA
        fila_invertida = (evento.y - self.MARGEN) // self.CELDA
        if not (0 <= col < self.ANCHO and 0 <= fila_invertida < self.ALTO):
            return None, None
        return col, self.ALTO - 1 - fila_invertida

    def _barco_en_celda(self, x: int, y: int):
        for barco in self.sesion.tablero_jugador.barcos:
            if barco.ocupa_coordenada(Vector2D(x, y)):
                return barco
        return None

    def _dibujar_tablero(self, canvas, tablero: Tablero, mostrar_barcos: bool) -> None:
        canvas.delete("all")
        self._celda_items_enemigo = {}

        for x in range(self.ANCHO):
            canvas.create_text(self.MARGEN + x * self.CELDA + self.CELDA // 2, 8,
                               text=str(x), fill=self.COLOR_TEXTO, font=("Consolas", 8))
        for y in range(self.ALTO):
            canvas.create_text(8, self.MARGEN + (self.ALTO - 1 - y) * self.CELDA + self.CELDA // 2,
                               text=str(y), fill=self.COLOR_TEXTO, font=("Consolas", 8))

        for x in range(self.ANCHO):
            for y in range(self.ALTO):
                px, py = self._a_pantalla(x, y)
                tupla = (x, y)
                relleno = self.COLOR_AGUA
                simbolo, color_simbolo = "", ""

                if tupla in tablero.disparos_acierto:
                    relleno = self.COLOR_IMPACTO
                    simbolo, color_simbolo = "✖", "white"
                elif tupla in tablero.disparos_agua:
                    relleno = self.COLOR_AGUA_FALLO
                    simbolo, color_simbolo = "✕", "#7a8aa0"
                elif tupla in tablero.rastro_proyeccion:
                    relleno = "#fdebd0"
                    simbolo, color_simbolo = "▸", self.COLOR_PROYECCION
                elif mostrar_barcos:
                    for barco in tablero.barcos:
                        if barco.ocupa_coordenada(Vector2D(x, y)):
                            if not barco.esta_hundido():
                                relleno = self.COLOR_BARCO
                                simbolo, color_simbolo = barco.icono, "white"
                            else:
                                relleno = "#5a6572"
                                simbolo, color_simbolo = "✖", "white"
                            break

                for scan in tablero.historial_sonar:
                    if tupla == scan["centro"].a_tupla_grilla():
                        relleno = "#e8d5f5"
                        simbolo, color_simbolo = "◉", self.COLOR_SONAR

                item = canvas.create_rectangle(
                    px, py, px + self.CELDA, py + self.CELDA,
                    fill=relleno, outline="#ffffff", width=1)
                if not mostrar_barcos:
                    self._celda_items_enemigo[tupla] = item
                if simbolo:
                    canvas.create_text(px + self.CELDA // 2, py + self.CELDA // 2,
                                       text=simbolo, fill=color_simbolo,
                                       font=("Consolas", 12, "bold"))

        # Resaltar el barco seleccionado en el tablero del jugador
        if mostrar_barcos and self.origen_seleccionado is not None:
            for barco in self.sesion.tablero_jugador.barcos:
                if barco.origen == self.origen_seleccionado and not barco.esta_hundido():
                    for celda in barco.celdas:
                        t = celda.a_tupla_grilla()
                        px, py = self._a_pantalla(t[0], t[1])
                        canvas.create_rectangle(
                            px + 1, py + 1, px + self.CELDA - 1, py + self.CELDA - 1,
                            outline=self.COLOR_BARCO_SELECCION, width=3)
                    break

    def _redibujar_todo(self) -> None:
        self._dibujar_tablero(self.canvas_jugador, self.sesion.tablero_jugador, True)
        self._dibujar_tablero(self.canvas_enemigo, self.sesion.tablero_enemigo, False)
        energia = self.sesion.energia_jugador
        self.barra_energia["value"] = energia
        self.var_energia.set(f"Energía: {energia}/6")

    # ------------------------------------------------------------ utilidades --
    def _estado(self, texto: str) -> None:
        self.var_estado.set(texto)

    def _mensaje(self, texto: str) -> None:
        self.var_mensaje.set(texto)

    def _limpiar_log(self) -> None:
        self.log.config(state="normal")
        self.log.delete("1.0", END)
        self.log.config(state="disabled")

    def _log(self, texto: str, estilo: str = "normal") -> None:
        self.log.config(state="normal")
        self.log.insert(END, texto + "\n")
        self.log.config(state="disabled")
        self.log.see(END)

    def _deshabilitar_controles(self) -> None:
        self.boton_disparar.config(state="disabled")
        for boton in self.botones_habilidad.values():
            boton.config(state="disabled")
        for widget in self.winfo_children():
            for sub in widget.winfo_children():
                for item in sub.winfo_children():
                    if isinstance(item, tk.Scale):
                        item.config(state="disabled")

    # ------------------------------------------------------------ limpieza ---
    def _limpiar(self) -> None:
        if not _MATPLOTLIB_DISPONIBLE:
            return
        figura = getattr(self, "figura_plano", None)
        if figura is not None:
            try:
                plt.close(figura)
            except Exception:
                pass
