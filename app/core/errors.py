from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.request_context import get_request_id
from app.schemas.prediction import ErrorResponse


def error_response(status_code: int, error_code: str, message: str) -> JSONResponse:
    payload = ErrorResponse(
        request_id=get_request_id(),
        error_code=error_code,
        message=message,
    ).model_dump()
    return JSONResponse(status_code=status_code, content=payload)


async def request_validation_error_handler(
    _request: Request,
    _error: RequestValidationError,
) -> JSONResponse:
    return error_response(
        status_code=400,
        error_code="INVALID_REQUEST",
        message="Request tidak valid.",
    )
