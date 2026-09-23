"""
Prueba manual de la función de limpieza de HTML -> texto legible.

Este script NO usa datos reales todavía (los equipos de Extractor aún no
mandan sus JSON). Se usa un HTML de ejemplo, armado a mano, que simula cómo
llegaría una noticia real: título, negritas, texto con un error de
codificación intencional y un <script> que no debe aparecer en el resultado.

Cómo correrlo:
    pip install beautifulsoup4 lxml ftfy
    python limpieza_html_test.py
"""

from bs4 import BeautifulSoup
import re
import ftfy

HTML_DE_EJEMPLO = """
<div>
    <h1>Accidente en Avenida Reforma</h1>
    <p>El pasado <b>martes</b> se registrÃ³ un choque sobre Avenida Reforma,
    en la colonia Centro.</p>
    <script>trackClick()</script>
    <footer>Compartir en redes sociales</footer>
</div>
"""


def limpiar_html(html_crudo: str) -> str:
    """Convierte HTML crudo en texto legible y normalizado."""
    # 1. Corregir posibles errores de codificación (tildes, ñ, etc.)
    html_arreglado = ftfy.fix_text(html_crudo)

    # 2. Parsear con lxml (más tolerante a HTML mal formado)
    soup = BeautifulSoup(html_arreglado, "lxml")

    # 3. Quitar nodos que no son contenido real de la noticia
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    # 4. Extraer el texto y normalizar espacios/saltos de línea
    texto = soup.get_text(separator=" ", strip=True)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


if __name__ == "__main__":
    print("Entrada (HTML crudo):")
    print(HTML_DE_EJEMPLO.strip())
    print("\nSalida (texto limpio):")
    print(limpiar_html(HTML_DE_EJEMPLO))
