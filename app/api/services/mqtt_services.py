#Lista de parametros que deben convertirse de C a F
from sqlalchemy.orm import Session
from app.api.schemas.models import Site, Room
from datetime import datetime

PARAMS_TO_CONVERT = ["reg_temp", "sensor1", "sensor2", "sensor3",
                     "sensor4", "sensor5", "change_over", "target",
                     "disch_temp"

                     ]

ROOT_TO_CONVERT = ["status" , "param"]

def celsius_to_fahrenheit(c):
    return round((c * 9/5) + 32, 2)

def parse_value(raw_value):
    if isinstance(raw_value, bool):
        return raw_value
    elif isinstance(raw_value, (int, float)):
        return raw_value
    elif isinstance(raw_value, str):
        if raw_value.lower() == "true":
            return True
        elif raw_value.lower() == "false":
            return False
        else:
            try:
                return float(raw_value)
            except ValueError:
                print("❌ Valor no es float ni bool válido.")
                return None
    else:
        print("❌ Tipo de valor no reconocido:", type(raw_value))
        return None
    
def parse_topic_and_value(payload, msg):
    raw_value = payload["d"]["value"][0]
    parts = msg.topic.strip("/").split("/")
    room = parts[2]
    root = parts[3]
    control = parts[4]
    var = parts[5]
    ts = parse_timestamp(payload.get("ts"))
    topic = msg.topic
    return raw_value, room, root, control, var, ts, topic

def initialize_and_update_latest_data(latest_data, room, root, control, var, value, ts):
    if room not in latest_data:
        latest_data[room] = {}
    if root not in latest_data[room]:
        latest_data[room][root] = {}
    if control not in latest_data[room][root]:
        latest_data[room][root][control] = {}
    
    latest_data[room][root][control][var] = {
        "value": value,
        "timestamp": ts
    }

def get_or_create_room_id(db: Session, room_name: str, site_name: str = "default_site") -> int:
    # Buscar el sitio, o crear si no existe
    site = db.query(Site).filter(Site.id == 1).first()
    # print(site.name)
    # if not site:
    #     site = Site(name=site_name, address="Sin dirección")
    #     db.add(site)
    #     db.commit()
    #     db.refresh(site)

    # Buscar la sala
    room = db.query(Room).filter(Room.name == room_name, Room.site_id == site.id).first()
    # print(room.name)
    # # Crear si no existe
    # if not room:
    #     room = Room(name=room_name, site_id=site.id)
    #     db.add(room)
    #     db.commit()
    #     db.refresh(room)

    return room.id

def parse_timestamp(value):
    if isinstance(value, (int, float)):
        # Si viene como UNIX timestamp
        return datetime.fromtimestamp(value)
    elif isinstance(value, str):
        try:
            # Intenta parsear un string tipo ISO
            return datetime.fromisoformat(value)
        except ValueError:
            pass
    return datetime.utcnow()  # Fallback a ahora
