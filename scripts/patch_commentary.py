#!/usr/bin/env python3
"""
patch_commentary.py — Backfill missing "From the Trenches" commentary
in existing CyberGrind daily news posts.

Usage:
    python3 scripts/patch_commentary.py content/blog/YYYY-MM-DD-cybernews.md
"""

import sys
import json
import urllib.request
import re

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"


def extract_headlines(content):
    """Extract headlines from existing post content."""
    headlines = []
    for line in content.splitlines():
        # Match lines like: - [Title](url) — *Source*
        match = re.match(r'^- \[(.+?)\]\(.+?\)\s*[—-]\s*\*(.+?)\*', line)
        if match:
            headlines.append({"title": match.group(1), "source": match.group(2)})
    return headlines


def generate_commentary(headlines):
    headline_list = "\n".join(f"- {h['title']} ({h['source']})" for h in headlines)

    prompt = f"""You are a cybersecurity practitioner writing a short commentary for a daily news blog called CyberGrind.

TODAY'S HEADLINES (you must ONLY reference these — do not mention any other CVEs, incidents, or stories):
{headline_list}

STRICT RULES:
1. You may ONLY reference stories from the list above. Do not invent, assume, or recall any other cybersecurity events.
2. Write 2-3 short paragraphs in plain prose. No bullet points, no headers.
3. Pick the 2 most interesting or actionable stories from the list above and give a direct practitioner take on them.
4. End with exactly one line starting with "**🔧 Patch Priority:**" — name a specific product or CVE from the headlines above and why it matters in one sentence.
5. Write in first person, direct and no-nonsense tone. No corporate speak.
6. Do not add any intro, outro, or commentary outside the paragraphs and patch priority line.
7. If you reference a story not in the list above, you have failed the task.

Write the commentary now, referencing ONLY the headlines provided:"""

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.5,
            "num_predict": 400,
        }
    }).encode()

    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=300) as response:
            data = json.loads(response.read().decode())
            return data.get("response", "").strip()
    except Exception as e:
        print(f"Ollama commentary generation failed: {e}")
        return None


def patch_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    # Check if commentary already exists
    if "## From the Trenches" in content:
        print(f"Commentary already exists in {filepath}, skipping.")
        return

    # Extract headlines
    headlines = extract_headlines(content)
    if not headlines:
        print(f"No headlines found in {filepath}, aborting.")
        return

    print(f"Found {len(headlines)} headlines in {filepath}")
    print("Generating commentary via Ollama...")

    commentary = generate_commentary(headlines)
    if not commentary:
        print("Commentary generation failed, aborting.")
        return

    # Insert commentary before the final line
    commentary_block = "\n## From the Trenches\n\n" + commentary + "\n\n---\n"

    # Insert before the last line (*Compiled daily...*)
    if "*Compiled daily" in content:
        content = content.replace(
            "\n*Compiled daily",
            commentary_block + "\n*Compiled daily"
        )
    else:
        # Fallback: append at end
        content = content.rstrip() + "\n" + commentary_block

    with open(filepath, "w") as f:
        f.write(content)

    print(f"Patched: {filepath}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 patch_commentary.py <path-to-post.md>")
        sys.exit(1)

    patch_file(sys.argv[1])
