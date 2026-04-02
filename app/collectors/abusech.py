import requests
import csv
import io

ARCH_TAGS = {"32-bit", "64-bit", "arm", "arm64", "elf", "mips", "x86", "x64", "exe", "dll", "apk", "js", "None"}

def parse_malware_tag(tags_str):
    if not tags_str or tags_str == "None":
        return "unknown"
    tags = [t.strip() for t in tags_str.split(",")]
    for tag in tags:
        if tag not in ARCH_TAGS and tag:
            return tag
    return tags[0] if tags else "unknown"

from app.database import get_connection

URLHAUS_CSV = "https://urlhaus.abuse.ch/downloads/csv_recent/"

def collect_abusech():
    print("Collecting abuse.ch URLhaus data...")
    try:
        response = requests.get(URLHAUS_CSV, timeout=30)
        response.raise_for_status()

        # Skip comment lines starting with #
        lines = [l for l in response.text.splitlines() if not l.startswith("#")]

        conn = get_connection()
        cursor = conn.cursor()
        inserted = 0

        reader = csv.reader(lines)
        for row in reader:
            if len(row) < 6:
                continue
            try:
                # Columns: id, date_added, url, url_status, last_online, threat, tags, urlhaus_link, reporter
                url_id      = row[0].strip()
                url         = row[2].strip()
                url_status  = row[3].strip()
                threat      = row[5].strip() if len(row) > 5 else "unknown"
                tags        = row[6].strip() if len(row) > 6 else ""
                malware     = parse_malware_tag(tags)

                cursor.execute("""
                    INSERT OR IGNORE INTO iocs (
                        ioc_type,
                        value,
                        malware,
                        threat,
                        status
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    "url",
                    url,
                    malware or "unknown",
                    threat or "unknown",
                    url_status or "unknown",
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except Exception as e:
                print(f"Error inserting IOC {row}: {e}")

        conn.commit()
        conn.close()
        print(f"abuse.ch: {inserted} new IOCs added")

    except Exception as e:
        print(f"Failed to collect abuse.ch data: {e}")