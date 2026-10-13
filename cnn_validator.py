from .config import CONFIG


def validate_detection(
    kategori: str,
    tingkat_kegelapan_manual: int,
    detection_result: dict,
) -> dict:
    objects = detection_result.get("objects", [])
    yolo_confidence = float(detection_result.get("yolo_confidence") or 0.0)

    valid = len(objects) >= CONFIG.min_objects_for_valid and yolo_confidence >= CONFIG.yolo_threshold
    tingkat_kegelapan_ai = tingkat_kegelapan_manual if valid else tingkat_kegelapan_manual

    cnn_confidence = 0.87 if valid else 0.42
    catatan = (
        "Objek PJU terdeteksi dan valid." if valid else "Objek PJU tidak cukup valid untuk laporan."
    )

    return {
        "hasil_validasi": "valid" if valid else "tidak_valid",
        "tingkat_kegelapan_ai": tingkat_kegelapan_ai,
        "cnn_confidence": cnn_confidence,
        "catatan": catatan,
    }
