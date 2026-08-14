"""
=============================================================================
MÓDULO: habilidades.py - Habilidades de Combate y Operaciones Vectoriales
=============================================================================
Cada habilidad del juego implementa una operación del álgebra lineal y genera
un informe pedagógico con el desglose matemático paso a paso (debugging visual)
para que los estudiantes comprendan la matemática detrás del juego.
=============================================================================
"""

from __future__ import annotations
import math
from typing import Dict, Any, List, Tuple, Optional
from vector2d import Vector2D
from tablero import Tablero, ResultadoDisparo


class HabilidadVectorial:
    """Clase base para las habilidades de combate vectorial"""
    nombre: str = "Habilidad"
    descripcion: str = "Descripción"
    icono: str = "+"
    energia_costo: int = 0


class DisparoBasicoSuma(HabilidadVectorial):
    """
    Habilidad: Disparo Estándar por Suma de Vectores
    Fórmula: P_impacto = P_origen + v_disparo
    Concepto: Suma de componentes (x1 + x2, y1 + y2)
    """
    nombre = "Disparo Vectorial (Suma)"
    descripcion = "Suma el vector de disparo a la posición de tu barco para calcular el impacto."
    icono = "+"
    energia_costo = 0  # Habilidad básica ilimitada

    @staticmethod
    def ejecutar(origen: Vector2D, vector_tiro: Vector2D, tablero_enemigo: Tablero) -> Dict[str, Any]:
        destino = origen + vector_tiro
        resultado_tablero = tablero_enemigo.procesar_disparo(destino)
        explicacion = origen.explicar_suma(vector_tiro, etiqueta_a="Pos_Barco", etiqueta_b="Vector_Tiro")

        return {
            "habilidad": "Disparo Vectorial (Suma)",
            "origen": origen,
            "vector_accion": vector_tiro,
            "destino": destino,
            "resultado_tablero": [resultado_tablero],
            "explicacion": explicacion
        }


class DisparoConViento(HabilidadVectorial):
    """
    Habilidad: Artillería Balística con Viento/Corriente
    Fórmula: P_impacto = P_origen + v_disparo + v_viento
    Concepto: Suma múltiple de vectores y compensación vectorial
    """
    nombre = "Artillería con Viento (Suma Múltiple)"
    descripcion = "Disparo afectado por la corriente marina/viento. Requiere compensar los vectores."
    icono = "≈"
    energia_costo = 1

    @staticmethod
    def ejecutar(origen: Vector2D, vector_tiro: Vector2D, viento: Vector2D, tablero_enemigo: Tablero) -> Dict[str, Any]:
        # Suma en dos etapas: primero tiro, luego desplazamiento por viento
        tiro_sin_viento = origen + vector_tiro
        destino_final = tiro_sin_viento + viento

        resultado_tablero = tablero_enemigo.procesar_disparo(destino_final)

        pasos = [
            f"1. Posición de lanzamiento = {origen}",
            f"2. Vector de tiro aplicado = {vector_tiro}  -->  Punto sin viento = {origen} + {vector_tiro} = {tiro_sin_viento}",
            f"3. Vector de viento/corriente = {viento}",
            f"4. Suma total de fuerzas: P_final = ({origen.x} + {vector_tiro.x} + {viento.x}, {origen.y} + {vector_tiro.y} + {viento.y})",
            f"5. Coordenada de impacto real = ({destino_final.x}, {destino_final.y})"
        ]

        explicacion = {
            "operacion": "Suma Múltiple con Viento (Compensación de Fuerzas)",
            "formula": "P_final = P_origen + V_tiro + V_viento",
            "vectores": {"Origen": str(origen), "Tiro": str(vector_tiro), "Viento": str(viento)},
            "pasos": pasos,
            "resultado": destino_final
        }

        return {
            "habilidad": "Artillería con Viento",
            "origen": origen,
            "vector_accion": vector_tiro,
            "viento": viento,
            "destino": destino_final,
            "resultado_tablero": [resultado_tablero],
            "explicacion": explicacion
        }


class TorpedoEscalar(HabilidadVectorial):
    """
    Habilidad: Torpedo Multiplicador Escalar
    Fórmula: P_impacto = P_origen + (k * u_direccion)
    Concepto: Multiplicación por escalar k * v = (k*x, k*y)
    """
    nombre = "Torpedo Escalar (Multiplicación k * v)"
    descripcion = "Elige una dirección base y multiplícala por un escalar k de propulsión."
    icono = "×"
    energia_costo = 2

    @staticmethod
    def ejecutar(origen: Vector2D, direccion: Vector2D, escalar_k: float | int, tablero_enemigo: Tablero) -> Dict[str, Any]:
        vector_escalado = direccion * escalar_k
        destino = origen + vector_escalado
        resultado_tablero = tablero_enemigo.procesar_disparo(destino)

        explicacion_escalar = direccion.explicar_escalar(escalar_k, etiqueta="Dir_Base")
        explicacion_suma = origen.explicar_suma(vector_escalado, etiqueta_a="Pos_Barco", etiqueta_b="Vector_Escalado")

        pasos = [
            f"1. Dirección unitaria o base: {direccion}",
            f"2. Multiplicador de potencia (escalar k) = {escalar_k}",
            f"3. Vector propulsado k * u = ({escalar_k} * {direccion.x}, {escalar_k} * {direccion.y}) = {vector_escalado}",
            f"4. Suma a la posición de origen: {origen} + {vector_escalado} = {destino}"
        ]

        explicacion = {
            "operacion": "Multiplicación Escalar + Desplazamiento",
            "formula": "P_impacto = P_origen + (k · Dir_base)",
            "valores": {"k": escalar_k, "Dirección": str(direccion), "Vector resultante": str(vector_escalado)},
            "pasos": pasos,
            "resultado": destino
        }

        return {
            "habilidad": "Torpedo Escalar",
            "origen": origen,
            "direccion": direccion,
            "escalar": escalar_k,
            "destino": destino,
            "resultado_tablero": [resultado_tablero],
            "explicacion": explicacion
        }


class SonarDistanciaEuclidiana(HabilidadVectorial):
    """
    Habilidad: Sónar Acústico de Gauss
    Fórmula: d = ||P_enemigo - P_sonar|| = sqrt((x2 - x1)^2 + (y2 - y1)^2)
    Concepto: Módulo, distancia euclidiana y Teorema de Pitágoras
    """
    nombre = "Sónar de Gauss (Módulo / Pitágoras)"
    descripcion = "Calcula la distancia euclidiana exacta al barco enemigo más cercano."
    icono = "√"
    energia_costo = 1

    @staticmethod
    def ejecutar(origen_sonar: Vector2D, tablero_enemigo: Tablero) -> Dict[str, Any]:
        info_cercano = tablero_enemigo.barco_mas_cercano(origen_sonar)

        if info_cercano is None:
            # Todos los barcos están hundidos o no hay
            return {
                "habilidad": "Sónar de Gauss",
                "origen": origen_sonar,
                "distancia": 0,
                "mensaje": " El sónar no detectó señales vivas (todos los navíos fueron neutralizados).",
                "explicacion": {"operacion": "Sónar", "pasos": ["No hay barcos enemigos a flote."]}
            }

        barco, dist_exacta = info_cercano
        # Buscar la celda viva más cercana para el cálculo matemático
        celda_mas_cercana = min(
            (c for c in barco.celdas if c.a_tupla_grilla() not in barco.impactos),
            key=lambda c: origen_sonar.distancia_a(c)
        )

        explicacion = origen_sonar.explicar_distancia(celda_mas_cercana, etiqueta_a="Emisor_Sónar", etiqueta_b="Eco_Enemigo")

        # Registrar el ping en el tablero
        tablero_enemigo.historial_sonar.append({"centro": origen_sonar, "distancia": dist_exacta})

        mensaje = (
            f"Eco detectado: Hay un navío hostil a exactamente {dist_exacta:.2f} unidades de distancia! "
            f"(Se encuentra en la circunferencia de radio R = {dist_exacta:.2f} centrada en {origen_sonar})"
        )

        return {
            "habilidad": "Sónar de Gauss",
            "origen": origen_sonar,
            "distancia": dist_exacta,
            "mensaje": mensaje,
            "explicacion": explicacion
        }


class CanonProyeccionOrbital(HabilidadVectorial):
    """
    Superpoder: Cañón de Proyección Vectorial Ortogonal
    Fórmula: proj_u(v) = [ (v · u) / ||u||^2 ] * u
    Concepto: Producto punto, magnitud al cuadrado y proyección de vectores.
    Efecto: Proyecta el ataque sobre una recta base y barre todas las casillas atravesadas.
    """
    nombre = "Cañón de Proyección Orbital (Superpoder)"
    descripcion = "Proyecta el vector de ataque sobre un vector base y barre toda la línea de sombra."
    icono = "⇀"
    energia_costo = 4

    @staticmethod
    def ejecutar(origen: Vector2D, vector_v: Vector2D, vector_u_base: Vector2D, tablero_enemigo: Tablero) -> Dict[str, Any]:
        if vector_u_base.es_cero():
            raise ValueError("El vector base para la proyección no puede ser nulo (0,0).")

        # 1. Calcular proyección matemática
        proyeccion = vector_v.proyeccion_sobre(vector_u_base)
        explicacion = vector_v.explicar_proyeccion(vector_u_base, etiqueta_v="Vector_Ataque", etiqueta_u="Eje_Radar")

        # 2. Generar todos los puntos discretos en la línea de la proyección desde el origen
        # Parametrización: P(t) = Origen + t * proyeccion con t en [0, 1]
        pasos_trazado = max(int(proyeccion.magnitud() * 2), 2)
        puntos_afectados: List[Vector2D] = []
        tuplas_afectadas: Set[Tuple[int, int]] = set()

        for step in range(pasos_trazado + 1):
            t = step / pasos_trazado
            pt = origen + (t * proyeccion)
            tupla = pt.a_tupla_grilla()
            if tupla not in tuplas_afectadas:
                tuplas_afectadas.add(tupla)
                puntos_afectados.append(Vector2D(tupla[0], tupla[1]))

        # Registrar rastro visual en el tablero
        tablero_enemigo.rastro_proyeccion.update(tuplas_afectadas)

        # 3. Procesar disparos sobre cada una de las casillas barridas por el rayo orbital
        resultados_tablero: List[ResultadoDisparo] = []
        for punto in puntos_afectados:
            res = tablero_enemigo.procesar_disparo(punto)
            resultados_tablero.append(res)

        aciertos = sum(1 for r in resultados_tablero if r.impacto and not r.repetido)
        hundidos = sum(1 for r in resultados_tablero if r.hundido)

        mensaje = (
            f"Rayo Orbital ejecutado. Proyección {proyeccion} barre {len(puntos_afectados)} casillas. "
            f"Impactos directos: {aciertos} | Barcos hundidos: {hundidos}."
        )

        return {
            "habilidad": "Cañón de Proyección Orbital",
            "origen": origen,
            "vector_v": vector_v,
            "vector_u": vector_u_base,
            "proyeccion": proyeccion,
            "puntos_barridos": puntos_afectados,
            "resultado_tablero": resultados_tablero,
            "mensaje": mensaje,
            "explicacion": explicacion
        }
