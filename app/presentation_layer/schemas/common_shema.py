from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    error_code: int | None = None
