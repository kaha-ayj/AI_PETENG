from PIL import Image
from pathlib import Path

p = Path("dataset_raw/public/gelap/pub_gelap_002.jpg")

with Image.open(p) as img:
    print("INFO GAMBAR:")
    for key, value in img.info.items():
        print(f"\n--- {key} ---")
        if isinstance(value, bytes):
            try:
                print(value.decode("utf-8", errors="replace"))
            except Exception:
                print(repr(value))
        else:
            print(value)

    print("\nEXIF LENGKAP:")
    for tag, value in img.getexif().items():
        print(tag, repr(value))
