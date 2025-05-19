# app/main.py

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.core.mqtt_client import start_mqtt, subscribers
from app.core.ws_manager import ws_manager
from app.api.routers import ws_endpoint, param_router
import asyncio

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Obtener el loop principal
main_event_loop = asyncio.get_event_loop()

@app.on_event("startup")
def on_startup():
    # Iniciar MQTT y agregar suscriptor que empuja por WebSocket
    start_mqtt(main_event_loop)
    subscribers.append(lambda data: app.state.send_ws_update(data))

@app.middleware("http")
async def inject_ws_manager(request, call_next):
    # Inyectar ws_manager en request.state y guardar función para usar desde MQTT
    request.state.ws_manager = ws_manager
    app.state.send_ws_update = lambda data: ws_manager.broadcast(data)
    return await call_next(request)

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    return FileResponse("app/static/dashboard.html")

# Registrar el router
app.include_router(ws_endpoint.router)
app.include_router(param_router.router)
