from baboteek_core.lexical import create_default_lexer
from baboteek_core.semantic import SemanticAnalyzer
from baboteek_core.syntax import SyntaxAnalyzer
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from baboteek_api.compiler.models import CompilationHistory
from baboteek_api.compiler.schemas import CompileRequest, CompileResultResponse, ErrorDetail, HistoryItemResponse


def _run_compiler_pipeline(source_code: str) -> CompileResultResponse:
    """Внутренний оркестратор, собирающий пайплайн из ядра компилятора."""

    lexer = create_default_lexer(source_code)
    lex_res = lexer.tokenize()
    if not lex_res.is_success:
        return CompileResultResponse(
            stage="lexical",
            is_success=False,
            errors=[
                ErrorDetail(message=e.message, row=e.row, column=e.column, token_value=None) for e in lex_res.errors
            ],
        )

    parser = SyntaxAnalyzer(lex_res.tokens)
    syn_res = parser.parse()
    if not syn_res.is_success:
        err = syn_res.error
        return CompileResultResponse(
            stage="syntax",
            is_success=False,
            errors=[ErrorDetail(message=err.message, row=err.row, column=err.column, token_value=err.token_value)],
        )

    sem = SemanticAnalyzer(lex_res.tokens)
    sem_res = sem.analyze()
    if not sem_res.is_success:
        return CompileResultResponse(
            stage="semantic",
            is_success=False,
            errors=[
                ErrorDetail(message=e.message, row=e.row, column=e.column, token_value=None) for e in sem_res.errors
            ],
        )

    return CompileResultResponse(stage="success", is_success=True, message="Compilation successful", errors=[])


async def check_ip_limit(db: AsyncSession, ip_address: str) -> None:
    """Проверяет лимит в 5 бесплатных попыток для гостя."""
    result = await db.execute(
        select(func.count(CompilationHistory.id))
        .where(CompilationHistory.ip_address == ip_address)
        .where(CompilationHistory.user_id.is_(None)),
    )
    count = result.scalar() or 0
    if count >= 5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Free compilation limit reached. Please register to continue.",
        )


async def run_and_save(
    db: AsyncSession,
    code_data: CompileRequest,
    ip_address: str,
    user_id: int | None = None,
) -> CompileResultResponse:
    # 1. Если гость, проверяем лимит
    if user_id is None:
        await check_ip_limit(db, ip_address)

    # 2. Запуск локального пайплайна
    result = _run_compiler_pipeline(code_data.code)

    # 3. Сохранение попытки в БД
    history_entry = CompilationHistory(
        user_id=user_id,
        ip_address=ip_address,
        code=code_data.code,
        is_success=result.is_success,
        stage=result.stage,
    )
    db.add(history_entry)
    await db.commit()

    return result


async def get_user_history(db: AsyncSession, user_id: int) -> list[HistoryItemResponse]:
    result = await db.execute(
        select(CompilationHistory)
        .where(CompilationHistory.user_id == user_id)
        .order_by(CompilationHistory.created_at.desc()),
    )
    db_history = result.scalars().all()
    return [HistoryItemResponse.model_validate(item) for item in db_history]
