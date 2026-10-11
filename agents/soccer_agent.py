import os
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel

from agents.tools.soccer_stats_search import soccer_stats_search
from agents.tools.web_search import web_search

BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "global.anthropic.claude-opus-5-5")

SYSTEM_PROMPT = """Eres un periodista deportivo especializado en fútbol. Escribes en \
español artículos de previa con una predicción razonada del resultado de un partido \
que aún no se ha jugado.

Antes de escribir, documéntate con tus dos herramientas de búsqueda:
- soccer_stats_search (SofaScore y FootyStats) para las estadísticas: forma reciente \
(últimos 5 partidos), enfrentamientos directos, clasificación, goles, xG y \
estadísticas de jugadores. Es tu fuente principal de datos.
- web_search con topic="news" y un time_range reciente para la actualidad: fecha, \
hora y estadio del próximo partido, lesiones, sanciones, convocatorias y declaraciones.

Los resultados pueden mezclar otros deportes (SofaScore también cubre baloncesto, \
tenis…), equipos femeninos, filiales o categorías inferiores. Usa solo los de fútbol \
y del primer equipo masculino, salvo que se pida otra cosa.

Basa el análisis y la predicción en lo que encuentres, no en lo que recuerdes: tus \
datos pueden estar desactualizados. Si no encuentras un dato, dilo en vez de \
inventarlo. Si no encuentras un próximo partido entre esos equipos, dilo claramente \
en el artículo.

El artículo debe incluir:
- Contexto del partido (fecha, estadio, competición, qué se juega cada equipo).
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
    # La fecha va en el mensaje (no en el prompt de sistema) para saber qué partido es
    # el "próximo" sin cambiar el prompt de sistema en cada petición.
    today = datetime.now(timezone.utc).date().isoformat()
    prompt = (
        f"Hoy es {today}. Escribe la previa con predicción del próximo partido "
        f"{home_team} (local) contra {away_team} (visitante)."
    )
    if competition:
        prompt += f"\nCompetición: {competition}."
    if section_title:
        prompt += f"\nSe publicará en la sección «{section_title}»."
    result = agent(prompt, structured_output_model=GeneratedArticle)
    return result.structured_output
