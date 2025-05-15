# app/websockets/ws_endpoint.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.ws_manager import ws_manager
from app.core.mqtt_client import latest_temperatures

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket para recibir conexiones del frontend.
    """
    await ws_manager.connect(websocket)
    print("🟢 Cliente WebSocket conectado")
    try:
        # Enviar las mediciones actuales al conectarse
        for room, sensors in latest_temperatures.items():
            for sensor, value in sensors.items():
                await websocket.send_json({
                    "room": room,
                    "name": sensor,
                    "value": value
                })

        while True:
            # Esperamos datos aunque no los usemos, para mantener la conexión viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"⚠️ Error inesperado en WebSocket: {e}")
        ws_manager.disconnect(websocket)
