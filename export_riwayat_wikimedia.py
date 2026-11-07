from pathlib import Path
from datetime import datetime, timedelta, timezone
import sqlite3
import csv

USER_DATA = Path.home() / "AppData/Local/Google/Chrome/User Data"
OUTPUT = Path.cwd() / "audit_dataset" / "wikimedia_chrome_history.csv"

def chrome_time(value):
    if not value:
        return ""
    try:
        dt = datetime(1601, 1, 1, tzinfo=timezone.utc)
        dt += timedelta(microseconds=int(value))
        return dt.astimezone().isoformat(timespec="seconds")
    except (ValueError, TypeError, OverflowError):
        return ""

results = []
profiles = list(USER_DATA.glob("*/History"))

print(f"Profil Chrome ditemukan: {len(profiles)}")

for db in profiles:
    profile = db.parent.name
    print(f"Memeriksa {profile}...")

    try:
        conn = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        tables = {
            row["name"] for row in
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }

        # Riwayat unduhan
        if "downloads" in tables:
            columns = {
                row["name"] for row in
                conn.execute("PRAGMA table_info(downloads)")
            }

            wanted = [
                c for c in (
                    "id", "target_path", "current_path",
                    "start_time", "tab_url", "tab_referrer_url"
                ) if c in columns
            ]

            query = "SELECT " + ", ".join(wanted) + " FROM downloads"

            for item in conn.execute(query):
                data = dict(item)
                download_id = data.get("id")

                chain = []
                if "downloads_url_chains" in tables:
                    chain = [
                        row[0] for row in conn.execute(
                            """SELECT url FROM downloads_url_chains
                               WHERE id=? ORDER BY chain_index""",
                            (download_id,)
                        )
                    ]

                all_urls = chain + [
                    data.get("tab_url") or "",
                    data.get("tab_referrer_url") or ""
                ]

                wikimedia_urls = [
                    url for url in all_urls
                    if "wikimedia.org" in url.lower()
                    or "wikipedia.org" in url.lower()
                ]

                if wikimedia_urls:
                    results.append({
                        "profile": profile,
                        "record_type": "download",
                        "timestamp": chrome_time(data.get("start_time")),
                        "title": "",
                        "target_path": data.get("target_path", ""),
                        "current_path": data.get("current_path", ""),
                        "url": " | ".join(dict.fromkeys(wikimedia_urls)),
                        "visit_count": ""
                    })

        # Riwayat halaman Wikimedia yang pernah dibuka
        if "urls" in tables:
            for item in conn.execute("""
                SELECT title, url, last_visit_time, visit_count
                FROM urls
                WHERE lower(url) LIKE '%wikimedia.org%'
                   OR lower(url) LIKE '%wikipedia.org/wiki/file:%'
            """):
                results.append({
                    "profile": profile,
                    "record_type": "page_history",
                    "timestamp": chrome_time(item["last_visit_time"]),
                    "title": item["title"] or "",
                    "target_path": "",
                    "current_path": "",
                    "url": item["url"],
                    "visit_count": item["visit_count"]
                })

        conn.close()

    except Exception as e:
        print(f"Gagal membaca {profile}: {e}")

fields = [
    "profile", "record_type", "timestamp", "title",
    "target_path", "current_path", "url", "visit_count"
]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(results)

downloads = sum(r["record_type"] == "download" for r in results)
pages = sum(r["record_type"] == "page_history" for r in results)

print("\n========== HASIL ==========")
print(f"Riwayat unduhan Wikimedia : {downloads}")
print(f"Riwayat halaman Wikimedia : {pages}")
print(f"File hasil                : {OUTPUT}")
