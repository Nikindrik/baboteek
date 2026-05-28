<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lucide-react/lucide/main/icons/terminal.svg">
    <img alt="Baboteek IDE" src="https://raw.githubusercontent.com/lucide-react/lucide/main/icons/terminal.svg" width="120" height="120">
  </picture>
  <br>Baboteek Compiler IDE
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-%3E%3D_3.14-blue?logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/Node.js-%3E%3D_20-green?logo=nodedotjs&logoColor=white" alt="Node.js Version">
  <img src="https://img.shields.io/badge/FastAPI-005571?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker">
</p>

Baboteek Compiler IDE is a comprehensive multi-component ecosystem designed for writing, debugging, and compiling source code written in the custom **Baboteek** programming language. The workspace features a high-performance compiler core, an asynchronous FastAPI backend with robust JWT authentication, and a modern Web IDE powered by Microsoft's Monaco Editor engine.

## Documentation

* [Developer Reference](./DEVELOPER.md) - Deep dive into compiler phases, delegates, and DI.
* [User Guide](./USER_GUIDE.md) - Learn how to write code, use examples, and resolve errors.

---

## Configuration & Environment (`.env`)

Create a `.env` file in the root workspace directory before starting the application:

```ini
# Database (PostgreSQL)
DATABASE_USER=postgres
DATABASE_PASSWORD=your_secure_db_password
DATABASE_NAME=baboteek_db

# API Settings
APP_NAME="Compiler API"
SECRET_KEY=your_production_jwt_secret_key_string
ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
FREE_COMPILE_LIMIT=5

# Internal Docker-network DB URL
DATABASE_URL=postgresql+asyncpg://postgres:your_secure_db_password@db:5432/baboteek_db

# CORS Configuration
CORS_ORIGINS=["http://localhost", "http://localhost:80", "http://localhost:5173", "http://127.0.0.1:5173"]

# Frontend Build Arguments
VITE_API_URL=http://localhost:8000
```

---

## Getting Started

### Method 1: Quick Start with Docker (Recommended)

Make sure you have Docker and Docker Compose installed on your machine.

1. Build and run all services in detached mode from the root directory:
   ```bash
   docker-compose up --build
   ```
2. **Access Points:**
   * **Web IDE:** [http://localhost](http://localhost) (Port 80)
   * **Interactive API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

### Method 2: Manual Local Execution (For Development)

This method is ideal for making live changes to the core grammar rules or frontend assets without rebuilding Docker images.

#### 1. Setup the Database (PostgreSQL)
* Ensure a local instance of PostgreSQL is running.
* Create an empty database matching the configuration (e.g., `baboteek_db`).
* Update the `DATABASE_URL` in your `.env` to point to `localhost` instead of `db`:
  ```ini
  DATABASE_URL=postgresql+asyncpg://postgres:your_secure_db_password@localhost:5432/baboteek_db
  ```

#### 2. Run the Backend API (`baboteek-api`)
Ensure [uv](https://github.com/astral-sh/uv) is installed.
```bash
# Sync workspace dependencies from the root directory
uv sync

# Run the FastAPI development server
uv run fastapi dev baboteek-api/src/baboteek_api/main.py
```

#### 3. Run the Frontend IDE (`baboteek-frontend`)
Ensure [Node.js](https://nodejs.org/) (>= 20) is installed.
```bash
# Navigate to the frontend workspace
cd baboteek-frontend

# Install dependencies and launch the Vite development server
npm install
npm run dev
```
*The Web IDE will be available at [http://localhost:5173](http://localhost:5173) with full hot-module replacement.*

---

## Grammar Specifications

The Baboteek compiler core processes code using a strict, statically-typed context-free grammar.

<p align="center">
  <img src="https://raw.githubusercontent.com/lucide-react/lucide/main/icons/workflow.svg" alt="Compiler Pipeline Architecture" width="80" height="80">
</p>

### Lexical Rules
* **Identifiers:** `[a-zA-Z][a-zA-Z0-9_]*`
* **Numbers:** `[0-9]+`
* **Keywords:** `program`, `var`, `begin`, `end`, `if`, `then`, `else`, `while`, `do`, `read`, `write`, `int`, `bool`, `true`, `false`
* **Operators:**
  * **Relational:** `>`, `<`, `>=`, `<=`, `=`, `!=`
  * **Additive:** `+`, `-`, `or`
  * **Multiplicative:** `*`, `/`, `and`
  * **Unary:** `not`

### Syntax Rules (BNF)
```bnf
<program>    ::= "program" "var" <declaration> "begin" <statement> { ";" <statement> } "end"
<declaration>::= <identifier> { "," <identifier> } ":" <type>
<type>       ::= "int" | "bool"
<statement>  ::= <compound> | <assignment> | <conditional> | <loop> | <input> | <output>
<compound>   ::= "begin" <statement> { ";" <statement> } "end"
<assignment> ::= <identifier> ":=" <expression>
<conditional>::= "if" <expression> "then" <statement> [ "else" <statement> ]
<loop>       ::= "while" <expression> "do" <statement>
<input>      ::= "read(" <identifier> ")"
<output>     ::= "write(" <expression> ")"
```

### Semantic Checks
* **Scope Validation:** Variable declaration is required before any use. No duplicate declarations are permitted.
* **Type Consistency:** Operators are restricted to compatible types (e.g., mathematical operators `+`, `-`, `*`, `/` require `int` operands, while `and`, `or`, `not` require `bool` operands).
