# Cleaner

# Módulo Cleaner — Extratron

**Responsable:** Alejandra Buelna
**Equipo:** Request / Collector / Cleaner (Ximena Lozada — Request/Collector, Alejandra Buelna — Cleaner)
**Proyecto:** Extratron — Plataforma de Extracción, Validación y Gestión de Información Geográfica
**Rama de trabajo individual:** `feature/cleaner-alejandra` (previa a fusionar en `dev`)

---

## 1. Objetivo del módulo

Recibir los JSON crudos que entregan los equipos de Extractor (uno por cada fuente: Facebook, Ensenada.net,
El Vigía, entre otras — 7 fuentes en total, cada una con entre 10 y 20 noticias en HTML), convertir el
contenido de cada noticia de HTML a **texto legible y normalizado**, y consolidar todo en **un solo JSON
de salida** con el texto limpio y la URL de origen de cada noticia.

Este módulo es el paso intermedio entre la extracción de datos crudos y la validación geográfica: si el
texto que entrego no está limpio, todo lo que sigue (detección de calles, colonias, fechas) se ve afectado.

## 2. Entradas y salidas

**Entrada** (uno por fuente, entregado por cada equipo de Extractor):

```json
{
  "fuente": "vigia",
  "noticias": [
    { "url": "https://vigia.net/nota1", "html": "<div><p>Texto con <b>etiquetas</b>...</p></div>" }
  ]
}
```

**Salida** (un solo JSON consolidado con las 7 fuentes):

```json
{
  "generado_en": "2026-09-18T10:00:00",
  "noticias": [
    { "fuente": "vigia", "url": "https://vigia.net/nota1", "texto": "Texto limpio y legible de la noticia." }
  ]
}
```

## 3. Tecnología

- **Python 3.11**
- `beautifulsoup4` + `lxml` — parsear el HTML y extraer el texto.
- `ftfy` — corregir codificación de caracteres (tildes, ñ, comillas mal codificadas).
- `re` (estándar) — limpiar espacios y saltos de línea sobrantes.
- `FastAPI` + `uvicorn` — exponer una API para que Request y los Extractores intercambien los JSON conmigo sin mandarse archivos manualmente.
- `python-multipart` — requerido por FastAPI para recibir archivos (`UploadFile`).
- `pytest` — pruebas del proceso de limpieza.

## 4. Estructura de carpetas

```
cleaner_alejandra/
  main.py                 # API FastAPI (recepción de JSON crudos y entrega del JSON limpio)
  cleaner.py               # Lógica de limpieza de HTML a texto
  data/
    raw/                    # JSON crudos recibidos por fuente
    clean/                  # JSON consolidado de salida
  pruebas/
    limpieza_html_test.py   # Prueba de la función de limpieza con HTML de ejemplo
    api_prueba.py            # Prueba mínima de la API (endpoints de subida y consulta)
  requirements.txt
  README.md
  Avance.md
```

## 5. Cómo ejecutar (estado de desarrollo)

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Documentación interactiva de la API: `http://localhost:8000/docs`

## 6. Estado actual

En desarrollo: Ya está definido el contrato de entrada/salida con el resto del equipo y probada la
base de la API (recepción de archivos y endpoint de consulta) con datos de ejemplo. Estoy a la espera de
que los equipos de Extractor empiecen a mandar sus JSON reales por fuente para conectar el flujo completo
y probar la limpieza con noticias reales.

Ver el detalle de avance semanal en [`Avance.md`](./Avance.md).
