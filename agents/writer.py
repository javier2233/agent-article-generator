import os

from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel

from agents.tools.web_search import web_search

BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "global.anthropic.claude-opus-5-5")

SYSTEM_PROMPT = """Eres un redactor que escribe artículos en español, claros y bien \
estructurados, a partir de un tema.

Antes de escribir, documéntate con la herramienta web_search: busca datos, cifras y \
novedades sobre el tema y basa el artículo en lo que encuentres, no en lo que \
recuerdes. Si el tema es de actualidad, usa topic="news". Cuando un dato venga de \
una fuente concreta, menciónala en el texto. Si la búsqueda falla, escribe con lo \
que sepas y no inventes datos.

Devuelve siempre el artículo con la herramienta de salida estructurada: un título \
de como máximo 255 caracteres y el contenido completo en Markdown."""


class GeneratedArticle(BaseModel):
    title: str = Field(max_length=255, description="Título del artículo")
    content: str = Field(description="Cuerpo del artículo en Markdown")


def generate_article(topic: str, section_title: str | None = None) -> GeneratedArticle:
    # Un Agent guarda el historial de la conversación: se crea uno por petición.
    agent = Agent(
        model=BedrockModel(model_id=BEDROCK_MODEL_ID, max_tokens=16000),
        system_prompt=SYSTEM_PROMPT,
        tools=[web_search],
        callback_handler=None,
    )
    prompt = f"Escribe un artículo sobre: {topic}"
    if section_title:
        prompt += f"\nSe publicará en la sección «{section_title}»."
    result = agent(prompt, structured_output_model=GeneratedArticle)
    return result.structured_output
