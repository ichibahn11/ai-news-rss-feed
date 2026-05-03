import os
import re
import yaml
from datetime import datetime, timedelta, timezone
from feedgen.feed import FeedGenerator
from exa_py import Exa


def load_queries(path="queries.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def search_category(exa, category_name, queries, results_per_query=2, days_back=3):
    start_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = []
    for query in queries:
        try:
            response = exa.search_and_contents(
                query,
                num_results=results_per_query,
                start_published_date=start_date,
                text={"max_characters": 300},
            )
            for r in response.results:
                if not r.url:
                    continue
                snippet = _strip_html(r.text or "")
                items.append({
                    "title": r.title or "Untitled",
                    "url": r.url,
                    "published": r.published_date,
                    "snippet": snippet or r.title or "No description available.",
                    "category": category_name,
                })
        except Exception as e:
            print(f"Warning: query '{query}' failed: {e}")
    return items


def _strip_html(text):
    return re.sub(r"<[^>]+>", "", text).strip()


def deduplicate(items):
    seen = set()
    unique = []
    for item in items:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)
    return unique


def sort_by_date(items):
    def parse(item):
        try:
            pub = item.get("published")
            if not pub:
                return datetime.min.replace(tzinfo=timezone.utc)
            return datetime.fromisoformat(pub.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return datetime.min.replace(tzinfo=timezone.utc)
    return sorted(items, key=parse, reverse=True)


def build_feed(items, output_path="feed.xml"):
    fg = FeedGenerator()
    fg.id("https://ichibahn11.github.io/ai-news-rss-feed/feed.xml")
    fg.title("GTM Intelligence Feed")
    fg.description("Daily AI and GTM engineering signals curated for the team")
    fg.link(href="https://ichibahn11.github.io/ai-news-rss-feed/feed.xml", rel="self")
    fg.link(href="https://ichibahn11.github.io/ai-news-rss-feed/", rel="alternate")
    fg.language("en")
    fg.lastBuildDate(datetime.now(timezone.utc))

    for item in items:
        fe = fg.add_entry()
        fe.id(item["url"])
        fe.title(item["title"])
        fe.link(href=item["url"])
        fe.description(item["snippet"])
        fe.category(term=item["category"])
        try:
            pub = item.get("published")
            pub_date = datetime.fromisoformat(pub.replace("Z", "+00:00")) if pub else datetime.now(timezone.utc)
        except (ValueError, AttributeError):
            pub_date = datetime.now(timezone.utc)
        fe.pubDate(pub_date)

    fg.rss_file(output_path)


def main():
    api_key = os.environ["EXA_API_KEY"]
    exa = Exa(api_key=api_key)
    config = load_queries()

    all_items = []
    for category in config["categories"]:
        print(f"Searching: {category['name']} ({len(category['queries'])} queries)")
        items = search_category(exa, category["name"], category["queries"])
        all_items.extend(items)

    all_items = deduplicate(all_items)
    all_items = sort_by_date(all_items)
    all_items = all_items[:50]

    build_feed(all_items)
    print(f"Feed generated: {len(all_items)} items written to feed.xml")


if __name__ == "__main__":
    main()
