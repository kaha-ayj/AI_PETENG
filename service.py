from typing import Dict, Any
from .config import CONFIG
from .yolo_detector import detect_objects
from .cnn_validator import validate_detection


def run_validation(request_payload: Dict[str, Any]) -> Dict[str, Any]:
    detection_result = detect_objects(request_payload["foto_url"], request_payload["kategori"])
    cnn_result = validate_detection(
        request_payload["kategori"],
        request_payload["tingkat_kegelapan_manual"],
        detection_result,
    )

    return {
        "hasil_validasi": cnn_result["hasil_validasi"],
        "tingkat_kegelapan_ai": cnn_result["tingkat_kegelapan_ai"],
        "objek_terdeteksi": detection_result["objects"],
        "cnn_confidence": cnn_result["cnn_confidence"],
        "yolo_confidence": detection_result["yolo_confidence"],
        "model_version": CONFIG.model_version,
        "catatan": cnn_result["catatan"],
    }
