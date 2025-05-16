# app/core/mqtt_client.py

import json
import paho.mqtt.client as mqtt
from collections import defaultdict
from typing import Callable, Dict, Union
import asyncio
from app.core.ws_registry import ws_managers
from app.config.topics import ALL_TOPICS  # o ROOM_TOPICS si necesitas por sala

# Estructura para guardar las últimas mediciones por sala y sensor
latest_data: Dict[str, Dict[str, Union[float, int, bool]]] = {
    "room1": {},
    "room2": {},
    "room3": {}
}
subscribers: list[Callable[[dict], None]] = []

async def notify_all_clients(room: str, root: str, control: str, var: str, value: any, ts: str):
    print(f"📤 Enviando update WebSocket a {room} -> {var}: {value}")
    message = {
                "room": room, 
                "root": root, 
                "control": control, 
                "var": var, 
                "value": value,
                "timestamp": ts
            }	
    await ws_managers["room1"].broadcast(message)

def on_connect(client, userdata, flags, rc):
    print("✅ Conectado al broker MQTT.")

    for topic in ALL_TOPICS:
        client.subscribe(topic)
        print(f"🔗 Suscrito a: {topic}")
    
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        value = float(payload["d"]["value"][0])
        ts = payload.get("ts")
        topic = msg.topic
        
        print(f"🔍 Payload: {payload}")
        print(f"🔍 value: {value}")
        print(f"🔍 ts: {ts}")
        print(f"🔍 topic: {topic}")

        # Para topic: weintek/ripening/room1/status/temperature/sensorX
        parts = msg.topic.strip("/").split("/")
        # parts = ['weintek', 'ripening', 'room1', 'status', 'temperature', 'sensor1']
        room = parts[2]         # 'room1'
        root = parts[3]
        control = parts[4]
        var = parts[5]       # 'sensor1'    
        print(f"🔍 parts: {parts}")
    
        # Inicializar nodos del diccionario si no existen
        if room not in latest_data:
            latest_data[room] = {}
        if root not in latest_data[room]:
            latest_data[room][root] = {}
        if control not in latest_data[room][root]:
            latest_data[room][root][control] = {}
        
        if room in latest_data:
            latest_data[room][root][control][var] = {
                "value": value,
                "timestamp": ts
            }
        
        # Usamos el loop guardado en lugar de get_event_loop()
        if mqtt_loop:
            mqtt_loop.call_soon_threadsafe(
                asyncio.create_task,
                notify_all_clients(room, root, control, var, value, ts)
            )
        else:
            print("⚠️ No se encontró event loop principal.")

    except Exception as e:
        print(f"❌ Error procesando mensaje MQTT: {e}")

def start_mqtt(loop):
    global mqtt_loop
    mqtt_loop = loop  # Guardamos el loop principal para usarlo luego

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_start()
