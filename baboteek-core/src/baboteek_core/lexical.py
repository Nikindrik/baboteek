from __future__ import annotations

import io
from dataclasses import dataclass, field
from enum import Enum
from typing import TextIO


@dataclass(slots=True)
class Token:
    type_: str
    value: str
    row: int
    column: int
    length: int


@dataclass(slots=True)
class LexerError:
    type_: str
    message: str
    row: int
    column: int


@dataclass(slots=True)
class LexerResult:
    tokens: list[Token] = field(default_factory=list)
    errors: list[LexerError] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return len(self.errors) == 0


class LexerState(Enum):
    H = "H"
    ID = "ID"
    NUM = "NUM"
    COM = "COM"
    STR = "STR"
    DELIM = "DELIM"
    END = "END"


@dataclass(frozen=True, slots=True)
class LanguageRules:
    keywords: set[str]
    double_char_ops: set[str]
    tokens_map: dict[str, str]

    def get_operator_type(self, lexeme: str) -> str:
        return self.tokens_map.get(lexeme, "UNKNOWN")


class SourceReader:
    def __init__(self, source: str | TextIO, buffer_size: int = 4096) -> None:
        self.stream: TextIO = io.StringIO(source) if isinstance(source, str) else source
        self.buffer_size: int = buffer_size
        self.buffer: str = ""
        self.pos: int = 0

        self.row: int = 1
        self.col: int = 1
        self.current_char: str | None = None
        self._eof: bool = False

        self.advance()

    def _fill_buffer(self) -> None:
        if self._eof:
            return

        chunk = self.stream.read(self.buffer_size)
        if not chunk:
            self._eof = True
            self.buffer = ""
            self.pos = 0
        else:
            self.buffer = chunk
            self.pos = 0

    def advance(self) -> None:
        if self.current_char == "\n":
            self.row += 1
            self.col = 1
        elif self.current_char is not None:
            self.col += 1

        if self.pos >= len(self.buffer):
            self._fill_buffer()

        if self.pos < len(self.buffer):
            self.current_char = self.buffer[self.pos]
            self.pos += 1
        else:
            self.current_char = None

    def peek(self) -> str | None:
        if self.pos < len(self.buffer):
            return self.buffer[self.pos]

        if self._eof:
            return None

        chunk = self.stream.read(self.buffer_size)
        if not chunk:
            self._eof = True
            return None

        self.buffer = self.buffer[self.pos :] + chunk
        self.pos = 0
        return self.buffer[self.pos]


class StateHandler:
    def handle(self, analyzer: LexicalAnalyzer) -> None:
        raise NotImplementedError


class StateHHandler(StateHandler):
    def handle(self, analyzer: LexicalAnalyzer) -> None:
        char = analyzer.reader.current_char

        if char is None:
            analyzer.state = LexerState.END
            return

        if char.isspace():
            analyzer.reader.advance()
        elif char.isalpha():
            analyzer.state = LexerState.ID
        elif char.isdigit():
            analyzer.state = LexerState.NUM
        elif char == "'":
            analyzer.state = LexerState.STR
        elif char == "{":
            analyzer.state = LexerState.COM
        else:
            analyzer.state = LexerState.DELIM


class StateIDHandler(StateHandler):
    def handle(self, analyzer: LexicalAnalyzer) -> None:
        row, col = analyzer.reader.row, analyzer.reader.col
        lexeme = []

        while (char := analyzer.reader.current_char) and (char.isalnum() or char == "_"):
            lexeme.append(char)
            analyzer.reader.advance()

        value = "".join(lexeme)
        if value in analyzer.rules.keywords:
            analyzer.add_token("KEYWORD", value, row, col)
        else:
            analyzer.add_token("ID", value, row, col)

        analyzer.state = LexerState.H


class StateNumHandler(StateHandler):
    def handle(self, analyzer: LexicalAnalyzer) -> None:
        row, col = analyzer.reader.row, analyzer.reader.col
        lexeme: list[str] = []
        reader = analyzer.reader

        self._consume_digits(reader, lexeme, hex_allowed=True)

        is_real = False
        if reader.current_char == ".":
            is_real = True
            self._consume_fraction(reader, lexeme)

        if reader.current_char and reader.current_char in "Ee":
            is_real = True
            self._consume_exponent(reader, lexeme)

        if not is_real:
            self._consume_suffix(reader, lexeme)

        analyzer.add_token("NUMBER", "".join(lexeme), row, col)
        analyzer.state = LexerState.H

    def _consume_digits(self, reader: SourceReader, lexeme: list[str], *, hex_allowed: bool) -> None:
        while char := reader.current_char:
            if char.isdigit() or (hex_allowed and char in "ABCDEFabcdef"):
                lexeme.append(char)
                reader.advance()
            else:
                break

    def _consume_fraction(self, reader: SourceReader, lexeme: list[str]) -> None:
        if reader.current_char:
            lexeme.append(reader.current_char)
            reader.advance()
            self._consume_digits(reader, lexeme, hex_allowed=False)

    def _consume_exponent(self, reader: SourceReader, lexeme: list[str]) -> None:
        if reader.current_char:
            lexeme.append(reader.current_char)
            reader.advance()

        if reader.current_char and reader.current_char in "+-":
            lexeme.append(reader.current_char)
            reader.advance()

        self._consume_digits(reader, lexeme, hex_allowed=False)

    def _consume_suffix(self, reader: SourceReader, lexeme: list[str]) -> None:
        char = reader.current_char
        if not char:
            return

        if char in "Dd":
            lexeme.append(char)
            reader.advance()
        elif char in "Bb":
            lexeme.append(char)
            reader.advance()
            while (c := reader.current_char) and c in "01":
                lexeme.append(c)
                reader.advance()
        elif char in "Oo":
            lexeme.append(char)
            reader.advance()
            while (c := reader.current_char) and c in "01234567":
                lexeme.append(c)
                reader.advance()
        elif char in "Hh":
            lexeme.append(char)
            reader.advance()
            self._consume_digits(reader, lexeme, hex_allowed=True)


class StateStrHandler(StateHandler):
    def handle(self, analyzer: LexicalAnalyzer) -> None:
        row, col = analyzer.reader.row, analyzer.reader.col
        lexeme = ["'"]

        analyzer.reader.advance()

        while (char := analyzer.reader.current_char) and char != "'":
            lexeme.append(char)
            analyzer.reader.advance()

        if analyzer.reader.current_char is None:
            analyzer.add_error("UNCLOSED_TOKEN", "Unclosed string literal", row, col)
            analyzer.state = LexerState.END
            return

        if analyzer.reader.current_char == "'":
            lexeme.append("'")
            analyzer.reader.advance()

        analyzer.add_token("STRING", "".join(lexeme), row, col)
        analyzer.state = LexerState.H


class StateComHandler(StateHandler):
    def handle(self, analyzer: LexicalAnalyzer) -> None:
        row, col = analyzer.reader.row, analyzer.reader.col
        analyzer.reader.advance()

        while (char := analyzer.reader.current_char) and char != "}":
            analyzer.reader.advance()

        if analyzer.reader.current_char is None:
            analyzer.add_error("UNCLOSED_TOKEN", "Unclosed comment block", row, col)
            analyzer.state = LexerState.END
            return

        if analyzer.reader.current_char == "}":
            analyzer.reader.advance()

        analyzer.state = LexerState.H


class StateDelimHandler(StateHandler):
    def handle(self, analyzer: LexicalAnalyzer) -> None:
        row, col = analyzer.reader.row, analyzer.reader.col
        current_char = analyzer.reader.current_char or ""
        next_char = analyzer.reader.peek() or ""

        possible_double = current_char + next_char

        if possible_double in analyzer.rules.double_char_ops:
            lexeme = possible_double
            analyzer.reader.advance()
            analyzer.reader.advance()
        else:
            lexeme = current_char
            analyzer.reader.advance()

        if lexeme in analyzer.rules.keywords:
            analyzer.add_token("KEYWORD", lexeme, row, col)
        else:
            token_type = analyzer.rules.get_operator_type(lexeme)
            if token_type == "UNKNOWN":
                analyzer.add_error("UNEXPECTED_CHAR", f"Unexpected character: '{lexeme}'", row, col)
            else:
                analyzer.add_token(token_type, lexeme, row, col)

        analyzer.state = LexerState.H


class LexicalAnalyzer:
    def __init__(
        self,
        source: str | TextIO,
        rules: LanguageRules,
        handlers: dict[LexerState, StateHandler],
        buffer_size: int = 4096,
    ) -> None:
        self.reader = SourceReader(source, buffer_size)
        self.rules = rules
        self.handlers = handlers

        self.result = LexerResult()
        self.state: LexerState = LexerState.H

    def add_token(self, type_: str, value: str, row: int, col: int) -> None:
        self.result.tokens.append(Token(type_, value, row, col, len(value)))

    def add_error(self, type_: str, message: str, row: int, col: int) -> None:
        self.result.errors.append(LexerError(type_, message, row, col))

    def tokenize(self) -> LexerResult:
        while self.state != LexerState.END:
            handler = self.handlers.get(self.state)
            if not handler:
                raise RuntimeError(f"Internal bug: No handler registered for state {self.state}")

            handler.handle(self)

        return self.result


def create_default_lexer(source: str | TextIO, buffer_size: int = 4096) -> LexicalAnalyzer:
    rules = LanguageRules(
        keywords={
            "program",
            "var",
            "begin",
            "end",
            "if",
            "else",
            "while",
            "for",
            "to",
            "step",
            "next",
            "readln",
            "writeln",
            "true",
            "false",
            "%",
            "!",
            "$",
        },
        double_char_ops={":=", "==", "!=", "<=", ">=", "&&", "||"},
        tokens_map={
            **dict.fromkeys({":", ",", ";", ".", "(", ")", "{", "}"}, "DELIMITER"),
            **dict.fromkeys({":="}, "ASSIGN"),
            **dict.fromkeys({"+", "-", "||"}, "ADD_OP"),
            **dict.fromkeys({"*", "/", "&&"}, "MUL_OP"),
            **dict.fromkeys({"<", "<=", ">", ">=", "==", "!="}, "REL_OP"),
        },
    )

    handlers: dict[LexerState, StateHandler] = {
        LexerState.H: StateHHandler(),
        LexerState.ID: StateIDHandler(),
        LexerState.NUM: StateNumHandler(),
        LexerState.STR: StateStrHandler(),
        LexerState.COM: StateComHandler(),
        LexerState.DELIM: StateDelimHandler(),
    }

    return LexicalAnalyzer(source, rules=rules, handlers=handlers, buffer_size=buffer_size)
