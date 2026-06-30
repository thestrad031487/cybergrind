---
title: "Repo Secret Scanner — Deployment Guide"
date: 2026-06-30
author: "Logan"
section: "Orange Book"
categories: ["Architecture"]
tags:
  - cloudflare-workers
  - wrangler
  - hugo
  - deployment
  - homelab
  - devops
description: "Step-by-step deployment guide for the CyberGrind Repo Secret Scanner — Cloudflare Worker setup, GitHub token scoping, Hugo integration, CORS configuration, and v2 improvement roadmap."
---

## Overview

This guide covers the complete deployment of the Repo Secret Scanner from a fresh clone to a live public tool. It assumes you're deploying into the same stack used for CyberGrind: Hugo + PaperMod on Cloudflare Pages, Cloudflare Workers for serverless backend functions, and GitHub for source control.

For the architecture behind what's being deployed, see [Repo Secret Scanner — Architecture & Design](/orange-book/repo-scanner-architecture/). For the detection pattern documentation, see [Repo Secret Scanner — Detection Patterns Reference](/orange-book/repo-scanner-detection-patterns/).

---

## Prerequisites

- Cloudflare account with Workers enabled
- `wrangler` CLI installed (`npm install -g wrangler`)
- GitHub account with permission to create Personal Access Tokens
- Hugo site repo with the `layouts/_default/` and `static/js/` conventions in place

---

## Step 1 — Create the Worker Directory

Keep the Worker separate from your Hugo site repo — it's a different deployment target with its own `wrangler.toml` and doesn't need to be part of the same git history.

```bash
mkdir ~/repo-scanner-worker
cd ~/repo-scanner-worker
```

Create `wrangler.toml`:

```toml
name = "repo-scanner"
main = "worker.js"
compatibility_date = "2026-06-30"

[observability]
enabled = true
```

---

## Step 2 — Authenticate Wrangler

```bash
wrangler login
```

This opens a browser window to authenticate with your Cloudflare account. Once authorized, wrangler stores credentials locally and you won't need to log in again for subsequent deployments.

---

## Step 3 — Create the GitHub Personal Access Token

The Worker needs a GitHub PAT to call the GitHub API at 5,000 requests/hour (vs. 60/hour unauthenticated). Scope it to the absolute minimum:

1. Go to `github.com/settings/tokens` → Generate new token (classic)
2. Set an expiration (90 days is reasonable — calendar a rotation reminder)
3. Select **only** `public_repo` under the `repo` scope — no other scopes needed
4. Generate and copy the token value

The token only needs to read public repository data. It cannot access private repos, cannot write anything, and cannot be used for any action beyond reading public code.

---

## Step 4 — Set the Token as a Worker Secret

```bash
cd ~/repo-scanner-worker
wrangler secret put GITHUB_TOKEN
```

Wrangler will prompt for the token value. Paste it and press enter. The secret is stored encrypted in Cloudflare's infrastructure — it's never visible again after this point, even to you. If you need to rotate it, run `wrangler secret put GITHUB_TOKEN` again with the new value.

If the Worker doesn't exist yet, wrangler will ask if you want to create it — confirm yes.

---

## Step 5 — Deploy the Worker

Place `worker.js` in `~/repo-scanner-worker/` (the full source is in the companion architecture article's GitHub repository), then:

```bash
wrangler deploy
```

Output confirms the deployment and gives you the default `*.workers.dev` URL:

```
Deployed repo-scanner triggers
  https://repo-scanner.YOUR-ACCOUNT.workers.dev
```

Test it immediately before setting up the custom domain:

```bash
curl -X POST https://repo-scanner.YOUR-ACCOUNT.workers.dev \
  -H "Content-Type: application/json" \
  -d '{"repo": "trufflesecurity/test_keys"}'
```

Expected response: two critical findings (a private key and an AWS access key), both redacted to first4/last4, with a clean summary dashboard payload.

---

## Step 6 — Set Up a Custom Domain

The `*.workers.dev` URL works but isn't consistent with the rest of your tooling. Set up a custom subdomain:

1. Go to **Cloudflare Dashboard → Workers & Pages → repo-scanner → Settings → Domains & Routes → Add → Custom Domain**
2. Enter your subdomain (e.g. `repo-scanner.cybergrind.org`)
3. Cloudflare automatically creates the DNS record and provisions a certificate

Once propagated (usually under a minute), test via the custom domain:

```bash
curl -X POST https://repo-scanner.cybergrind.org \
  -H "Content-Type: application/json" \
  -d '{"repo": "thestrad031487/cybergrind"}'
```

---

## Step 7 — Hugo Frontend Integration

The frontend follows the same layout + static JS pattern used by the other CyberGrind tools (ip-reputation, cve-research, etc.).

**Content file** — `content/tools/repo-scanner.md`:

```yaml
---
title: "Repo Secret Scanner"
layout: "repo-scanner"
draft: false
---
```

**Layout file** — `layouts/_default/repo-scanner.html`:
The full layout is the Hugo `define "main"` template containing the input box, results container, severity dashboard markup, CSS, and a `<script src="/js/repo-scanner.js">` reference. See the source in the repo.

**Static JS** — `static/js/repo-scanner.js`:
Contains `parseRepoInput()`, `escapeHtml()`, `renderResults()`, and `scanRepo()`, wrapped in a `DOMContentLoaded` listener. The `WORKER_URL` constant at the top should point to your custom domain.

---

## Step 8 — Add to Hugo Nav

The CyberGrind Tools dropdown requires two updates — `hugo.toml` for pages using the theme's default header, and `layouts/partials/header.html` for the hardcoded custom dropdown:

In `hugo.toml`, add after Risk Register:

```toml
[[menu.main]]
  identifier = "reposcanner"
  name = "Repo Secret Scanner"
  url = "/tools/repo-scanner/"
  parent = "tools"
  weight = 4
```

In `layouts/partials/header.html`, add after the Risk Register `<li>`:

```html
<li><a href="/tools/repo-scanner/">Repo Secret Scanner</a></li>
```

---

## Step 9 — Test the Full Stack

```bash
hugo --minify 2>&1 | grep -E "Pages|Total|ERROR|WARN"
git add content/tools/repo-scanner.md layouts/_default/repo-scanner.html static/js/repo-scanner.js hugo.toml layouts/partials/header.html
git commit -m "Add Repo Secret Scanner tool"
git pull --rebase
git push origin main
```

Once Cloudflare Pages deploys, verify in browser:
- Tool page loads at `/tools/repo-scanner/`
- "Repo Secret Scanner" appears in Tools dropdown
- Paste a repo URL and confirm the severity dashboard renders with real results

---

## CORS Configuration

The Worker's `jsonResponse` function locks the `Access-Control-Allow-Origin` header to `https://cybergrind.org`:

```javascript
'Access-Control-Allow-Origin': 'https://cybergrind.org'
```

This means the Worker API cannot be called from any other origin — protecting your GitHub token's rate limit quota from being consumed by third-party sites.

**Local development gotcha:** When testing with `hugo server` (which runs on `localhost:1313`), the browser will block requests to the Worker due to CORS. Two options:

1. Temporarily change the CORS header to `*` for local testing, then change it back before deploying
2. Use `curl` directly to test the Worker independently of the frontend during development

Always lock CORS back to the production domain before deploying.

---

## Token Rotation

The GitHub PAT has an expiration date you set in Step 3. When it expires, the Worker will return GitHub API 401 errors for every scan.

Rotation process:

1. Generate a new token at `github.com/settings/tokens` with the same `public_repo` scope
2. `wrangler secret put GITHUB_TOKEN` in the `~/repo-scanner-worker/` directory
3. Paste the new token value
4. Test with a curl scan to confirm the new token is active

No redeployment of `worker.js` is needed — secrets are stored and updated independently of the Worker code.

---

## v2 Improvement Roadmap

These are the features explicitly deferred from v1, in rough priority order:

**KV-based response caching** — Cache scan results keyed on `{owner}/{repo}/{commit-sha}` with a 1-hour TTL. Eliminates redundant scanning of unchanged repos and cuts GitHub API usage significantly if the tool gets real traffic. Cloudflare Workers KV is available on the free tier.

**Rate limiting** — Add Cloudflare's built-in rate limiting rules on the Worker route to prevent a single user from exhausting the GitHub token's hourly quota. Set a per-IP limit (e.g. 10 scans/hour) via the Cloudflare dashboard → Security → WAF → Rate Limiting.

**Private repo support** — Requires a GitHub OAuth flow: redirect the user to GitHub for authorization, receive an OAuth token scoped to their private repos, use it for the scan, and discard it immediately after (no token storage). Significant build complexity and trust requirement — not suitable until the tool has established public credibility.

**Full git history scanning** — Walk commit history via the Commits API, fetch diff content per commit, scan additions only. Rate-limit intensive — would require aggressive caching and probably a higher GitHub API tier to be practical for repos with thousands of commits.

**Remediation guidance per finding type** — Instead of just reporting `AWS Access Key found in config.py:42`, return actionable next steps: "Rotate at console.aws.amazon.com/iam, check CloudTrail for usage since [date], add to .gitignore." Currently out of scope but straightforward to add to the severity map.

---

## Key Sources

1. **Cloudflare Workers Documentation** — [developers.cloudflare.com/workers](https://developers.cloudflare.com/workers/)
2. **Wrangler CLI Reference** — [developers.cloudflare.com/workers/wrangler](https://developers.cloudflare.com/workers/wrangler/)
3. **GitHub Personal Access Tokens** — [docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
4. **Cloudflare Workers KV** — [developers.cloudflare.com/kv](https://developers.cloudflare.com/kv/)
5. **Hugo Layouts Documentation** — [gohugo.io/templates/introduction](https://gohugo.io/templates/introduction/)
