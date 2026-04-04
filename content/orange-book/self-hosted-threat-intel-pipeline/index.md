---
title: "Self-Hosted Threat Intel Pipeline"
categories: ["Architecture"]
tags: ["threat intelligence", "homelab", "docker", "fastapi", "python", "blue team", "SOC"]
description: "How I built a personal CTI pipeline using free open source feeds, Python, FastAPI, Docker, and Cloudflare Tunnel — running on a Windows workstation and serving live data on CyberGrind."
draft: false
---

## What I Built and Why

Most threat intelligence dashboards are either expensive enterprise platforms or simple embeds pulling from someone else's API. Neither felt right for a portfolio — one costs money, the other doesn't demonstrate anything about your actual capabilities.

So I built my own.

The result is a self-hosted CTI pipeline that collects from free public feeds, stores data in a local SQLite database, serves it via a FastAPI REST API, and displays live dashboards on CyberGrind at [/tools/live-cves/](/tools/live-cves/) and [/tools/threat-intel-feeds/](/tools/threat-intel-feeds/).

This post covers what I built, why each decision was made, and the full architecture so you can replicate it.

---

## The Stack

Everything here is free and open source:

| Component | Technology | Why |
|---|---|---|
| Collector | Python + requests + feedparser | Simple, readable, easy to extend |
| Storage | SQLite | Lightweight, no server required, Pi-friendly |
| API | FastAPI + uvicorn | Fast, automatic OpenAPI docs, minimal boilerplate |
| Tunnel | Cloudflare cloudflared | Public HTTPS endpoint with no port forwarding or IP exposure |
| Frontend | Hugo + vanilla JS fetch | Static site stays fast, data loads live from API |

---

## Architecture

```
[ CISA KEV / abuse.ch URLhaus / RSS Feeds ]
            ↓  Python collectors (cron)
         SQLite Database
            ↓
      FastAPI REST API
            ↓
   Cloudflare Tunnel → api.cybergrind.org
            ↓
   Hugo frontend (JS fetch on page load)
```

The collectors run on a schedule inside Docker. CISA KEV refreshes every 24 hours, abuse.ch IOCs every hour, and news feeds every 2 hours. Hugo pages fetch from the public API endpoint at runtime — no rebuild needed for fresh data.

---

## Data Sources

Three free feeds power the pipeline:

**CISA Known Exploited Vulnerabilities (KEV)**
The authoritative list of CVEs actively exploited in the wild, published by CISA as a public JSON endpoint. No API key, no rate limits, updated continuously. This is the single best free feed for prioritizing patch management.

**abuse.ch URLhaus**
A community-driven feed tracking URLs used for malware distribution. Over 21,000 active IOCs at time of writing, available as a public CSV with no authentication required. Note: their REST API now requires auth — use the CSV feed instead.

**Security News RSS**
Aggregated from Krebs on Security, Bleeping Computer, The Hacker News, CISA, and SANS Internet Storm Center. Feedparser handles the parsing; the collector pulls the 20 most recent articles per source per run.

---

## The Backend

The backend is a Python project containerized with Docker Compose. On startup it initializes the SQLite database, runs all three collectors immediately, then schedules them to run periodically using APScheduler.

FastAPI exposes four endpoints:

- `GET /api/health` — simple health check
- `GET /api/news` — security news, filterable by source
- `GET /api/cves` — CISA KEV entries, filterable by vendor
- `GET /api/iocs` — abuse.ch malicious URLs, filterable by threat type and status

All endpoints support a `limit` query parameter and return JSON. CORS is configured to allow requests from `https://cybergrind.org` and `http://localhost:1313` for local Hugo development.

---

## The Tunnel

Running on a Windows workstation means no static IP and no desire to open firewall ports. Cloudflare Tunnel solves this cleanly — `cloudflared` creates an outbound connection to Cloudflare's edge, which routes requests to your local API without exposing your IP or touching your router.

One gotcha: if you're running a VPN, QUIC (UDP) is likely blocked. The fix is simple:

```bash
cloudflared tunnel --protocol http2 run cybergrind-api
```

The `protocol: http2` line can be added to your config file permanently so you don't have to type it every time.

---

## The Frontend

The Hugo pages use vanilla JavaScript to fetch from `api.cybergrind.org` on page load. No framework, no build step — just a `fetch()` call that populates the DOM with live data.

The live CVE page highlights overdue remediation deadlines in orange/red, which makes the data immediately actionable rather than just informational. The threat intel feeds page has a tabbed interface switching between security news and live IOCs.

One production gotcha: Cloudflare Pages enforces a Content Security Policy defined in `static/_headers`. The API domain needs to be explicitly added to `connect-src` or the browser will silently block the fetch calls:

```
Content-Security-Policy: connect-src 'self' https://api.cybergrind.org ...
```

---

## What This Demonstrates

For a portfolio this stack covers a lot of ground in one project:

- **Data pipeline thinking** — collection, storage, serving, presentation as distinct layers
- **Python** — requests, feedparser, APScheduler, SQLite
- **API design** — REST endpoints, CORS, query parameters, error handling
- **Docker** — containerization, volumes, environment variables
- **Infrastructure** — Cloudflare Tunnel, DNS, HTTPS, CSP headers
- **Frontend** — Hugo templating, vanilla JS, async fetch, DOM manipulation

More importantly it produces something genuinely useful — a real-time view of active CVEs and malicious IOCs that I actually check.

---

## Limitations and Honest Notes

**Uptime depends on your workstation being on.** If the machine sleeps or shuts down, `api.cybergrind.org` goes dark. For a portfolio demo this is acceptable — the solution is migrating to a cheap VPS or Raspberry Pi, which is straightforward since everything is Dockerized.

**SQLite is fine until it isn't.** At 21,000+ IOC records it's still fast, but for production scale you'd want PostgreSQL. The schema is simple enough that migration is a clean lift.

**abuse.ch malware tag parsing** needs refinement. Some IOCs show `32-bit` as the malware family because the tags field contains architecture metadata alongside actual family names. A simple filter on the collector side would fix this.

---

## Source and Live Demo

The live dashboards are running now:

- [Live CVE Feed →](/tools/live-cves/)
- [Threat Intel Feeds →](/tools/threat-intel-feeds/)

The full backend code lives in a private repo. If you're building something similar and want to compare notes, reach out via [GitHub](https://github.com/thestrad031487) or [LinkedIn](https://linkedin.com/in/jasonrwacker).
