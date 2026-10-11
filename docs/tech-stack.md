# Stack tecnológico

## Lenguaje

| Tecnología | Versión | Uso |
|---|---|---|
| **Python** | 3.13 | Lenguaje de todo el backend. Imagen base `python:3.13-slim`. |

## Frameworks y librerías

Versiones que resolvió `pip` a fecha de 2026-10-10, como referencia.

**Política de versiones:** `requirements.txt` no fija versiones a propósito, para usar siempre las más recientes. Si una actualización rompe algo, se hace un plan de actualización para adaptar el código en lugar de fijar la versión antigua.

| Librería | Versión | Para qué se usa |
|---|---|---|
| [**FastAPI**](https://fastapi.tiangolo.com/) | 0.143.0 | Framework web: rutas, validación, inyección de dependencias y documentación OpenAPI automática (`/docs`, `/redoc`). |
| [**Uvicorn**](https://www.uvicorn.org/) (`[standard]`) | 0.54.0 | Servidor ASGI que ejecuta la app. El extra `standard` añade `uvloop`, `httptools` y recarga automática. |
| [**SQLModel**](https://sqlmodel.tiangolo.com/) | 0.0.48 | ORM. Combina SQLAlchemy y Pydantic: un modelo sirve como tabla y como esquema de la API. |
| [**SQLAlchemy**](https://www.sqlalchemy.org/) | 2.1.4 | Motor del ORM (lo instala SQLModel). Se usa directamente para tipos de columna como `DateTime(timezone=True)`. |
| [**Pydantic**](https://docs.pydantic.dev/) | 2.14.0 | Validación y serialización de datos (lo instalan FastAPI y SQLModel). |
| [**Alembic**](https://alembic.sqlalchemy.org/) | 1.20.0 | Migraciones del esquema de la base de datos. |
| [**psycopg**](https://www.psycopg.org/psycopg3/) (`[binary]`) | 3.3.6 | Driver de PostgreSQL (versión 3). El extra `binary` trae libpq precompilada, así que no hace falta compilar nada en la imagen. |

## Base de datos

| Tecnología | Versión | Uso |
|---|---|---|
| **PostgreSQL** | 17 (imagen `postgres:17-alpine`) | Base de datos relacional principal. |

## Infraestructura

| Tecnología | Uso |
|---|---|
| **Docker** | Imagen del servidor (`Dockerfile`). |
| **Docker Compose** | Orquesta los servicios `app` y `db`, la red interna, el volumen y el orden de arranque (`docker-compose.yml`). |

## Por qué estas elecciones

- **FastAPI**: tipado, validación automática y documentación OpenAPI sin configuración extra.
- **SQLModel**: del mismo autor que FastAPI y pensado para él. Evita duplicar modelos de base de datos y de API. Al ser SQLAlchemy por debajo, se puede bajar a SQLAlchemy cuando haga falta.
- **Alembic**: la herramienta de migraciones estándar para SQLAlchemy, con autogeneración a partir de los modelos.
- **psycopg 3**: el driver moderno de PostgreSQL, con soporte síncrono y asíncrono. SQLAlchemy lo usa con el prefijo `postgresql+psycopg://`.
