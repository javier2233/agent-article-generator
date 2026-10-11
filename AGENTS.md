# AGENTS.md

Guía para agentes de IA (y personas) que trabajan en este repositorio. La documentación completa está en [`docs/`](docs/README.md).

## Proyecto

**agent-article-generator**: API REST en Python para gestionar artículos, respaldada por PostgreSQL. Todo se ejecuta con Docker Compose.

## Stack

- Python 3.13 · FastAPI · Uvicorn
- SQLModel (sobre SQLAlchemy 2) · Alembic
- PostgreSQL 17 · psycopg 3
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
- **Fechas**: siempre con zona horaria (UTC) y columnas `DateTime(timezone=True)`.
- **Esquema de BD**: nunca usar `SQLModel.metadata.create_all()`. Todo cambio de esquema pasa por una migración de Alembic. Revisa siempre el archivo autogenerado antes de aplicarlo.
- **Configuración**: por variables de entorno (`DATABASE_URL`, `POSTGRES_*`). La URL debe empezar por `postgresql+psycopg://`.
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
