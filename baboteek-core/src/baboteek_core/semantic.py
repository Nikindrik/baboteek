from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SemanticError:
    message: str
    row: int
    column: int


@dataclass(slots=True)
class SemanticResult:
    is_success: bool = True
    errors: list[SemanticError] = field(default_factory=list)


class SymbolTable:
    def __init__(self):
        self._table: dict[str, str] = {"%": "%", "!": "!", "$": "$"}

    def declare(self, name: str, var_type: str):
        if name in self._table:
            raise KeyError(f"Variable '{name}' already declared.")
        self._table[name] = var_type

    def lookup(self, name: str) -> str:
        if name not in self._table:
            raise KeyError(f"Variable '{name}' is not declared.")
        return self._table[name]

    def update(self, name: str, var_type: str):
        self._table[name] = var_type


class SemanticAnalyzer:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.symbols = SymbolTable()
        self.result = SemanticResult()

    def _advance(self):
        self.pos += 1

    def _current(self) -> Token | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def analyze(self) -> SemanticResult:
        try:
            while not self._is_eof():
                token = self._current()
                match (token.type_, token.value):
                    case ("KEYWORD", "var"):
                        self._parse_var_decl()
                    case ("ID", _):
                        self._parse_assignment()
                    case _:
                        self._advance()
        except KeyError as e:
            self._add_error(str(e).strip("'"), self._current())
        except Exception as e:
            self._add_error(str(e), self._current())
        return self.result

    def _is_eof(self) -> bool:
        return self.pos >= len(self.tokens)

    def _add_error(self, message: str, token: Token | None):
        self.result.is_success = False
        row, col = (token.row, token.column) if token else (0, 0)
        self.result.errors.append(SemanticError(message, row, col))

    def _parse_var_decl(self):
        self._advance()  # skip var
        while (token := self._current()) and token.type_ == "ID":
            ids = []
            while (t := self._current()) and t.type_ == "ID":
                ids.append(t.value)
                self._advance()
                if self._current() and self._current().value == ",":
                    self._advance()

            self._expect("DELIMITER", ":")
            type_token = self._expect("KEYWORD")

            if type_token.value not in ["%", "!", "$"]:
                raise Exception(f"Invalid type: {type_token.value}")

            for i in ids:
                self.symbols.declare(i, type_token.value)
            self._expect("DELIMITER", ";")

    def _parse_assignment(self):
        var_token = self._expect("ID")
        var_type = self.symbols.lookup(var_token.value)
        self._expect("ASSIGN", ":=")
        expr_type = self._analyze_expression()

        if var_type != expr_type:
            raise Exception(f"Type mismatch: cannot assign {expr_type} to {var_type}")

    def _analyze_expression(self) -> str:
        """Упрощенная проверка типов выражений (возвращает итоговый тип)."""
        token = self._current()
        self._advance()

        if token.type_ == "ID":
            return self.symbols.lookup(token.value)
        if token.type_ == "NUMBER":
            return self._detect_num(token.value)
        if token.value in ("true", "false"):
            return "$"
        return "%"

    def _detect_num(self, val: str) -> str:
        if val.endswith(("b", "B", "o", "O", "h", "H", "d", "D")) or val.isdigit():
            return "%"
        return "!"

    def _expect(self, type_: str, val: str | None = None) -> Token:
        t = self._current()
        if t and t.type_ == type_ and (val is None or t.value == val):
            self._advance()
            return t
        raise Exception(f"Expected {val or type_}")
