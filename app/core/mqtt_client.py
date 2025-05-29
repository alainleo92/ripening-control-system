# app/core/mqtt_client.py

import json
import time
import paho.mqtt.client as mqtt
from typing import Callable, Dict, Union
import asyncio
from app.core.ws_registry import ws_managers
from app.config.topics import ALL_TOPICS  # o ROOM_TOPICS si necesitas por sala
from app.api.services.mqtt_services import PARAMS_TO_CONVERT, celsius_to_fahrenheit, ROOT_TO_CONVERT, parse_value, parse_topic_and_value, initialize_and_update_latest_data, get_or_create_room_id
from app.config.mqtt import BROKER_HOST, BROKER_PORT, MAX_RETRIES, RETRY_DELAY 
from app.db.init_db import SessionLocal  # tu sessionmaker
from datetime import datetime
import uuid
from app.api.schemas.models import Measurement

global mqtt_client  # Agregado
client = mqtt.Client()
mqtt_connected = False
main_event_loop = None

# Estructura para guardar las últimas mediciones por sala y sensor
latest_data: Dict[str, Dict[str, Union[float, int, bool]]] = {
    "room1": {},
    "room2": {},
    "room3": {}
}
subscribers: list[Callable[[dict], None]] = []

async def notify_all_clients(room: str, root: str, control: str, var: str, value: any, ts: str, mqtt_connected: bool):
    #print(f"📤 Enviando update WebSocket a {room} -> {var}: {value}")
    
    message = {
                "room": room, 
                "root": root, 
                "control": control, 
                "var": var, 
                "value": value,
                "timestamp": ts,
                "mqtt_status": mqtt_connected
            }	
    
    await ws_managers[room].broadcast(message)

def on_connect(client, userdata, flags, rc):
    print("✅ Conectado al broker MQTT.")
    mqtt_connected = True

    for topic in ALL_TOPICS:
        client.subscribe(topic)
        #print(f"🔗 Suscrito a: {topic}")
    
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        
        raw_value, room, root, control, var, ts, topic = parse_topic_and_value(payload, msg)
        # print(f"🔍 raw_value: {raw_value}, room: {room}, root: {root}, control: {control}, var: {var}")
        value = parse_value(raw_value)
        
        if control == "temperature" and var in PARAMS_TO_CONVERT and root in ROOT_TO_CONVERT:
                value = celsius_to_fahrenheit(value)
                # print(f"🔍 value: {value}")

        # Inicializar nodos del diccionario si no existen
        initialize_and_update_latest_data(latest_data, room, root, control, var, value, ts)
        
        # Usamos el loop guardado en lugar de get_event_loop()
        if mqtt_loop:
            mqtt_loop.call_soon_threadsafe(
                asyncio.create_task,
                notify_all_clients(room, root, control, var, value, ts, mqtt_connected)
            )
        else:
            print("⚠️ No se encontró event loop principal.")

        value_str = str(value) 
        id = str(uuid.uuid4())
        db = SessionLocal()
        room_id = get_or_create_room_id(db, room_name=room, site_name="Finca La Esperanza")  # o extraído dinámicamente del topic
        # print(room_id)
        
        #Guardar en la base de datos
        try:
            measurement = Measurement(
                room_id=room_id, 
                control=control,
                root= root,
                var=var,
                value=value,
                timestamp=ts,
            )
            db.add(measurement)
            db.commit()
        
        except Exception as e:
            print(f"❌ Error al guardar en DB: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error procesando mensaje MQTT: {e}")

def on_disconnect(client, userdata, rc):
    print("🔌 Desconectado. Reintentando conexión...")
    mqtt_connected = False
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

# async def save_measurement(room, root, control, var, value):
#     async with SessionLocal() as session:
#         m = Measurement(room= room, 
#                         root= root, 
#                         control= control, 
#                         var= var, 
#                         value= value)
#         session.add(m)
#         await session.commit()

def start_mqtt(loop):
    
    global mqtt_loop
    mqtt_loop = loop  # Guardamos el loop principal para usarlo luego

    mqtt_client = connect_mqtt_with_retries()
    if mqtt_client:
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect
        mqtt_client.loop_start()
