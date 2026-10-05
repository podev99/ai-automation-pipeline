import json
import os
from typing import Set

STORAGE_FILE = "seen_articles.json"


def load_seen_articles(file_path: str = STORAGE_FILE) -> Set[str]:
    """Loads the set of processed article links from a local JSON file."""
    if not os.path.exists(file_path):
        return set()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load storage file ({e}). Starting fresh.")
        return set()


def save_seen_article(article_link: str, file_path: str = STORAGE_FILE) -> None:
    """Appends a new processed article link to the local JSON file."""
    seen_articles = load_seen_articles(file_path)
    seen_articles.add(article_link)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(list(seen_articles), f, indent=2)


if __name__ == "__main__":
    # Test storage operations
    test_link = "https://example.com/article-1"

    print(f"Is processed before saving? {test_link in load_seen_articles()}")
    save_seen_article(test_link)
    print(f"Is processed after saving? {test_link in load_seen_articles()}")