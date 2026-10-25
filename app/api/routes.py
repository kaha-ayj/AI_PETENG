from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()

@router.post("/validate", tags=["AI Validation"])
async def validate_report(
    image: UploadFile = File(...),
):
    allowed_types = {"image/jpeg", "image/png", "image/webp"}

    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Format foto harus JPG, PNG, atau WEBP.",
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Foto yang diunggah kosong.",
        )

    max_size = 10 * 1024 * 1024

    if len(image_bytes) > max_size:
        raise HTTPException(
            status_code=413,
            detail="Ukuran foto maksimal 10 MB.",
        )

    return {
        "success": True,
        "message": (
            "Foto diterima. Model AI belum diimplementasikan."
        ),
        "filename": image.filename,
        "size_bytes": len(image_bytes),
        "ai_status": "belum_diproses",
        "lighting_level": None,
    }
