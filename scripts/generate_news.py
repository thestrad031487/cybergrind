import os
import datetime
import urllib.request
import urllib.error
import json

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
        req = urllib.request.Request(url, headers={"User-Agent": "CyberGrind/1.0"})
        with urllib.request.urlopen(req) as response:
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

    prompt = f"""You are a cybersecurity practitioner with 13+ years of experience writing a daily news blog called CyberGrind. Your audience is blue teamers and security practitioners doing hands-on work.

Here are today's cybersecurity headlines:

{headline_list}

Write a "From the Trenches" commentary section for these headlines. Follow these rules exactly:
- 2-3 short paragraphs, plain prose, no bullet points
- Pick the 2 most actionable or interesting stories and give your honest practitioner take
- Finish with a single line starting with "**🔧 Patch Priority:**" naming the most critical thing to patch today and why in one sentence
- Write in first person, direct and no-nonsense tone
- Do not use phrases like "as a cybersecurity professional" or "it's important to note"
- Do not add any intro or outro, just the commentary paragraphs and the patch priority line
- Do not use headers or markdown except for the bold patch priority line

Output only the commentary text, nothing else."""

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
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
