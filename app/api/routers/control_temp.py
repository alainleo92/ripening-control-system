from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, sessionmaker
from api.schemas.models import control_temp

router = APIRouter(
    prefix='/control_temp',
    tags=['CT']
)

@router.get("")
async def status_var(
    room_control_temp : control_temp 
):
    status = room_control_temp.status_var
    
