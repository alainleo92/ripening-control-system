from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.schemas.models import Base, Site, Room  # Ajusta el import según tu estructura

# Ruta a la base de datos SQLite
DATABASE_URL = "sqlite:///app/db/ripening.db"

# Crear engine y sesión
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def init_data():
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)

    # Verificar si ya hay sitios creados
    if session.query(Site).count() == 0:
        # Crear sitio
        site = Site(name="Finca La Esperanza", address="Ti Arriba, Nave 4")
        session.add(site)
        session.flush()  # Para obtener el site.id

        # Agregar rooms asociados
        rooms = [
            Room(name="room1", site_id=site.id),
            Room(name="room2", site_id=site.id),
            Room(name="room3", site_id=site.id),
        ]
        session.add_all(rooms)
        session.commit()
        print("✅ Datos iniciales insertados correctamente.")
    else:
        print("⚠️ La base de datos ya tiene datos. No se insertó nada.")

if __name__ == "__main__":
    init_data()
