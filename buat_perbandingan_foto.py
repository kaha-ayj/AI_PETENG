from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path.cwd()
DATASET = ROOT / "dataset_raw" / "public"
DOWNLOADS = Path.home() / "Downloads"
OUTPUT = ROOT / "audit_dataset" / "perbandingan_foto_dataset.jpg"

targets = [
    "gelap/pub_gelap_001.jpg",
    "gelap/pub_gelap_002.jpg",
    "redup/pub_redup_001.jpg",
    "terang/pub_terang_001.jpg",
]

candidates = [
    "gelap.jpg",
    "gelap1.jpeg",
    "gelap2.jpg",
    "gelapp.jpg",
    "redup.jpg",
    "road night.jpg",
    "road night 2.jpg",
    "road night 3.jpg",
]

font_path = Path("C:/Windows/Fonts/arial.ttf")
try:
    font = ImageFont.truetype(str(font_path), 16)
    title_font = ImageFont.truetype(str(font_path), 21)
except OSError:
    font = ImageFont.load_default()
    title_font = font

cell_w, cell_h = 250, 175
target_w, target_h = 320, 365
gap = 16
margin = 24
title_h = 32
group_h = 410

width = margin * 2 + target_w + gap + 4 * cell_w + 3 * gap
height = margin * 2 + 35 + len(targets) * (group_h + gap)

sheet = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(sheet)

def paste_image(path, x, y, max_w, max_h, label):
    if not path.exists():
        draw.rectangle(
            (x, y, x + max_w, y + max_h),
            outline="red", width=2
        )
        draw.text((x + 8, y + 8), f"TIDAK DITEMUKAN: {label}", fill="red", font=font)
        return

    try:
        with Image.open(path) as source:
            img = ImageOps.exif_transpose(source).convert("RGB")
            img.thumbnail((max_w - 10, max_h - 10))

        px = x + (max_w - img.width) // 2
        py = y + (max_h - img.height) // 2
        sheet.paste(img, (px, py))
        draw.rectangle((x, y, x + max_w, y + max_h), outline="gray")
    except Exception as e:
        draw.text((x + 5, y + 5), f"Gagal: {e}", fill="red", font=font)

draw.text((margin, margin), "PERBANDINGAN 4 FOTO DATASET DENGAN UNDUHAN ASLI",
          fill="black", font=title_font)

top = margin + 45

for target in targets:
    dataset_path = DATASET / target
    draw.text((margin, top), f"DATASET: {target}", fill="blue", font=font)

    paste_image(
        dataset_path,
        margin,
        top + 25,
        target_w,
        target_h,
        target
    )

    start_x = margin + target_w + gap

    for i, candidate in enumerate(candidates):
        col = i % 4
        row = i // 4

        x = start_x + col * (cell_w + gap)
        y = top + 25 + row * (cell_h + gap)

        draw.text((x, y - 21), candidate, fill="darkgreen", font=font)
        paste_image(
            DOWNLOADS / candidate,
            x,
            y,
            cell_w,
            cell_h - 25,
            candidate
        )

    top += group_h + gap

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
sheet.save(OUTPUT, quality=92)

print(f"Lembar perbandingan dibuat: {OUTPUT}")
