# app/core/mqtt_client.py

import json
import time
import paho.mqtt.client as mqtt
from collections import defaultdict
from typing import Callable, Dict, Union
import asyncio
from app.core.ws_registry import ws_managers
from app.config.topics import ALL_TOPICS  # o ROOM_TOPICS si necesitas por sala

BROKER_HOST = "localhost"
BROKER_PORT = 1883
MAX_RETRIES = 10
RETRY_DELAY = 5  # segundos entre intentos

global mqtt_client  # Agregado
client = mqtt.Client()

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
    
    await ws_managers[room].broadcast(message)

def on_connect(client, userdata, flags, rc):
    print("✅ Conectado al broker MQTT.")

    for topic in ALL_TOPICS:
        client.subscribe(topic)
        print(f"🔗 Suscrito a: {topic}")
    
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        # value = float(payload["d"]["value"][0])
        
        raw_value = payload["d"]["value"][0]

        if isinstance(raw_value, bool):
            value = raw_value
        elif isinstance(raw_value, (int, float)):
            value = raw_value
        elif isinstance(raw_value, str):
            if raw_value.lower() == "true":
                value = True
            elif raw_value.lower() == "false":
                value = False
            else:
                try:
                    value = float(raw_value)
                except ValueError:
                    print("❌ Valor no es float ni bool válido.")
                    return
        else:
            print("❌ Tipo de valor no reconocido:", type(raw_value))
            return

        
        ts = payload.get("ts")
        topic = msg.topic
        
        # print(f"🔍 Payload: {payload}")
        # print(f"🔍 value: {value}")
        # print(f"🔍 ts: {ts}")
        # print(f"🔍 topic: {topic}")

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

def on_disconnect(client, userdata, rc):
    print("🔌 Desconectado. Reintentando conexión...")
    connect_mqtt_with_retries()

def connect_mqtt_with_retries():
    # client = mqtt.Client()
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client.connect(BROKER_HOST, BROKER_PORT, 60)
            print("✅ Conectado al broker MQTT")
            return client
        except Exception as e:
            print(f"🔁 Intento {attempt}/{MAX_RETRIES} fallido: {e}")
            time.sleep(RETRY_DELAY)
    
    print("❌ No se pudo conectar al broker después de varios intentos.")
    return None

def publish(topic: str, value: str):
    """Publica un mensaje en el broker MQTT."""
    if client:
        print(f"📤 Publicando en {topic}: {value}")
        client.publish(topic, value)
    else:
        print("❌ Cliente MQTT no inicializado.")

def start_mqtt(loop):
    
    global mqtt_loop
    mqtt_loop = loop  # Guardamos el loop principal para usarlo luego

    mqtt_client = connect_mqtt_with_retries()
    if mqtt_client:
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect
        mqtt_client.loop_start()
