"""Audit gambar dataset AI PETENG tanpa mengubah file sumber.

Pemakaian:
    python cek_dataset.py
    python cek_dataset.py --output-dir audit_dataset

Audit memeriksa file gambar secara rekursif pada dataset_raw dan dataset.
Label yang dilaporkan hanya label sementara berdasarkan nama folder; audit tidak
memverifikasi kesesuaian visual label tersebut.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
DATASET_ROOTS = (Path("dataset_raw"), Path("dataset"))
EXPECTED_SPLITS = ("train", "val", "test")
EXPECTED_CLASSES = ("terang", "redup", "gelap")
CURATION_FIELDS = [
    "image_id", "path_relative", "source_type", "source_reference", "license",
    "temporary_class", "confirmed_class", "road_relevance", "photo_quality",
    "review_status", "reviewer", "reviewed_at", "review_notes",
    "audit_read_status", "format", "width", "height", "size_bytes", "sha256",
]
VALID_REVIEW_STATUSES = {"belum_ditinjau", "diterima", "ditolak", "perlu_tinjauan"}


def relative_path(path: Path) -> str:
    return path.as_posix()


def temporary_class(path: Path, root: Path) -> str | None:
    """Ambil nama folder kelas langsung di bawah root split/source."""
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return None
    return parts[1] if len(parts) >= 2 else None


def exact_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frame_count(path: Path) -> int | None:
    try:
        with Image.open(path) as image:
            count = 0
            while True:
                try:
                    image.seek(count)
                    count += 1
                except EOFError:
                    return count
    except Exception:
        return None


def audit_file(path: Path, root: Path) -> dict[str, Any]:
    item: dict[str, Any] = {
        "path": relative_path(path),
        "root": relative_path(root),
        "temporary_class": temporary_class(path, root),
        "extension": path.suffix.lower(),
        "format": None,
        "frame_count": None,
        "width": None,
        "height": None,
        "size_bytes": path.stat().st_size,
        "read_status": "ok",
        "error": None,
        "sha256": None,
        "manual_review_required": True,
        "manual_review_reason": "Label folder dan relevansi visual belum dikonfirmasi manusia.",
    }

    try:
        item["sha256"] = exact_hash(path)
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            item["format"] = image.format
            item["frame_count"] = frame_count(path)
            item["width"], item["height"] = image.size
    except Exception as error:  # Pillow dapat melempar beberapa tipe error.
        item["read_status"] = "failed"
        item["error"] = str(error)
        item["manual_review_reason"] = "File gagal dibaca oleh Pillow."

    return item


def collect_files() -> list[tuple[Path, Path]]:
    files: list[tuple[Path, Path]] = []
    for root in DATASET_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                files.append((path, root))
    return files


def build_report() -> dict[str, Any]:
    records = [audit_file(path, root) for path, root in collect_files()]
    by_hash: defaultdict[str, list[str]] = defaultdict(list)
    for record in records:
        if record["sha256"]:
            by_hash[record["sha256"]].append(record["path"])

    duplicate_groups = [paths for paths in by_hash.values() if len(paths) > 1]
    counts: dict[str, dict[str, int]] = {}
    for root in DATASET_ROOTS:
        root_records = [r for r in records if r["root"] == relative_path(root)]
        counts[relative_path(root)] = dict(Counter(
            r["temporary_class"] or "(kelas_tidak_ditemukan)" for r in root_records
        ))

    empty_expected: list[str] = []
    for root_name, root in (("dataset_raw/own", Path("dataset_raw/own")),
                            ("dataset_raw/public", Path("dataset_raw/public"))):
        for class_name in EXPECTED_CLASSES:
            folder = root / class_name
            if not folder.exists() or not any(
                p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS for p in folder.rglob("*")
            ):
                empty_expected.append(f"{root_name}/{class_name}")
    for split in EXPECTED_SPLITS:
        for class_name in EXPECTED_CLASSES:
            folder = Path("dataset") / split / class_name
            if not folder.exists() or not any(
                p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS for p in folder.rglob("*")
            ):
                empty_expected.append(f"dataset/{split}/{class_name}")

    return {
        "audit_scope": [relative_path(root) for root in DATASET_ROOTS],
        "supported_extensions": sorted(IMAGE_EXTENSIONS),
        "total_images": len(records),
        "readable_images": sum(r["read_status"] == "ok" for r in records),
        "failed_images": sum(r["read_status"] == "failed" for r in records),
        "counts_by_root_and_temporary_class": counts,
        "empty_expected_class_folders": empty_expected,
        "duplicate_method": "SHA-256 hash of original file bytes; detects exact byte duplicates only.",
        "duplicate_limitations": "It does not detect resized, recompressed, re-encoded, or visually similar images.",
        "exact_duplicate_groups": duplicate_groups,
        "records": records,
        "format_notes": [
            "Ekstensi file menunjukkan nama akhiran, sedangkan format adalah format aktual yang dibaca Pillow.",
            "File .jpg dengan format MPO bukan otomatis rusak; MPO dapat memiliki beberapa frame.",
            "Frame pertama digunakan hanya untuk inspeksi metadata; tidak ada frame yang diekspor atau diubah.",
        ],
        "warnings": [
            "temporary_class is inferred from the folder name and is not a confirmed visual label.",
            "All readable images require human review for relevance, label, source, and license.",
        ],
    }


def source_type(path: str) -> str:
    parts = Path(path).parts
    if len(parts) >= 2 and parts[0] == "dataset_raw" and parts[1] in {"public", "own"}:
        return parts[1]
    return "unknown"


def image_id(record: dict[str, Any]) -> str:
    digest = record.get("sha256") or hashlib.sha256(record["path"].encode()).hexdigest()
    return f"img_{digest[:12]}"


def build_curation_records(report: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for record in report["records"]:
        records.append({
            "image_id": image_id(record),
            "path_relative": record["path"],
            "source_type": source_type(record["path"]),
            "source_reference": "",
            "license": "",
            "temporary_class": record["temporary_class"] or "",
            "confirmed_class": "",
            "road_relevance": "",
            "photo_quality": "",
            "review_status": "belum_ditinjau",
            "reviewer": "",
            "reviewed_at": "",
            "review_notes": "",
            "audit_read_status": record["read_status"],
            "format": record["format"] or "",
            "width": record["width"] or "",
            "height": record["height"] or "",
            "size_bytes": record["size_bytes"],
            "sha256": record["sha256"] or "",
        })
    return records


def write_outputs(report: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "dataset_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    fields = [
        "path", "root", "temporary_class", "extension", "format", "frame_count", "width",
        "height", "size_bytes", "read_status", "error", "sha256",
        "manual_review_required", "manual_review_reason",
    ]
    with (output_dir / "dataset_audit.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(report["records"])

    curation_records = build_curation_records(report)
    with (output_dir / "dataset_curation_template.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=CURATION_FIELDS)
        writer.writeheader()
        writer.writerows(curation_records)


def show_gallery() -> None:
    import matplotlib.pyplot as plt

    images = []
    for path, _root in collect_files():
        try:
            with Image.open(path) as image:
                image.seek(0)
                preview = ImageOps.exif_transpose(image).convert("RGB")
                preview.thumbnail((900, 700))
                images.append((path, preview.copy()))
        except Exception as error:
            print(f"Gagal menampilkan {path}: {error}")

    if not images:
        print("Tidak ada gambar yang dapat ditampilkan.")
        return

    figure, axes = plt.subplots(len(images), 1, figsize=(12, 6 * len(images)), squeeze=False)
    for axis, (path, image) in zip(axes[:, 0], images):
        axis.imshow(image)
        axis.set_title(f"Frame 0 | {path}")
        axis.axis("off")
    figure.tight_layout()
    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit dataset AI PETENG tanpa mengubah data asli.")
    parser.add_argument("--output-dir", type=Path, default=Path("audit_dataset"))
    parser.add_argument("--gallery", action="store_true", help="Tampilkan frame pertama setiap gambar untuk review manual.")
    args = parser.parse_args()
    report = build_report()
    write_outputs(report, args.output_dir)
    if args.gallery:
        show_gallery()
    print(json.dumps({k: report[k] for k in (
        "total_images", "readable_images", "failed_images",
        "counts_by_root_and_temporary_class", "empty_expected_class_folders",
        "exact_duplicate_groups",
    )}, indent=2, ensure_ascii=False))
    print(f"Laporan JSON: {args.output_dir / 'dataset_audit.json'}")
    print(f"Laporan CSV : {args.output_dir / 'dataset_audit.csv'}")


if __name__ == "__main__":
    main()
