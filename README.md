# 🍌 Ripening Control Dashboard

Sistema web de monitoreo en tiempo real para cámaras de maduración de frutas y vegetales. Utiliza **FastAPI**, **WebSocket** y **MQTT** para visualizar datos desde sensores conectados a un PLC Danfoss a través de una HMI Weintek.

## 📦 Características

- Visualización en tiempo real de datos (temperatura, humedad, gas, válvulas, etc.)
- Interfaz HTML única y dinámica para múltiples cámaras (`room1`, `room2`, `room3`)
- WebSocket por sala con datos en vivo
- MQTT broker para recibir datos desde el sistema físico
- Navegación lateral entre salas
- Estructura de tópicos clara y organizada

---

## 🧠 Estructura del sistema

```
app/
├── core/
│   ├── mqtt_client.py         # Cliente MQTT
│   ├── room_topics.py         # Tópicos organizados por sala
│   └── ws_manager.py          # Manejador de conexiones WebSocket
├── static/
│   └── dashboard.html         # Interfaz HTML dinámica
├── websockets/
│   └── ws_endpoint.py         # Endpoints WebSocket para cada sala
└── main.py                    # Entrada principal de FastAPI
```

---

## 🌐 Interfaz Web

- Accede a cualquier sala desde:
  ```
  http://localhost:8000/room/room1
  http://localhost:8000/room/room2
  http://localhost:8000/room/room3
  ```
- Cada sala renderiza datos desde WebSocket usando JavaScript.
- Los datos se muestran en **cards dinámicas** (3 por fila).
- Se muestra fecha y hora de cada medición.

---

## 🧪 Ejemplo de WebSocket

```js
const ws = new WebSocket(`ws://${location.host}/ws/room1`);
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Renderizar datos en la UI
};
```

---

## 🚨 MQTT

- Se usa `paho-mqtt` para recibir datos del sistema físico.
- Los tópicos están definidos dinámicamente en `room_topics.py`:

```python
ROOM_TOPICS = {
  "room1": [ "weintek/ripening/room1/status/temperature/sensor1", ... ],
  "room2": [ "room2/status/temperature/sensor1", ... ],
  "room3": [ "room3/status/temperature/sensor1", ... ],
}
```

---

## ⚙️ Instalación

```bash
git clone https://github.com/tu-usuario/ripening-dashboard.git
cd ripening-dashboard
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 📋 Requisitos

- Python 3.10+
- FastAPI
- Uvicorn
- paho-mqtt

---

## 📈 Roadmap

- [x] WebSocket por sala
- [x] UI dinámica con 1 archivo HTML
- [x] Navegación lateral entre salas
- [ ] Edición remota de parámetros vía MQTT
- [ ] Autenticación de usuarios

---

## 🧑‍💻 Autor

Desarrollado por [Alain Rodriguez / Dynamiqs].

---