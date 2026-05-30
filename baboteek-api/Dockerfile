# Используем стабильный образ Python
FROM python:3.14-slim

# Копируем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Устанавливаем рабочую директорию
WORKDIR /app

# Шаг 1: Копируем файлы конфигурации воркспейса и README (чтобы удовлетворить требования сборщика)
COPY pyproject.toml uv.lock README.md ./
COPY baboteek-core/pyproject.toml baboteek-core/README.md* ./baboteek-core/
COPY baboteek-api/pyproject.toml baboteek-api/README.md* ./baboteek-api/

# Шаг 2: Создаем пустые заглушки модулей, чтобы удовлетворить проверки uv во время кэширования
RUN mkdir -p baboteek-core/src/baboteek_core && touch baboteek-core/src/baboteek_core/__init__.py
RUN mkdir -p baboteek-api/src/baboteek_api && touch baboteek-api/src/baboteek_api/__init__.py

# Дополнительно создаем README, если их не было в копировании
RUN touch baboteek-core/README.md baboteek-api/README.md

# Шаг 3: Теперь uv без проблем скачает и закеширует все внешние зависимости без dev-пакетов
RUN uv sync --frozen --no-cache --no-dev --no-install-project

# Шаг 4: Перезаписываем фейковые заглушки реальным исходным кодом проектов
COPY baboteek-core/src ./baboteek-core/src
COPY baboteek-api/src ./baboteek-api/src

# Скопируем и реальные README, если они обновились
COPY baboteek-core/README.md ./baboteek-core/README.md
COPY baboteek-api/README.md ./baboteek-api/README.md

# Шаг 5: Моментально дособираем наши готовые пакеты
RUN uv sync --frozen --no-cache --no-dev

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "baboteek-api/src/baboteek_api/main.py", "--host", "0.0.0.0", "--port", "8000"]