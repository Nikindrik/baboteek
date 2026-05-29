from datetime import datetime

from pydantic import BaseModel


class CompileRequest(BaseModel):
    code: str


class ErrorDetail(BaseModel):
    message: str
    row: int
    column: int
    token_value: str | None = None


class CompileResultResponse(BaseModel):
    stage: str
    is_success: bool
    message: str | None = None
    errors: list[ErrorDetail] = []


class HistoryItemResponse(BaseModel):
    id: int
    code: str
    is_success: bool
    stage: str
    created_at: datetime

    class Config:
        from_attributes = True


class CodeExampleResponse(BaseModel):
    id: int
    title: str
    code: str
    description: str | None = None

    class Config:
        from_attributes = True


class CodeExampleCreate(BaseModel):
    title: str
    code: str
    description: str | None = None
