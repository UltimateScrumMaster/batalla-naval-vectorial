"""
=================================================================================
MÓDULO: juego_naval/logica/laboratorio.py - Matemática del Laboratorio de Vectores
=================================================================================
Funciones puras de cálculo y de dibujo del Laboratorio, extraídas de
`interfaz_grafica.py` (migración a la arquitectura unificada). No dependen de
tkinter ni de la ventana: reciben/retornan datos y dibujan sobre un eje `ax` de
matplotlib que la capa de presentación les pasa.
=================================================================================
"""

from typing import Any, Dict

from juego_naval.dominio.vector2d import Vector2D

# Paleta de colores (modo claro, legible en pizarra digital y proyector)
COLOR_U = "#1f77b4"        # azul: vector U
COLOR_V = "#d62728"        # rojo: vector V
COLOR_RESULTADO = "#2ca02c"  # verde: resultado
COLOR_SOMBRA = "#ff7f0e"   # naranja: sombra de proyección / auxiliares
COLOR_AUX = "#888888"      # gris: líneas auxiliares

# Operaciones disponibles en el laboratorio (clave interna -> etiqueta visible)
OPCIONES_LABORATORIO: Dict[str, str] = {
    "suma": "Suma (U + V)",
    "resta": "Resta (U - V)",
    "escalar": "Multiplicación por Escalar (k·V)",
    "modulo": "Módulo / Magnitud (||V||)",
    "distancia": "Distancia entre U y V (||U - V||)",
    "punto": "Producto Punto (U · V)",
    "proyeccion": "Proyección Ortogonal (proj_U(V))",
}


# =============================================================================
# FUNCIONES PURAS DE CÁLCULO (comprobables con unittest, sin interfaz gráfica)
# =============================================================================

def calcular_resultado_laboratorio(opcion: str, u: Vector2D, v: Vector2D,
                                   k: float = 1.0) -> Dict[str, Any]:
    """Calcula el resultado algebraico de una operación del laboratorio.

    Args:
        opcion: Clave de OPCIONES_LABORATORIO (ej: "suma", "proyeccion").
        u: Vector U del laboratorio.
        v: Vector V del laboratorio.
        k: Escalar para la multiplicación.

    Returns:
        Diccionario con: opcion, tipo ("vector" | "escalar"), resultado,
        operacion, formula, pasos y, en caso de error, "error": True.
    """
    opcion = opcion.lower().strip()
    u = Vector2D(u.x, u.y)
    v = Vector2D(v.x, v.y)

    if opcion == "suma":
        exp = u.explicar_suma(v, "U", "V")
        return {"opcion": "suma", "tipo": "vector", "resultado": u + v,
                "operacion": exp["operacion"], "formula": exp["formula"],
                "pasos": exp["pasos"]}

    if opcion == "resta":
        r = u - v
        pasos = [
            f"1. Coordenada X = {u.x} - ({v.x}) = {r.x}",
            f"2. Coordenada Y = {u.y} - ({v.y}) = {r.y}",
            f"3. Vector Resta = ({r.x}, {r.y})",
        ]
        return {"opcion": "resta", "tipo": "vector", "resultado": r,
                "operacion": "Resta de Vectores",
                "formula": "U - V = (Ux - Vx, Uy - Vy)", "pasos": pasos}

    if opcion == "escalar":
        exp = v.explicar_escalar(k, "V")
        return {"opcion": "escalar", "tipo": "vector", "resultado": v * k,
                "operacion": exp["operacion"], "formula": exp["formula"],
                "pasos": exp["pasos"]}

    if opcion == "modulo":
        m = v.magnitud()
        mag2 = v.magnitud_cuadrada()
        pasos = [
            f"1. Cuadrados de las componentes: ({v.x})² = {v.x ** 2},  ({v.y})² = {v.y ** 2}",
            f"2. Suma de cuadrados = {mag2}",
            f"3. Raíz cuadrada: ||V|| = sqrt({mag2}) = {m:.2f}",
        ]
        return {"opcion": "modulo", "tipo": "escalar", "resultado": m,
                "operacion": "Módulo / Magnitud del Vector",
                "formula": "||V|| = sqrt(x² + y²)", "pasos": pasos}

    if opcion == "distancia":
        exp = u.explicar_distancia(v, "U", "V")
        return {"opcion": "distancia", "tipo": "escalar",
                "resultado": round(u.distancia_a(v), 2),
                "operacion": exp["operacion"], "formula": exp["formula"],
                "pasos": exp["pasos"]}

    if opcion == "punto":
        p = u.producto_punto(v)
        pasos = [
            f"1. Multiplicación de componentes X: {u.x} × {v.x} = {u.x * v.x}",
            f"2. Multiplicación de componentes Y: {u.y} × {v.y} = {u.y * v.y}",
            f"3. Suma final: U · V = {p}",
        ]
        return {"opcion": "punto", "tipo": "escalar", "resultado": p,
                "operacion": "Producto Punto / Producto Escalar",
                "formula": "U · V = (Ux × Vx) + (Uy × Vy)", "pasos": pasos}

    if opcion == "proyeccion":
        if u.es_cero():
            return {"opcion": "proyeccion", "tipo": "vector",
                    "resultado": Vector2D(0, 0),
                    "operacion": "Proyección Vectorial Ortogonal",
                    "formula": "proj_U(V) = [(V · U) / ||U||²] · U",
                    "pasos": ["La base U no puede ser el vector nulo (0, 0)."],
                    "error": True}
        exp = v.explicar_proyeccion(u, "V", "U")
        return {"opcion": "proyeccion", "tipo": "vector",
                "resultado": exp["resultado"],
                "operacion": exp["operacion"], "formula": exp["formula"],
                "pasos": exp["pasos"]}

    raise ValueError(f"Operación de laboratorio desconocida: {opcion}")


def calcular_preview_disparo(origen: Vector2D, vector: Vector2D,
                             ancho: int = 10, alto: int = 10) -> Dict[str, Any]:
    """Calcula el destino de un disparo vectorial y si cae dentro del tablero.

    Args:
        origen: Posición del barco (P).
        vector: Vector de disparo (V).
        ancho, alto: Dimensiones del tablero (por defecto 10x10, índices 0..9).

    Returns:
        Diccionario con: origen, vector, destino, dentro, ancho, alto.
    """
    destino = origen + vector
    dentro = (0 <= destino.x < ancho) and (0 <= destino.y < alto)
    return {"origen": origen, "vector": vector, "destino": destino,
            "dentro": dentro, "ancho": ancho, "alto": alto}


# =============================================================================
# FUNCIONES DE DIBUJO SOBRE UN EJE DE MATPLOTLIB
# =============================================================================

def configurar_plano(ax, limite: float, titulo: str = "") -> None:
    """Prepara un plano cartesiano con ejes, cuadrícula y escala 1:1."""
    ax.clear()
    ax.axhline(0, color="black", linewidth=1.0)
    ax.axvline(0, color="black", linewidth=1.0)
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-limite, limite)
    ax.set_ylim(-limite, limite)
    if titulo:
        ax.set_title(titulo)


def dibujar_flecha(ax, origen: Vector2D, vector: Vector2D,
                   color: str, etiqueta: str = "") -> None:
    """Dibuja una flecha con punta real y longitud proporcional a la magnitud."""
    mag = vector.magnitud()
    if mag < 1e-9:
        ax.plot(origen.x, origen.y, marker="o", color=color, zorder=4)
        if etiqueta:
            ax.annotate(f"{etiqueta} = (0, 0)", (origen.x, origen.y),
                        textcoords="offset points", xytext=(8, 8), color=color)
        return
    ax.arrow(origen.x, origen.y, vector.x, vector.y,
             color=color, head_width=0.25, head_length=0.45, width=0.02,
             length_includes_head=True, clip_on=False, zorder=3)


def _proxy_leyenda(ax, color: str, etiqueta: str, linestyle: str = "-") -> None:
    """Añade una entrada de leyenda sin necesidad de objetos visibles."""
    ax.plot([], [], color=color, linewidth=2, linestyle=linestyle, label=etiqueta)


def dibujar_laboratorio(ax, opcion: str, u: Vector2D, v: Vector2D,
                        k: float, resultado: Dict[str, Any]) -> None:
    """Dibuja en 'ax' la representación gráfica de la operación elegida."""
    opcion = opcion.lower().strip()
    configurar_plano(ax, 8, OPCIONES_LABORATORIO.get(opcion, opcion))

    _proxy_leyenda(ax, COLOR_U, "Vector U")
    _proxy_leyenda(ax, COLOR_V, "Vector V")
    _proxy_leyenda(ax, COLOR_RESULTADO, "Resultado")

    dibujar_flecha(ax, Vector2D(0, 0), u, COLOR_U)
    dibujar_flecha(ax, Vector2D(0, 0), v, COLOR_V)

    if opcion == "suma":
        r = u + v
        dibujar_flecha(ax, Vector2D(0, 0), r, COLOR_RESULTADO, "U+V")
        ax.plot([u.x, r.x], [u.y, r.y], color=COLOR_V, linewidth=1,
                linestyle=":", alpha=0.6)
        ax.plot([v.x, r.x], [v.y, r.y], color=COLOR_U, linewidth=1,
                linestyle=":", alpha=0.6)

    elif opcion == "resta":
        r = u - v
        dibujar_flecha(ax, Vector2D(0, 0), r, COLOR_RESULTADO, "U-V")
        ax.plot([u.x, u.x + v.x], [u.y, u.y + v.y], color=COLOR_V, linewidth=1,
                linestyle=":", alpha=0.6)
        ax.plot([v.x, v.x + u.x], [v.y, v.y + u.y], color=COLOR_U, linewidth=1,
                linestyle=":", alpha=0.6)

    elif opcion == "escalar":
        if k == 0:
            dibujar_flecha(ax, Vector2D(0, 0), v, COLOR_V)
            ax.annotate("k·V = (0, 0) (vector nulo)", (0.2, -0.9),
                        color=COLOR_RESULTADO, fontsize=10)
        else:
            dibujar_flecha(ax, Vector2D(0, 0), v * k, COLOR_RESULTADO, "k·V")
            if abs(k) != 1:
                ax.plot([v.x * min(1, k), v.x], [v.y * min(1, k), v.y],
                        color=COLOR_SOMBRA, linewidth=1, linestyle=":")

    elif opcion == "modulo":
        medio = Vector2D(v.x / 2, v.y / 2)
        ax.annotate(f"||V|| = {resultado['resultado']:.2f}",
                    (medio.x, medio.y), color=COLOR_RESULTADO,
                    fontsize=11, fontweight="bold",
                    xytext=(0, 10), textcoords="offset points")

    elif opcion == "distancia":
        ax.plot([u.x, v.x], [u.y, v.y], color=COLOR_SOMBRA, linewidth=1.5,
                linestyle="--", alpha=0.9)
        medio = Vector2D((u.x + v.x) / 2, (u.y + v.y) / 2)
        ax.annotate(f"d = {resultado['resultado']:.2f}",
                    (medio.x, medio.y), color=COLOR_SOMBRA,
                    fontsize=11, fontweight="bold",
                    xytext=(0, 10), textcoords="offset points")

    elif opcion == "punto":
        _proxy_leyenda(ax, COLOR_SOMBRA, "Valor del producto")
        ax.annotate(f"U · V = {resultado['resultado']}",
                    (0.3, _limite_y_seguro(ax)), color=COLOR_SOMBRA,
                    fontsize=12, fontweight="bold")

    elif opcion == "proyeccion":
        _proxy_leyenda(ax, COLOR_SOMBRA, "Sombra (perpendicular)", linestyle="--")
        if u.es_cero():
            ax.annotate("Base U nula: no se puede proyectar.", (0.2, 0.3),
                        color=COLOR_V, fontsize=11, fontweight="bold")
        else:
            proy = v.proyeccion_sobre(u)
            dibujar_flecha(ax, Vector2D(0, 0), proy, COLOR_RESULTADO, "proj_U(V)")
            if v.magnitud() > 1e-9 and proy.magnitud() > 1e-9:
                ax.plot([proy.x, v.x], [proy.y, v.y], color=COLOR_SOMBRA,
                        linewidth=1.5, linestyle="--", alpha=0.9)
                ax.plot(v.x, v.y, marker="o", color=COLOR_SOMBRA, zorder=4)

    ax.legend(loc="upper right", fontsize=9)


def _limite_y_seguro(ax) -> float:
    """Devuelve un valor ligeramente dentro del límite inferior del eje Y."""
    ymin, _ = ax.get_ylim()
    return ymin + 0.4


def dibujar_preview_disparo(ax, preview: Dict[str, Any]) -> None:
    """Dibuja la grilla del tablero y la flecha del disparo previsto."""
    ancho = preview["ancho"]
    alto = preview["alto"]
    origen = preview["origen"]
    vector = preview["vector"]
    destino = preview["destino"]

    configurar_plano(ax, ancho, "Simulador de Disparo Vectorial (P + V)")
    ax.set_xticks(range(ancho + 1))
    ax.set_yticks(range(alto + 1))
    ax.grid(True, which="major", color="#bbbbbb", linewidth=0.6)
    ax.set_xlim(-1, ancho)
    ax.set_ylim(-1, alto)

    _proxy_leyenda(ax, COLOR_U, "Origen (barco P)")
    _proxy_leyenda(ax, COLOR_V, "Vector de disparo V")
    _proxy_leyenda(ax, COLOR_RESULTADO, "Impacto dentro")
    _proxy_leyenda(ax, COLOR_SOMBRA, "Impacto fuera")

    ax.plot(origen.x, origen.y, marker="o", markersize=10, color=COLOR_U, zorder=4)
    ax.annotate(f"P{origen}", (origen.x, origen.y), textcoords="offset points",
                xytext=(-2, 8), color=COLOR_U, fontweight="bold")

    dibujar_flecha(ax, origen, vector, COLOR_V)

    color_impacto = COLOR_RESULTADO if preview["dentro"] else COLOR_SOMBRA
    ax.plot(destino.x, destino.y, marker="*", markersize=16, color=color_impacto, zorder=5)
    ax.annotate(f"P+V = {destino}", (destino.x, destino.y),
                textcoords="offset points", xytext=(8, -12),
                color=color_impacto, fontweight="bold")

    ax.legend(loc="upper right", fontsize=9)
