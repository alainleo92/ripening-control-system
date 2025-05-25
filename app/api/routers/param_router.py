# app/routers/param_router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel 
from app.core.mqtt_client import publish
from datetime import datetime
import json
from typing import Union

router = APIRouter(
    prefix="/param",
    tags=["parametros"]
)

class ParamUpdate(BaseModel):
    room: str
    control: str # e.g., "rh" o "temperature"
    parameter: str  # ejemplo: "target", "differential"
    value: Union[float, bool, str]

BOOLEAN_PARAMS = [
                    "enable_control", "ovd_cool", "ovd_heat", 
                    "humidity_mode", "heat_mode", "vent_mode", "dich_monitor",
                    "ovd_dh", "ovd_hm", "gas_on_off", "ovd_gas", "ovd_vent"
                    ]

@router.post("/update")
async def update_param(data: ParamUpdate):
    # Validar entradas mínimamente
    allowed_rooms = {"room1", "room2", "room3"}
    allowed_controls = {"rh", "temperature", "gas", "vent"}

    if data.parameter in BOOLEAN_PARAMS and not isinstance(data.value, bool):
        raise HTTPException(status_code=400, detail="Este parámetro requiere un valor booleano.")

    if data.room not in allowed_rooms:
        raise HTTPException(status_code=400, detail="Sala inválida")
    if data.control not in allowed_controls:
        raise HTTPException(status_code=400, detail="Control inválido")
    
    value = data.value
    if isinstance(value, str):
        if value.lower() in {"true", "false"}:
            value = value.lower() == "true"
        else:
            try:
                value = float(value)
            except ValueError:
                raise HTTPException(status_code=400, detail="Valor inválido. Debe ser float o bool.")


    topic = f"weintek/ripening/{data.room}/cmd/param/{data.control}/{data.parameter}"
    print(type(data.value))
    msg = {
        "d": {
            "value": [data.value],
            "ts": datetime.utcnow().isoformat()
        }
    }
    print(f"🔍 msg: {msg}")
    

    publish(topic, json.dumps(msg))

    return {
        "status": "ok",
        "topic": topic,
        "value_sent": data.value
    }
