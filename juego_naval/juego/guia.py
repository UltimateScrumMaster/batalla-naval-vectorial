"""
=================================================================================
MÓDULO: juego_naval/juego/guia.py - Manual de fórmulas y habilidades
=================================================================================
Contenido pedagógico del Manual de Fórmulas y Habilidades, extraído de
`interfaz.mostrar_guia_habilidades` (Rich) como datos puros reutilizables.
=================================================================================
"""

# (tipo de vector, qué significa, ejemplo)
DICCIONARIO_VECTORES = (
    ("P_barco (Posición del barco)", "Dónde está tu navío. Punto de partida de todos tus disparos.", "(2, 3)"),
    ("V_tiro (Vector de tiro)", "Cuánto y hacia dónde viaja el proyectil. Se SUMA a la posición del barco.", "(3, 2) = 3 a la derecha, 2 arriba"),
    ("P_impacto (Punto de impacto)", "Dónde cae la bala. Resultado de P_barco + V_tiro.", "(2,3) + (3,2) = (5,5)"),
    ("V_viento (Vector de viento)", "Fuerza que empuja y desvía tu proyectil. Debes compensarla.", "(1,-1) sopla derecha y abajo"),
    ("u_dir (Dirección base)", "Orientación pura del torpedo, sin potencia. Generalmente corto.", "(1,0) u (1,1)"),
    ("k (Escalar)", "Número que multiplica la potencia/alcance del vector (no es un vector).", "k = 3 triplica el alcance"),
    ("k·u (Vector escalado)", "El vector original estirado k veces: mismo sentido, más largo.", "3·(1,2) = (3,6)"),
    ("Δv (Vector diferencia)", "Distancia y dirección que separa un punto de otro.", "T - P = (5,7) - (2,3) = (3,4)"),
    ("||v|| (Módulo / Magnitud)", "La longitud de la flecha: cuánto mide el vector (Pitágoras).", "||(3,4)|| = 5"),
    ("V_ataque (Vector satelital)", "Dirección del rayo del Cañón Orbital (superpoder).", "(3,4)"),
    ("U_radar (Vector base)", "Eje de referencia sobre el que se proyecta el rayo orbital.", "(1,0) eje horizontal"),
    ("proj_U(V) (Proyección)", "La 'sombra' del vector de ataque sobre el eje del radar.", "proj_(1,0)((3,4)) = (3,0)"),
)

REGLA_DE_ORO = ("Regla de oro: los vectores con P son PUNTOS (dónde estás / dónde cae). "
                "Los vectores con V o U son FLECHAS DE MOVIMIENTO "
                "(cuánto te mueves y hacia dónde).")

# (habilidad, costo, fórmula matemática, concepto pedagógico)
CATALOGO_HABILIDADES = (
    ("Disparo Simple (Suma)", "0", "P_final = P_barco + V_tiro",
     "Suma básica de componentes (x1+x2, y1+y2)."),
    ("Artillería con Viento (Suma múltiple)", "1", "P_final = P_barco + V_tiro + V_viento",
     "Suma múltiple de 3 vectores. Enseña a compensar fuerzas contrarias."),
    ("Torpedo Escalar (Multiplicación)", "2", "P_final = P_barco + (k · u_dir)",
     "Multiplicación de un vector por un escalar (magnificación de alcance)."),
    ("Sónar de Gauss (Módulo)", "1", "d = ||Δv|| = sqrt(Δx² + Δy²)",
     "Módulo del vector diferencia y distancia euclidiana por Pitágoras."),
    ("Proyección Orbital (Superpoder)", "4", "proj_u(v) = [(v·u)/||u||²] · u",
     "SUPERPODER: Producto punto, proyección ortogonal y barrido lineal de sombra."),
)

CONSEJO_VISUAL = ("Consejo: usa el Laboratorio de Vectores del menú para ver estas "
                  "fórmulas DIBUJADAS sobre el plano cartesiano (flechas, "
                  "paralelogramo y sombra de proyección).")
