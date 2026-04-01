from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import init_db, get_connection
from app.collectors.cisa import collect_cisa_kev
from app.collectors.abusech import collect_abusech
from app.collectors.news import collect_news

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
    # Then schedule them to run periodically
    scheduler.add_job(collect_cisa_kev, "interval", hours=24)
    scheduler.add_job(collect_abusech, "interval", hours=1)
    scheduler.add_job(collect_news, "interval", hours=2)
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

# --- Health check ---
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CyberGrind Threat Intel API"}