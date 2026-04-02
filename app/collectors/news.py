import feedparser
from app.database import get_connection

RSS_FEEDS = [
    {"url": "https://krebsonsecurity.com/feed/", "source": "Krebs on Security"},
    {"url": "https://www.bleepingcomputer.com/feed/", "source": "Bleeping Computer"},
    {"url": "https://feeds.feedburner.com/TheHackersNews", "source": "The Hacker News"},
    {"url": "https://www.cisa.gov/news.xml", "source": "CISA"},
    {"url": "https://isc.sans.edu/rssfeed.xml", "source": "SANS ISC"},
]

def collect_news():
    print("Collecting security news...")
    conn = get_connection()
    cursor = conn.cursor()
    inserted = 0

    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries[:20]:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO news (
                            title,
                            link,
                            source,
                            summary,
                            published
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        entry.get("title"),
                        entry.get("link"),
                        feed["source"],
                        entry.get("summary", "")[:500],
                        entry.get("published", ""),
                    ))
                    if cursor.rowcount > 0:
                        inserted += 1
                except Exception as e:
                    print(f"Error inserting article: {e}")

            print(f"{feed['source']}: processed {len(parsed.entries[:20])} articles")

        except Exception as e:
            print(f"Failed to collect from {feed['source']}: {e}")

    conn.commit()
    conn.close()
    print(f"News: {inserted} new articles added")