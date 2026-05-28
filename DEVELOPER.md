# Baboteek Compiler Core: Developer Reference

<p align="center">
  <img src="https://raw.githubusercontent.com/lucide-react/lucide/main/icons/cpu.svg" alt="Compiler Core" width="80" height="80">
</p>

This document provides a technical deep dive into the inner workings of the `compiler-core` package, its modular recursive-descent architecture, and integration with the Web API.

## Compiler Architecture

The compilation engine is split into three decoupled phases to enforce the **Single Responsibility Principle (SRP)**. The shared state is managed sequentially through an immutable token list.

```
[Raw Source Code] 
       │
       ▼  (Lexical Phase)
 ┌───────────┐
 │   Lexer   │ ──► States: H, ID, NUM, STR, COM, DELIM
 └───────────┘
       │
       ▼  (Tokens Stream)
 ┌───────────┐
 │  Parser   │ ──► Delegates: Declaration, Statement, Expression
 └───────────┘
       │
       ▼  (Abstract Syntax Verification)
 ┌───────────┐
 │ Semantic  │ ──► Type Checking & SymbolTable Scope Validation
 └───────────┘
       │
       ▼
[Compilation Result] (CompileResult API Model)
```

---

## 1. Lexical Analysis (`lexer.py`)

The Lexer utilizes a Deterministic Finite Automaton (DFA) state machine. It reads characters from a custom `SourceReader` stream.

*   **Buffering & Streaming**: `SourceReader` supports `str` and `TextIO` streams. It reads chunks using a specified `buffer_size` (default: `4096` bytes).
*   **DFA States**: Transition rules are defined in `LexerState`. The machine matches identifiers, numbers, delimiters, string literals, and ignores comments (`{ comment }`).
*   **Sentinel Pattern**: To avoid type checker warnings regarding `None` values (such as `Uncaught TypeError: unsupported operand`), the end of a file is represented by the `EOF_CHAR = '\0'` sentinel.

---

## 2. Syntax Analysis (`parser.py`)

The parser is implemented as a **Modular Recursive Descent Parser** with delegated responsibilities. Instead of a single giant class, parsing tasks are distributed across logical delegate classes:

*   **`TokenStream`**: Manages cursor positioning, EOF detection, and implements safe `expect(token_type, value)` matching.
*   **`DeclarationParser`**: Parses structural entry points, variable declarations (`var`), and type tokens (`int`, `bool`).
*   **`StatementParser`**: Parses commands like `if-then-else`, `while-do`, assignments, and IO commands (`read`, `write`). It uses Python's structural pattern matching (`match-case`) on token attributes for fast routing.
*   **`ExpressionParser`**: Handles math and logic precedence climbing (Relational < Additive < Multiplicative < Unary).

---

## 3. Semantic Analysis (`semantic.py`)

The Semantic Analyzer verifies scope and type consistency across parsed tokens.

*   **`SymbolTable`**: Holds declared variables and their associated types (`%` for integers, `$` for booleans, `!` for reals).
*   **Type Checker**: Resolves types of expressions dynamically. It raises semantic errors if mismatching types are detected (e.g., trying to add an integer to a boolean).

---

## API Layer Integration (FastAPI)

The API layer acts as a thin wrapper (Facade) around the core logic. 

*   **Dependency Injection**: The `SyntaxAnalyzer` acts as a Dependency Injection (DI) container, wiring up the dependencies dynamically:
    ```python
    self.stream = TokenStream(tokens)
    self.expr_parser = ExpressionParser(self.stream)
    self.stmt_parser = StatementParser(self.stream, self.expr_parser)
    self.decl_parser = DeclarationParser(self.stream, self.stmt_parser)
    ```
*   **Unified Errors**: All compiler-core phases catch and translate internal panics into `ParserErrorMetadata` and `SemanticError` structures. These are compiled into `ParserResult` objects, ready to be serialized as JSON by FastAPI.