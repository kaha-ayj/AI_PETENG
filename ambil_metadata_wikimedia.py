
from pathlib import Path
from html.parser import HTMLParser
import csv
import hashlib
import html
import time
import requests

ROOT = Path("dataset_raw/public")
OUTPUT = Path("audit_dataset/wikimedia_metadata_auto.csv")

API_URL = "https://commons.wikimedia.org/w/api.php"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class HTMLTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def get_text(self):
        return " ".join(self.parts).strip()


def clean_html(value):
    if not value:
        return ""

    parser = HTMLTextParser()
    parser.feed(str(value))
    return html.unescape(parser.get_text())


def metadata_value(metadata, key):
    item = metadata.get(key, {})
    if isinstance(item, dict):
        return clean_html(item.get("value", ""))
    return clean_html(item)


def get_sha1(path):
    digest = hashlib.sha1()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def lookup_commons(session, sha1):
    params = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "list": "allimages",
        "aisha1": sha1,
        "ailimit": 1,
        "aiprop": "timestamp|url|sha1|extmetadata",
    }

    response = session.get(
        API_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    images = data.get("query", {}).get("allimages", [])

    return images[0] if images else None


def main():
    if not ROOT.exists():
        print(f"Folder tidak ditemukan: {ROOT}")
        return

    files = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )

    if not files:
        print("Tidak ditemukan foto.")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "PETENG-Dataset-Metadata-Audit/1.0"
    })

    results = []

    for index, path in enumerate(files, start=1):
        relative_path = path.as_posix()
        class_name = path.parent.name
        sha1 = get_sha1(path)

        print(f"[{index}/{len(files)}] Memeriksa {path.name}...")

        row = {
            "local_file": relative_path,
            "class_folder": class_name,
            "sha1": sha1,
            "commons_title": "",
            "source_reference": "",
            "file_url": "",
            "author": "",
            "credit": "",
            "attribution": "",
            "license": "",
            "license_url": "",
            "usage_terms": "",
            "copyrighted": "",
            "lookup_status": "",
        }

        try:
            item = lookup_commons(session, sha1)

            if item is None:
                row["lookup_status"] = "TIDAK_DITEMUKAN"
            else:
                ext = item.get("extmetadata", {})

                row.update({
                    "commons_title": item.get("title", item.get("name", "")),
                    "source_reference": item.get("descriptionurl", ""),
                    "file_url": item.get("url", ""),
                    "author": metadata_value(ext, "Artist"),
                    "credit": metadata_value(ext, "Credit"),
                    "attribution": metadata_value(ext, "Attribution"),
                    "license": metadata_value(ext, "LicenseShortName"),
                    "license_url": metadata_value(ext, "LicenseUrl"),
                    "usage_terms": metadata_value(ext, "UsageTerms"),
                    "copyrighted": metadata_value(ext, "Copyrighted"),
                })

                if row["license"] or row["license_url"]:
                    row["lookup_status"] = "COCOK"
                else:
                    row["lookup_status"] = "COCOK_LISENSI_PERLU_CEK"

        except requests.RequestException as error:
            row["lookup_status"] = f"ERROR_API: {error}"
        except Exception as error:
            row["lookup_status"] = f"ERROR: {error}"

        results.append(row)
        time.sleep(0.5)

    fields = list(results[0].keys())

    with OUTPUT.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    matched = sum(
        row["lookup_status"] == "COCOK"
        for row in results
    )

    not_found = sum(
        row["lookup_status"] == "TIDAK_DITEMUKAN"
        for row in results
    )

    print("\n========== HASIL AUDIT WIKIMEDIA ==========")
    print(f"Total foto       : {len(results)}")
    print(f"Metadata cocok   : {matched}")
    print(f"Tidak ditemukan  : {not_found}")
    print(f"File hasil       : {OUTPUT}")


if __name__ == "__main__":
    main()
