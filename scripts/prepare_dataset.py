r"""Prepare a reproducible train/validation/test dataset from dataset_raw.

Usage:
    .venv\Scripts\python.exe scripts/prepare_dataset.py
    .venv\Scripts\python.exe scripts/prepare_dataset.py --overwrite

The source images are never moved or modified. The command copies them into
``dataset/{train,val,test}`` and writes manifests under ``artifacts``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
CLASSES = ("bukan_jalan", "terang", "redup", "gelap")
SPLITS = ("train", "val", "test")


@dataclass(frozen=True)
class ImageRecord:
    image_id: str
    label: str
    split: str
    source_path: str
    destination_path: str
    sha256: str
    source_file: Path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_images(source_root: Path) -> dict[str, list[Path]]:
    images: dict[str, list[Path]] = {}
    for label in CLASSES:
        class_dir = source_root / label
        if not class_dir.is_dir():
            raise FileNotFoundError(f"Folder kelas tidak ditemukan: {class_dir}")
        files = sorted(
            path for path in class_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        )
        if len(files) < 3:
            raise ValueError(f"Kelas {label!r} membutuhkan minimal 3 gambar.")
        images[label] = files
    return images


def split_counts(total: int) -> dict[str, int]:
    test_count = max(1, round(total * 0.15))
    val_count = max(1, round(total * 0.15))
    train_count = total - val_count - test_count
    if train_count < 1:
        raise ValueError(f"Jumlah gambar terlalu sedikit untuk split: {total}")
    return {"train": train_count, "val": val_count, "test": test_count}


def build_records(
    images: dict[str, list[Path]],
    source_root: Path,
    output_root: Path,
    seed: int,
) -> list[ImageRecord]:
    rng = random.Random(seed)
    records: list[ImageRecord] = []

    for label in CLASSES:
        files = list(images[label])
        rng.shuffle(files)
        counts = split_counts(len(files))
        cursor = 0
        for split in SPLITS:
            for source_path in files[cursor:cursor + counts[split]]:
                digest = file_sha256(source_path)
                image_id = f"img_{digest[:12]}"
                destination = output_root / split / label / source_path.name
                records.append(ImageRecord(
                    image_id=image_id,
                    label=label,
                    split=split,
                    source_path=source_path.relative_to(source_root.parent.parent).as_posix(),
                    destination_path=destination.relative_to(output_root).as_posix(),
                    sha256=digest,
                    source_file=source_path,
                ))
            cursor += counts[split]

    return records


def write_manifests(records: list[ImageRecord], artifacts_root: Path, seed: int) -> None:
    artifacts_root.mkdir(parents=True, exist_ok=True)
    manifest_path = artifacts_root / "dataset_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8-sig") as file:
        fieldnames = list(asdict(records[0])) if records else []
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(
            {key: value for key, value in asdict(record).items() if key != "source_file"}
            for record in records
        )

    summary: dict[str, dict[str, int]] = {split: {label: 0 for label in CLASSES} for split in SPLITS}
    for record in records:
        summary[record.split][record.label] += 1
    (artifacts_root / "dataset_split_summary.json").write_text(
        json.dumps({"seed": seed, "counts": summary}, indent=2),
        encoding="utf-8",
    )


def prepare_dataset(
    source_root: Path = Path("dataset_raw/public"),
    output_root: Path = Path("dataset"),
    artifacts_root: Path = Path("artifacts"),
    seed: int = 2026,
    overwrite: bool = False,
) -> list[ImageRecord]:
    images = collect_images(source_root)
    records = build_records(images, source_root, output_root, seed)

    if output_root.exists() and any(path.is_file() for path in output_root.rglob("*")) and not overwrite:
        raise FileExistsError(
            f"Output {output_root} tidak kosong. Gunakan --overwrite untuk mengganti hasil split."
        )

    if overwrite and output_root.exists():
        shutil.rmtree(output_root)

    for record in records:
        destination = output_root / record.destination_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(record.source_file, destination)

    write_manifests(records, artifacts_root, seed)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("dataset_raw/public"))
    parser.add_argument("--output", type=Path, default=Path("dataset"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts"))
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    records = prepare_dataset(
        source_root=args.source,
        output_root=args.output,
        artifacts_root=args.artifacts,
        seed=args.seed,
        overwrite=args.overwrite,
    )
    print(f"Berhasil menyiapkan {len(records)} gambar.")
    print(f"Manifest: {args.artifacts / 'dataset_manifest.csv'}")
    print(f"Ringkasan: {args.artifacts / 'dataset_split_summary.json'}")


if __name__ == "__main__":
    main()
