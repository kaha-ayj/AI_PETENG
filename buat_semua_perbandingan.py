from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import csv
import textwrap

ROOT = Path.cwd()
HISTORY = ROOT / "audit_dataset" / "wikimedia_chrome_history.csv"
DATASET = ROOT / "dataset_raw" / "public"
DOWNLOADS = Path.home() / "Downloads"

OUTPUT = ROOT / "audit_dataset" / "semua_unduhan_wikimedia.jpg"
CSV_OUTPUT = ROOT / "audit_dataset" / "daftar_kandidat_wikimedia.csv"

targets = [
    ("T1 - gelap_001", DATASET / "gelap/pub_gelap_001.jpg"),
    ("T2 - gelap_002", DATASET / "gelap/pub_gelap_002.jpg"),
    ("T3 - redup_001", DATASET / "redup/pub_redup_001.jpg"),
    ("T4 - terang_001", DATASET / "terang/pub_terang_001.jpg"),
]

with open(HISTORY, newline="", encoding="utf-8-sig") as f:
    history = list(csv.DictReader(f))

candidates = []
seen = set()

for row in history:
    if row.get("record_type") != "download":
        continue

    possible_paths = [
        row.get("target_path", ""),
        row.get("current_path", ""),
    ]

    path = next(
        (Path(p) for p in possible_paths if p and Path(p).is_file()),
        None
    )

    if path is None:
        continue

    if path.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
        continue

    key = str(path.resolve()).lower()
    if key in seen:
        continue

    try:
        with Image.open(path) as img:
            img.verify()
    except Exception:
        continue

    seen.add(key)

    candidates.append({
        "id": f"D{len(candidates)+1:02d}",
        "filename": path.name,
        "path": path,
        "timestamp": row.get("timestamp", ""),
        "url": row.get("url", ""),
    })

# Simpan daftar ID dan URL sumber
CSV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(CSV_OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "id", "filename", "path", "timestamp", "url"
        ]
    )
    writer.writeheader()

    for item in candidates:
        writer.writerow({
            "id": item["id"],
            "filename": item["filename"],
            "path": str(item["path"]),
            "timestamp": item["timestamp"],
            "url": item["url"],
        })

# Pengaturan lembar gambar
try:
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
except OSError:
    font = ImageFont.load_default()
    title_font = font

margin = 20
gap = 12
cols = 5
cell_w = 220
cell_h = 165
target_h = 225

width = margin * 2 + cols * cell_w + (cols - 1) * gap
candidate_rows = (len(candidates) + cols - 1) // cols
candidate_start = margin + 275

height = (
    candidate_start
    + candidate_rows * cell_h
    + max(0, candidate_rows - 1) * gap
    + margin
)

sheet = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(sheet)

def add_image(path, x, y, w, h):
    try:
        with Image.open(path) as original:
            img = ImageOps.exif_transpose(original).convert("RGB")
            img.thumbnail((w - 8, h - 8))

        px = x + (w - img.width) // 2
        py = y + (h - img.height) // 2

        sheet.paste(img, (px, py))
        draw.rectangle((x, y, x + w, y + h), outline="gray")
    except Exception:
        draw.text((x + 5, y + 5), "Gagal membaca gambar", fill="red")

draw.text(
    (margin, margin),
    "4 FOTO DATASET - PERBANDINGAN SUMBER WIKIMEDIA",
    fill="black",
    font=title_font
)

# Empat foto dataset di bagian atas
target_w = (width - 2 * margin - 3 * gap) // 4

for i, (label, path) in enumerate(targets):
    x = margin + i * (target_w + gap)
    y = margin + 40

    draw.text((x, y), label, fill="blue", font=font)
    add_image(path, x, y + 22, target_w, target_h - 22)

# Semua foto unduhan Wikimedia
draw.text(
    (margin, candidate_start - 28),
    f"KANDIDAT UNDUHAN WIKIMEDIA ({len(candidates)} FOTO)",
    fill="darkgreen",
    font=title_font
)

for i, item in enumerate(candidates):
    col = i % cols
    row = i // cols

    x = margin + col * (cell_w + gap)
    y = candidate_start + row * (cell_h + gap)

    label = f'{item["id"]} | {item["filename"]}'
    label = textwrap.shorten(label, width=31, placeholder="...")

    draw.text((x, y), label, fill="darkgreen", font=font)
    add_image(item["path"], x, y + 22, cell_w, 135)

sheet.save(OUTPUT, quality=92)

print("\n========== HASIL ==========")
print(f"Foto Wikimedia berhasil dibaca : {len(candidates)}")
print(f"Lembar perbandingan            : {OUTPUT}")
print(f"Daftar URL dan nama file       : {CSV_OUTPUT}")
