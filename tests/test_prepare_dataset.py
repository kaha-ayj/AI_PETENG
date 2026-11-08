from pathlib import Path

from PIL import Image

from scripts.prepare_dataset import prepare_dataset


def create_source(root: Path) -> None:
    for label_index, label in enumerate(("bukan_jalan", "terang", "redup", "gelap")):
        directory = root / label
        directory.mkdir(parents=True)
        for index in range(4):
            Image.new("RGB", (32, 32), color=(label_index * 50, index * 20, 40)).save(
                directory / f"{label}_{index}.jpg",
                format="JPEG",
            )


def test_prepare_dataset_creates_reproducible_split(tmp_path):
    source = tmp_path / "dataset_raw" / "public"
    output = tmp_path / "dataset"
    artifacts = tmp_path / "artifacts"
    create_source(source)

    first = prepare_dataset(source, output, artifacts, seed=42)
    first_manifest = (artifacts / "dataset_manifest.csv").read_text(encoding="utf-8-sig")

    output2 = tmp_path / "dataset2"
    artifacts2 = tmp_path / "artifacts2"
    second = prepare_dataset(source, output2, artifacts2, seed=42)
    second_manifest = (artifacts2 / "dataset_manifest.csv").read_text(encoding="utf-8-sig")

    assert len(first) == 16
    assert [record.split for record in first].count("train") == 8
    assert [record.split for record in first].count("val") == 4
    assert [record.split for record in first].count("test") == 4
    assert first_manifest == second_manifest
    assert len({record.sha256 for record in first}) == 16
    assert all((output / record.split / record.label / Path(record.source_path).name).exists() for record in first)
