---
title: "Repo Secret Scanner — Architecture & Design"
date: 2026-06-30
author: "Logan"
section: "Orange Book"
categories: ["Architecture"]
tags:
  - cloudflare-workers
  - github-api
  - secret-scanning
  - credential-detection
  - homelab
  - appsec
  - devops
description: "How the CyberGrind Repo Secret Scanner was designed and built — the GitHub tree API approach, why no clone is needed, the Tier 1/2/3 detection architecture, and every design decision made along the way."
---

## Overview

The Repo Secret Scanner at `cybergrind.org/tools/repo-scanner/` scans public GitHub repositories for exposed credentials — AWS keys, GitHub tokens, Slack tokens, Stripe keys, private keys, and more — without ever cloning the repository. It runs entirely on a Cloudflare Worker, reads files directly via the GitHub API, and returns a severity-scored dashboard of findings with matched secrets redacted before they ever leave the scanner.

This article covers the architectural decisions behind the build: why the GitHub tree API instead of a clone, how the detection tiers work, what design tradeoffs were made for v1, and what the request flow looks like end to end.

---

## The Core Constraint — No Filesystem

The most important design decision wasn't about detection logic — it was about the runtime environment.

Cloudflare Workers don't have a filesystem. There's no persistent disk, no shell access, no way to run `git clone` and walk a local directory. This rules out the approach most local secret scanners take (gitleaks, trufflehog) — which is to clone the repo, then scan the working tree or git history directly.

The alternative: use the GitHub API to replicate what a clone-and-walk would do, without any of the infrastructure.

---

## The GitHub Tree API Approach

A naive implementation would walk a repo directory-by-directory, making one API call per directory to list its contents, then another call per file to fetch content. For a 300-file repo, that's potentially hundreds of sequential API calls before a single line of detection logic runs.

The better approach is the GitHub Git Trees API:

```
GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1
```

One call. It returns every file path and blob SHA in the entire repository tree, including their sizes. This means:

- **One API call** to get the complete file inventory
- **Filter before fetching** — skip binaries, lockfiles, and noise paths based on the tree response alone, with zero extra API calls
- **Batch fetch** only the files worth scanning, in controlled concurrent chunks

For a 300-file repo, that's one tree call plus however many content fetches survive the filter — typically far fewer than 300 once lockfiles, binaries, and vendored directories are excluded.

---

## Request Flow

```
User submits owner/repo
  ↓
Parse and validate input
  ↓
GET /repos/{owner}/{repo} — confirm repo exists, is public, get default branch
  ↓
GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1 — full file inventory
  ↓
Filter tree: skip binaries, noise paths, files over 1MB
  ↓
Sort remaining files alphabetically (deterministic scan order)
  ↓
Cap at 500 files — flag partial scan if over limit
  ↓
Batch fetch file content via raw.githubusercontent.com (10 concurrent)
  ↓
Run Tier 1 → Tier 2 → Tier 3 detection on each file's content
  ↓
Score findings by severity
  ↓
Redact matched secrets (first 4 / last 4 characters only)
  ↓
Build summary: bySeverity, byType, topFiles
  ↓
Return JSON response to frontend
```

The raw content fetch goes to `raw.githubusercontent.com` rather than the Contents API (`/repos/{owner}/{repo}/contents/{path}`) because raw content is a direct HTTP response rather than a JSON envelope with base64-encoded content — simpler, faster, and doesn't require a decode step.

---

## The Detection Tier Architecture

Rather than a flat list of regex patterns, detection is organized into three tiers with different confidence levels and false-positive characteristics.

### Tier 1 — High-confidence prefix matches

These patterns target credentials with distinctive enough prefixes that a regex match alone is strong evidence of a real secret. No entropy check needed — the prefix structure is sufficiently specific.

Examples: `AKIA[A-Z0-9]{16}` for AWS access keys, `ghp_[A-Za-z0-9]{36}` for GitHub PATs, `sk_live_[0-9a-zA-Z]{24,}` for Stripe live keys, `-----BEGIN RSA PRIVATE KEY-----` for private key headers.

False-positive rate: very low. These are fired against the TruffleHog test fixtures repo and correctly identified an AWS access key and a private key header with zero false positives.

### Tier 2 — Keyword-gated generic patterns

These patterns match on variable naming conventions — `api_key = "..."`, `secret = "..."`, `password = "..."` — rather than on the credential value's own structure. They're noisier because they depend entirely on the variable name being recognizable as security-relevant.

The tradeoff is coverage: plenty of real credentials don't have a distinctive prefix (a custom internal API key issued by your own service won't look like an AWS key) but will almost always be assigned to a variable with a recognizable name.

False-positive rate: medium. A `.env.example` file with `API_KEY=your-api-key-here` will fire Tier 2 rules unless the value matches the known false-positive allowlist.

### Tier 3 — Shannon entropy fallback

For anything that doesn't match a known prefix and isn't sitting next to a recognizable keyword, the scanner falls back to statistical analysis. Shannon entropy measures the randomness of a string — a genuinely random secret (a 40-character base64 string) has high entropy; a human-readable word or placeholder doesn't.

```
entropy = -Σ p(x) * log2(p(x))
```

Practical thresholds: quoted string literals above 4.5 bits/character with a minimum length of 16 characters are flagged as high-entropy findings.

Tier 3 findings are automatically scored "low" severity to reflect their higher false-positive rate — they require human review before acting on them.

**Deduplication:** Tier 3 is skipped entirely for lines that already produced a Tier 1 or Tier 2 match, avoiding double-counting.

---

## Severity Scoring

Detection confidence (how sure we are it matched something) and severity (how bad it is if it did) are different axes. A Tier 3 entropy match could theoretically be a critical production credential — but we don't know that from structure alone, so it's scored "low" pending human review. A Tier 1 AWS key match is both high-confidence and critical regardless of which tier found it.

The scoring is independent of detection tier:

| Severity | Credential Types |
|---|---|
| Critical | AWS keys, Stripe live keys, private keys, GitHub PATs, Anthropic/OpenAI keys, database connection strings |
| High | Slack tokens, Cloudflare tokens, SendGrid keys, Google API keys, Twilio SIDs |
| Medium | Generic keyword-matched API keys, secrets, passwords, access tokens |
| Low | High-entropy string (entropy-only, unrecognized pattern) |

---

## Redaction

Findings are never returned with the full matched value — not even to the user scanning their own repo. The response shows first 4 / last 4 characters with asterisks in between:

```
AKIA****************ZAM2
sk_l**********************3x9f
```

This protects against the API response being logged, screenshot, or accidentally shared. The user already knows their own credentials; what they need is the file path and line number to locate and rotate the secret, not the value itself reproduced in a scan report.

---

## Design Decisions — What's Not in v1

Several features were explicitly scoped out:

**Private repos** — would require an OAuth flow where the user grants the tool read access to their private code. The trust jump is significant, the build complexity is meaningful, and the security surface (storing user OAuth tokens) is outside the risk appetite for a public tool running on a free Worker. Public-only for v1.

**Full git history scanning** — detecting secrets that were committed and later deleted requires walking every commit in the repo's history, not just the current file state. This is what tools like `gitleaks detect --log-opts="--all"` do locally. In a serverless Worker, the only equivalent would be paginating through the Commits API and fetching diff content per commit — feasible in theory, but the API call volume for a repo with thousands of commits would exhaust rate limits immediately. Not in v1.

**Streaming progress** — a scan of 500 files with 10 concurrent fetches completes in roughly 15-30 seconds on a typical repo. Cloudflare Workers have a CPU time limit per invocation, not a wall-clock limit, so this fits within a single request/response cycle. Streaming would add significant complexity (Server-Sent Events or a polling architecture) for a problem the conservative file cap mostly avoids.

**Caching** — repeated scans of the same repo re-fetch and re-scan everything. A KV-based cache keyed on `owner/repo/{commit-sha}` with a short TTL would eliminate redundant work if the tool gets real traffic. Explicitly noted as the highest-value v2 addition.

---

## Infrastructure

The scanner runs as a Cloudflare Worker with a GitHub Personal Access Token stored as a Worker secret via `wrangler secret put`. The token is scoped to public repository read access only — no write access, no private repo access.

The frontend is a standard Hugo layout file (`layouts/_default/repo-scanner.html`) with a separate static JavaScript file (`static/js/repo-scanner.js`), following the same convention as the other CyberGrind tools. The Worker is deployed at `repo-scanner.cybergrind.org` as a custom domain on the Cloudflare Workers route.

CORS is locked to `https://cybergrind.org` on the Worker, so the API endpoint cannot be called from arbitrary origins.

---

## Key Sources

1. **GitHub REST API — Git Trees** — [docs.github.com/rest/git/trees](https://docs.github.com/en/rest/git/trees)
2. **GitHub REST API — Rate Limits** — [docs.github.com/rest/overview/rate-limits](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
3. **Cloudflare Workers — Limits** — [developers.cloudflare.com/workers/platform/limits](https://developers.cloudflare.com/workers/platform/limits/)
4. **Shannon Entropy** — Claude E. Shannon, "A Mathematical Theory of Communication," 1948
5. **Gitleaks** — [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) — reference implementation for detection architecture patterns
