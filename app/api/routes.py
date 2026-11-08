from fastapi import APIRouter, File, UploadFile

from app.core.config import MODEL_PATH, MODEL_VERSION
from app.core.errors import error_response
from app.core.request_context import get_request_id
from app.schemas.prediction import ErrorResponse, ValidationResponse
from app.services.image_validation import ImageValidationError, validate_image_bytes
from app.services.prediction_service import (
    InferenceError,
    ModelUnavailableError,
    PredictionService,
)

router = APIRouter()
prediction_service = PredictionService()


@router.post(
    "/validate",
    tags=["AI Validation"],
    response_model=ValidationResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
async def validate_report(image: UploadFile = File(...)):
    image_bytes = await image.read()
    try:
        validate_image_bytes(image_bytes, image.content_type)
    except ImageValidationError as error:
        return error_response(error.status_code, error.error_code, error.message)

    try:
        result = prediction_service.predict(image_bytes)
    except ModelUnavailableError as error:
        return error_response(503, "MODEL_UNAVAILABLE", str(error))
    except InferenceError as error:
        return error_response(500, "INFERENCE_FAILED", str(error))

    return ValidationResponse(
        success=True,
        request_id=get_request_id(),
        filename=image.filename,
        size_bytes=len(image_bytes),
        **result,
    )


@router.get("/ready", tags=["Health"], response_model=dict)
def readiness_check():
    try:
        if not prediction_service.loaded:
            prediction_service.load()
    except ModelUnavailableError:
        return {
            "status": "not_ready",
            "model_loaded": False,
            "model_version": MODEL_VERSION,
            "model_path": str(MODEL_PATH),
        }
    return {
        "status": "ready",
        "model_loaded": True,
        "model_version": MODEL_VERSION,
    }
