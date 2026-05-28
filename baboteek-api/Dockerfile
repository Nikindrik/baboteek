FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY baboteek-core ./baboteek-core
COPY baboteek-api ./baboteek-api

RUN uv sync --frozen --no-cache

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "baboteek-api/src/baboteek_api/main.py", "--host", "0.0.0.0", "--port", "8000"]