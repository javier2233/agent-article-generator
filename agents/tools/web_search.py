import os
from typing import Literal

from strands import tool
from tavily import TavilyClient

# Extracto máximo por resultado: suficiente para redactar sin llenar el contexto.
MAX_CONTENT_CHARS = 1500


@tool
def web_search(
    query: str,
    topic: Literal["general", "news"] = "general",
    time_range: Literal["day", "week", "month", "year"] | None = None,
    max_results: int = 5,
) -> list[dict]:
    """Busca en internet información actual sobre un tema.

    Úsala para documentarte antes de escribir: datos, cifras, fechas, novedades
    y fuentes. Haz consultas concretas y, si hace falta, varias búsquedas sobre
    aspectos distintos del tema.

    Args:
        query: Consulta de búsqueda, concreta y en el idioma más adecuado para el tema.
        topic: "news" para noticias y actualidad; "general" para el resto.
        time_range: Limita los resultados a los publicados en el último día, semana, mes o año.
        max_results: Número de resultados, entre 1 y 10.

    Returns:
        Lista de resultados con título, URL, fecha de publicación (si se conoce)
        y un extracto del contenido.
    """
    client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    response = client.search(
        query,
        topic=topic,
        time_range=time_range,
        max_results=min(max(max_results, 1), 10),
    )
    return [
        {
            "title": result.get("title"),
            "url": result.get("url"),
            "published_date": result.get("published_date"),
            "content": (result.get("content") or "")[:MAX_CONTENT_CHARS],
        }
        for result in response.get("results", [])
    ]
