from typing import Literal

from strands import tool

from agents.tools import _tavily

SOURCES = {
    "sofascore": "sofascore.com",
    "footystats": "footystats.org",
}


@tool
def soccer_stats_search(
    query: str,
    source: Literal["sofascore", "footystats"] | None = None,
    max_results: int = 5,
) -> list[dict]:
    """Busca estadísticas de fútbol solo en SofaScore y FootyStats.

    Úsala para los datos de los equipos y del partido: forma reciente, resultados,
    enfrentamientos directos (H2H), clasificación, goles, xG, porcentaje de ambos
    marcan (BTTS) o de más de 2,5 goles, y estadísticas de jugadores. Las consultas
    funcionan mejor en inglés y con los nombres oficiales de los equipos, p. ej.
    "Real Madrid vs FC Barcelona h2h stats".

    Args:
        query: Consulta de búsqueda, en inglés y con los nombres de los equipos.
        source: "sofascore" o "footystats" para buscar solo en una de las dos webs;
            sin valor, busca en ambas.
        max_results: Número de resultados, entre 1 y 10.

    Returns:
        Lista de resultados con título, URL, fecha de publicación (si se conoce)
        y un extracto del contenido.
    """
    domains = [SOURCES[source]] if source else list(SOURCES.values())
    return _tavily.search(query, max_results, include_domains=domains)
