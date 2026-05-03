import pytest
from datetime import datetime, timezone
from feed_generator import deduplicate, sort_by_date, build_feed
import os


def make_item(url, published, category="General AI", title="Test Title", snippet="Test snippet"):
    return {"url": url, "published": published, "category": category, "title": title, "snippet": snippet}


def test_deduplicate_removes_duplicate_urls():
    items = [
        make_item("https://example.com/a", "2026-05-03T10:00:00Z"),
        make_item("https://example.com/a", "2026-05-03T10:00:00Z"),
        make_item("https://example.com/b", "2026-05-03T09:00:00Z"),
    ]
    result = deduplicate(items)
    assert len(result) == 2
    assert result[0]["url"] == "https://example.com/a"
    assert result[1]["url"] == "https://example.com/b"


def test_deduplicate_preserves_order():
    items = [
        make_item("https://example.com/c", "2026-05-03T08:00:00Z"),
        make_item("https://example.com/a", "2026-05-03T10:00:00Z"),
        make_item("https://example.com/b", "2026-05-03T09:00:00Z"),
        make_item("https://example.com/a", "2026-05-03T10:00:00Z"),
    ]
    result = deduplicate(items)
    assert [r["url"] for r in result] == [
        "https://example.com/c",
        "https://example.com/a",
        "https://example.com/b",
    ]


def test_sort_by_date_newest_first():
    items = [
        make_item("https://example.com/old", "2026-05-01T08:00:00Z"),
        make_item("https://example.com/new", "2026-05-03T10:00:00Z"),
        make_item("https://example.com/mid", "2026-05-02T12:00:00Z"),
    ]
    result = sort_by_date(items)
    assert result[0]["url"] == "https://example.com/new"
    assert result[1]["url"] == "https://example.com/mid"
    assert result[2]["url"] == "https://example.com/old"


def test_sort_by_date_handles_missing_date():
    items = [
        make_item("https://example.com/a", None),
        make_item("https://example.com/b", "2026-05-03T10:00:00Z"),
    ]
    result = sort_by_date(items)
    assert result[0]["url"] == "https://example.com/b"


def test_build_feed_creates_valid_rss_file(tmp_path):
    output = str(tmp_path / "feed.xml")
    items = [
        make_item("https://example.com/a", "2026-05-03T10:00:00Z", category="GTM Engineering", title="Article A"),
        make_item("https://example.com/b", "2026-05-02T08:00:00Z", category="Tool Stack", title="Article B"),
    ]
    build_feed(items, output_path=output)
    assert os.path.exists(output)
    content = open(output).read()
    assert "<rss" in content
    assert "Article A" in content
    assert "Article B" in content
    assert "GTM Intelligence Feed" in content
    assert "GTM Engineering" in content


def test_build_feed_plain_text_descriptions(tmp_path):
    output = str(tmp_path / "feed.xml")
    items = [make_item("https://example.com/a", "2026-05-03T10:00:00Z", snippet="<p>Some <b>html</b> snippet</p>")]
    build_feed(items, output_path=output)
    content = open(output).read()
    assert "Some" in content
