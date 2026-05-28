from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from baboteek_api.auth.dependencies import get_current_user_optional, get_current_user_required
from baboteek_api.compiler import service
from baboteek_api.compiler.schemas import CompileRequest, CompileResultResponse, HistoryItemResponse
from baboteek_api.database import get_db
from baboteek_api.models import User

router = APIRouter(prefix="/compiler", tags=["compiler"])


@router.post("/compile", response_model=CompileResultResponse)
async def compile_code(
    request: CompileRequest,
    http_request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
):
    client_ip = http_request.client.host if http_request.client else "127.0.0.1"

    user_id = current_user.id if current_user else None

    result = await service.run_and_save(db=db, code_data=request, ip_address=client_ip, user_id=user_id)

    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.model_dump())

    return result


@router.get("/history")
async def get_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user_required)],
) -> list[HistoryItemResponse]:
    """Возвращает историю компиляций только для авторизованного пользователя."""
    return await service.get_user_history(db, current_user.id)
