from fastapi import APIRouter, Depends, HTTPException 
from fastapi.responses import FileResponse, HTMLResponse
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
        if measurement:
            result[var] = measurement.value  # ej. "target": 23.5
            print(f"!!!!!Measurement: {var} ={measurement.value}")
        else:
            result[var] = None

    return {
        "room": room_name,
        "values": result
    }

@router.get("/all/{root}/{control}/{room_name}")
def get_all_root_values_for_room(room_name: str, root: str, control: str,  db: Session = Depends(get_db)):

    room = db.query(Room).filter(Room.name == room_name).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    result = {}
    measurement = (
        db.query(Measurement)
        .filter(Measurement.room_id == room.id, Measurement.root == root, Measurement.control == control)
            .order_by(Measurement.var.asc())
            .all()
        )
    if measurement:
        for m in measurement:
            if m.var not in result:
                result[m.var] = m.value.strip('\x00')
                # print(f"!!!!!Measurement: {m.var} ={m.value}")
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "room": room_name,
        "root": root,
        "control": control,
        "values": result
    }

@router.get("/room-dashboard", response_class=HTMLResponse)
def serve_room_dashboard():
    return FileResponse("app/static/control_dashboard.html")