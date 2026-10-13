from pydantic import BaseModel, Field
from typing import List, Optional


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class DetectedObject(BaseModel):
    label: str
    confidence: float
    bbox: BoundingBox


class ValidasiRequest(BaseModel):
    id_laporan: str
    foto_url: str
    kategori: str
    tingkat_kegelapan_manual: int = Field(ge=1, le=3)


class ValidasiData(BaseModel):
    hasil_validasi: str
    tingkat_kegelapan_ai: int
    objek_terdeteksi: List[DetectedObject]
    cnn_confidence: Optional[float]
    yolo_confidence: Optional[float]
    model_version: str
    catatan: str


class ValidasiResponse(BaseModel):
    status: str
    data: ValidasiData
