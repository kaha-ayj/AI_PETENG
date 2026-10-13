from fastapi import FastAPI, HTTPException
from .schemas import ValidasiRequest, ValidasiResponse
from .service import run_validation


app = FastAPI(title="AI_PETENG", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/validasi", response_model=ValidasiResponse)
def validasi(request: ValidasiRequest) -> ValidasiResponse:
    result = run_validation(request.model_dump())
    return ValidasiResponse(status="sukses", data=result)
