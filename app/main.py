from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="AI PETENG API",
    description=(
        "Layanan AI untuk membantu validasi laporan "
        "jalan gelap dan klasifikasi tingkat pencahayaan."
    ),
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1/ai")


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "AI PETENG",
        "message": "AI PETENG API berjalan",
    }