from pathlib import Path
import csv
import numpy as np
from PIL import Image

ROOT = Path.cwd()
DATASET = ROOT / "dataset_raw" / "public"
CSV_PATH = ROOT / "audit_dataset" / "chrome_download_history.csv"
DOWNLOADS = Path.home() / "Downloads"
OUTPUT = ROOT / "audit_dataset" / "kandidat_foto_mirip.csv"

def phash(path):
    with Image.open(path) as img:
        img = img.convert("L").resize((32, 32), Image.Resampling.LANCZOS)
        pixels = np.asarray(img, dtype=np.float64)

    n = 32
    x = np.arange(n)
    u = np.arange(n)
    matrix = np.cos(np.pi * (2 * x[None, :] + 1) * u[:, None] / (2 * n))
    matrix[0, :] *= np.sqrt(1 / n)
    matrix[1:, :] *= np.sqrt(2 / n)

    transformed = matrix @ pixels @ matrix.T
    low = transformed[:8, :8].flatten()[1:]
    median = np.median(low)

    result = 0
    for i, value in enumerate(low > median):
        if value:
            result |= 1 << i
    return result

def distance(a, b):
    return (a ^ b).bit_count()

with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

missing = [
    row for row in rows
    if not row.get("download_url", "").strip()
]

downloads = []
for path in DOWNLOADS.iterdir():
    if path.is_file() and path.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
        try:
            downloads.append((path, phash(path)))
        except Exception:
            pass

results = []

print(f"Foto yang perlu dicari : {len(missing)}")
print(f"Foto Downloads diperiksa: {len(downloads)}")

for row in missing:
    dataset_file = ROOT / row["dataset_file"]

    try:
        target_hash = phash(dataset_file)
    except Exception as e:
        print(f"Gagal membaca {dataset_file.name}: {e}")
        continue

    candidates = []
    for path, candidate_hash in downloads:
        score = distance(target_hash, candidate_hash)
        candidates.append((score, path))

    candidates.sort(key=lambda item: item[0])

    print(f"\n=== {dataset_file.name} ===")
    for score, path in candidates[:8]:
        print(f"Jarak {score:2} | {path.name}")

        results.append({
            "dataset_file": row["dataset_file"],
            "class_folder": row["class_folder"],
            "candidate_download_file": path.name,
            "phash_distance": score,
            "download_path": str(path),
        })

with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "dataset_file", "class_folder",
            "candidate_download_file",
            "phash_distance", "download_path"
        ]
    )
    writer.writeheader()
    writer.writerows(results)

print(f"\nHasil lengkap disimpan di: {OUTPUT}")
