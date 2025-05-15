# app/core/mqtt_client.py

import json
import paho.mqtt.client as mqtt
from collections import defaultdict
from typing import Callable
import asyncio
from app.core.ws_manager import ws_manager  # importa correctamente según tu estructura

TOPICS = [
    "weintek/ripening/room1/status/temperature/sensor1",
    "weintek/ripening/room1/status/temperature/sensor2",
    "weintek/ripening/room1/status/temperature/sensor3",
    "weintek/ripening/room1/status/temperature/sensor4",
    "weintek/ripening/room1/status/temperature/sensor5",
    "weintek/ripening/room1/status/temperature/change_over"
    "weintek/ripening/room1/status/rh/reg_rh",
    "weintek/ripening/room1/status/rh/sensor1",
    "weintek/ripening/room1/status/rh/sensor2",
    "weintek/ripening/room1/status/rh/sensor3",
    "weintek/ripening/room1/status/rh/sensor4",
    "weintek/ripening/room1/status/rh/sensor5",
    "weintek/ripening/room1/status/rh/change_over"
]

# Estructura para guardar las últimas mediciones por sala y sensor
latest_temperatures = defaultdict(dict)
latest_data = {}
subscribers: list[Callable[[dict], None]] = []

async def notify_all_clients(room: str, root: str, control: str, var: str, value: float):
    message = {
                "room": room, 
                "root": root, 
                "control": control, 
                "var": var, 
                "value": value}
    await ws_manager.broadcast(message)

def on_connect(client, userdata, flags, rc):
    print("✅ Conectado al broker MQTT.")
    for topic in TOPICS:
        client.subscribe(topic)
        print(f"🔗 Suscrito a: {topic}")
    
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"🔍 Payload: {payload}")
        value = float(payload["d"]["value"][0])
        print(f"🔍 value: {value}")

        # Para topic: weintek/ripening/room1/status/temperature/sensorX
        parts = msg.topic.strip("/").split("/")
        # parts = ['weintek', 'ripening', 'room1', 'status', 'temperature', 'sensor1']
        room = parts[2]         # 'room1'
        root = parts[3]
        control = parts[4]
        var = parts[5]       # 'sensor1'    
        print(f"🔍 parts: {parts}")
    
        # latest_temperatures[room][var] = value

        # Inicializar nodos del diccionario si no existen
        if room not in latest_data:
            latest_data[room] = {}
        if root not in latest_data[room]:
            latest_data[room][root] = {}
        if control not in latest_data[room][root]:
            latest_data[room][root][control] = {}
        
        latest_data[room][root][control][var] = {
                        "value": value[0] if isinstance(value, list) else value,
                        }

        # print(f"🔍 latest_temperatures {room}/{root}/{control}/{var}: {latest_temperatures[room][var]}")
        
        # Usamos el loop guardado en lugar de get_event_loop()
        if mqtt_loop:
            mqtt_loop.call_soon_threadsafe(
                asyncio.create_task,
                notify_all_clients(room, root, control, var, value)
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
