from fastapi import FastAPI

app = FastAPI(title="Sistema de Maduración de Frutas")

@app.get("/")
def read_root():
    return {"message": "Bienvenido al sistema de maduración"}
