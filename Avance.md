# Avance — Módulo Cleaner

**Responsable:** Alejandra Buelna
**Periodo cubierto:** 5 de septiembre – 18 de septiembre de 2026 (semana y media)
**Módulo:** Request / Collector / Cleaner — parte Cleaner

---

## 1. Resumen de la semana

Esta primera semana y media la enfoqué en tres cosas: entender bien qué me toca hacer dentro del módulo
(a diferencia de lo que hace Collector), definir junto con Ximena y los equipos de Extractor el contrato
de datos que vamos a usar, e investigar/probar las herramientas que voy a necesitar: limpieza de HTML con
`BeautifulSoup` y una API con `FastAPI` para poder recibir y entregar los JSON sin depender de mandarnos
archivos manualmente por WhatsApp o Drive.

Todavía no proceso noticias reales porque los equipos de Extractor aún no me mandan sus JSON, así que las
pruebas de esta etapa las hice con HTML de ejemplo que armé yo misma, simulando cómo vendría una noticia
real (títulos, párrafos, negritas, enlaces dentro del texto, etc.).

## 2. Qué estudiamos / investigué

- **Diferencia entre parsear y limpiar HTML.** Repasé cómo funciona el DOM de una página y por qué no basta
  con quitar las etiquetas `<...>` con un regex simple (rompe con HTML mal formado, entidades como `&nbsp;`
  o `&amp;`, y con contenido dentro de `<script>`/`<style>` que no debe conservarse).
- **BeautifulSoup + lxml.** Cómo se recorre el árbol del documento, la diferencia entre `.get_text()` y
  `.get_text(separator=" ", strip=True)`, y cómo eliminar explícitamente los nodos `<script>`, `<style>`,
  `<nav>` y `<footer>` antes de extraer el texto (si no, se cuela texto de menús y publicidad).
  Fuente principal: documentación oficial de Beautiful Soup 4.
- **Codificación de texto (encoding).** Investigué por qué a veces el HTML trae caracteres mal codificados
  (por ejemplo "informaciÃ³n" en vez de "información") y cómo la librería `ftfy` (*fixes text for you*)
  detecta y corrige automáticamente ese tipo de errores de codificación sin que yo tenga que adivinar el
  encoding original de cada fuente.
- **Expresiones regulares básicas** (`re.sub`) para colapsar espacios múltiples, saltos de línea repetidos
  y espacios antes de signos de puntuación que quedan después de quitar las etiquetas.
- **APIs REST y FastAPI.** Qué es un endpoint, diferencia entre `GET` y `POST`, qué es un `UploadFile`, cómo
  FastAPI genera documentación automática en `/docs`, y por qué se necesita `uvicorn` como servidor ASGI
  para correr la aplicación (FastAPI define la API, pero no se ejecuta sola).
- **CORS y redes locales.** Investigué la diferencia entre correr la API en `127.0.0.1` (solo mi máquina) y
  en `0.0.0.0` (visible para otras computadoras en la misma red), porque mis compañeros necesitan conectarse
  desde sus propias laptops.

## 3. Acuerdos a los que llegamos como equipo

- **Contrato de entrada:** cada equipo de Extractor me manda un JSON por fuente con la lista de noticias en
  HTML crudo (URL + HTML), sin que ellos tengan que preocuparse por cómo lo voy a limpiar.
- **Contrato de salida:** yo entrego **un solo JSON consolidado** con las noticias de las 7 fuentes ya en
  texto legible, cada una con su `url` y su `texto` limpio. Se decidió consolidar todo en un solo archivo
  (en vez de uno por fuente) para no repetir el proceso de lectura/escritura siete veces y para que a los
  módulos de Catastro/PostgreSQL les llegue una sola fuente de verdad.
- **Canal de intercambio:** siguiendo la sugerencia del profesor, vamos a usar una API hecha con FastAPI en
  vez de mandarnos archivos manualmente. Ximena y yo acordamos que yo expongo los endpoints porque el
  Cleaner es el punto donde se junta todo el flujo antes de pasar a Catastro.
- **Nombres de fuente estandarizados:** acordamos usar claves cortas y en minúsculas (`facebook`,
  `ensenada_net`, `vigia`, etc.) para evitar inconsistencias al filtrar por fuente más adelante.

## 4. Pruebas de código realizadas

### 4.1 Prueba de limpieza de HTML

Antes de tener datos reales, armé un HTML de ejemplo (con negritas, un enlace y saltos de línea sucios) para
probar que la función de limpieza extrae solo el texto legible. El código está en
[`pruebas/limpieza_html_test.py`](./pruebas/limpieza_html_test.py).

**Resultado obtenido al correrlo:**
```
Entrada (HTML crudo):
<div><h1>Accidente en Avenida Reforma</h1><p>El pasado <b>martes</b> se registrÃ³ un choque...
<script>trackClick()</script></div>

Salida (texto limpio):
Accidente en Avenida Reforma
El pasado martes se registró un choque sobre Avenida Reforma, en la colonia Centro.
```

Confirmé que el script `<script>trackClick()</script>` no aparece en la salida y que el error de
codificación (`registrÃ³` → `registró`) se corrige con `ftfy` antes de limpiar el HTML.

### 4.2 Prueba mínima de la API

Probé una versión mínima de la API con dos endpoints: uno para "recibir" un JSON crudo de prueba
(`POST /raw/{fuente}`) y otro para consultar el resultado (`GET /clean`). Código en
[`pruebas/api_prueba.py`](./pruebas/api_prueba.py).

**Pasos de la prueba:**
1. Corrí `uvicorn api_prueba:app --reload --port 8000`.
2. Abrí `http://localhost:8000/docs` y usé el botón "Try it out" para mandar un JSON de ejemplo a
   `POST /raw/vigia`.
3. Confirmé en `GET /clean` que el conteo de noticias recibidas coincidía con lo que mandé.
4. Repetí la prueba desde el navegador de mi compañera Ximena, conectada a la misma red WiFi, usando mi
   IP local (`http://192.168.1.XX:8000/docs`) en vez de `localhost`, para confirmar que sí se puede acceder
   desde otra máquina.

## 5. Documentación de fallos / errores encontrados

| # | Error | Causa | Solución aplicada |
|---|---|---|---|
| 1 | `ModuleNotFoundError: No module named 'multipart'` al mandar un archivo con `UploadFile` | FastAPI necesita `python-multipart` para procesar archivos subidos y no viene incluido por defecto | `pip install python-multipart` |
| 2 | `ERROR: [Errno 48] Address already in use` al correr `uvicorn` | Ya había una instancia anterior del servidor corriendo en el puerto 8000 (no la había cerrado bien) | Cerrar el proceso anterior o correr con `--port 8001` |
| 3 | Texto de salida con símbolos raros (`Ã³`, `Â¿`) | El HTML de origen no especificaba correctamente su codificación (no era UTF-8 limpio) | Pasar el texto por `ftfy.fix_text()` antes de parsear con BeautifulSoup |
| 4 | Al llamar a la API desde la laptop de Ximena no conectaba | Estaba corriendo `uvicorn` con host `127.0.0.1` (solo visible en mi propia máquina) | Cambiar a `--host 0.0.0.0` para que sea visible en la red local |
| 5 | El texto limpio traía texto de menú/publicidad pegado al inicio | `get_text()` se aplicó directo sobre todo el documento sin quitar antes `<nav>`, `<footer>` y `<script>` | Eliminar esos nodos explícitamente con `.decompose()` antes de extraer el texto |

## 6. Qué aprendimos

**Sobre Python / lenguaje:**
- La importancia de separar responsabilidades en funciones puras (una función que solo limpia texto, sin
  mezclar lógica de red ni de la API), para poder probarla con `pytest` sin necesitar levantar el servidor.
- Manejo básico de excepciones al leer JSON mal formado (`json.JSONDecodeError`) para que un archivo dañado
  de un compañero no tumbe toda la API.

**Sobre BeautifulSoup / lxml:**
- `lxml` como parser es más tolerante a HTML mal formado que el parser por defecto de Python
  (`html.parser`), lo cual es importante porque no controlamos la calidad del HTML de cada fuente.
- Que limpiar bien implica *quitar* nodos completos (script, style, nav, footer) antes de extraer texto, no
  solo extraer y luego intentar arreglar el resultado.

**Sobre FastAPI / Uvicorn (framework):**
- FastAPI separa la definición de la API (rutas, tipos de datos) de su ejecución real (Uvicorn), a
  diferencia de otros frameworks más "todo en uno" que había visto antes.
- La documentación automática en `/docs` es muy útil para que mis compañeros prueben mis endpoints sin
  necesitar escribir código, lo cual ayuda porque no todos en el equipo tienen el mismo nivel en Python.
- La diferencia entre correr localmente (`127.0.0.1`), en red local (`0.0.0.0`) y exponerla a internet
  (herramientas como ngrok), y por qué para nuestro proyecto de clase probablemente baste con red local.

## 7. Código de ejemplo creado

Ver los archivos completos en la carpeta [`pruebas/`](./pruebas). Resumen de lo más relevante:

```python
# Fragmento de cleaner.py — función principal de limpieza (creada por mí, en pruebas)
from bs4 import BeautifulSoup
import re
import ftfy

def limpiar_html(html_crudo: str) -> str:
    html_arreglado = ftfy.fix_text(html_crudo)
    soup = BeautifulSoup(html_arreglado, "lxml")

    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    texto = soup.get_text(separator=" ", strip=True)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto
```

## 8. Evidencia visual

*(Pendiente de anexar en esta carpeta: captura de `http://localhost:8000/docs` mostrando los endpoints, y
captura de la prueba exitosa desde la laptop de Ximena conectada por red local. Se agregan en el próximo
avance, junto con las primeras capturas del JSON consolidado real.)*

## 9. Próximos pasos

- Recibir los primeros JSON reales de los equipos de Extractor y correr la limpieza sobre noticias reales
  (no solo el HTML de ejemplo).
- Ajustar `limpiar_html()` según los casos reales que aparezcan (tablas, imágenes con texto alternativo,
  enlaces incrustados en medio del texto).
- Guardar el JSON consolidado también en disco (`data/clean/consolidado.json`), no solo en memoria.
- Escribir pruebas formales con `pytest` (por ahora las pruebas fueron manuales, vía `/docs`).
- Fusionar esta rama (`feature/cleaner-alejandra`) con la rama `dev` una vez que el flujo completo con datos
  reales esté validado con Ximena y con Extractor.
