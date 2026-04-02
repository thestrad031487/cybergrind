import requests
from app.database import get_connection

CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

def collect_cisa_kev():
    print("Collecting CISA KEV data...")
    try:
        response = requests.get(CISA_KEV_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        vulnerabilities = data.get("vulnerabilities", [])

        conn = get_connection()
        cursor = conn.cursor()
        inserted = 0

        for vuln in vulnerabilities:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO cves (
                        cve_id,
                        vendor,
                        product,
                        vulnerability_name,
                        date_added,
                        short_description,
                        required_action,
                        due_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vuln.get("cveID"),
                    vuln.get("vendorProject"),
                    vuln.get("product"),
                    vuln.get("vulnerabilityName"),
                    vuln.get("dateAdded"),
                    vuln.get("shortDescription"),
                    vuln.get("requiredAction"),
                    vuln.get("dueDate"),
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except Exception as e:
                print(f"Error inserting CVE {vuln.get('cveID')}: {e}")

        conn.commit()
        conn.close()
        print(f"CISA KEV: {inserted} new entries added")

    except Exception as e:
        print(f"Failed to collect CISA KEV data: {e}")