# Baboteek Compiler System 🚀

<p align="center">
  <img src="https://img.shields.io/badge/Language-Baboteek-blue" alt="Language">
  <img src="https://img.shields.io/badge/Framework-FastAPI-green" alt="FastAPI">
  <img src="https://img.shields.io/badge/Tooling-uv-orange" alt="uv">
</p>

**Baboteek Compiler System** — это полноценная экосистема для разработки на языке Baboteek. Проект включает в себя высокопроизводительное ядро компиляции и современный веб-интерфейс для работы с кодом в браузере.

---

## 🛠 Архитектура проекта
Проект построен с использованием подхода **Workspace** (управление через `uv`), что обеспечивает чистое разделение ответственности:

*   **`compiler-core`**: Сердце системы. Модульный конвейер, состоящий из:
    *   *Лексера*: конечный автомат с поддержкой буферизированного чтения.
    *   *Парсера*: рекурсивный спуск с делегированием задач по уровням грамматики.
    *   *Семантического анализатора*: контроль типов и областей видимости через таблицу символов.
*   **`compiler-api`**: Веб-интерфейс на **FastAPI**. Обеспечивает безопасную работу через JWT-аутентификацию и предоставляет стандартизированные JSON-ответы для фронтенд-приложений.

---

## 🚀 Начало работы

### 1. Подготовка окружения
Убедитесь, что у вас установлен [uv](https://github.com/astral-sh/uv).
```bash
# Клонируйте репозиторий и перейдите в него
git clone <your-repo-url>
cd baboteek

# Синхронизируйте зависимости
uv sync
```

Запуск

```bash
uv run fastapi dev packages/compiler-api/src/compiler_api/main.py
```