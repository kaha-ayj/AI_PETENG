
import os
import csv
import sqlite3
import hashlib
import ntpath
from pathlib import Path
from datetime import datetime, timedelta, timezone

DATASET = Path("dataset_raw/public")
DOWNLOADS = Path.home() / "Downloads"
CHROME = (
    Path(os.environ["LOCALAPPDATA"])
    / "Google" / "Chrome" / "User Data"
)
OUTPUT = Path("audit_dataset/chrome_download_history.csv")

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def chrome_time(value):
    if not value:
        return ""

    return (
        datetime(1601, 1, 1, tzinfo=timezone.utc)
        + timedelta(microseconds=value)
    ).isoformat()


def main():
    dataset_files = [
        p for p in DATASET.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSIONS
    ]

    download_files = [
        p for p in DOWNLOADS.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSIONS
    ]

    print(f"Foto dataset       : {len(dataset_files)}")
    print(f"Foto di Downloads  : {len(download_files)}")

    # Hash semua foto Downloads.
    downloads_by_hash = {}

    for path in download_files:
        try:
            digest = sha256(path)
            downloads_by_hash.setdefault(digest, []).append(path)
        except OSError as error:
            print(f"Gagal membaca {path.name}: {error}")

    # Baca riwayat Chrome.
    history_by_name = {}
    profiles = list(CHROME.glob("*/History"))

    print(f"Profil Chrome      : {len(profiles)}")

    for db in profiles:
        print(f"Memeriksa {db.parent.name}...")

        try:
            uri = db.resolve().as_uri() + "?mode=ro"

            with sqlite3.connect(uri, uri=True, timeout=10) as conn:
                rows = conn.execute("""
                    SELECT
                        d.id,
                        d.target_path,
                        d.start_time,
                        d.referrer,
                        d.tab_url,
                        c.url,
                        c.chain_index
                    FROM downloads d
                    LEFT JOIN downloads_url_chains c
                        ON c.id = d.id
                    ORDER BY d.start_time DESC, c.chain_index DESC
                """).fetchall()

            grouped = {}

            for row in rows:
                download_id, target, timestamp, referrer, tab_url, url, index = row

                name = ntpath.basename(target or "").casefold()

                if download_id not in grouped:
                    grouped[download_id] = {
                        "filename": ntpath.basename(target or ""),
                        "download_url": url or "",
                        "referrer": referrer or "",
                        "tab_url": tab_url or "",
                        "downloaded_at": chrome_time(timestamp),
                        "timestamp": timestamp or 0,
                        "chain_index": index if index is not None else -1,
                    }
                elif index is not None and index > grouped[download_id]["chain_index"]:
                    grouped[download_id]["download_url"] = url or ""
                    grouped[download_id]["chain_index"] = index

            for item in grouped.values():
                key = item["filename"].casefold()
                history_by_name.setdefault(key, []).append(item)

        except sqlite3.Error as error:
            print(f"Database gagal dibaca: {error}")

    # Cocokkan foto dataset dengan foto asli Downloads.
    results = []

    for dataset_file in dataset_files:
        digest = sha256(dataset_file)
        matches = downloads_by_hash.get(digest, [])

        if not matches:
            results.append({
                "dataset_file": dataset_file.as_posix(),
                "class_folder": dataset_file.parent.name,
                "sha256": digest,
                "original_download_filename": "",
                "download_url": "",
                "referrer": "",
                "tab_url": "",
                "downloaded_at": "",
                "match_status": "TIDAK_COCOK_HASH",
            })
            continue

        for original in matches:
            history = history_by_name.get(original.name.casefold(), [])

            if history:
                latest = max(history, key=lambda x: x["timestamp"])
                status = "COCOK_HASH_DAN_RIWAYAT"
            else:
                latest = {}
                status = "COCOK_HASH_TANPA_RIWAYAT"

            results.append({
                "dataset_file": dataset_file.as_posix(),
                "class_folder": dataset_file.parent.name,
                "sha256": digest,
                "original_download_filename": original.name,
                "download_url": latest.get("download_url", ""),
                "referrer": latest.get("referrer", ""),
                "tab_url": latest.get("tab_url", ""),
                "downloaded_at": latest.get("downloaded_at", ""),
                "match_status": status,
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "dataset_file",
        "class_folder",
        "sha256",
        "original_download_filename",
        "download_url",
        "referrer",
        "tab_url",
        "downloaded_at",
        "match_status",
    ]

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print("\n========== HASIL PENCOCOKAN ==========")
    print(f"Total foto dataset : {len(dataset_files)}")
    print(f"Pasangan ditemukan: {sum(r['match_status'].startswith('COCOK') for r in results)}")
    print(f"URL dan riwayat    : {sum(r['match_status'] == 'COCOK_HASH_DAN_RIWAYAT' for r in results)}")
    print(f"Tidak cocok hash   : {sum(r['match_status'] == 'TIDAK_COCOK_HASH' for r in results)}")
    print(f"Hasil CSV          : {OUTPUT}")


if __name__ == "__main__":
    main()
