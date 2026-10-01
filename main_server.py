#!/usr/bin/env python3
"""
Entry point para iniciar el servidor WebSocket de Batalla Naval Vectorial.
Permite conectar clientes desacoplados (como el frontend en Godot Engine / C#).
"""

import argparse
import asyncio
from juego_naval.servidor.ws_server import main_servidor

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor WebSocket de Batalla Naval Vectorial")
    parser.add_argument("--host", default="127.0.0.1", help="Host de escucha (por defecto 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Puerto de escucha (por defecto 8765)")
    args = parser.parse_args()

    try:
        asyncio.run(main_servidor(host=args.host, port=args.port))
    except KeyboardInterrupt:
        print("\n[BNV-WS] Servidor detenido.")
