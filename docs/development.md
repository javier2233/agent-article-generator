# Desarrollo

## Requisitos

- Docker Desktop (o Docker Engine con el plugin Compose)

No hace falta tener Python ni PostgreSQL instalados en tu máquina: todo corre en contenedores.

## Arrancar el proyecto

```bash
docker compose up --build
```

La API queda en `http://localhost:8000` y PostgreSQL en `localhost:5432`. Las migraciones se aplican solas al arrancar.

Para pararlo:

```bash
docker compose down      # Para los contenedores (los datos se conservan)
docker compose down -v   # Para los contenedores y borra los datos
```

## Variables de entorno

Se pueden definir en un archivo `.env` en la raíz (Compose lo lee automáticamente). `.env` está excluido de la imagen por `.dockerignore`.

| Variable | Por defecto | Uso |
|---|---|---|
| `POSTGRES_USER` | `postgres` | Usuario de PostgreSQL |
| `POSTGRES_PASSWORD` | `postgres` | Contraseña de PostgreSQL |
| `POSTGRES_DB` | `app` | Nombre de la base de datos |

| `AWS_REGION` | `us-west-2` (lo aplica Strands si no se define) | Región de Amazon Bedrock |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | — | Credenciales de AWS para Bedrock |
| `AWS_SESSION_TOKEN` | — | Solo con credenciales temporales (SSO, roles asumidos) |
| `TAVILY_API_KEY` | — | Clave de la API de Tavily para las tools `web_search` y `soccer_stats_search` (gratuita en [app.tavily.com](https://app.tavily.com)) |
| `BEDROCK_MODEL_ID` | `global.anthropic.claude-opus-5-5` | Modelo (id o perfil de inferencia) que usa soccerAgent |

`DATABASE_URL` se construye en `docker-compose.yml` a partir de las anteriores; no hace falta definirla.

`docker-compose.yml` pasa todo el contenido de `.env` al contenedor `app` (`env_file`, opcional: si `.env` no existe, arranca igual). Por eso las variables de AWS solo hay que ponerlas en `.env`; ver `.env.example`.

> Los valores por defecto solo sirven para desarrollo local. En cualquier otro entorno, define credenciales propias.

## Amazon Bedrock

`POST /articles/predictions` necesita acceso a Bedrock. Sin credenciales, el resto de la API funciona y ese endpoint responde `502` (el log de `app` muestra `NoCredentialsError`).

1. Ten una cuenta de AWS con acceso al modelo de `BEDROCK_MODEL_ID` habilitado en Bedrock, en la región de `AWS_REGION`.
2. La identidad necesita el permiso `bedrock:InvokeModelWithResponseStream` sobre ese modelo o perfil de inferencia.
3. Copia `.env.example` a `.env` y rellena `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (y `AWS_SESSION_TOKEN` si son temporales).
4. Reinicia `app` para que lea las variables: `docker compose up -d app`.

Prueba:

```bash
curl -X POST localhost:8000/articles/predictions \
  -H 'Content-Type: application/json' \
  -d '{"home_team": "Real Madrid", "away_team": "FC Barcelona", "match_date": "2026-10-26", "competition": "LaLiga"}'
```

Si falla, mira `docker compose logs app`: `AccessDeniedException` (permisos o modelo no habilitado), `ValidationException` (id de modelo no válido en esa región).

## Tavily

Las tools `web_search` y `soccer_stats_search` usan `TAVILY_API_KEY` de `.env`. Sin clave, el SDK de Tavily funciona en modo sin clave con un límite de uso bajo: sirve para probar, no para uso continuado. Si la búsqueda falla (límite, clave no válida), el agente recibe el error y escribe sin documentarse.

Probar las tools sin pasar por el agente:

```bash
docker compose exec app python -c "from agents.tools.web_search import web_search; print(web_search(query='Real Madrid lesiones', topic='news', max_results=2))"
docker compose exec app python -c "from agents.tools.soccer_stats_search import soccer_stats_search; print(soccer_stats_search(query='Real Madrid vs FC Barcelona h2h stats', source='footystats', max_results=2))"
```

## Flujo de trabajo

- **Cambios en el código Python**: se recargan solos (`--reload` y la carpeta montada en `/app`).
- **Cambios en `requirements.txt` o `Dockerfile`**: reconstruye con `docker compose up --build`.
- **Cambios en modelos**: genera y revisa una migración (ver [database.md](database.md#cómo-cambiar-el-esquema)).

## Comandos útiles

```bash
docker compose logs -f app                 # Logs del servidor
docker compose exec app sh                 # Shell dentro del contenedor
docker compose exec db psql -U postgres -d app   # Consola de PostgreSQL
```

## Entorno local para el editor (opcional)

Para que el editor reconozca las librerías (autocompletado, sin avisos de paquetes no instalados):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Este entorno es solo para el editor. La aplicación se sigue ejecutando en Docker.
