"""
Prueba mínima de la API con FastAPI para el módulo Cleaner.

Objetivo de esta prueba: confirmar que puedo recibir un JSON crudo de una
fuente (simulando lo que mandará un equipo de Extractor) y consultarlo
después desde otro endpoint. Todavía no incluye la limpieza real del HTML
ni el guardado en disco; eso se integra en la siguiente etapa.

Cómo correrlo:
    pip install fastapi uvicorn python-multipart
    uvicorn api_prueba:app --reload --host 0.0.0.0 --port 8000

Luego abrir http://localhost:8000/docs para probarlo desde el navegador.
"""

from fastapi import FastAPI, UploadFile
import json

app = FastAPI(title="Cleaner API - Extratron (prueba)")

# Almacenamiento temporal en memoria (solo para esta prueba)
raw_data: dict = {}


@app.get("/")
def status():
    return {"status": "ok", "modulo": "cleaner", "fuentes_recibidas": list(raw_data.keys())}


@app.post("/raw/{fuente}")
async def recibir_json(fuente: str, file: UploadFile):
    """Recibe el JSON crudo (URL + HTML) de una fuente específica."""
    contenido = await file.read()
    datos = json.loads(contenido)
    raw_data[fuente] = datos
    return {
        "status": "recibido",
        "fuente": fuente,
        "noticias_recibidas": len(datos.get("noticias", [])),
    }


@app.get("/clean")
def obtener_resumen():
    """Endpoint de prueba: por ahora solo confirma cuántas noticias hay por fuente."""
    resumen = {
        fuente: len(datos.get("noticias", []))
        for fuente, datos in raw_data.items()
    }
    return {"fuentes": resumen, "total_fuentes": len(raw_data)}
