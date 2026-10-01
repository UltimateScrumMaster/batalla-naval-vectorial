"""
=================================================================================
MÓDULO: juego_naval/servidor/ws_server.py - Servidor WebSocket para Batalla Naval
=================================================================================
Servidor asíncrono WebSocket (vía asyncio + websockets) que actúa como backend
para clientes desacoplados (como Godot Engine en C#, clientes Web, etc.).

Maneja:
  * Creación y gestión de sesiones de partida (SesionBatalla).
  * Serialización de estado del tablero y eventos en formato JSON estándar.
  * Cálculo de vistas previas de disparo en tiempo real.
  * Ejecución de habilidades y resolución de turnos de la IA con explicaciones
    matemáticas paso a paso.
=================================================================================
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Set

import websockets
from websockets.server import WebSocketServerProtocol

from juego_naval.dominio.vector2d import Vector2D
from juego_naval.dominio.tablero import Tablero
from juego_naval.logica.sesion import (
    SesionBatalla,
    EstadoBatalla,
    COSTOS_HABILIDAD,
    NOMBRES_HABILIDAD,
)
from juego_naval.logica.laboratorio import (
    calcular_preview_disparo,
    limitar_impacto,
    limite_escalar,
    calcular_resultado_laboratorio,
)

logger = logging.getLogger("BNV_Server")


# =============================================================================
# SERIALIZACIÓN A DICCIONARIOS JSON-FRIENDLY
# =============================================================================

class BNVJsonEncoder(json.JSONEncoder):
    """Encoder JSON que serializa Vector2D, sets y objetos internos."""
    def default(self, o: Any) -> Any:
        if isinstance(o, Vector2D):
            return [int(o.x), int(o.y)]
        if isinstance(o, set):
            return sorted(list(o))
        if hasattr(o, "__dict__"):
            return o.__dict__
        return super().default(o)


def vector_a_lista(v: Optional[Vector2D]) -> list[int]:
    if v is None:
        return [0, 0]
    return [int(v.x), int(v.y)]


def tablero_a_dict(tablero: Tablero, revelar_todo: bool = False) -> Dict[str, Any]:
    """Serializa un Tablero a un diccionario listo para JSON."""
    barcos_data = []
    for b in tablero.barcos:
        esta_hundido = b.esta_hundido()
        celdas = []
        for pos in b.celdas:
            impactada = (int(pos.x), int(pos.y)) in b.impactos
            if tablero.es_oculto and not revelar_todo and not impactada and not esta_hundido:
                continue
            celdas.append({
                "x": int(pos.x),
                "y": int(pos.y),
                "impactada": impactada
            })

        barcos_data.append({
            "nombre": b.nombre,
            "tamano": b.tamano,
            "icono": b.icono,
            "hundido": esta_hundido,
            "celdas": celdas,
            "origen": vector_a_lista(b.origen) if (not tablero.es_oculto or revelar_todo or esta_hundido) else None,
            "direccion": vector_a_lista(b.direccion) if (not tablero.es_oculto or revelar_todo or esta_hundido) else None,
        })

    return {
        "ancho": tablero.ancho,
        "alto": tablero.alto,
        "es_oculto": tablero.es_oculto,
        "titulo": tablero.titulo,
        "barcos": barcos_data,
        "disparos_agua": [list(pt) for pt in sorted(tablero.disparos_agua)],
        "disparos_acierto": [list(pt) for pt in sorted(tablero.disparos_acierto)],
        "historial_sonar": tablero.historial_sonar,
        "rastro_proyeccion": [list(pt) for pt in sorted(tablero.rastro_proyeccion)],
        "marcas_temporales": [{"pos": list(k), "simbolo": v[0], "estilo": v[1]}
                              for k, v in tablero.marcas_temporales.items()]
    }


def sesion_a_dict(sesion: SesionBatalla) -> Dict[str, Any]:
    """Serializa el estado completo de una SesionBatalla."""
    emisores_disponibles = []
    for b in sesion.tablero_jugador.barcos:
        if not b.esta_hundido():
            for pos in b.celdas:
                tupla = (int(pos.x), int(pos.y))
                if tupla not in b.impactos:
                    emisores_disponibles.append({
                        "barco": b.nombre,
                        "pos": [int(pos.x), int(pos.y)]
                    })

    return {
        "turno": sesion.turno,
        "energia": sesion.energia_jugador,
        "energia_max": 6,
        "viento": vector_a_lista(sesion.viento),
        "estado": sesion.estado.name,
        "emisores_disponibles": emisores_disponibles,
        "habilidades": {
            clave: {
                "nombre": NOMBRES_HABILIDAD[clave],
                "costo": COSTOS_HABILIDAD[clave]
            }
            for clave in COSTOS_HABILIDAD
        },
        "tablero_jugador": tablero_a_dict(sesion.tablero_jugador, revelar_todo=True),
        "tablero_enemigo": tablero_a_dict(sesion.tablero_enemigo, revelar_todo=False),
    }


# =============================================================================
# MANEJADOR DEL SERVIDOR WEBSOCKET
# =============================================================================

class ServidorJuegoNaval:
    """Gestiona conexiones de clientes y el estado de sus partidas."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.sesiones: Dict[WebSocketServerProtocol, SesionBatalla] = {}
        self.clientes_conectados: Set[WebSocketServerProtocol] = set()

    async def iniciar_partida(self, ws: WebSocketServerProtocol, payload: Dict[str, Any]) -> None:
        semilla = payload.get("semilla")
        sesion = SesionBatalla(semilla=semilla)
        self.sesiones[ws] = sesion
        logger.info(f"[{ws.remote_address}] Nueva partida iniciada.")
        await self.enviar_evento(ws, "SESSION_READY", sesion_a_dict(sesion))

    async def manejar_preview(self, ws: WebSocketServerProtocol, payload: Dict[str, Any]) -> None:
        sesion = self.sesiones.get(ws)
        if not sesion:
            await self.enviar_error(ws, "No hay una partida activa. Envía START_GAME primero.")
            return

        skill = payload.get("habilidad", "suma").lower()
        ox, oy = payload.get("origen", [0, 0])
        vx, vy = payload.get("vector_v", [0, 0])
        ux, uy = payload.get("vector_u", [1, 0])
        k = payload.get("k", 1)

        origen = Vector2D(ox, oy)
        vec_v = Vector2D(vx, vy)
        vec_u = Vector2D(ux, uy)

        if skill == "viento":
            v_recortado = limitar_impacto(origen, vec_v, viento=sesion.viento)
            impacto = origen + v_recortado + sesion.viento
        elif skill == "torpedo":
            k_tope = limite_escalar(origen, vec_u)
            k_efectivo = max(0, min(k, k_tope))
            impacto = origen + (k_efectivo * vec_u)
            v_recortado = vec_u
        elif skill == "orbital":
            impacto = origen + (vec_v.proyeccion_sobre(vec_u) if not vec_u.es_cero() else Vector2D(0, 0))
            v_recortado = vec_v
        elif skill == "sonar":
            impacto = origen
            v_recortado = Vector2D(0, 0)
        else:  # suma
            v_recortado = limitar_impacto(origen, vec_v)
            impacto = origen + v_recortado

        dentro = (0 <= impacto.x < 10) and (0 <= impacto.y < 10)

        res_json = {
            "skill": skill,
            "origen": [int(origen.x), int(origen.y)],
            "impacto": [int(impacto.x), int(impacto.y)],
            "dentro_del_mapa": dentro,
            "vector_recortado": [int(v_recortado.x), int(v_recortado.y)],
        }
        await self.enviar_evento(ws, "PREVIEW_RESULT", res_json)

    async def manejar_ataque(self, ws: WebSocketServerProtocol, payload: Dict[str, Any]) -> None:
        sesion = self.sesiones.get(ws)
        if not sesion:
            await self.enviar_error(ws, "No hay partida activa.")
            return

        if sesion.estado != EstadoBatalla.TURNO_JUGADOR:
            await self.enviar_error(ws, f"No es tu turno. Estado actual: {sesion.estado.name}")
            return

        skill = payload.get("habilidad", "suma")
        ox, oy = payload.get("origen", [0, 0])
        vx, vy = payload.get("vector_v", [0, 0])
        ux, uy = payload.get("vector_u", [1, 0])
        k = payload.get("k", 1)

        origen = Vector2D(ox, oy)
        vec_v = Vector2D(vx, vy)
        vec_u = Vector2D(ux, uy)

        res_jugador, error = sesion.ejecutar_ataque_jugador(
            skill=skill,
            origen=origen,
            vector_a=vec_v,
            vector_b=vec_u,
            escalar_k=k
        )

        if error:
            await self.enviar_evento(ws, "ACTION_REJECTED", {"error": error})
            return

        turno_data = {
            "ataque_jugador": {
                "habilidad": skill,
                "resultado": res_jugador,
            },
            "ataque_ia": None,
            "nuevo_estado": sesion_a_dict(sesion)
        }

        if sesion.estado == EstadoBatalla.TURNO_JUGADOR:
            res_ia = sesion.ejecutar_turno_ia()
            if sesion.estado == EstadoBatalla.TURNO_JUGADOR:
                sesion.comenzar_turno_jugador()

            turno_data["ataque_ia"] = res_ia
            turno_data["nuevo_estado"] = sesion_a_dict(sesion)

        await self.enviar_evento(ws, "TURN_RESOLVED", turno_data)

    async def manejar_laboratorio(self, ws: WebSocketServerProtocol, payload: Dict[str, Any]) -> None:
        opcion = payload.get("opcion", "suma")
        ux, uy = payload.get("u", [2, 3])
        vx, vy = payload.get("v", [3, 2])
        k = payload.get("k", 2.0)

        u = Vector2D(ux, uy)
        v = Vector2D(vx, vy)

        calc = calcular_resultado_laboratorio(opcion, u, v, k)
        res_obj = {
            "opcion": calc.get("opcion"),
            "tipo": calc.get("tipo"),
            "operacion": calc.get("operacion"),
            "formula": calc.get("formula"),
            "pasos": calc.get("pasos"),
            "resultado": (vector_a_lista(calc.get("resultado"))
                          if isinstance(calc.get("resultado"), Vector2D)
                          else calc.get("resultado")),
            "error": calc.get("error", False)
        }
        await self.enviar_evento(ws, "LAB_RESULT", res_obj)

    async def enviar_evento(self, ws: WebSocketServerProtocol, tipo: str, payload: Any) -> None:
        mensaje = json.dumps({"type": tipo, "payload": payload}, cls=BNVJsonEncoder)
        await ws.send(mensaje)

    async def enviar_error(self, ws: WebSocketServerProtocol, mensaje: str) -> None:
        await self.enviar_evento(ws, "ERROR", {"mensaje": mensaje})

    async def handler(self, ws: WebSocketServerProtocol) -> None:
        self.clientes_conectados.add(ws)
        logger.info(f"Cliente conectado desde {ws.remote_address}")
        try:
            await self.enviar_evento(ws, "CONNECTED", {
                "mensaje": "Conectado al servidor de Batalla Naval Vectorial",
                "version": "2.7.0-hybrid-ws"
            })

            async for raw_msg in ws:
                try:
                    data = json.loads(raw_msg)
                    msg_type = data.get("type", "")
                    payload = data.get("payload", {})

                    if msg_type == "START_GAME":
                        await self.iniciar_partida(ws, payload)
                    elif msg_type == "GET_PREVIEW":
                        await self.manejar_preview(ws, payload)
                    elif msg_type == "FIRE_SKILL":
                        await self.manejar_ataque(ws, payload)
                    elif msg_type == "CALC_LAB":
                        await self.manejar_laboratorio(ws, payload)
                    elif msg_type == "GET_STATE":
                        sesion = self.sesiones.get(ws)
                        if sesion:
                            await self.enviar_evento(ws, "STATE_UPDATE", sesion_a_dict(sesion))
                        else:
                            await self.enviar_error(ws, "No hay sesión activa.")
                    else:
                        await self.enviar_error(ws, f"Tipo de mensaje desconocido: '{msg_type}'")

                except json.JSONDecodeError:
                    await self.enviar_error(ws, "Mensaje JSON inválido.")
                except Exception as e:
                    logger.exception(f"Error procesando mensaje: {e}")
                    await self.enviar_error(ws, f"Error interno del servidor: {str(e)}")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Cliente {ws.remote_address} desconectado.")
        finally:
            self.clientes_conectados.discard(ws)
            if ws in self.sesiones:
                del self.sesiones[ws]


async def main_servidor(host: str = "127.0.0.1", port: int = 8765) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [BNV-WS] %(message)s")
    servidor = ServidorJuegoNaval(host=host, port=port)
    logger.info(f"Iniciando Servidor WebSocket de Batalla Naval Vectorial en ws://{host}:{port}...")
    async with websockets.serve(servidor.handler, host, port):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main_servidor())
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
