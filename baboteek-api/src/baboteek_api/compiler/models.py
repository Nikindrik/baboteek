from pydantic import BaseModel

class ErrorDetail(BaseModel):
    message: str
    row: int
    column: int
    token_value: str | None = None

class CompileResult(BaseModel):
    stage: str
    is_success: bool
    message: str | None = None
    errors: list[ErrorDetail] = []