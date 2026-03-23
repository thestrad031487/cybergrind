import os
import datetime
import urllib.request
import json

# --- Config ---
BLOG_DIR = "content/blog"
TODAY = datetime.date.today()
FILENAME = f"{BLOG_DIR}/{TODAY.strftime('%Y-%m-%d')}-cybernews.md"

# --- Fetch headlines from NewsAPI ---
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

def generate_post(headlines):
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

    lines += [
        "",
        "---",
        "*Compiled daily. Stay patched, stay vigilant.*",
    ]

    return "\n".join(lines)

def main():
    os.makedirs(BLOG_DIR, exist_ok=True)

    if os.path.exists(FILENAME):
        print(f"Post already exists: {FILENAME}")
        return

    headlines = fetch_headlines()
    content = generate_post(headlines)

    with open(FILENAME, "w") as f:
        f.write(content)

    print(f"Created: {FILENAME}")

if __name__ == "__main__":
    main()