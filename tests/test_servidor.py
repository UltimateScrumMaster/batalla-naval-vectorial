"""
=================================================================================
TESTS: test_servidor.py - Pruebas asíncronas para el Servidor WebSocket
=================================================================================
Valida el ciclo de vida del servidor WebSocket:
  - Conexión y evento CONNECTED
  - Inicio de partida con START_GAME y recepción de SESSION_READY
  - Solicitud de PREVIEW de disparo y cálculo correcto
  - Ejecución de disparo y resolución de turno (FIRE_SKILL)
  - Cálculo de laboratorio (CALC_LAB)
=================================================================================
"""

import asyncio
import json
import unittest
import websockets

from juego_naval.servidor.ws_server import ServidorJuegoNaval


class TestServidorWebSocket(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.host = "127.0.0.1"
        self.port = 8789  # Puerto dedicado para tests
        self.servidor = ServidorJuegoNaval(self.host, self.port)
        self.server = await websockets.serve(self.servidor.handler, self.host, self.port)

    async def asyncTearDown(self):
        self.server.close()
        await self.server.wait_closed()

    async def test_conexion_y_bienvenida(self):
        uri = f"ws://{self.host}:{self.port}"
        async with websockets.connect(uri) as ws:
            raw = await ws.recv()
            data = json.loads(raw)
            self.assertEqual(data["type"], "CONNECTED")
            self.assertIn("version", data["payload"])

    async def test_iniciar_partida(self):
        uri = f"ws://{self.host}:{self.port}"
        async with websockets.connect(uri) as ws:
            await ws.recv()  # Consume CONNECTED

            # Enviar START_GAME con semilla fija
            await ws.send(json.dumps({
                "type": "START_GAME",
                "payload": {"semilla": 42}
            }))

            raw_resp = await ws.recv()
            data = json.loads(raw_resp)
            self.assertEqual(data["type"], "SESSION_READY")
            payload = data["payload"]
            self.assertEqual(payload["turno"], 1)
            self.assertEqual(payload["energia"], 2)
            self.assertEqual(payload["tablero_jugador"]["ancho"], 10)
            self.assertEqual(len(payload["tablero_jugador"]["barcos"]), 5)
            self.assertIn("habilidades", payload)

    async def test_preview_disparo(self):
        uri = f"ws://{self.host}:{self.port}"
        async with websockets.connect(uri) as ws:
            await ws.recv()  # Consume CONNECTED

            # Iniciar partida
            await ws.send(json.dumps({"type": "START_GAME", "payload": {"semilla": 100}}))
            await ws.recv()  # Consume SESSION_READY

            # Pedir PREVIEW
            await ws.send(json.dumps({
                "type": "GET_PREVIEW",
                "payload": {
                    "habilidad": "suma",
                    "origen": [2, 3],
                    "vector_v": [3, 2]
                }
            }))

            raw_resp = await ws.recv()
            data = json.loads(raw_resp)
            self.assertEqual(data["type"], "PREVIEW_RESULT")
            self.assertEqual(data["payload"]["impacto"], [5, 5])
            self.assertTrue(data["payload"]["dentro_del_mapa"])

    async def test_preview_orbital(self):
        uri = f"ws://{self.host}:{self.port}"
        async with websockets.connect(uri) as ws:
            await ws.recv()  # Consume CONNECTED
            await ws.send(json.dumps({"type": "START_GAME", "payload": {"semilla": 100}}))
            await ws.recv()  # Consume SESSION_READY

            # Proyección de (3, 4) sobre (1, 0) desde origen (2, 2) -> proy=(3, 0) -> impacto=(5, 2)
            await ws.send(json.dumps({
                "type": "GET_PREVIEW",
                "payload": {
                    "habilidad": "orbital",
                    "origen": [2, 2],
                    "vector_v": [3, 4],
                    "vector_u": [1, 0]
                }
            }))

            raw_resp = await ws.recv()
            data = json.loads(raw_resp)
            self.assertEqual(data["type"], "PREVIEW_RESULT")
            self.assertEqual(data["payload"]["impacto"], [5, 2])
            self.assertTrue(data["payload"]["dentro_del_mapa"])

    async def test_ejecutar_disparo_y_turno(self):
        uri = f"ws://{self.host}:{self.port}"
        async with websockets.connect(uri) as ws:
            await ws.recv()  # Consume CONNECTED

            # Iniciar partida
            await ws.send(json.dumps({"type": "START_GAME", "payload": {"semilla": 100}}))
            raw_ready = await ws.recv()
            data_ready = json.loads(raw_ready)
            emisor = data_ready["payload"]["emisores_disponibles"][0]["pos"]

            # Disparar habilidad suma (gratis en costo)
            await ws.send(json.dumps({
                "type": "FIRE_SKILL",
                "payload": {
                    "habilidad": "suma",
                    "origen": emisor,
                    "vector_v": [1, 1]
                }
            }))

            raw_resp = await ws.recv()
            data = json.loads(raw_resp)
            self.assertEqual(data["type"], "TURN_RESOLVED")
            payload = data["payload"]
            self.assertIsNotNone(payload["ataque_jugador"])
            self.assertIsNotNone(payload["nuevo_estado"])
            # Se ejecutó el turno de la IA también
            self.assertIsNotNone(payload["ataque_ia"])

    async def test_calculo_laboratorio(self):
        uri = f"ws://{self.host}:{self.port}"
        async with websockets.connect(uri) as ws:
            await ws.recv()  # Consume CONNECTED

            await ws.send(json.dumps({
                "type": "CALC_LAB",
                "payload": {
                    "opcion": "suma",
                    "u": [2, 3],
                    "v": [4, 1]
                }
            }))

            raw_resp = await ws.recv()
            data = json.loads(raw_resp)
            self.assertEqual(data["type"], "LAB_RESULT")
            self.assertEqual(data["payload"]["resultado"], [6, 4])
            self.assertEqual(data["payload"]["operacion"], "Suma de Vectores")


if __name__ == "__main__":
    unittest.main()
