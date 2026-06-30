---
title: "Repo Secret Scanner — Detection Patterns Reference"
date: 2026-06-30
author: "Logan"
section: "Orange Book"
categories: ["Architecture"]
tags:
  - secret-scanning
  - credential-detection
  - regex
  - entropy
  - appsec
  - devops
description: "Complete reference for the CyberGrind Repo Secret Scanner detection patterns — Tier 1 prefix patterns, Tier 2 keyword-gated rules, Shannon entropy analysis, and what the scanner structurally cannot catch."
---

## Overview

The Repo Secret Scanner uses three detection tiers: high-confidence prefix-matched patterns (Tier 1), keyword-gated generic patterns (Tier 2), and Shannon entropy analysis for unrecognized secrets (Tier 3). This article documents every pattern in the current ruleset, their sources, their known limitations, and the structural gaps no static scanner can close.

This is the reference document for the detection logic. For the architectural decisions behind how these tiers fit together, see the companion article: [Repo Secret Scanner — Architecture & Design](/orange-book/repo-scanner-architecture/).

---

## Tier 1 — High-Confidence Prefix Patterns

These patterns match on distinctive credential-specific prefixes or structures. A match here is high-confidence — false positives are rare because the prefix itself is specific enough to be almost uniquely associated with a real credential format.

All Tier 1 patterns are sourced from official provider documentation or confirmed against real credential formats.

### AWS Credentials

```
(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}
```

AWS access key IDs use a multi-prefix format documented in the AWS IAM User Guide. `AKIA` is the most commonly seen prefix (long-term IAM user credentials), but the full family includes: `A3T` (various), `AGPA` (group), `AIDA` (user), `AROA` (role), `AIPA` (instance profile), `ANPA` (managed policy), `ANVA` (virtual MFA), and `ASIA` (STS temporary credentials).

A common mistake in older scanners is matching only `AKIA` — this misses STS session tokens (`ASIA`) and several other legitimate credential types. The full prefix family is the correct approach.

**Note:** The AWS secret access key (the other half of the credential pair) has no distinctive prefix — it's a 40-character base64 string. It will only be caught by Tier 3 entropy analysis if it appears in a quoted string literal near an AWS key.

### GitHub Personal Access Tokens

```
gh[pousr]_[A-Za-z0-9]{36}    (classic PATs)
github_pat_[A-Za-z0-9_]{82}  (fine-grained PATs)
```

GitHub introduced structured token prefixes in 2021. Classic PATs use a two-character type prefix:
- `ghp_` — personal access token
- `gho_` — OAuth token
- `ghu_` — user-to-server token
- `ghs_` — server-to-server token
- `ghr_` — refresh token

Fine-grained PATs (introduced 2022) use the `github_pat_` prefix followed by 82 characters. Both formats are matched.

**Note:** This is the format that was exposed in your own repo's git remote URL earlier in this session — a real-world example of exactly what this scanner is designed to catch.

### Slack Tokens

```
xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,34}
```

Slack tokens use a well-structured prefix format documented in the Slack API authentication docs:
- `xoxb-` — bot token
- `xoxa-` — app-level token
- `xoxp-` — user token
- `xoxr-` — refresh token
- `xoxs-` — workspace token

The pattern matches the full three-segment structure (prefix-workspace_id-token_body) rather than just the prefix, keeping false positives low.

### Stripe Keys

```
sk_live_[0-9a-zA-Z]{24,}   (secret key, live mode)
rk_live_[0-9a-zA-Z]{24,}   (restricted key, live mode)
```

Stripe test keys (`sk_test_`, `rk_test_`) are intentionally excluded — test mode keys cannot access production data and their presence in a repo is generally acceptable. Only live mode keys are flagged as critical findings.

### Google API Key

```
AIza[0-9A-Za-z_-]{35}
```

Google API keys use the `AIza` prefix, documented in the Google Cloud API documentation. The 35-character suffix gives this pattern very low false-positive potential.

### Cloudflare API Token

```
v1\.0-[A-Za-z0-9_-]{30,}
```

Cloudflare API tokens (distinct from legacy global API keys) use the `v1.0-` prefix. This format was confirmed against the Cloudflare API documentation. Legacy global API keys are a 37-character hex string with no prefix — they're only catchable via Tier 2 keyword-gating or Tier 3 entropy.

### SendGrid API Key

```
SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}
```

SendGrid API keys use a two-segment dotted structure after the `SG.` prefix. The segment lengths are consistent enough that this pattern has very low false-positive potential.

### Private Key Headers

```
-----BEGIN (RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----
```

PEM format private key headers are unambiguous — no credential type other than a private key starts with this exact string. All common key types are covered: RSA, EC (elliptic curve), OpenSSH, DSA, and PGP.

### Anthropic API Key

```
sk-ant-api03-[A-Za-z0-9_-]{93,}
```

Anthropic API keys use the `sk-ant-api03-` prefix. The long suffix (93+ characters) makes false positives essentially impossible.

### OpenAI API Key

```
sk-[A-Za-z0-9]{20,}T3BlbkFJ[A-Za-z0-9]{20,}
```

OpenAI keys contain the base64-encoded string `T3BlbkFJ` (which decodes to `OpenAI`) embedded in the key body. This embedded marker is the distinguishing feature — the `sk-` prefix alone is too generic (Stripe also uses `sk-`).

### Twilio Account SID

```
\btwilio[\s\S]{0,40}AC[a-f0-9]{32}\b
```

Twilio Account SIDs (`AC` + 32 hex characters) have no prefix that uniquely identifies them as Twilio credentials — `AC[a-f0-9]{32}` would match too broadly. The pattern is therefore keyword-gated: it only fires when the word "twilio" appears within 40 characters of the SID pattern.

---

## Tier 2 — Keyword-Gated Generic Patterns

These patterns match on variable naming conventions rather than on the credential value's own structure. They're intentionally broader than Tier 1 and have a meaningfully higher false-positive rate — a `.env.example` file with placeholder values will frequently trigger these rules.

All Tier 2 findings are scored "medium" severity and require manual review to confirm whether the matched value is a real credential or a placeholder.

### Generic API Key

```
(?:api[_-]?key)\s*[=:]\s*['"]([A-Za-z0-9_\-]{16,})['"]
```

Matches variable names like `api_key`, `apikey`, `api-key` followed by an assignment operator and a quoted string value of at least 16 characters.

### Generic Secret

```
(?:secret[_-]?key|secret)\s*[=:]\s*['"]([A-Za-z0-9_\-]{16,})['"]
```

Matches `secret_key`, `secret` variable names. Note that `secret` alone is a very common variable name in non-credential contexts — this rule produces more noise than the others.

### Generic Access Token

```
(?:access[_-]?token|auth[_-]?token)\s*[=:]\s*['"]([A-Za-z0-9_\-.]{16,})['"]
```

Matches `access_token`, `auth_token`, `access-token`, `auth-token` patterns. Common in OAuth configuration files.

### Generic Password

```
password\s*[=:]\s*['"]([^'"]{8,})['"]
```

Matches hardcoded password assignments. Highest false-positive rate of all Tier 2 rules — configuration files frequently contain placeholder password values like `password = "changeme"`. The known false-positive allowlist catches many of these.

### Database Connection String

```
(?:postgres|mysql|mongodb):\/\/[^:\s]+:([^@\s]+)@[^\s'"]+
```

Matches database connection strings with embedded credentials. This is scored "critical" rather than "medium" despite being a Tier 2 pattern because a matched database URI with an embedded password is an unambiguous real credential, not a structural guess.

---

## Tier 3 — Shannon Entropy Analysis

For credentials that don't match any known prefix and aren't sitting next to a recognizable keyword, the scanner falls back to statistical randomness analysis.

### The Formula

```
entropy(s) = -Σ p(x) * log₂(p(x))
```

For each unique character `x` in string `s`, `p(x)` is the probability of that character appearing (its count divided by the string length). The sum produces a bits-per-character measurement of randomness.

### Practical Values

| String | Entropy | Notes |
|---|---|---|
| `password` | ~2.75 bits/char | Low — repeated characters, common word |
| `changeme123` | ~3.1 bits/char | Low — predictable pattern |
| `AKIAIOSFODNN7EXAMPLE` | ~3.8 bits/char | Medium — but caught by Tier 1 prefix |
| `wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY` | ~4.6 bits/char | High — real AWS secret key pattern |
| `xoxb-123456-789012345-aBcDeFgHiJkLmNoPqRsTuVwXyZ (example only)` | ~4.8 bits/char | High — but caught by Tier 1 Slack pattern |

### Thresholds Used

- **Minimum length:** 16 characters (filters out short random-looking identifiers)
- **Entropy threshold:** > 4.5 bits/character
- **Character set:** alphanumeric plus `+`, `/`, `=`, `_`, `-` (base64 and URL-safe base64 charset)
- **Context:** quoted string literals only — `'value'` or `"value"`

### Deduplication

Tier 3 is skipped for any line that already produced a Tier 1 or Tier 2 match. This prevents double-counting and keeps the findings list clean.

---

## Known False-Positive Allowlist

The following values are automatically excluded from all tiers regardless of pattern match:

- `AKIAIOSFODNN7EXAMPLE` — AWS documentation example key
- `your_api_key` / `your-api-key` — common placeholder
- `xxxxxxxxxxxxxxxxxxxx` — common redaction placeholder
- `changeme` — common placeholder password
- `example.com` — common example domain

This list is intentionally conservative — only values that appear explicitly in provider documentation as examples or that are universally recognized placeholders are included. Anything not on this list is reported and left to the user to assess.

---

## What This Scanner Cannot Catch

These are structural limitations of static regex and entropy analysis — not bugs, but inherent constraints of the approach.

**Runtime-constructed secrets:** A credential assembled at runtime through string concatenation (`key = prefix + middle + suffix`) is invisible to static analysis. The scanner sees three strings, not a credential.

**Multi-line secrets:** The scanner processes files line by line. A secret split across two lines — common in YAML multi-line blocks or long string literals — won't match any pattern that expects the credential on a single line.

**Obfuscated secrets:** A credential base64-encoded, hex-encoded, or ROT13-rotated before being committed will not match any Tier 1 or Tier 2 pattern. Tier 3 entropy analysis may or may not catch it depending on the encoding's entropy characteristics.

**Git history:** The scanner reads the current state of files only. A secret committed in an earlier commit and deleted in a later one is not present in the current tree and will not be found. For full history scanning, `gitleaks detect --log-opts="--all"` run locally is the appropriate tool.

**Custom internal credential formats:** A 32-character hex string issued by your own service has no prefix the scanner can recognize and may or may not have high enough entropy to trigger Tier 3. If you know your internal credential formats, add custom patterns to the Worker's `TIER1_PATTERNS` array.

**Encrypted secrets:** Environment variable references (`${MY_SECRET}`) or secrets manager references (`sm://projects/...`) indicate a credential is being pulled from external storage — the actual value is never in the file.

---

## Key Sources

1. **AWS IAM Identifier Reference** — [docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html)
2. **GitHub Token Formats** — [docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github)
3. **Slack Token Types** — [api.slack.com/authentication/token-types](https://api.slack.com/authentication/token-types)
4. **Cloudflare API Token Docs** — [developers.cloudflare.com/fundamentals/api/get-started/](https://developers.cloudflare.com/fundamentals/api/get-started/)
5. **Gitleaks Default Ruleset** — [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) — reference for pattern structure and entropy thresholds
6. **Shannon, C.E.** — "A Mathematical Theory of Communication," Bell System Technical Journal, 1948
