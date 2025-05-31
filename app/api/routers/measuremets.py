from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.init_db import session as db
from app.api.schemas.models import Measurement, Room
from typing import List
from app.config.database import get_db
from datetime import datetime
from app.api.services.mqtt_services import celsius_to_fahrenheit

router = APIRouter(prefix="/api/measurements", tags=["measurements"])

@router.get("/room/{room_name}", response_model=List[dict]) #Obten las ultimas 100 mediciones almacenadas en bd
def get_measurements_by_room(room_name: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.name == room_name).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    measurements = db.query(Measurement)\
        .filter(Measurement.room_id == room.id)\
        .order_by(Measurement.timestamp.desc())\
        .limit(100)\
        .all()

    return [
        {
            "root": m.root,
            "control": m.control,
            "var": m.var,
            "value": m.value,
            "timestamp": m.timestamp.isoformat()
        }
        for m in measurements
    ]

@router.get("/latest/{control}/{room_name}")
def get_latest_control_values_for_room(room_name: str, control: str, db: Session = Depends(get_db)):
    var_of_interest = [
        "target",
        "reg",
        "differential"
    ]
    room = db.query(Room).filter(Room.name == room_name).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    result = {}
    for var in var_of_interest:
        measurement = (
            db.query(Measurement)
            .filter(Measurement.room_id == room.id, Measurement.control == control, Measurement.var == var)
            .order_by(Measurement.timestamp.desc())
            .first()
        )
        print(measurement)
        if measurement:
            result[var] = measurement.value  # ej. "target": 23.5
        else:
            result[var] = None

    return {
        "room": room_name,
        "values": result
    }