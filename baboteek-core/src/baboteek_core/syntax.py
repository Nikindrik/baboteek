from __future__ import annotations

from dataclasses import dataclass

from baboteek_core.lexical import Token


class ParseError(Exception):
    def __init__(self, message: str, token: Token | None):
        super().__init__(message)
        self.message = message
        self.token = token


@dataclass(slots=True)
class ParserErrorMetadata:
    message: str
    row: int
    column: int
    token_value: str


@dataclass(slots=True)
class ParserResult:
    is_success: bool = True
    error: ParserErrorMetadata | None = None


class TokenStream:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.position = 0

    @property
    def is_eof(self) -> bool:
        return self.position >= len(self.tokens)

    def current(self) -> Token | None:
        return None if self.is_eof else self.tokens[self.position]

    def advance(self) -> None:
        if not self.is_eof:
            self.position += 1

    def expect(self, token_type: str, value: str | None = None) -> Token:
        token = self.current()
        if token is None:
            raise ParseError(
                f"Unexpected EOF. Expected {token_type} '{value or ''}'", None
            )

        if token.type_ == token_type and (value is None or token.value == value):
            self.advance()
            return token

        expected = f"{token_type} '{value}'" if value else token_type
        raise ParseError(
            f"Expected {expected}, but got {token.type_} '{token.value}'", token
        )


class ExpressionParser:
    def __init__(self, stream: TokenStream) -> None:
        self.stream = stream

    def parse_expression(self) -> None:
        self.parse_term()
        while (token := self.stream.current()) and token.type_ in {"ADD_OP", "REL_OP"}:
            self.stream.advance()
            self.parse_term()

    def parse_term(self) -> None:
        self.parse_factor()
        while (token := self.stream.current()) and token.type_ == "MUL_OP":
            self.stream.advance()
            self.parse_factor()

    def parse_factor(self) -> None:
        token = self.stream.current()
        if not token:
            raise ParseError("Unexpected EOF in expression", None)

        match (token.type_, token.value):
            case ("ID" | "STRING", _):
                self.stream.advance()
            case ("NUMBER", _):
                self._parse_number()
            case ("DELIMITER", "("):
                self.stream.expect("DELIMITER", "(")
                self.parse_expression()
                self.stream.expect("DELIMITER", ")")
            case ("KEYWORD", "true" | "false"):
                self.stream.advance()
            case ("ADD_OP", "+" | "-"):
                self.stream.advance()
                self.parse_factor()
            case _:
                raise ParseError(
                    f"Unexpected token in expression: '{token.value}'", token
                )

    def _parse_number(self) -> None:
        token = self.stream.current()
        if not token:
            return

        if (
            self._is_binary(token)
            or self._is_octal(token)
            or self._is_decimal(token)
            or self._is_hexadecimal(token)
            or self._is_real(token)
        ):
            self.stream.advance()
        else:
            raise ParseError(f"Invalid number format: '{token.value}'", token)

    def _is_binary(self, t: Token) -> bool:
        return t.value.endswith(("b", "B")) and all(c in "01" for c in t.value[:-1])

    def _is_octal(self, t: Token) -> bool:
        return t.value.endswith(("o", "O")) and all(
            c in "01234567" for c in t.value[:-1]
        )

    def _is_decimal(self, t: Token) -> bool:
        return t.value.isdigit() or (
            t.value.endswith(("d", "D")) and t.value[:-1].isdigit()
        )

    def _is_hexadecimal(self, t: Token) -> bool:
        return t.value.endswith(("h", "H")) and all(
            c in "0123456789ABCDEFabcdef" for c in t.value[:-1]
        )

    def _is_real(self, t: Token) -> bool:
        try:
            float(t.value)
            return True
        except ValueError:
            return False


class StatementParser:
    def __init__(self, stream: TokenStream, expr_parser: ExpressionParser) -> None:
        self.stream = stream
        self.expr_parser = expr_parser

    def parse_statements(self) -> None:
        while token := self.stream.current():
            match (token.type_, token.value):
                case ("KEYWORD", "begin"):
                    self._parse_compound_statement()
                case ("ID", _):
                    self._parse_assignment()
                case ("KEYWORD", "readln"):
                    self._parse_io_statement("readln")
                case ("KEYWORD", "writeln"):
                    self._parse_io_statement("writeln", is_expr=True)
                case ("KEYWORD", "if"):
                    self._parse_if_else()
                case ("KEYWORD", "for"):
                    self._parse_for_loop()
                case ("KEYWORD", "while"):
                    self._parse_while_loop()
                case ("KEYWORD", "next") | ("DELIMITER", ";"):
                    self.stream.advance()
                case ("KEYWORD", "end"):
                    return
                case _:
                    raise ParseError(
                        f"Unexpected statement start: '{token.value}'", token
                    )

    def _parse_compound_statement(self) -> None:
        self.stream.expect("KEYWORD", "begin")
        self.parse_statements()
        self.stream.expect("KEYWORD", "end")

    def _parse_assignment(self) -> None:
        self.stream.expect("ID")
        self.stream.expect("ASSIGN", ":=")
        self.expr_parser.parse_expression()

    def _parse_io_statement(self, keyword: str, is_expr: bool = False) -> None:
        self.stream.expect("KEYWORD", keyword)
        if is_expr:
            self.expr_parser.parse_expression()
        else:
            self.stream.expect("ID")

        while (
            (token := self.stream.current())
            and token.type_ == "DELIMITER"
            and token.value == ","
        ):
            self.stream.expect("DELIMITER", ",")
            if is_expr:
                self.expr_parser.parse_expression()
            else:
                self.stream.expect("ID")

    def _parse_if_else(self) -> None:
        self.stream.expect("KEYWORD", "if")
        self.stream.expect("DELIMITER", "(")
        self.expr_parser.parse_expression()
        self.stream.expect("DELIMITER", ")")
        self._parse_compound_statement()

        if (
            (token := self.stream.current())
            and token.type_ == "KEYWORD"
            and token.value == "else"
        ):
            self.stream.advance()
            self._parse_compound_statement()

    def _parse_for_loop(self) -> None:
        self.stream.expect("KEYWORD", "for")
        self._parse_assignment()
        self.stream.expect("KEYWORD", "to")
        self.expr_parser.parse_expression()

        if (t := self.stream.current()) and t.type_ == "KEYWORD" and t.value == "step":
            self.stream.expect("KEYWORD", "step")
            self.expr_parser.parse_expression()

        self.stream.expect("KEYWORD", "begin")
        while token := self.stream.current():
            if token.type_ == "KEYWORD" and token.value == "next":
                self.stream.advance()
            elif token.type_ == "KEYWORD" and token.value == "end":
                break
            else:
                self.parse_statements()
        self.stream.expect("KEYWORD", "end")

    def _parse_while_loop(self) -> None:
        self.stream.expect("KEYWORD", "while")
        self.stream.expect("DELIMITER", "(")
        self.expr_parser.parse_expression()
        self.stream.expect("DELIMITER", ")")
        self._parse_compound_statement()


class DeclarationParser:
    def __init__(self, stream: TokenStream, stmt_parser: StatementParser) -> None:
        self.stream = stream
        self.stmt_parser = stmt_parser

    def parse_program(self) -> None:
        self.stream.expect("KEYWORD", "program")
        self.stream.expect("KEYWORD", "var")
        self._parse_var_decl()
        self.stream.expect("KEYWORD", "begin")
        self.stmt_parser.parse_statements()
        self.stream.expect("KEYWORD", "end")
        self.stream.expect("DELIMITER", ".")

    def _parse_var_decl(self) -> None:
        while True:
            self.stream.expect("ID")
            while (
                (token := self.stream.current())
                and token.type_ == "DELIMITER"
                and token.value == ","
            ):
                self.stream.expect("DELIMITER", ",")
                self.stream.expect("ID")

            self.stream.expect("DELIMITER", ":")
            self.stream.expect("KEYWORD")  # Тип данных
            self.stream.expect("DELIMITER", ";")

            if not (token := self.stream.current()) or token.type_ != "ID":
                break


class SyntaxAnalyzer:
    def __init__(self, tokens: list[Token]) -> None:
        self.stream = TokenStream(tokens)
        self.expr_parser = ExpressionParser(self.stream)
        self.stmt_parser = StatementParser(self.stream, self.expr_parser)
        self.decl_parser = DeclarationParser(self.stream, self.stmt_parser)

        self.result = ParserResult()

    def parse(self) -> ParserResult:
        if not self.stream.tokens:
            self.result.is_success = False
            self.result.error = ParserErrorMetadata("No tokens to parse", 0, 0, "")
            return self.result

        try:
            self.decl_parser.parse_program()
        except ParseError as e:
            self.result.is_success = False
            if e.token:
                self.result.error = ParserErrorMetadata(
                    e.message, e.token.row, e.token.column, e.token.value
                )
            else:
                last = self.stream.tokens[-1]
                self.result.error = ParserErrorMetadata(
                    e.message, last.row, last.column, "EOF"
                )

        return self.result
