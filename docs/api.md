# API

URL base: `http://localhost:8000`

La documentación interactiva se genera automáticamente:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Esquema OpenAPI: `http://localhost:8000/openapi.json`

## Endpoints

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| `GET` | `/health` | Comprueba que la API y la base de datos responden | `200` |
| `POST` | `/articles` | Crea un artículo | `201` · `ArticleRead` |
| `GET` | `/articles` | Lista artículos (paginado) | `200` · `ArticleRead[]` |
| `GET` | `/articles/{article_id}` | Obtiene un artículo por id | `200` · `ArticleRead`, o `404` |

### `GET /health`

```bash
curl localhost:8000/health
```
```json
{"status": "ok", "database": "connected"}
```

### `POST /articles`

Cuerpo (`ArticleCreate`):

| Campo | Tipo | Obligatorio | Restricciones |
|---|---|---|---|
| `title` | string | Sí | Máximo 255 caracteres |
| `content` | string | Sí | |

```bash
curl -X POST localhost:8000/articles \
  -H 'Content-Type: application/json' \
  -d '{"title": "Hola", "content": "Primer artículo"}'
```
```json
{"title": "Hola", "content": "Primer artículo", "id": 1, "created_at": "2026-10-10T18:00:00Z"}
```

Si el cuerpo no es válido, FastAPI responde `422` con el detalle del error.

### `GET /articles`

Parámetros de consulta:

| Parámetro | Por defecto | Descripción |
|---|---|---|
| `offset` | `0` | Número de artículos que se saltan |
| `limit` | `100` | Número máximo de artículos devueltos |

```bash
curl 'localhost:8000/articles?offset=0&limit=10'
```

### `GET /articles/{article_id}`

```bash
curl localhost:8000/articles/1
```

Si no existe: `404` con `{"detail": "Article not found"}`.
