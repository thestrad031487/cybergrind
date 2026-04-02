from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import init_db, get_connection
from app.collectors.cisa import collect_cisa_kev
from app.collectors.abusech import collect_abusech
from app.collectors.news import collect_news
from app.collectors.malwarebazaar import collect_malwarebazaar

app = FastAPI(title="CyberGrind Threat Intelligence API")

# CORS so Hugo frontend can fetch from api.cybergrind.org
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cybergrind.org",
        "http://localhost:1313",
        "http://127.0.0.1:1313",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Scheduler runs collectors on a schedule
scheduler = BackgroundScheduler()

@app.on_event("startup")
def startup():
    init_db()
    # Run collectors immediately on startup
    collect_cisa_kev()
    collect_abusech()
    collect_news()
    collect_malwarebazaar()
    # Then schedule them to run periodically
    scheduler.add_job(collect_cisa_kev, "interval", hours=24)
    scheduler.add_job(collect_abusech, "interval", hours=1)
    scheduler.add_job(collect_news, "interval", hours=2)
    scheduler.add_job(collect_malwarebazaar, "interval", hours=6)
    scheduler.start()

@app.on_event("shutdown")
def shutdown():
    scheduler.shutdown()

# --- News endpoints ---
@app.get("/api/news")
def get_news(source: str = None, limit: int = Query(default=20, le=100)):
    conn = get_connection()
    cursor = conn.cursor()
    if source:
        cursor.execute(
            "SELECT * FROM news WHERE source = ? ORDER BY created_at DESC LIMIT ?",
            (source, limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM news ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"count": len(rows), "results": rows}

# --- CVE endpoints ---
@app.get("/api/cves")
def get_cves(vendor: str = None, limit: int = Query(default=20, le=100)):
    conn = get_connection()
    cursor = conn.cursor()
    if vendor:
        cursor.execute(
            "SELECT * FROM cves WHERE vendor LIKE ? ORDER BY date_added DESC LIMIT ?",
            (f"%{vendor}%", limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM cves ORDER BY date_added DESC LIMIT ?",
            (limit,)
        )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"count": len(rows), "results": rows}

# --- IOC endpoints ---
@app.get("/api/iocs")
def get_iocs(threat: str = None, status: str = None, limit: int = Query(default=20, le=100)):
    conn = get_connection()
    cursor = conn.cursor()
    if threat:
        cursor.execute(
            "SELECT * FROM iocs WHERE threat = ? ORDER BY created_at DESC LIMIT ?",
            (threat, limit)
        )
    elif status:
        cursor.execute(
            "SELECT * FROM iocs WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status, limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM iocs ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"count": len(rows), "results": rows}

import os
import requests as http_requests

VT_API_KEY = os.getenv("VT_API_KEY", "")

# --- Hash endpoints ---
@app.get("/api/hashes")
def get_hashes(family: str = None, limit: int = Query(default=20, le=100)):
    conn = get_connection()
    cursor = conn.cursor()
    if family:
        cursor.execute(
            "SELECT * FROM hashes WHERE malware_family LIKE ? ORDER BY first_seen DESC LIMIT ?",
            (f"%{family}%", limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM hashes ORDER BY first_seen DESC LIMIT ?",
            (limit,)
        )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"count": len(rows), "results": rows}

# --- VirusTotal lookup ---
@app.get("/api/vt/lookup/{hash}")
def vt_lookup(hash: str):
    if not VT_API_KEY:
        return {"error": "VirusTotal API key not configured"}
    if len(hash) not in [32, 40, 64]:
        return {"error": "Invalid hash — must be MD5 (32), SHA1 (40), or SHA256 (64) characters"}
    try:
        response = http_requests.get(
            f"https://www.virustotal.com/api/v3/files/{hash}",
            headers={"x-apikey": VT_API_KEY},
            timeout=15
        )
        if response.status_code == 404:
            return {"found": False, "hash": hash, "message": "Hash not found in VirusTotal database"}
        if response.status_code == 429:
            return {"error": "VirusTotal rate limit reached — free tier allows 500 lookups/day"}
        response.raise_for_status()
        data = response.json()
        attrs = data.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        results = attrs.get("last_analysis_results", {})
        detections = {k: v["result"] for k, v in results.items() if v.get("category") == "malicious" and v.get("result")}
        return {
            "found": True,
            "hash": hash,
            "name": attrs.get("meaningful_name") or attrs.get("names", ["unknown"])[0] if attrs.get("names") else "unknown",
            "file_type": attrs.get("type_description", "unknown"),
            "file_size": attrs.get("size", 0),
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "undetected": stats.get("undetected", 0),
            "total_engines": sum(stats.values()),
            "detections": detections,
            "first_submission": attrs.get("first_submission_date"),
            "last_analysis": attrs.get("last_analysis_date"),
            "tags": attrs.get("tags", []),
        }
    except Exception as e:
        return {"error": f"Lookup failed: {str(e)}"}

# --- Health check ---
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CyberGrind Threat Intel API"}