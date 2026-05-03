# GTM Intelligence Feed

A self-updating RSS feed of curated AI and GTM engineering news, refreshed every morning at 7:00 AM ET.

**Feed URL:** `https://ichibahn11.github.io/ai-news-rss-feed/feed.xml`

## How It Works

Every day at 11:00 AM UTC (7:00 AM ET), a GitHub Actions workflow:

1. Reads the search queries defined in `queries.yaml`
2. Runs each query against the [Exa.ai](https://exa.ai) search API with a 3-day rolling date window
3. Deduplicates results by URL, sorts newest-first, and caps at 50 items
4. Writes a valid RSS 2.0 file (`feed.xml`) with category tags
5. Commits `feed.xml` back to the repo, where GitHub Pages serves it instantly

```
queries.yaml
    │
    ▼
Exa.ai API (27 queries, 3-day window)
    │
    ▼
Deduplicate → Sort by date → Cap at 50
    │
    ▼
feed.xml → GitHub Pages → Your RSS reader
```

## Subscribe in Slack

In any Slack channel, run:

```
/feed subscribe https://ichibahn11.github.io/ai-news-rss-feed/feed.xml
```

New articles will post to that channel each morning automatically.

## What's Covered

The feed tracks 5 categories across 27 search queries:

| Category | Topics |
|---|---|
| **General AI** | Foundation models, AEO/GEO, retrieval bots, vibe coding |
| **GTM Engineering** | Context engineering, waterfall enrichment, agentic GTM |
| **Tool Stack** | Clay, N8N, Octave, Lemlist, Exa.ai, Lovable, Cursor |
| **Key Practitioners** | Yash Tekriwal, Brendan Short, Kellen Casebeer, and more |
| **Alpha Signals** | Technographic data, board transcripts, high-signal triggers |

See `contentfilter.md` for the full content scoping logic.

## Updating the Feed

To add, remove, or change what gets tracked, edit `queries.yaml`:

```yaml
categories:
  - name: "Tool Stack"
    queries:
      - "Clay data enrichment workflow"   # ← add, remove, or edit queries here
      - "N8N Make.com automation workflow AI"
```

Commit and push — the next morning's run picks up the changes automatically. Keep the total query count under 30 to stay within the Exa.ai free tier (~1,000 searches/month).

## Running Locally

```bash
# Install dependencies
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run the feed generator
EXA_API_KEY=your_key_here python feed_generator.py

# Run tests
pytest tests/
```

## Tech Stack

- **Python 3.11** — feed generator script
- **[Exa.ai](https://exa.ai)** — semantic web search API
- **[feedgen](https://github.com/lkiesow/python-feedgen)** — RSS 2.0 XML generation
- **GitHub Actions** — daily cron scheduler
- **GitHub Pages** — static file hosting for `feed.xml`

## Files

| File | Purpose |
|---|---|
| `feed_generator.py` | Main script: search → deduplicate → sort → write XML |
| `queries.yaml` | Human-editable list of search queries by category |
| `contentfilter.md` | Reference doc describing the full content scoping logic |
| `.github/workflows/generate_feed.yml` | Daily GitHub Actions workflow |
| `index.html` | Landing page at the GitHub Pages URL |
| `feed.xml` | Generated RSS feed (updated daily by the workflow) |
