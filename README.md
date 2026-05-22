# PI Challenge — RAG API

API en FastAPI que responde preguntas sobre el documento `docs/documento.docx`.

## Requisitos

- Python 3.11+
- Cuenta en [OpenAI](https://platform.openai.com/) (API key)
- Cuenta en [Chroma Cloud](https://www.trychroma.com/) (API key, tenant y database)
- Docker y Docker Compose *(solo si vas a correr con Docker)*

## Instalación

```bash
git clone https://github.com/solanodz/pi_challenge_ai.git
cd pi_challenge_ai

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

Editá `.env` con tus credenciales (ver tabla abajo).

## Variables de entorno

Copiá `.env.example` a `.env` y completá cada valor:


| Variable                 | Qué es                                                                      |
| ------------------------ | --------------------------------------------------------------------------- |
| `OPENAI_API_KEY`         | Tu API key de OpenAI                                                        |
| `OPENAI_CHAT_MODEL`      | Modelo de chat (ej. `gpt-4o-mini`)                                          |
| `OPENAI_EMBEDDING_MODEL` | Modelo de embeddings (`text-embedding-3-small`)                             |
| `CORPUS_PATH`            | Ruta al documento (default: `docs/documento.docx`)                          |
| `CHROMA_API_KEY`         | API key de Chroma Cloud                                                     |
| `CHROMA_TENANT`          | Tenant ID de Chroma Cloud                                                   |
| `CHROMA_DATABASE`        | Nombre de la base en Chroma                                                 |
| `CHROMA_COLLECTION`      | Nombre de la colección donde se guardan los chunks                          |
| `RETRIEVAL_DISTANCE_MAX` | Umbral de similitud (default: `1.77`; no hace falta cambiarlo para empezar) |


Las credenciales de Chroma las encontrás en el dashboard de Chroma Cloud.

## Cómo correr el proyecto

### Opción 1 — Local (recomendado)

Un comando carga el documento en Chroma y levanta la API:

```bash
python scripts/run_local.py --reload
```

Si ya corriste el ingest antes y solo querés la API:

```bash
python scripts/run_local.py --skip-ingest --reload
```

La API queda en **[http://localhost:8000](http://localhost:8000)**.

### Opción 2 — Docker

Asegurate de tener el `.env` configurado y ejecutá:

```bash
docker compose up --build
```

La API queda en **[http://localhost:8000](http://localhost:8000)**. El contenedor hace el ingest automáticamente al arrancar.

Para arrancar sin re-ingestar (más rápido, si el índice ya existe en Chroma):

```bash
SKIP_INGEST=true docker compose up --build
```

## Probar que funciona

Con la API corriendo en **[http://localhost:8000](http://localhost:8000)**:

### Postman (recomendado)

Usá **Postman Desktop** (app instalada), no la versión web: desde el navegador no se puede llamar a `http://localhost:8000`.

- **[Documentación pública en Postman Documenter](https://documenter.getpostman.com/view/46472328/2sBXwjwZZa)** — descripción de endpoints y ejemplos.
- **[Importar colección](https://solanodezuasnabar.postman.co/workspace/b6a61666-0a49-4f66-86ba-61f100a90747/collection/46472328-13b9e234-892f-45a3-b7a0-2cba4942ee2c?action=share&source=copy-link&creator=46472328)** — requests listos para ejecutar.

Pasos:

1. Importá la colección en Postman Desktop (link de arriba).
2. Asegurate de que las requests apunten a `http://localhost:8000`.
3. Ejecutá **Health** y luego **Ask** (u otras requests de la colección).

### curl

```bash
curl http://localhost:8000/health
```

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"user_name":"John Doe","question":"Quien es Zara?"}'
```

## Documentación de la API

Detalle de endpoints, códigos HTTP, ejemplos de request/response y campos: **[API.md](API.md)**.

Documentación interactiva en Postman: **[Colección para el Challenge AI — PI Consulting](https://documenter.getpostman.com/view/46472328/2sBXwjwZZa)**.