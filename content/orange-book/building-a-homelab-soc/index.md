---
title: "How We Built CyberGrind"
date: 2026-04-02T08:00:00-05:00
categories: ["Architecture"]
tags: ["project", "hugo", "cloudflare", "docker", "python", "homelab", "devops"]
description: "A full walkthrough of how CyberGrind was designed and built — from Hugo and GitHub to Cloudflare Pages, Workers, a self-hosted CTI pipeline, and a daily news automation system."
draft: false
---

CyberGrind is a personal cybersecurity portfolio, threat intelligence platform, and educational resource — all running on free and open source tooling. This article documents how it was built: the design decisions, the architecture, how all the pieces connect, and the gotchas learned along the way.

This isn't a tutorial. It's a technical record of real decisions made while building a real project. Everything here is running in production.

---

## Design System & Brand

Before writing a single line of code, the site needed an identity. A cybersecurity portfolio that looks like a generic blog communicates nothing about the person behind it.

The design brief was simple: dark, terminal-influenced, readable, and distinctive without being gimmicky.

**Color palette:**

| Token | Value | Usage |
|---|---|---|
| Cyber Orange | `#FF8C00` | Primary accent, CTAs, section markers |
| Amber Glow | `#FFAD33` | Secondary highlight, hover states |
| Deep Charcoal | `#1A1C1E` | Page background |
| Steel Gray | `#8E9297` | Body text, secondary labels |

Orange was chosen deliberately — it sits outside the standard blue/purple palette that dominates security tooling, which makes CyberGrind immediately visually distinct. The dark background and monospace touches reinforce the terminal aesthetic without going full hacker-movie cliché.

**Typography:** Syne (display/headings) paired with Space Mono (code, labels, UI accents). Syne is geometric and authoritative; Space Mono is unambiguously a terminal font. Together they work across both editorial content and technical tooling pages.

**Logo:** The `>_ cg` terminal prompt mark, deployed as an SVG favicon and site logo. Simple enough to read at 16px, memorable enough to stand alone.

All accent colors are defined as CSS custom properties in `assets/css/extended/custom.css` so they cascade consistently across the PaperMod theme and any custom HTML.

---

## Hugo & Site Structure

The site is built with **Hugo v0.158.0 extended** using the **PaperMod** theme as a Git submodule.

Hugo was chosen over other static site generators for three reasons: it's fast (sub-second builds), the PaperMod theme provides a solid dark-mode foundation to build on, and it generates a JSON search index out of the box for Fuse.js-powered search.

**Key `hugo.toml` settings:**

```toml
env = "production"           # Enables OG tags, Twitter cards, Schema.org markup
mainSections = ["blog"]
paginate = 5
summaryLength = 30

[outputs]
home = ["HTML", "RSS", "JSON"]   # JSON required for Fuse.js search index

[markup.goldmark.renderer]
unsafe = true                # Required for raw HTML in markdown content
```

The `env = "production"` line is easy to miss and critical — without it, Open Graph tags and Schema.org structured data are silently omitted from the output, which kills social sharing previews and SEO signals.

**Content sections:**

```
content/
├── blog/          # Daily automated CyberNews posts
├── orange-book/   # Deep-dive articles + infographic stubs
├── tools/         # One page per tool
├── about.md
└── search.md
```

The Orange Book uses a custom list layout (`layouts/orange-book/list.html`) that prefers the `description` frontmatter field over Hugo's auto-generated `.Summary`, giving full control over how articles appear in the index. Infographics get their own layout (`layouts/orange-book/infographic.html`) that renders a full-height iframe — the HTML file lives in `static/infographics/` and is completely self-contained.

**Hugo template hierarchy matters.** A few things that bit us during development:

- The homepage uses `layouts/_default/home.html` — not `layouts/index.html`
- PaperMod's `list.html` can silently override custom list layouts if placed in the wrong directory
- `.Paginate` can only be called once per template — calling it in both a base layout and a section layout causes a build error

---

## GitHub & Version Control

The repository is hosted at `github.com/thestrad031487/cybergrind` with a straightforward branch strategy: everything ships from `main`. Cloudflare Pages watches `main` and auto-deploys on every push.

**PaperMod is a Git submodule**, not a vendored copy. This keeps theme updates clean but requires one extra step after a fresh clone:

```bash
git submodule update --init --recursive
```

**The daily news bot** complicates the standard push workflow. The automation script commits and pushes a new post every day at 11am CT. If you push from a dev machine without pulling first, Git will reject it with a non-fast-forward error. The fix is always pulling before pushing:

```bash
git pull --no-rebase
git push
```

The `--no-rebase` flag was set globally on the primary dev machine to suppress the prompt that appears when local and remote histories diverge:

```bash
git config --global pull.rebase false
```

**Windows CRLF line endings** are a recurring gotcha. Hugo's frontmatter parser is sensitive to carriage returns — a file edited on Windows and committed without normalization can cause silent build failures where Hugo simply doesn't recognize the frontmatter. Fix any affected file with:

```bash
sed -i 's/\r//' path/to/file.md
```

---

## Cloudflare Pages — Auto-Deploy Pipeline

Cloudflare Pages provides free static site hosting with automatic deploys triggered by GitHub pushes. The connection is straightforward: authorize Cloudflare to access the GitHub repository, point it at the `main` branch, set the build command to `hugo --minify`, and set the output directory to `public`.

Every push to `main` triggers a build. Cloudflare clones the repo, runs Hugo, and deploys the output to their global CDN — typically live within 60–90 seconds.

**`static/_headers`** is where production security lives. Cloudflare Pages serves this file as HTTP response headers for every page:

```
/*
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; connect-src 'self' https://api.cybergrind.org https://epss-worker.wacker-jason.workers.dev ...
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  Strict-Transport-Security: max-age=31536000; includeSubDomains
```

The `connect-src` directive is the one that requires ongoing attention — every new Cloudflare Worker URL or external API endpoint needs to be explicitly added here or the browser will silently block the fetch calls. This has been the most common source of "why isn't this working?" moments during development.

**www redirect** is handled via Cloudflare's dynamic redirect rules rather than a `_redirects` file, because the file-based approach doesn't preserve URL paths. The rule matches `www.cybergrind.org/*` and redirects to `https://cybergrind.org/$1` with a 301.

---

## Cloudflare Workers — API Proxy Layer

Direct API calls from the browser have two problems: they expose API keys in client-side JavaScript, and they're subject to rate limits that can be exhausted quickly by multiple visitors. Cloudflare Workers solve both problems by sitting between the browser and the upstream API.

Each Worker is a small JavaScript function deployed to Cloudflare's edge. It receives the request from the browser, attaches the API key from a Worker Secret (stored in the Cloudflare dashboard, never in code), forwards the request to the upstream service, caches the response, and returns it to the browser.

**Workers deployed:**

| Worker | Upstream Source | Cache TTL |
|---|---|---|
| EPSS Worker | FIRST EPSS API + NVD | Per request |
| IP Reputation Worker | AbuseIPDB | None (live lookup) |
| KEV Worker | CISA KEV catalog | 1 hour |
| Recent KEV Worker | CISA KEV (10 most recent) | 1 hour |
| Threat Map Worker | AbuseIPDB blacklist | 6 hours |
| OSINT Feeds Worker | IPsum + Emerging Threats + Feodo Tracker | 1 hour |

A minimal Worker looks like this:

```javascript
export default {
  async fetch(request, env) {
    const cache = caches.default;
    const cacheKey = new Request(request.url);

    let response = await cache.match(cacheKey);
    if (response) return response;

    response = await fetch("https://upstream-api.example.com/endpoint", {
      headers: {
        "Key": env.API_KEY,
        "Accept": "application/json"
      }
    });

    const cachedResponse = new Response(response.body, response);
    cachedResponse.headers.set("Cache-Control", "public, max-age=3600");
    await cache.put(cacheKey, cachedResponse.clone());

    return cachedResponse;
  }
};
```

The API key lives in `env.API_KEY` — a Worker Secret set via the Cloudflare dashboard. It never touches the codebase.

**Each Worker needs its own `connect-src` entry** in `static/_headers`. Missing this is the single most common source of broken tool pages — the browser fetch succeeds structurally but the CSP blocks the response.

---

## Self-Hosted CTI Pipeline

The Cloudflare Workers handle edge caching and API proxying, but they don't store data. For tools that need a persistent, queryable database — live CVEs, IOC feeds, malware hashes — a proper backend is needed.

The pipeline runs on a Windows workstation and is fully containerized with Docker Compose. The architecture:

```
External Feeds (CISA KEV, abuse.ch, RSS, MalwareBazaar)
        ↓
  Python Collectors (APScheduler)
        ↓
   SQLite Database
        ↓
  FastAPI REST API
        ↓
Cloudflare Tunnel → api.cybergrind.org
        ↓
  Hugo frontend (JS fetch on page load)
```

**Project structure:**

```
cybergrind-api/
├── app/
│   ├── main.py          # FastAPI app, CORS config, scheduler startup
│   ├── database.py      # SQLite connection and schema init
│   └── collectors/
│       ├── cisa.py      # CISA KEV — runs every 24h
│       ├── abusech.py   # URLhaus IOCs — runs every 1h
│       ├── news.py      # RSS feeds — runs every 2h
│       └── malwarebazaar.py  # Malware hashes — runs every 6h
├── data/                # SQLite volume (gitignored)
├── docker-compose.yml
└── requirements.txt
```

**FastAPI** was chosen over Flask for its automatic OpenAPI documentation, native async support, and Pydantic validation. Every endpoint is immediately self-documenting at `/docs`.

**SQLite** works fine for this scale. At tens of thousands of IOC records, query times are still sub-100ms. The schema is intentionally simple — if the project outgrows SQLite, migrating to PostgreSQL is a clean lift since Docker Compose handles the service swap.

A typical collector follows this pattern:

```python
import requests, sqlite3
from datetime import datetime

def collect_cisa_kev(db_path: str):
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    data = requests.get(url).json()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for vuln in data.get("vulnerabilities", []):
        cur.execute("""
            INSERT OR REPLACE INTO cves
            (cve_id, vendor, product, name, date_added, due_date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            vuln["cveID"], vuln["vendorProject"], vuln["product"],
            vuln["vulnerabilityName"], vuln["dateAdded"],
            vuln.get("dueDate"), vuln["shortDescription"]
        ))

    conn.commit()
    conn.close()
```

`INSERT OR REPLACE` handles deduplication — if a CVE already exists in the database, the record is updated rather than duplicated.

**CORS configuration** in FastAPI needs to explicitly allow both the production domain and localhost for local Hugo development:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cybergrind.org",
        "http://localhost:1313"
    ],
    allow_methods=["GET"],
    allow_headers=["*"]
)
```

### Cloudflare Tunnel

Running a public API from a home workstation without exposing your IP or opening firewall ports is exactly what Cloudflare Tunnel is designed for. `cloudflared` creates an outbound connection from the workstation to Cloudflare's edge — incoming requests to `api.cybergrind.org` are routed back through that tunnel to the local FastAPI instance.

```bash
cloudflared tunnel create cybergrind-api
cloudflared tunnel route dns cybergrind-api api.cybergrind.org
cloudflared tunnel run cybergrind-api
```

One important gotcha: if you're running a VPN that blocks UDP, QUIC will fail silently. Force HTTP/2 explicitly:

```bash
cloudflared tunnel --protocol http2 run cybergrind-api
```

On Windows, `cloudflared` runs as a registered service so the tunnel comes up automatically on boot — no manual intervention needed after a restart.

---

## Daily News Automation

Every day at 11am CT, a new cybersecurity news post is automatically generated and published to the site. No manual intervention. The pipeline has three stages:

**1. Fetch headlines** — `generate_news.py` calls the NewsAPI with cybersecurity-focused keywords and retrieves the day's top headlines.

**2. Generate commentary** — The headlines are passed to a locally running Ollama instance (Llama 3.2 3B model) with a strict prompt that constrains the model to only reference the provided headlines. This produces the "From the Trenches" editorial section. Running inference locally means no data leaves the machine and there are no per-token costs.

**3. Commit and publish** — The script writes a Hugo markdown post with the headlines and commentary, then the wrapper script (`daily_news.sh`) commits and pushes to GitHub. Cloudflare Pages detects the push and auto-deploys within 90 seconds.

The post format is consistent: headlines listed with source attribution, a horizontal rule, then the AI-generated commentary section, then a patch priority callout if any CVEs were mentioned.

**Ollama readiness polling** is built into the wrapper script — it checks every 2 seconds (up to 60 seconds) whether Ollama is responsive before attempting generation. This handles the case where the cron job fires before Ollama has fully loaded the model on wake-from-sleep.

**Hallucination mitigation:** The model prompt explicitly instructs Llama 3.2 to reference only the provided headlines and to acknowledge uncertainty rather than fill gaps with plausible-sounding fabrications. Temperature is kept low. Commentary is clearly labeled as AI-generated throughout the site.

The daily news bot and manual development pushes share the same `main` branch, which means pull-before-push discipline is essential. The bot commits on its own schedule — if you push without pulling, Git will reject it.

---

## What We'd Do Differently

Every project has hindsight. A few honest notes:

**Start with a content security policy from day one.** Adding CSP headers after the fact means auditing every external resource the site already loads and adding it to `connect-src`, `script-src`, and `style-src` retroactively. Starting with a strict policy and relaxing it as needed is much cleaner.

**Cloudflare Worker source files need their own directory structure.** Workers developed directly in the Cloudflare dashboard are hard to version control. Each Worker should live in its own directory with a `wrangler.jsonc` config from the start.

**The SQLite volume needs a backup strategy.** The `data/` directory is gitignored (correctly — you don't want tens of thousands of IOC records in version control), but that means it's not backed up anywhere. A simple cron job copying the SQLite file to cloud storage would solve this.

**Hugo's template resolution order is non-obvious.** The theme's templates can silently win over custom layouts depending on directory placement. When a layout isn't rendering as expected, the answer is almost always in the Hugo template hierarchy documentation.

---

## The Full Architecture

See the companion infographic for a visual map of how all these components connect — from GitHub push to live page, and from external threat feed to browser dashboard.

→ [CyberGrind Architecture Diagram](/orange-book/cybergrind-architecture/)

---

## References

- [Hugo Documentation](https://gohugo.io/documentation/)
- [PaperMod Theme](https://github.com/adityatelange/hugo-PaperMod)
- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama](https://ollama.com/)
- [CISA KEV Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [abuse.ch URLhaus](https://urlhaus.abuse.ch/)
