# app/core/ws_manager.py

from fastapi import WebSocket
from typing import Dict, List
from collections import defaultdict

class WebSocketManager:
    """
    Administra las conexiones WebSocket activas.
    Permite conectar, desconectar y enviar datos a todos los clientes.
    """

    def __init__(self):
        # Agrupa clientes por room: "room1", "room2", ...
        self.connections: Dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, room: str):
        """
        Acepta una nueva conexión WebSocket y la añade a la lista de conexiones activas.
        """
        await websocket.accept()
        self.connections[room].append(websocket)
        print(f"🟢 Cliente conectado a {room}. Total: {len(self.connections[room])}")

    def disconnect(self, websocket: WebSocket):
        """
        Elimina una conexión WebSocket de la lista de activas.
        """
        for room, ws_list in self.connections.items():
            if websocket in ws_list:
                ws_list.remove(websocket)
                print(f"🔴 Cliente desconectado de {room}. Total: {len(ws_list)}")
                break

    async def broadcast(self, message: dict):
        """
        Envía un mensaje JSON a todos los clientes conectados.
        """
        room = message.get("room")
        if not room:
            print("⚠️ Mensaje sin campo 'room'. No se envía.")
            return
        
        disconnected = []
        
        for connection in self.connections.get(room, []):
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"⚠️ Error enviando mensaje a un cliente de {room}: {e}")
                disconnected.append(connection)

        for ws in disconnected:
            self.disconnect(ws)

ws_manager = WebSocketManager()
