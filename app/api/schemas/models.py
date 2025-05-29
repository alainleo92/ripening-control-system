from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base 
from datetime import datetime

Base = declarative_base()

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    description = Column(String)

    rooms = relationship("Room", back_populates="site")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"))

    site = relationship("Site", back_populates="rooms")
    measurements = relationship("Measurement", back_populates="room")

class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    control = Column(String, nullable=False) #e.g., rh, temperature, gas, ventilation
    root = Column(String, nullable=False) #e.g., status, alarms, param
    var = Column(String, nullable=False)  # e.g., reg_temp, target, differential
    value = Column(String, nullable=False)  # Almacenamos como string para aceptar float, int, bool
    timestamp = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room", back_populates="measurements")
