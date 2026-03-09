---
name: "easy-search"
description: "Simple web search using multiple search engines with no API key required. Supports Google, Bing, DuckDuckGo, Baidu and returns parsed results."
---

# Easy Search Skill

A lightweight web search skill that doesn't require API keys. It uses direct HTTP requests to popular search engines and parses results using regex patterns.

## Features

- **No API key required** - Uses public search interfaces
- **Multiple engines** - Google, Bing, DuckDuckGo, Baidu
- **Proxy support** - Respects ALL_PROXY environment variable
- **Smart parsing** - Extracts titles and URLs from results
- **User agent rotation** - Helps avoid anti-bot detection

## Requirements

- Python 3.6+
- Required packages are bundled or use standard library

## Commands

```bash
# Basic search (default: 5 results)
python3 {baseDir}/scripts/search.py --query "your search terms"

# Specify engine (google, bing, duckduckgo, baidu)
python3 {baseDir}/scripts/search.py --query "your terms" --engine duckduckgo

# More results
python3 {baseDir}/scripts/search.py --query "your terms" --results 10

# JSON output
python3 {baseDir}/scripts/search.py --query "your terms" --format json

# Markdown output (more readable)
python3 {baseDir}/scripts/search.py --query "your terms" --format md
```

## Search Engines

| Engine | Notes |
|--------|-------|
| `google` | Best global search, may need proxy |
| `bing` | Good alternative, works well in many regions |
| `duckduckgo` | Privacy-focused, simpler to parse |
| `baidu` | Chinese content, easier to parse |

## Output Formats

### JSON (default)
```json
{
  "query": "search terms",
  "engine": "google",
  "results": [
    {
      "title": "Result Title",
      "url": "https://example.com",
      "snippet": "Brief description..."
    }
  ]
}
```

### Markdown
```
## Search Results for: your terms

1. [Result Title](https://example.com)
   Brief description...

2. [Another Title](https://another.com)
   More info...
```

## Examples

```bash
# Search for Python tutorials
python3 {baseDir}/scripts/search.py --query "Python programming tutorial" --engine google

# Search Chinese content
python3 {baseDir}/scripts/search.py --query "人工智能最新进展" --engine baidu

# Get more results in Markdown
python3 {baseDir}/scripts/search.py --query "machine learning frameworks" --results 15 --format md

# Use DuckDuckGo for privacy
python3 {baseDir}/scripts/search.py --query "privacy tools" --engine duckduckgo
```

## Notes

- Search results are fetched using HTTP requests, not a full browser
- Some engines may limit or block requests; try different engines if one fails
- Proxy setting via ALL_PROXY environment variable is respected
- Results are best-effort; some search pages may return empty results due to anti-bot measures

## Troubleshooting

- **Empty results**: Try a different engine (e.g., switch from Google to DuckDuckGo)
- **Connection errors**: Check your proxy settings or network connection
- **Rate limiting**: Wait a bit between searches, or switch engines