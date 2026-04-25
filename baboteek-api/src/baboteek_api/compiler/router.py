from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from baboteek_api.compiler.service import run_compiler_pipeline
from baboteek_api.compiler.models import CompileResult

router = APIRouter(prefix="/compiler", tags=["compiler"])


class CompileRequest(BaseModel):
    code: str


@router.post("/compile", response_model=CompileResult)
async def compile_code(request: CompileRequest):
    result = run_compiler_pipeline(request.code)

    if not result.is_success:
        raise HTTPException(status_code=400, detail=result.model_dump())

    return result
