from typing import Literal

from strands import tool

from agents.tools import _tavily


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
    return _tavily.search(query, max_results, topic=topic, time_range=time_range)
