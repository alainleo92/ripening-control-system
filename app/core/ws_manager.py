# app/core/ws_manager.py

from fastapi import WebSocket
from typing import List

class WebSocketManager:
    """
    Administra las conexiones WebSocket activas.
    Permite conectar, desconectar y enviar datos a todos los clientes.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Acepta una nueva conexión WebSocket y la añade a la lista de conexiones activas.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🟢 Cliente conectado. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        Elimina una conexión WebSocket de la lista de activas.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"🔴 Cliente desconectado. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """
        Envía un mensaje JSON a todos los clientes conectados.
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"⚠️ Error enviando mensaje a un cliente: {e}")
                disconnected.append(connection)
        for ws in disconnected:
            self.disconnect(ws)

ws_manager = WebSocketManager()
