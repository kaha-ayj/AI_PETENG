from __future__ import annotations

from io import BytesIO

from PIL import Image, UnidentifiedImageError

from app.core.config import (
    ALLOWED_IMAGE_TYPES,
    MAX_UPLOAD_SIZE_BYTES,
    MIN_IMAGE_HEIGHT,
    MIN_IMAGE_WIDTH,
)


class ImageValidationError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 400):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


def validate_image_bytes(
    image_bytes: bytes,
    content_type: str | None,
) -> tuple[int, int, str]:
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ImageValidationError(
            "UNSUPPORTED_MEDIA_TYPE",
            "Format foto harus JPG, PNG, atau WEBP.",
        )

    if not image_bytes:
        raise ImageValidationError("EMPTY_FILE", "Foto yang diunggah kosong.")

    if len(image_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise ImageValidationError(
            "FILE_TOO_LARGE",
            "Ukuran foto maksimal 10 MB.",
            status_code=413,
        )

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.verify()
        with Image.open(BytesIO(image_bytes)) as image:
            width, height = image.size
            actual_format = image.format or ""
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise ImageValidationError(
            "INVALID_IMAGE",
            "Isi file bukan gambar yang valid.",
        ) from error

    if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
        raise ImageValidationError(
            "IMAGE_TOO_SMALL",
            f"Resolusi foto minimal {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT} piksel.",
        )

    return width, height, actual_format
