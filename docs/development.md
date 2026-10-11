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

`DATABASE_URL` se construye en `docker-compose.yml` a partir de las anteriores; no hace falta definirla.

> Los valores por defecto solo sirven para desarrollo local. En cualquier otro entorno, define credenciales propias.

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
