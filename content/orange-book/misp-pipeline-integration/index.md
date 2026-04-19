---
title: "Wiring MISP Into a Self-Hosted AI Security Pipeline"
date: 2026-04-19
description: "How to connect a self-hosted MISP instance to a local AI agent pipeline so the Risk Analyst reasons from live threat indicators rather than training data alone — covering API key generation, the CTI collector, pipeline integration, and surfacing intel on the web."
tags: ["homelab", "AI", "MISP", "threat-intel", "pipeline", "agents", "docker", "CTI"]
categories: ["orange-book"]
draft: false
---

The [multi-agent security pipeline](/orange-book/cybersecurity-agents-pipeline/) we built earlier produces useful reports — structured risk analysis, mitigations, recommendations. But it has a ceiling: every agent reasons from what the model learned during training. It doesn't know about the domain that started hosting malware last week, the C2 infrastructure tied to a campaign your MISP instance just ingested, or the specific indicators your feeds have flagged today.

This article closes that gap. It walks through connecting a self-hosted MISP instance to the pipeline so the Risk Analyst agent receives live threat indicators alongside its research context — and cites them specifically in its output. It also covers surfacing that intelligence on the CyberGrind tools pages.

If you haven't set up the AI stack or the pipeline yet, start with the [Self-Hosted AI Stack](/orange-book/self-hosted-ai-stack/) and [Building Cybersecurity Agents](/orange-book/cybersecurity-agents-pipeline/) articles first.

---

## Part 1 — Infrastructure: Getting MISP API Access

Recent versions of MISP (2.5+) use a separate `auth_keys` table with bcrypt-hashed keys rather than the legacy plaintext `authkey` field in the `users` table. This is a meaningful security improvement, but it means the usual approach of reading the key from the database and using it directly doesn't work.

### Why the Auth Key Process Is Non-Trivial

If you query `SELECT authkey FROM users`, you get a legacy hash that the API won't accept. The actual API keys live in `auth_keys`, stored as bcrypt hashes — which means you can't recover an existing key, only generate a new one.

The `cake User authkey` CLI command exists for this but has format validation requirements that make it awkward to use directly. The reliable path is to generate the key and hash it inside the container using PHP, then insert it manually.

### Generating a Valid Key

First, generate a 40-character hex key on the host:

```bash
NEW_KEY=$(openssl rand -hex 20)
echo "Key: $NEW_KEY"
echo -n "$NEW_KEY" | wc -c  # confirm exactly 40 chars
```

MISP requires exactly 40 characters. The `openssl rand -hex 20` output is always 40 hex characters — don't use a longer or shorter string or the insert will fail silently.

Next, generate the bcrypt hash and verify it inside the misp-core container:

```bash
docker compose exec misp-core bash -c "cat > /tmp/genkey.php << 'EOF'
<?php
\$key = '$NEW_KEY';
\$hash = password_hash(\$key, PASSWORD_BCRYPT);
echo 'Hash: ' . \$hash . PHP_EOL;
echo 'Verify: ' . (password_verify(\$key, \$hash) ? 'OK' : 'FAIL') . PHP_EOL;
EOF
php /tmp/genkey.php"
```

Confirm the verify output says `OK` before proceeding. If it says `FAIL`, the hash was generated incorrectly — don't insert it.

### Inserting Into auth_keys

The `auth_keys` table requires several fields that have no defaults:

```bash
UUID=$(cat /proc/sys/kernel/random/uuid)
docker compose exec db mysql -u root -pMispRoot2026 misp -e "
INSERT INTO auth_keys (uuid, user_id, authkey, authkey_start, authkey_end, comment, created, expiration)
VALUES (
  '$UUID', 1,
  '\$2y\$12\$YOUR_HASH_HERE',
  '${NEW_KEY:0:4}',
  '${NEW_KEY: -4}',
  'cybergrind-cti-pipeline',
  UNIX_TIMESTAMP(), 0
);"
```

`authkey_start` and `authkey_end` are the first and last 4 characters of the plaintext key. MISP uses these for fast lookups before running the full bcrypt comparison.

### Flushing the Redis Cache

MISP caches auth key lookups in Redis. After inserting a new key, flush the cache or the API will continue rejecting the key even though it's correctly stored:

```bash
docker compose exec redis redis-cli -a redispassword FLUSHALL
```

Find the Redis password in the MISP config:

```bash
docker compose exec misp-core bash -c "grep redis_password /var/www/MISP/app/Config/config.php | head -1"
```

### Verifying the Key

Test against the MISP REST API:

```bash
curl -s -k -H "Authorization: $NEW_KEY" \
  -H "Accept: application/json" \
  https://localhost/attributes/restSearch \
  -d '{"limit":1}' | head -c 200
```

A JSON response with `Attribute` data confirms the key works. An authentication error means either the hash is wrong, Redis wasn't flushed, or the key length isn't exactly 40 characters.

Store the key in your `.env` files:

```bash
# ~/misp/.env
MISP_API_KEY=your_40_char_key_here
MISP_URL=https://localhost

# C:\cybergrind-api\.env (Windows CTI pipeline)
MISP_API_KEY=your_40_char_key_here
MISP_URL=https://host.docker.internal
```

Note: `host.docker.internal` is used from within Docker containers on Windows to reach services on the host — including the MISP instance running in WSL2.

---

## Part 2 — Infrastructure: The CTI Collector

### Where It Lives

The collector sits at `app/collectors/misp.py` alongside the existing abuse.ch, CISA KEV, and MalwareBazaar collectors. It follows the same pattern: fetch data from a source, normalize it to the shared IOC schema, store it with `INSERT OR IGNORE`.

### What It Does

The collector queries MISP's `/attributes/restSearch` endpoint every 6 hours for attributes with `to_ids=True` — meaning attributes marked as actionable threat indicators, not just contextual data. It supports IPs, domains, URLs, hashes, and email addresses.

```python
payload = {
    "timestamp": timestamp,  # attributes modified since last run
    "to_ids": True,          # actionable indicators only
    "deleted": False,
    "limit": 1000,
    "returnFormat": "json"
}
```

Each attribute is normalized to the existing IOC schema:

```python
def normalize_attribute(attr):
    attr_type = attr.get("type", "")
    value = attr.get("value", "")
    # maps ip-src/ip-dst → "ip", domain/hostname → "domain", etc.
    # strips port from ip|port types
    # handles filename|hash pairs
```

A `source` column distinguishes MISP IOCs from abuse.ch ones — critical for the pipeline integration that queries by source.

### The Initial Pull

On first startup, the collector runs with `hours_back=720` (30 days) to pull existing MISP intelligence rather than starting empty. Subsequent scheduled runs use 6 hours.

In `main.py`:

```python
collect_misp(hours_back=720)  # startup — full historical pull
scheduler.add_job(collect_misp, "interval", hours=6)  # ongoing
```

### Key Gotchas

**Import path:** Use `from app.database import get_connection` not `from database import get_connection`. The pipeline runs from the project root, not from inside `app/`.

**Git Bash path mangling:** When passing `-e DB_PATH=/tmp/test.db` in Git Bash on Windows, the shell converts `/tmp` to a Windows path. Use `//tmp` to prevent this.

**`verify=False`:** MISP uses a self-signed certificate by default. The collector disables SSL verification for internal connections. This is intentional — the connection is local, not internet-facing.

### New API Endpoints

Three new endpoints expose MISP data through the CTI API:

```
GET /api/misp/iocs          — paginated MISP IOC feed, filterable by type
GET /api/misp/search?value= — search by indicator value (partial match)
GET /api/misp/threat?q=     — search by threat category name
```

The threat search endpoint is what makes the pipeline integration work — it lets the agent query by threat category (`fakeapp`, `android_joker`) rather than needing to know specific indicator values in advance.

---

## Part 3 — Pipeline Integration: Wiring MISP Into the Risk Analyst

### The Architecture

The integration lives in `security-agents/tools/misp_context.py`. It sits between the CTI API and the agent pipeline — extracting keywords from the report topic, querying for relevant IOCs, and formatting them as structured context for the Risk Analyst.

```
Topic: "android fakeapp campaign infrastructure"
    ↓
misp_context.py
    ↓
GET /api/misp/search?value=fakeapp
GET /api/misp/threat?q=fakeapp
GET /api/misp/threat?q=android
    ↓
12 live IOCs retrieved
    ↓
Risk Analyst receives: research output + formatted IOC context
```

### Keyword Extraction

The extractor strips common words that would return irrelevant or no results, and uses the remaining terms to drive both value-based and threat-category searches:

```python
SKIP_KEYWORDS = {
    "security", "attack", "threat", "risk", "vulnerability",
    "malware", "network", "the", "and", "for", ...
}

def extract_keywords(topic: str) -> list:
    words = topic.lower().split()
    keywords = [w for w in words if len(w) > 3 and w not in SKIP_KEYWORDS]
    return keywords[:5]
```

This is why topics like "docker container hardening" return no MISP context — those are infrastructure terms, not threat indicators. Topics like "android fakeapp campaign" return real IOCs because `fakeapp` and `android` match both indicator values and threat category names in the database.

### Dual Search Strategy

Two search methods run for each keyword:

```python
def fetch_by_value(keyword):
    # Matches indicator values — good for domain/IP fragments
    GET /api/misp/search?value={keyword}

def fetch_by_threat(keyword):
    # Matches threat category names — good for malware family names
    GET /api/misp/threat?q={keyword}
```

Combined, this catches both cases: a topic mentioning a specific domain fragment finds it by value, while a topic mentioning a malware family name finds related infrastructure by threat category.

### Context Injection

The pipeline injects MISP context between the Researcher and Risk Analyst stages:

```python
misp_context = get_misp_context(topic)
if misp_context:
    risk_context = f"{research}\n\n{misp_context}"
else:
    risk_context = research  # graceful fallback

risks = self.risk.run(risk_context)
```

If no IOCs are found the pipeline continues normally — the MISP integration degrades gracefully rather than blocking the report.

### The Updated Risk Analyst Prompt

The prompt instructs the agent to use IOC data when present and reference specific indicators:

```python
RISK_PROMPT = """You are a cybersecurity risk analyst with access to live threat intelligence.

Your job is to identify specific risks associated with the given topic, drawing on:
1. The research context provided
2. Any live MISP threat indicators included in the context

For each risk, provide:
- Risk name
- Impact: High / Medium / Low
- Likelihood: High / Medium / Low
- Brief description of the threat vector
- If relevant MISP IOCs are present, reference them specifically

Focus on realistic, actionable risks. Avoid generic statements.
Prioritize risks by impact first, then likelihood."""
```

### Example Output

Here's what the Risk Analyst produces when live IOCs are present — note the specific indicator citations:

```
Risk: SSL/TLS Certificate Abuse
Impact: Medium | Likelihood: Low
Description: Legitimate-appearing certificates used to establish trust with victims.
MISP IOCs: shadowroute.co (threat: android_fakeapp)

Risk: Proxy Server Abuse
Impact: Low | Likelihood: Medium
Description: Intermediate servers disguise actual domain names and IP addresses.
MISP IOCs: muyo.click, seblu.pro (threat: android_joker)

Risk: C&C Server Abuse
Impact: Low | Likelihood: Medium
Description: Centralizes command execution, updates, and data exfiltration.
MISP IOCs: task-vault-54a2-356814497283.us-central1.run.app (threat: fakeapp)
```

These are real indicators from MISP Event 1910 and 1912 in the local instance — not hallucinated, not generic. The model is grounding its risk analysis in current intelligence.

---

## Part 4 — Surfacing Intel on CyberGrind

Two interfaces expose the MISP data publicly on cybergrind.org.

### MISP Tab on Threat Intel Feeds

The [Threat Intel Feeds](/tools/threat-intel-feeds/) tool now has a third tab alongside Security News and Live IOCs. The MISP Intel tab shows a filterable live feed of recent indicators, filterable by type (IP, domain, hash, URL, email). It pulls from `/api/misp/iocs` and links directly to the standalone lookup tool.

### MISP IOC Lookup Tool

The [MISP IOC Lookup](/tools/misp-ioc-lookup/) is a dedicated search interface. Enter any indicator value — or a fragment — and it returns full match details: type, threat category, source event, and first seen date. Multiple matches are shown in a table.

The tool uses `/api/misp/search` which does partial value matching, so searching for `shadow` will return `shadowroute.co` and any other indicators containing that string.

---

## Part 5 — Security Considerations

**Data stays local.** The MISP instance runs in Docker on a WSL2 host. The collector queries it over `host.docker.internal` from within the Windows Docker environment — traffic never leaves the machine. IOC data is stored in the SQLite database and served through the CTI API, which is the only internet-facing component.

**API key storage.** The MISP API key lives in `.env` files on the host and is passed to containers as an environment variable. It's never committed to version control. The `docker-compose.yml` references it as an environment variable rather than hardcoding it.

**Redis cache behavior.** MISP caches authentication lookups in Redis. Any time the auth key changes — rotation, new key generation — the Redis cache must be flushed or the old cached result will continue to reject the new key. This caught us during setup and is worth documenting explicitly.

**The CTI API is internet-facing.** The `/api/misp/iocs`, `/api/misp/search`, and `/api/misp/threat` endpoints are publicly accessible through the Cloudflare Tunnel at `api.cybergrind.org`. This is intentional — the tools pages need to reach them from the browser. The data returned is already-public threat intelligence from MISP's open feeds, so exposure isn't a concern. The MISP instance itself is not exposed.

**What MISP doesn't protect.** The pipeline integration doesn't validate or verify the IOCs it receives — it trusts the CTI API, which trusts MISP. If a MISP feed were compromised and injected false indicators, those would flow into the pipeline output. For a homelab setup this is an acceptable risk; for production threat intel workflows, feed validation and source reputation tracking would be appropriate additions.

---

## Closing

The pipeline now does something qualitatively different from before. When a report topic intersects with indicators in the MISP database, the Risk Analyst cites specific live IOCs rather than reasoning from generalized training knowledge alone. Reports on topics with active threat intel coverage are grounded in current data — domains, IPs, and hashes that were actually observed in campaigns.

The next unlock is OpenCTI connected to MISP as a feed aggregator. OpenCTI can ingest from dozens of sources — MISP, TAXII feeds, commercial threat intel — and expose a unified API. Wiring that into the pipeline would significantly expand the IOC coverage beyond what a single MISP instance provides.

That article is coming. For now, the self-hosted AI stack has a functional threat intelligence backbone.

---

*This article is part of the CyberGrind Orange Book — hands-on technical build documentation from the homelab.*
