from pathlib import Path
from PIL import Image, ExifTags

files = [
    Path("dataset_raw/public/gelap/pub_gelap_001.jpg"),
    Path("dataset_raw/public/gelap/pub_gelap_002.jpg"),
    Path("dataset_raw/public/redup/pub_redup_001.jpg"),
    Path("dataset_raw/public/terang/pub_terang_001.jpg"),
]

for path in files:
    print("\n" + "=" * 65)
    print("FILE:", path.name)

    with Image.open(path) as img:
        print("Format:", img.format)
        print("Ukuran:", img.size)

        exif = img.getexif()

        if exif:
            print("\n--- EXIF ---")
            for tag_id, value in exif.items():
                name = ExifTags.TAGS.get(tag_id, str(tag_id))
                if isinstance(value, bytes):
                    value = f"[data biner, {len(value)} bytes]"
                print(f"{name}: {str(value)[:300]}")
        else:
            print("\nEXIF: Tidak ditemukan")

        print("\n--- METADATA GAMBAR ---")
        for key, value in img.info.items():
            if isinstance(value, bytes):
                value = f"[data biner, {len(value)} bytes]"
            print(f"{key}: {str(value)[:300]}")
