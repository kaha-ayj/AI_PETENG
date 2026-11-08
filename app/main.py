import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.routes import router
from app.core.errors import request_validation_error_handler
from app.middleware import RequestContextMiddleware

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI PETENG API",
    description=(
        "Layanan AI untuk membantu validasi laporan "
        "jalan gelap dan klasifikasi tingkat pencahayaan."
    ),
    version="1.0.0",
)

app.add_exception_handler(RequestValidationError, request_validation_error_handler)
app.add_middleware(RequestContextMiddleware)
app.include_router(router, prefix="/api/v1/ai")


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "AI PETENG",
        "message": "AI PETENG API berjalan",
    }