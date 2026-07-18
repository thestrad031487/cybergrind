#!/usr/bin/env python3
"""
generate_ciso_brief.py

Generates a strategic/governance-angle companion post to the daily CyberNews
digest. Reads the already-scraped headlines from that day's cybernews post
(no re-scraping) and reframes 3-4 of them through Ollama with a board-level
risk/compliance/budget lens instead of the tactical "From the Trenches" angle.

Usage:
    python3 generate_ciso_brief.py --date 2026-07-15 \
        --blog-dir /path/to/cybergrind/content/blog \
        --ollama-model llama3.2:3b

Assumes:
    - That day's content/blog/YYYY-MM-DD-cybernews.md already exists
    - Ollama is running locally (default http://localhost:11434)
    - `requests` is installed (already in your requirements.txt)
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

STRATEGIC_SYSTEM_PROMPT = """You are writing a short daily "CISO Briefing" for a \
cybersecurity practitioner's blog. This briefing is for a security leadership \
/ board audience, not a technical one.

STRICT RULES:
1. Pick ONLY the 3-4 stories from the list below that have genuine board-level \
relevance (business risk, regulatory impact, budget/resourcing decisions). \
Skip purely technical/tactical items with no governance angle.
2. For each story you pick, write 2-3 sentences of real strategic analysis: \
business risk, regulatory/compliance implications, and what a CISO should \
actually DO about it (policy, vendor risk, board reporting, insurance — not \
just "patch it").
3. Do NOT start with an introductory sentence like "Here's my take" or "Let's \
look at". Start directly with your first story's analysis.
4. Do NOT include more than one "Boardroom Takeaway" line. Only one, ever.
5. The single "Boardroom Takeaway" line MUST be the very last line of your \
entire response — after all story analysis, nothing follows it.
6. Format the takeaway EXACTLY like this, with no quotation marks around it: \
**Boardroom Takeaway:** <one sentence naming the single thing worth raising \
in the next leadership meeting>
7. Write in a direct, first-person practitioner voice. No corporate buzzwords \
("synergy", "leverage", "paradigm"). No headers other than what's requested.
8. Keep the entire response under 400 words.
9. If you violate any rule above, you have failed the task."""


def strip_unicode_noise(text: str) -> str:
    """Strip zero-width and other non-printable Unicode characters."""
    # Zero-width space, zero-width non-joiner/joiner, BOM, and other
    # invisible formatting characters that have no business in scraped text.
    zero_width_pattern = re.compile(
        r"[\u200B-\u200F\u202A-\u202E\u2060-\u206F\uFEFF]"
    )
    return zero_width_pattern.sub("", text)


def extract_headlines(cybernews_path: Path) -> list[str]:
    """Pull the bulleted headline list out of the day's CyberNews post."""
    text = cybernews_path.read_text(encoding="utf-8")
    text = strip_unicode_noise(text)
    headline_lines = re.findall(r"^- \[.+?\]\(.+?\) — \*.+?\*$", text, re.MULTILINE)
    if not headline_lines:
        raise ValueError(f"No headlines found in {cybernews_path}")
    return headline_lines


def call_ollama(model: str, headlines: list[str]) -> str:
    prompt = (
        STRATEGIC_SYSTEM_PROMPT
        + "\n\nToday's headlines:\n"
        + "\n".join(headlines)
    )
    response = requests.post(
        OLLAMA_URL,
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def build_post(date_str: str, headlines: list[str], commentary: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    pretty_date = dt.strftime("%B %d, %Y")

    headline_block = "\n".join(headlines)

    return f"""---
title: "CISO Briefing {date_str}"
date: {date_str}T08:15:00-05:00
description: "Strategic and governance-angle cybersecurity briefing for {pretty_date}."
tags: ["news", "ciso", "governance", "daily"]
categories: ["CISO Briefing"]
draft: false
---

## Today's Stories, Governance Lens — {pretty_date}

{headline_block}

---

{commentary}

---

*A strategic companion to the daily [CyberNews]({{{{< ref "/blog/{date_str}-cybernews" >}}}}) digest. Compiled daily.*
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--blog-dir", required=True, type=Path)
    parser.add_argument("--ollama-model", default="llama3.1:8b")
    args = parser.parse_args()

    cybernews_path = args.blog_dir / f"{args.date}-cybernews.md"
    if not cybernews_path.exists():
        print(f"ERROR: {cybernews_path} not found. Run the CyberNews step first.", file=sys.stderr)
        sys.exit(1)

    headlines = extract_headlines(cybernews_path)
    commentary = call_ollama(args.ollama_model, headlines)
    post = build_post(args.date, headlines, commentary)

    out_path = args.blog_dir / f"{args.date}-ciso-brief.md"
    out_path.write_text(post, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
