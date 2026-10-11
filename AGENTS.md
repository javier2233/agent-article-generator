# AGENTS.md

Guía para agentes de IA (y personas) que trabajan en este repositorio. La documentación completa está en [`docs/`](docs/README.md).

## Proyecto

**agent-article-generator**: API REST en Python para gestionar artículos, respaldada por PostgreSQL, que genera artículos de previa con predicción de partidos de fútbol con un agente de IA ([Strands Agents](https://strandsagents.com/) sobre Amazon Bedrock). Todo se ejecuta con Docker Compose.

## Stack

- Python 3.13 · FastAPI · Uvicorn
- SQLModel (sobre SQLAlchemy 2) · Alembic
- PostgreSQL 17 · psycopg 3
- Strands Agents · Amazon Bedrock (Claude)
- Docker · Docker Compose

Detalle y versiones en [docs/tech-stack.md](docs/tech-stack.md).

## Estructura

```
main.py              # Crea la app FastAPI y registra los routers
api/                 # Endpoints: un router por recurso
  deps.py            #   Dependencias compartidas (SessionDep)
  health.py          #   /health
  articles.py        #   /articles
  sections.py        #   /sections
agents/              # Agentes de Strands: un archivo por agente
  soccer_agent.py    #   soccerAgent: previas con predicción de partidos (generate_match_prediction)
  tools/             #   Tools de los agentes: un archivo por tool
    _tavily.py       #     Cliente de Tavily compartido (no es una tool)
    web_search.py    #     Búsqueda web general con Tavily
    soccer_stats_search.py  # Estadísticas de fútbol en SofaScore y FootyStats (Tavily)
db.py                # Engine y sesión de base de datos
models.py            # Modelos SQLModel (tablas y esquemas de la API)
migrations/          # Alembic: env.py, plantilla y versions/
alembic.ini          # Configuración de Alembic
Dockerfile           # Imagen del servidor
docker-compose.yml   # Servicios app + db
docs/                # Documentación del proyecto
```

## Comandos

```bash
docker compose up --build                                   # Arrancar todo
docker compose exec app alembic revision --autogenerate -m "msg"  # Nueva migración
docker compose exec app alembic upgrade head                # Aplicar migraciones
docker compose down -v                                      # Parar y borrar datos
```

## Convenciones

- **Modelos**: cada entidad tiene un `XBase` con los campos comunes, la tabla `X(XBase, table=True)` y los esquemas `XCreate` / `XRead` / `XUpdate` para la API. En `XUpdate` todos los campos son opcionales y los que no admiten nulo en la tabla rechazan `null` con un `field_validator`. Ver `models.py`.
- **Endpoints**: van en `api/`, un archivo por recurso con su `APIRouter(prefix="/recurso", tags=["recurso"])`. Para un recurso nuevo, crea `api/<recurso>.py` y regístralo en `main.py` con `app.include_router(...)`. `main.py` no contiene endpoints.
- **Sesión**: los endpoints reciben la sesión con `SessionDep` (de `api/deps.py`). No crear sesiones a mano en los endpoints.
- **Agentes**: van en `agents/`, un archivo por agente, con una función pública que los endpoints llaman (p. ej. `generate_match_prediction`). El archivo va en snake_case (`soccer_agent.py`) y el `name` del `Agent` en camelCase (`soccerAgent`). Se crea un `Agent` por petición (guarda historial). Los datos de cada petición (y la fecha actual) van en el mensaje al agente, en un bloque etiquetado (p. ej. `<partido>`), nunca en el prompt de sistema, que es fijo. La salida se pide estructurada con `structured_output_model` y un modelo Pydantic. El modelo se configura con `BEDROCK_MODEL_ID`; los endpoints no crean modelos ni agentes.
- **Tools**: van en `agents/tools/`, un archivo por tool, como funciones con `@tool` de Strands. El docstring y los type hints son lo que ve el modelo (descripción y esquema): escríbelos para el modelo, con `Args:` por parámetro. Devuelven solo lo necesario (recortado) para no llenar el contexto. El prompt de sistema del agente debe decir cuándo usar cada tool. Las búsquedas con Tavily pasan por `agents/tools/_tavily.py` (los módulos con `_` son helpers, no tools).
- **Fechas**: siempre con zona horaria (UTC) y columnas `DateTime(timezone=True)`.
- **Esquema de BD**: nunca usar `SQLModel.metadata.create_all()`. Todo cambio de esquema pasa por una migración de Alembic. Revisa siempre el archivo autogenerado antes de aplicarlo.
- **Configuración**: por variables de entorno (`DATABASE_URL`, `POSTGRES_*`, `AWS_*`, `BEDROCK_MODEL_ID`, `TAVILY_API_KEY`). La URL debe empezar por `postgresql+psycopg://`. Las credenciales de AWS y las claves de API van en `.env`, nunca en el código ni en `docker-compose.yml`.
- **Dependencias**: añadirlas a `requirements.txt` y reconstruir la imagen (`docker compose up --build`).

## Documentación obligatoria

**Todo cambio en el proyecto debe documentarse en `docs/` en el mismo cambio.** Una tarea no está terminada hasta que la documentación refleja el estado real del código.

| Si cambias... | Actualiza |
|---|---|
| Servicios, capas, flujo de peticiones o estructura de archivos | [docs/architecture.md](docs/architecture.md) |
| Lenguaje, frameworks, librerías (`requirements.txt`) o imágenes de Docker | [docs/tech-stack.md](docs/tech-stack.md) |
| Modelos, tablas, relaciones o migraciones | [docs/database.md](docs/database.md) (incluido el historial de migraciones) |
| Endpoints, parámetros, cuerpos o respuestas de la API | [docs/api.md](docs/api.md) |
| Comandos, variables de entorno o flujo de desarrollo | [docs/development.md](docs/development.md) |
| Algo que no encaja en ninguno | Crea un archivo nuevo en `docs/` y añádelo al índice [docs/README.md](docs/README.md) |

Si el cambio afecta a la estructura, el stack, los comandos o las convenciones, actualiza también este `AGENTS.md`.
