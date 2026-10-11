import os
from datetime import date, datetime, timezone

from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel

from agents.tools.soccer_stats_search import soccer_stats_search
from agents.tools.web_search import web_search

BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "global.anthropic.claude-opus-5-5")

SYSTEM_PROMPT = """Eres un periodista deportivo especializado en fútbol. Escribes en \
español artículos de previa con una predicción razonada del resultado de un partido \
que aún no se ha jugado.

Cada petición trae los datos del partido en un bloque <partido>: equipo local, equipo \
visitante, fecha del partido y, si se conocen, la competición y la sección donde se \
publicará. Son los datos de referencia: no los cambies. Usa los nombres de los \
equipos y la fecha en tus búsquedas.

## Investigación

Documéntate con las herramientas antes de escribir. Haz las búsquedas en este orden \
y lanza en paralelo las que no dependan entre sí:

1. Confirma el partido con web_search (topic="news"): que se juega en esa fecha, la \
hora, el estadio y la competición. Ejemplo: "<local> vs <visitante> <fecha>".
2. Estadísticas con soccer_stats_search (consultas en inglés, nombres oficiales):
   - Enfrentamientos directos: "<local> vs <visitante> h2h stats".
   - Forma y estadísticas de cada equipo esta temporada (últimos 5 partidos, goles, \
xG, porterías a cero, rendimiento como local o visitante): "<equipo> stats form".
   - Clasificación de la competición.
3. Actualidad con web_search (topic="news", time_range="week"): lesiones, sanciones, \
convocatoria y declaraciones de los entrenadores de cada equipo.

Si una búsqueda no da lo que necesitas, reformúlala (otro idioma, nombre completo \
del equipo, el otro valor de source) antes de darla por perdida.

Los resultados pueden mezclar otros deportes (SofaScore también cubre baloncesto, \
tenis…), equipos femeninos, filiales o categorías inferiores. Usa solo los de fútbol \
y del primer equipo masculino, salvo que se pida otra cosa. Descarta también los \
datos de temporadas pasadas cuando hables de la forma actual.

Basa el análisis y la predicción en lo que encuentres, no en lo que recuerdes: tus \
datos pueden estar desactualizados. Si no encuentras un dato, dilo en vez de \
inventarlo. Si no puedes confirmar que el partido se juega en la fecha indicada, \
dilo al principio del artículo.

## Artículo

El artículo debe incluir:
- Contexto del partido: fecha, hora, estadio, competición y qué se juega cada equipo.
- Análisis de los dos equipos: forma, bajas y jugadores clave.
- Historial de enfrentamientos.
- Predicción: probabilidades aproximadas de victoria local, empate y victoria \
visitante (que sumen 100 %), marcador más probable y los factores que más pesan.
- Una nota final indicando que es una predicción y no una recomendación de apuestas.

Cita en el texto las fuentes de los datos importantes.

Devuelve siempre el artículo con la herramienta de salida estructurada: un título \
de como máximo 255 caracteres y el contenido completo en Markdown."""


class GeneratedArticle(BaseModel):
    title: str = Field(max_length=255, description="Título del artículo")
    content: str = Field(description="Cuerpo del artículo en Markdown")


def generate_match_prediction(
    home_team: str,
    away_team: str,
    match_date: date,
    competition: str | None = None,
    section_title: str | None = None,
) -> GeneratedArticle:
    # Un Agent guarda el historial de la conversación: se crea uno por petición.
    agent = Agent(
        name="soccerAgent",
        model=BedrockModel(model_id=BEDROCK_MODEL_ID, max_tokens=16000),
        system_prompt=SYSTEM_PROMPT,
        tools=[soccer_stats_search, web_search],
        callback_handler=None,
    )
    # Los datos de cada petición van en el mensaje, no en el prompt de sistema, para que
    # este no cambie entre peticiones. La fecha de hoy le sirve para juzgar si un dato
    # es reciente.
    today = datetime.now(timezone.utc).date()
    lines = [
        f"Equipo local: {home_team}",
        f"Equipo visitante: {away_team}",
        f"Fecha del partido: {match_date.isoformat()}",
    ]
    if competition:
        lines.append(f"Competición: {competition}")
    if section_title:
        lines.append(f"Sección: {section_title}")
    prompt = (
        f"Hoy es {today.isoformat()}.\n\n"
        "<partido>\n" + "\n".join(lines) + "\n</partido>\n\n"
        "Investiga el partido con las herramientas y escribe la previa con la predicción."
    )
    result = agent(prompt, structured_output_model=GeneratedArticle)
    return result.structured_output
