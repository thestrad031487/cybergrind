import os
import datetime
import urllib.request
import urllib.error
import json
import ssl

# --- Config ---
BLOG_DIR = "content/blog"
TODAY = datetime.date.today()
FILENAME = f"{BLOG_DIR}/{TODAY.strftime('%Y-%m-%d')}-cybernews.md"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

# --- NewsAPI ---
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

def fetch_headlines():
    if not NEWS_API_KEY:
        return [
            {"title": "CISA Adds New KEV Entry", "url": "https://cisa.gov", "source": "CISA"},
            {"title": "Critical Vulnerability Discovered", "url": "#", "source": "SecurityWeek"},
        ]

    url = (
        "https://newsapi.org/v2/everything"
        f"?q=cybersecurity+vulnerability+threat"
        f"&sortBy=publishedAt"
        f"&pageSize=10"
        f"&apiKey={NEWS_API_KEY}"
    )

    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "CyberGrind/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            data = json.loads(response.read().decode())
            articles = data.get("articles", [])
            return [
                {"title": a["title"], "url": a["url"], "source": a["source"]["name"]}
                for a in articles
                if a.get("title") and "[Removed]" not in a["title"]
            ]
    except Exception as e:
        print(f"Failed to fetch headlines: {e}")
        return []

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

def generate_post(headlines, commentary=None):
    date_str = TODAY.strftime("%B %d, %Y")
    iso_date = TODAY.strftime("%Y-%m-%dT08:00:00-05:00")

    lines = [
        "---",
        f'title: "CyberNews {TODAY.strftime("%Y-%m-%d")}"',
        f"date: {iso_date}",
        f'description: "Daily cybersecurity headlines and practitioner commentary for {date_str}."',
        'tags: ["news", "daily"]',
        'categories: ["Daily News"]',
        "draft: false",
        "---",
        "",
        f"## Cybersecurity Headlines — {date_str}",
        "",
    ]

    for item in headlines:
        lines.append(f"- [{item['title']}]({item['url']}) — *{item['source']}*")

    lines += ["", "---", ""]

    if commentary:
        lines += [
            "## From the Trenches",
            "",
            commentary,
            "",
            "---",
            "",
        ]

    lines.append("*Compiled daily. Stay patched, stay vigilant.*")

    return "\n".join(lines)

def main():
    os.makedirs(BLOG_DIR, exist_ok=True)

    if os.path.exists(FILENAME):
        print(f"Post already exists: {FILENAME}")
        return

    print("Fetching headlines...")
    headlines = fetch_headlines()
    if not headlines:
        print("No headlines fetched, aborting.")
        return

    print(f"Got {len(headlines)} headlines")
    print("Generating commentary via Ollama...")
    commentary = generate_commentary(headlines)
    if not commentary:
        print("Warning: commentary generation failed, post will be created without it")

    content = generate_post(headlines, commentary)

    with open(FILENAME, "w") as f:
        f.write(content)

    print(f"Created: {FILENAME}")

if __name__ == "__main__":
    main()
