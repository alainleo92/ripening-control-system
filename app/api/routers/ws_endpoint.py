# app/websockets/ws_endpoint.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from app.core.ws_registry import ws_managers
from app.core.mqtt_client import latest_data, mqtt_connected

router = APIRouter()

@router.websocket("/ws/{room}")
#    """
#    Endpoint WebSocket para recibir conexiones del frontend.
#    """
async def websocket_endpoint_room(websocket: WebSocket, room: str):
    try:
        # Validar que la sala exista
        if room not in latest_data:
            await websocket.close(code=1008)
            print(f"❌ Sala {room} no existe")
            return

        manager = ws_managers[room]
        await manager.connect(websocket, room)
        print(f"🟢 Cliente conectado a {room}")

        # Enviar mediciones actuales al conectar
        for root, control_data in latest_data[room].items():
            #print(f"roott: {root}")
            for control, sensors_data in control_data.items():
                #print(f"controll: {control}")
                for var, payload in sensors_data.items():
                   # print(f"valuee: {payload.get('value')}")
                    if not isinstance(payload, dict):
                        print(f"⚠️ Payload mal formado para {var}: {payload}")
                        continue

                    await websocket.send_json({
                        "room": room,
                        "root": root,
                        "control": control,
                        "var": var,
                        "value": payload.get("value"),
                        "timestamp": payload.get("timestamp"),
                        "mqtt_status": mqtt_connected
                    })

        while True:
            # Esperamos datos aunque no los usemos, para mantener la conexión viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"🔴 Cliente desconectado de {room}")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"⚠️ Error inesperado en WebSocket ({room}): {e}")
        manager.disconnect(websocket)

@router.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    return FileResponse("app/static/dashboard.html")





