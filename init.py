from app.config.database import engine
from app.api.schemas.models import Base

Base.metadata.create_all(bind=engine)
print("✔️ Base de datos y tabla creada")