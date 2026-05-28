from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from baboteek_api.compiler.models import CompilationHistory
from baboteek_api.compiler.schemas import CompileRequest, CompileResultResponse, ErrorDetail


async def check_ip_limit(db: AsyncSession, ip_address: str) -> None:
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
    # 1. Если пользователь не авторизован, проверяем лимит по IP
    if user_id is None:
        await check_ip_limit(db, ip_address)

    core_result = run_compiler_pipeline(code_data.code)

    history_entry = CompilationHistory(
        user_id=user_id,
        ip_address=ip_address,
        code=code_data.code,
        is_success=core_result.is_success,
        stage=core_result.stage,
    )
    db.add(history_entry)
    await db.commit()

    return CompileResultResponse(
        stage=core_result.stage,
        is_success=core_result.is_success,
        message=core_result.message,
        errors=[
            ErrorDetail(message=e.message, row=e.row, column=e.column, token_value=e.token_value)
            for e in core_result.errors
        ],
    )


async def get_user_history(db: AsyncSession, user_id: int) -> list[CompilationHistory]:
    result = await db.execute(
        select(CompilationHistory)
        .where(CompilationHistory.user_id == user_id)
        .order_by(CompilationHistory.created_at.desc()),
    )
    return list(result.scalars().all())
