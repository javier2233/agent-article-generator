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
| `POST` | `/articles/generate` | Genera un artículo con IA a partir de un tema y lo guarda | `201` · `ArticleRead`, `422` o `502` |
| `GET` | `/articles` | Lista artículos (paginado) | `200` · `ArticleRead[]` |
| `GET` | `/articles/{article_id}` | Obtiene un artículo por id | `200` · `ArticleRead`, o `404` |
| `PATCH` | `/articles/{article_id}` | Modifica un artículo | `200` · `ArticleRead`, o `404` |
| `DELETE` | `/articles/{article_id}` | Borra un artículo | `204`, o `404` |
| `POST` | `/sections` | Crea una sección | `201` · `SectionRead` |
| `GET` | `/sections` | Lista secciones (paginado) | `200` · `SectionRead[]` |
| `GET` | `/sections/{section_id}` | Obtiene una sección por id | `200` · `SectionRead`, o `404` |
| `PATCH` | `/sections/{section_id}` | Modifica una sección | `200` · `SectionRead`, o `404` |
| `DELETE` | `/sections/{section_id}` | Borra una sección | `204`, o `404` |
| `GET` | `/sections/{section_id}/articles` | Lista los artículos de una sección (paginado) | `200` · `ArticleRead[]`, o `404` |

Todos los ids son UUID. Un id con formato no válido responde `422`. Los listados aceptan `offset` (por defecto `0`) y `limit` (por defecto `100`).

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
| `section_id` | UUID | No | Debe ser el id de una sección existente; si no existe, responde `422` con `{"detail": "Section not found"}` |

```bash
curl -X POST localhost:8000/articles \
  -H 'Content-Type: application/json' \
  -d '{"title": "Hola", "content": "Primer artículo", "section_id": "65f10685-1c23-4f41-b634-ecacb1d76e7a"}'
```
```json
{"title": "Hola", "content": "Primer artículo", "section_id": "65f10685-1c23-4f41-b634-ecacb1d76e7a", "id": "60c503dc-7656-45e1-b1dc-404f6586d562", "created_at": "2026-10-10T18:00:00Z"}
```

Si el cuerpo no es válido, FastAPI responde `422` con el detalle del error.

### `POST /articles/generate`

Genera el título y el contenido (Markdown) con el agente redactor (Strands + Amazon Bedrock), que antes se documenta buscando en internet (tool `web_search`, con Tavily). Guarda el artículo y lo devuelve. Tarda lo que tarde el modelo: puede ser más de un minuto.

Cuerpo (`ArticleGenerate`):

| Campo | Tipo | Obligatorio | Restricciones |
|---|---|---|---|
| `topic` | string | Sí | Entre 1 y 1000 caracteres. Tema o indicaciones para el artículo |
| `section_id` | UUID | No | Sección donde se guarda; su título se pasa al agente como contexto. Si no existe: `422` con `{"detail": "Section not found"}` |

```bash
curl -X POST localhost:8000/articles/generate \
  -H 'Content-Type: application/json' \
  -d '{"topic": "La historia del café", "section_id": "15345934-bb22-4197-8a2a-9b618a6ebe4b"}'
```
```json
{"title": "De Etiopía a tu taza: breve historia del café", "content": "## Orígenes\n...", "section_id": "15345934-bb22-4197-8a2a-9b618a6ebe4b", "id": "0b8f6c2e-3a51-4f7e-9c1d-2a4e5f6b7c8d", "created_at": "2026-10-10T18:00:00Z"}
```

Si la llamada al modelo falla (sin credenciales de AWS, sin permisos, modelo no disponible…): `502` con `{"detail": "Article generation failed"}`. El detalle está en los logs de `app`. Configuración en [development.md](development.md#amazon-bedrock).

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
curl localhost:8000/articles/60c503dc-7656-45e1-b1dc-404f6586d562
```

Si no existe: `404` con `{"detail": "Article not found"}`. Si el id no es un UUID válido: `422`.

### `PATCH /articles/{article_id}`

Cuerpo (`ArticleUpdate`): solo se modifican los campos enviados. Un cuerpo vacío (`{}`) no cambia nada.

| Campo | Tipo | Obligatorio | Restricciones |
|---|---|---|---|
| `title` | string | No | Máximo 255 caracteres. No admite `null` (`422`) |
| `content` | string | No | No admite `null` (`422`) |
| `section_id` | UUID o `null` | No | Debe ser una sección existente (`422` si no). `null` quita el artículo de su sección |

```bash
# Mover el artículo a otra sección
curl -X PATCH localhost:8000/articles/60c503dc-7656-45e1-b1dc-404f6586d562 \
  -H 'Content-Type: application/json' \
  -d '{"section_id": "15345934-bb22-4197-8a2a-9b618a6ebe4b"}'

# Quitarlo de su sección
curl -X PATCH localhost:8000/articles/60c503dc-7656-45e1-b1dc-404f6586d562 \
  -H 'Content-Type: application/json' \
  -d '{"section_id": null}'
```

Si el artículo no existe: `404`.

### `DELETE /articles/{article_id}`

```bash
curl -X DELETE localhost:8000/articles/60c503dc-7656-45e1-b1dc-404f6586d562
```

Responde `204` sin cuerpo. Si no existe: `404`.

### `POST /sections`

Cuerpo (`SectionCreate`):

| Campo | Tipo | Obligatorio | Restricciones |
|---|---|---|---|
| `title` | string | Sí | Máximo 255 caracteres |

```bash
curl -X POST localhost:8000/sections \
  -H 'Content-Type: application/json' \
  -d '{"title": "Tecnología"}'
```
```json
{"title": "Tecnología", "id": "15345934-bb22-4197-8a2a-9b618a6ebe4b"}
```

### `GET /sections`

```bash
curl 'localhost:8000/sections?offset=0&limit=10'
```

### `GET /sections/{section_id}`

```bash
curl localhost:8000/sections/15345934-bb22-4197-8a2a-9b618a6ebe4b
```

Si no existe: `404` con `{"detail": "Section not found"}`.

### `PATCH /sections/{section_id}`

Cuerpo (`SectionUpdate`): solo se modifican los campos enviados. Un cuerpo vacío (`{}`) no cambia nada.

| Campo | Tipo | Obligatorio | Restricciones |
|---|---|---|---|
| `title` | string | No | Máximo 255 caracteres. No admite `null` (`422`) |

```bash
curl -X PATCH localhost:8000/sections/15345934-bb22-4197-8a2a-9b618a6ebe4b \
  -H 'Content-Type: application/json' \
  -d '{"title": "Tech"}'
```

### `DELETE /sections/{section_id}`

```bash
curl -X DELETE localhost:8000/sections/15345934-bb22-4197-8a2a-9b618a6ebe4b
```

Responde `204` sin cuerpo. Los artículos de la sección **no se borran**: quedan con `section_id: null`.

### `GET /sections/{section_id}/articles`

```bash
curl localhost:8000/sections/15345934-bb22-4197-8a2a-9b618a6ebe4b/articles
```

Devuelve los artículos cuyo `section_id` es esta sección. Si la sección no existe: `404`.
