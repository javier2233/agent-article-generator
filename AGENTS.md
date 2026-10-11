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
main.py              # App FastAPI y endpoints
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

- **Modelos**: cada entidad tiene un `XBase` con los campos comunes, la tabla `X(XBase, table=True)` y los esquemas `XCreate` / `XRead` para la API. Ver `models.py`.
- **Sesión**: los endpoints reciben la sesión con `SessionDep` (inyección de dependencias de FastAPI). No crear sesiones a mano en los endpoints.
- **Fechas**: siempre con zona horaria (UTC) y columnas `DateTime(timezone=True)`.
- **Esquema de BD**: nunca usar `SQLModel.metadata.create_all()`. Todo cambio de esquema pasa por una migración de Alembic. Revisa siempre el archivo autogenerado antes de aplicarlo.
- **Configuración**: por variables de entorno (`DATABASE_URL`, `POSTGRES_*`). La URL debe empezar por `postgresql+psycopg://`.
- **Dependencias**: añadirlas a `requirements.txt` y reconstruir la imagen (`docker compose up --build`).
- **Documentación**: si cambias arquitectura, stack, modelos o endpoints, actualiza el archivo correspondiente en `docs/`.
