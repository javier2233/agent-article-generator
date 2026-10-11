import os

from tavily import TavilyClient

# Extracto máximo por resultado: suficiente para redactar sin llenar el contexto.
MAX_CONTENT_CHARS = 1500


def search(query: str, max_results: int, **options) -> list[dict]:
    """Busca con Tavily y devuelve los resultados recortados para el modelo."""
    client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    response = client.search(query, max_results=min(max(max_results, 1), 10), **options)
    return [
        {
            "title": result.get("title"),
            "url": result.get("url"),
            "published_date": result.get("published_date"),
            "content": (result.get("content") or "")[:MAX_CONTENT_CHARS],
        }
        for result in response.get("results", [])
    ]
