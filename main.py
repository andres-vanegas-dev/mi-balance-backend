from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
from pydantic import BaseModel  # opcional, para validación

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FILE = "data.json"

# ---------- UTILIDADES ----------
def read_data():
    with open(FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- RUTA INICIAL ----------
@app.get("/")
def home():
    return {"message": "API Finanzas funcionando"}

# ---------- INGRESOS ----------
@app.get("/ingresos")
def get_ingresos():
    return read_data()["ingresos"]

@app.post("/ingresos")
def add_ingreso(ingreso: dict):
    data = read_data()
    ingreso["id"] = len(data["ingresos"]) + 1
    ingreso["fecha"] = str(datetime.now())
    data["ingresos"].append(ingreso)
    save_data(data)
    return ingreso

# ---------- GASTOS ----------
@app.get("/gastos")
def get_gastos():
    return read_data()["gastos"]

@app.post("/gastos")
def add_gasto(gasto: dict):
    data = read_data()
    gasto["id"] = len(data["gastos"]) + 1
    gasto["fecha"] = str(datetime.now())
    data["gastos"].append(gasto)
    save_data(data)
    return gasto

# ---------- BALANCE ----------
@app.get("/balance")
def get_balance():
    data = read_data()
    total_ingresos = sum(i["monto"] for i in data["ingresos"])
    total_gastos = sum(g["monto"] for g in data["gastos"])
    return {
        "ingresos": total_ingresos,
        "gastos": total_gastos,
        "balance": total_ingresos - total_gastos
    }

# ---------- RECORDATORIOS ----------
@app.get("/recordatorios")
def get_recordatorios():
    data = read_data()
    return data.get("recordatorios", [])

@app.post("/recordatorios")
def add_recordatorio(recordatorio: dict):
    data = read_data()
    if "recordatorios" not in data:
        data["recordatorios"] = []
    recordatorio["id"] = len(data["recordatorios"]) + 1
    # Aseguramos el campo completado (por defecto False)
    recordatorio["completado"] = recordatorio.get("completado", False)
    # La fecha ya viene como string "YYYY-MM-DD"
    # Guardamos también la fecha de creación
    recordatorio["creado"] = str(datetime.now())
    data["recordatorios"].append(recordatorio)
    save_data(data)
    return recordatorio

@app.patch("/recordatorios/{id}")
def update_recordatorio(id: int, payload: dict):
    """
    Actualiza parcialmente un recordatorio.
    Se espera un JSON con los campos a modificar (ej: {"completado": true}).
    """
    data = read_data()
    for r in data.get("recordatorios", []):
        if r.get("id") == id:
            # Actualizar solo los campos enviados
            r.update(payload)
            save_data(data)
            return r
    raise HTTPException(status_code=404, detail="Recordatorio no encontrado")

@app.delete("/recordatorios/{id}")
def delete_recordatorio(id: int):
    data = read_data()
    if "recordatorios" not in data:
        raise HTTPException(status_code=404, detail="No hay recordatorios")
    original_len = len(data["recordatorios"])
    data["recordatorios"] = [r for r in data["recordatorios"] if r.get("id") != id]
    if len(data["recordatorios"]) == original_len:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
    save_data(data)
    return {"message": "Recordatorio eliminado"}

# Endpoint opcional para próximos recordatorios
@app.get("/recordatorios/proximos")
def get_proximos_recordatorios():
    data = read_data().get("recordatorios", [])
    from datetime import date
    hoy = date.today()
    proximos = []
    for r in data:
        try:
            fecha_r = datetime.strptime(r["fecha"], "%Y-%m-%d").date()
            if fecha_r >= hoy:
                proximos.append(r)
        except:
            continue
    proximos.sort(key=lambda r: r["fecha"])
    return proximos