# Arquitectura

## Visión general

La aplicación son dos contenedores orquestados con Docker Compose:

```mermaid
flowchart LR
    client[Cliente HTTP] -->|:8000| app
    subgraph Docker Compose
        app["app<br/>FastAPI + Uvicorn<br/>Python 3.13"] -->|psycopg 3<br/>:5432| db[("db<br/>PostgreSQL 17")]
        db --- vol[(volumen<br/>postgres_data)]
    end
```

| Servicio | Imagen | Puerto | Función |
|---|---|---|---|
| `app` | Construida desde `Dockerfile` (`python:3.13-slim`) | 8000 | Servidor de la API |
| `db` | `postgres:17-alpine` | 5432 | Base de datos |

## Capas de la aplicación

```
main.py     →  Capa HTTP: rutas FastAPI, validación de entrada/salida
models.py   →  Capa de datos: modelos SQLModel (tabla + esquemas Pydantic)
db.py       →  Acceso a datos: engine de SQLAlchemy y sesión por petición
migrations/ →  Evolución del esquema con Alembic
```

- **`main.py`** define la app FastAPI y los endpoints. Cada endpoint recibe una `Session` mediante la dependencia `SessionDep`.
- **`models.py`** define cada entidad con SQLModel. Un mismo modelo es a la vez tabla de la base de datos y esquema de validación de Pydantic.
- **`db.py`** crea el `engine` a partir de `DATABASE_URL` (con `pool_pre_ping` para descartar conexiones caídas) y expone `get_session()`, que abre una sesión por petición y la cierra al terminar.
- **`migrations/`** contiene la configuración de Alembic. `env.py` importa `models` para registrar las tablas y reutiliza el `engine` de `db.py`.

## Flujo de una petición

1. Uvicorn recibe la petición HTTP y la pasa a FastAPI.
2. FastAPI valida el cuerpo con el esquema correspondiente (p. ej. `ArticleCreate`).
3. FastAPI resuelve `SessionDep` llamando a `get_session()`, que abre una sesión.
4. El endpoint lee o escribe con la sesión (`session.get`, `session.exec(select(...))`, `session.add` + `commit`).
5. FastAPI serializa la respuesta con el `response_model` (p. ej. `ArticleRead`).
6. Al terminar la petición, la sesión se cierra.

## Arranque

1. Compose arranca `db` y espera a que su healthcheck (`pg_isready`) responda.
2. Arranca `app`, que ejecuta `alembic upgrade head` para aplicar las migraciones pendientes.
3. Después lanza `uvicorn main:app` con `--reload`.

## Persistencia

Los datos de PostgreSQL se guardan en el volumen con nombre `postgres_data` y sobreviven a reinicios y a `docker compose down`. Solo se borran con `docker compose down -v`.

El código del proyecto se monta en `/app` dentro del contenedor, así que los cambios se recargan sin reconstruir la imagen (salvo si cambias dependencias o el `Dockerfile`).
