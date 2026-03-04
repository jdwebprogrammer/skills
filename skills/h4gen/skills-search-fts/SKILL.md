---
name: skills-search-fts
description: Instantly find the best AI agent skills, tools, and capabilities from across the entire web.
version: 1.0.2
metadata:
  openclaw:
    requires:
      bins:
        - python3
    files: ["scripts/*"]
    emoji: "\U0001F680"
---

# Global Skills Search

Stop building from scratch. This skill gives you instant access to a massive library of 240,000+ pre-built agent skills, specialized tool definitions, and expert system prompts indexed from across the internet.

## Why use this?

Discover existing high-quality capabilities for any task—fast. Whether you need a specialized web scraper, a financial analyzer, or a niche API integration, this search engine finds the most relevant, battle-tested agent tools available.

## Usage

Search by keywords to find exactly the capabilities you need.

```bash
python3 scripts/search.py "YOUR_QUERY"
```

## Example Queries

- **Basic**: `python3 scripts/search.py "browser automation"`
- **Multi-Skill**: `python3 scripts/search.py "reddit AND sentiment analysis"`
- **Specific**: `python3 scripts/search.py "stripe payment integration"`

## Response Format

The tool returns a prioritized list of matching skills, including their names, origins, and descriptions so you can instantly select the best one for your objective.
