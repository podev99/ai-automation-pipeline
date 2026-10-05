from typing import Dict, Optional
import feedparser


def fetch_latest_entry(rss_url: str) -> Optional[Dict[str, str]]:
    """Fetches the latest article entry from a given RSS feed URL using a custom User-Agent."""
    custom_user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    feed = feedparser.parse(rss_url, agent=custom_user_agent)

    if not feed.entries:
        return None

    latest_entry = feed.entries[0]
    return {
        "title": latest_entry.get("title", ""),
        "link": latest_entry.get("link", ""),
        "summary": latest_entry.get("summary", ""),
    }


if __name__ == "__main__":
    # Test with a stable tech RSS feed
    test_url = "https://news.ycombinator.com/rss"
    entry = fetch_latest_entry(test_url)
    print("Latest RSS Entry:")
    print(entry)