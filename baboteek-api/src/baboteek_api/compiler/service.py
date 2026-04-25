from baboteek_core.lexical import create_default_lexer
from baboteek_core.syntax import SyntaxAnalyzer
from baboteek_core.semantic import SemanticAnalyzer
from baboteek_api.compiler.models import CompileResult, ErrorDetail


def run_compiler_pipeline(source_code: str) -> CompileResult:
    lexer = create_default_lexer(source_code)
    lex_res = lexer.tokenize()
    if not lex_res.is_success:
        return CompileResult(
            stage="lexical",
            is_success=False,
            errors=[
                ErrorDetail(
                    message=e.message, row=e.row, column=e.column, token_value=None
                )
                for e in lex_res.errors
            ],
        )

    parser = SyntaxAnalyzer(lex_res.tokens)
    syn_res = parser.parse()
    if not syn_res.is_success:
        return CompileResult(
            stage="syntax",
            is_success=False,
            errors=[
                ErrorDetail(
                    message=syn_res.error.message,
                    row=syn_res.error.row,
                    column=syn_res.error.column,
                    token_value=syn_res.error.token_value,
                )
            ],
        )

    sem = SemanticAnalyzer(lex_res.tokens)
    sem_res = sem.analyze()
    if not sem_res.is_success:
        return CompileResult(
            stage="semantic",
            is_success=False,
            errors=[
                ErrorDetail(message=e.message, row=e.row, column=e.column)
                for e in sem_res.errors
            ],
        )

    return CompileResult(
        stage="success", is_success=True, message="Compilation successful"
    )
