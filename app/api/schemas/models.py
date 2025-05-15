from pydantic import BaseModel

from sqlalchemy import Column, Float, Integer, String, create_engine, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

class control_temp_param(BaseModel):
    is_control_temp : bool  # Habilitacion de uso de control de temperatura
    param_target : float    # Target del controlador de temperatura 

class control_temp_status(BaseModel):
    reg_temp : float  # Habilitacion de uso de control de temperatura
    param_target : float    # Target del controlador de temperatura 

class control_temp(BaseModel):
    status_var : control_temp_status
    param : control_temp_param

class ripening_room(BaseModel):
    control_temp_data : control_temp 

