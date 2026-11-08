from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


LightingClass = Literal["terang", "redup", "gelap"]
AIStatus = Literal[
    "belum_diproses",
    "diproses",
    "selesai",
    "perlu_tinjauan_manual",
    "gagal",
]
PhotoStatus = Literal["layak_dinilai", "tidak_layak", "perlu_tinjauan"]


class ValidationResponse(BaseModel):
    success: bool
    request_id: str | None = None
    ai_status: AIStatus
    photo_status: PhotoStatus | None = None
    lighting_class: LightingClass | None = None
    confidence: float | None = None
    model_version: str | None = None
    filename: str | None = None
    size_bytes: int | None = None
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    request_id: str | None = None
    ai_status: Literal["gagal"] = "gagal"
    error_code: str
    message: str
