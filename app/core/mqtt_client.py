# app/core/mqtt_client.py

import json
import paho.mqtt.client as mqtt
from collections import defaultdict
from typing import Callable, Dict, Union
import asyncio
from app.core.ws_manager import ws_manager  # importa correctamente según tu estructura

TOPICS = [
    "weintek/ripening/room1/status/temperature/reg_temp",
    "weintek/ripening/room1/status/temperature/sensor1",
    "weintek/ripening/room1/status/temperature/sensor2",
    "weintek/ripening/room1/status/temperature/sensor3",
    "weintek/ripening/room1/status/temperature/sensor4",
    "weintek/ripening/room1/status/temperature/sensor5",
    "weintek/ripening/room1/status/temperature/change_over",
    "weintek/ripening/room1/status/temperature/cool_valve_status",
    "weintek/ripening/room1/status/temperature/heat_valve_status",
    "weintek/ripening/room1/status/temperature/disch_temp",

    "weintek/ripening/room1/alarms/temperature/sensor1",
    "weintek/ripening/room1/alarms/temperature/sensor2",
    "weintek/ripening/room1/alarms/temperature/sensor3",
    "weintek/ripening/room1/alarms/temperature/sensor4",
    "weintek/ripening/room1/alarms/temperature/sensor5",

    "weintek/ripening/room1/status/rh/reg_rh",
    "weintek/ripening/room1/status/rh/sensor1",
    "weintek/ripening/room1/status/rh/sensor2",
    "weintek/ripening/room1/status/rh/sensor3",
    "weintek/ripening/room1/status/rh/sensor4",
    "weintek/ripening/room1/status/rh/sensor5",
    "weintek/ripening/room1/status/rh/change_over",
    "weintek/ripening/room1/status/rh/dh_valve_status",
    "weintek/ripening/room1/status/rh/hm_valve_status",

    "weintek/ripening/room1/alarms/rh/sensor1",
    "weintek/ripening/room1/alarms/rh/sensor2",
    "weintek/ripening/room1/alarms/rh/sensor3",
    "weintek/ripening/room1/alarms/rh/sensor4",
    "weintek/ripening/room1/alarms/rh/sensor5",

    "weintek/ripening/room1/param/temperature/target",
    "weintek/ripening/room1/param/temperature/differential",
    "weintek/ripening/room1/param/temperature/k_change_over",
    "weintek/ripening/room1/param/temperature/cool_nz",
    "weintek/ripening/room1/param/temperature/heat_nz",
    "weintek/ripening/room1/param/temperature/ovd_cool",
    "weintek/ripening/room1/param/temperature/ovd_cool_percent",
    "weintek/ripening/room1/param/temperature/ovd_heat",
    "weintek/ripening/room1/param/temperature/ovd_heat_percent",
    "weintek/ripening/room1/param/temperature/chover_delay",
    "weintek/ripening/room1/param/temperature/monitor1",
    "weintek/ripening/room1/param/temperature/monitor2",
    "weintek/ripening/room1/param/temperature/monitor3",
    "weintek/ripening/room1/param/temperature/monitor4",
    "weintek/ripening/room1/param/temperature/monitor5",
    "weintek/ripening/room1/param/temperature/control_sensor",
    "weintek/ripening/room1/param/temperature/enable_control",
    "weintek/ripening/room1/param/temperature/humidity_mode",
    "weintek/ripening/room1/param/temperature/heat_mode",
    "weintek/ripening/room1/param/temperature/vent_mode",
    "weintek/ripening/room1/param/temperature/dich_monitor",

    "weintek/ripening/room1/param/rh/target",
    "weintek/ripening/room1/param/rh/differential",
    "weintek/ripening/room1/param/rh/k_change_over",
    "weintek/ripening/room1/param/rh/dh_nz",
    "weintek/ripening/room1/param/rh/hm_nz",
    "weintek/ripening/room1/param/rh/ovd_dh",
    "weintek/ripening/room1/param/rh/ovd_dh_percent",
    "weintek/ripening/room1/param/rh/ovd_hm",
    "weintek/ripening/room1/param/rh/ovd_hm_percent",
    "weintek/ripening/room1/param/rh/chover_delay",
    "weintek/ripening/room1/param/rh/monitor1",
    "weintek/ripening/room1/param/rh/monitor2",
    "weintek/ripening/room1/param/rh/monitor3",
    "weintek/ripening/room1/param/rh/monitor4",
    "weintek/ripening/room1/param/rh/monitor5",
    "weintek/ripening/room1/param/rh/control_sensor",

    "weintek/ripening/room1/param/gas/inyec_time",
    "weintek/ripening/room1/param/gas/gas_on_off",
    "weintek/ripening/room1/param/gas/ovd_gas",
    "weintek/ripening/room1/param/vent/vent_interval",
    "weintek/ripening/room1/param/vent/vent_delay",
    "weintek/ripening/room1/param/vent/ovd_vent",
]

# Estructura para guardar las últimas mediciones por sala y sensor
latest_data: Dict[str, Dict[str, Union[float, int, bool]]] = {}
subscribers: list[Callable[[dict], None]] = []

async def notify_all_clients(room: str, root: str, control: str, var: str, value: any, ts: str):
    message = {
                "room": room, 
                "root": root, 
                "control": control, 
                "var": var, 
                "value": value,
                "timestamp": ts
            }	
    await ws_manager.broadcast(message)

def on_connect(client, userdata, flags, rc):
    print("✅ Conectado al broker MQTT.")
    for topic in TOPICS:
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
        
        latest_data[room][root][control][var] = {
                        "value": value[0] if isinstance(value, list) else value,
                        "timestamp": ts,
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
