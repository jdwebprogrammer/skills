#!/usr/bin/env python3
"""
Easy Search - A simple web search tool with no API key required.
Supports multiple search engines and respects proxy settings.
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from typing import List, Dict, Optional


# User agents rotation for anti-bot detection
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


# Search engine configurations
ENGINES = {
    "google": {
        "name": "Google",
        "url_template": "https://www.google.com/search?q={query}&num={num}",
        "result_patterns": [
            (r'<h3[^>]*><a[^>]*href=\"([^\"]+)\"[^>]*>([^<]+)</a></h3>', "title_url"),
            (r'<a[^>]*class=\"[^\"]*\"[^>]*href=\"(\/url\?q[^\"]+)\"[^>]*>([^<]+)</a>', "google_redirect"),
        ],
    },
    "bing": {
        "name": "Bing",
        "url_template": "https://www.bing.com/search?q={query}&count={num}",
        "result_patterns": [
            (r'<h2[^>]*><a[^>]*href=\"([^\"]+)\"[^>]*>([^<]+)</a></h2>', "title_url"),
            (r'<cite>([^<]+)</cite>', "url_only"),
        ],
    },
    "duckduckgo": {
        "name": "DuckDuckGo",
        "url_template": "https://duckduckgo.com/html/?q={query}",
        "result_patterns": [
            (r'<a[^>]*class=\"result__a\"[^>]*href=\"([^\"]+)\"[^>]*>([^<]+)</a>', "title_url"),
            (r'<a[^>]*rel=\"nofollow\"[^>]*href=\"([^\"]+)\"[^>]*>([^<]+)</a>', "title_url"),
        ],
    },
    "baidu": {
        "name": "Baidu",
        "url_template": "https://www.baidu.com/s?wd={query}&rn={num}",
        "result_patterns": [
            (r'<h3[^>]*class=[\'"][^\'"]*[tT][^\'"]*[\'"][^>]*>.*?<a[^>]*href=\"([^\"]+)\"[^>]*>([^<]+)</a>', "baidu_link"),
            (r'<a[^>]*data-click=\".*?href=[\'\"]([^\'\"]+)[\'\"][^>]*>([^<]+)</a>', "data_click"),
        ],
    },
}


def get_proxy_handler():
    """Create proxy handler from environment variables."""
    proxy_url = os.environ.get("ALL_PROXY") or os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    if proxy_url:
        return {
            "https": urllib.request.ProxyHandler({"https": proxy_url}),
            "http": urllib.request.ProxyHandler({"http": proxy_url}),
        }
    return {"https": urllib.request.HTTPHandler(), "http": urllib.request.HTTPHandler()}


def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch URL content with proxy support."""
    try:
        # Prepare opener with proxy support
        handlers = get_proxy_handler()
        socket_handler = urllib.request.HTTPSHandler() if url.startswith("https") else urllib.request.HTTPHandler()
        opener = urllib.request.build_opener(handlers.get("https", socket_handler), handlers.get("http", socket_handler))

        # Add user agent
        import random
        user_agent = random.choice(USER_AGENTS)

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8",
            },
        )

        with opener.open(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None


def parse_results(html: str, engine: str, max_results: int) -> List[Dict[str, str]]:
    """Parse search results from HTML."""
    if engine not in ENGINES:
        return []

    results = []
    seen_urls = set()
    engine_config = ENGINES[engine]

    for pattern, pattern_type in engine_config["result_patterns"]:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for match in matches:
            if len(results) >= max_results:
                break

            if pattern_type == "title_url":
                url, title = match
                # Clean up URLs
                if url.startswith("/url?q="):
                    url = urllib.parse.unquote(re.search(r"/url\?q=([^&]+)", url).group(1))
                elif url.startswith("///"):
                    url = url[3:]
            elif pattern_type == "google_redirect":
                url, title = match
                if url.startswith("/url?q="):
                    url = urllib.parse.unquote(re.search(r"/url\?q=([^&]+)", url).group(1))
            elif pattern_type == "baidu_link":
                url, title = match
                # Baidu URLs may be encoded
            elif pattern_type == "data_click":
                url, title = match
                # Extract actual URL from data-click
                url_match = re.search(r'url[:]?[=:](["\']?)([^"\']+)\1', url)
                if url_match:
                    url = url_match.group(2)
            elif pattern_type == "url_only":
                url = match
                title = ""
            else:
                continue

            # Skip invalid URLs
            if not url or url.startswith("#") or url.startswith("javascript:"):
                continue

            # Skip duplicates
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Extract snippet if possible
            snippet = ""
            snippet_match = re.search(r'<span[^>]*class[^\"]*([^\"]+)\"[^\>]*>([^<]+)</span>', html[html.find(url):html.find(url)+500])
            if snippet_match:
                snippet = snippet_match.group(2).strip()

            results.append({
                "title": title.strip() if title else "No title",
                "url": url.strip(),
                "snippet": snippet
            })

    return results


def search(query: str, engine: str = "google", max_results: int = 5) -> Dict:
    """Perform web search."""
    if engine not in ENGINES:
        return {"error": f"Unknown engine: {engine}. Available: {', '.join(ENGINES.keys())}"}

    # Encode query
    encoded_query = urllib.parse.quote_plus(query)

    # Build URL
    num_results = max_results + 5  # Request more to account for filtering
    url = ENGINES[engine]["url_template"].format(query=encoded_query, num=num_results)

    # Fetch HTML
    html = fetch_url(url)

    if html is None:
        return {"error": f"Failed to fetch search results from {ENGINES[engine]['name']}"}

    # Parse results
    results = parse_results(html, engine, max_results)

    return {
        "query": query,
        "engine": engine,
        "results": results[:max_results]
    }


def format_markdown(results: Dict) -> str:
    """Format results as Markdown."""
    lines = [f"## Search Results for: {results['query']}", f"Engine: {results['engine'].upper()}", ""]

    for i, item in enumerate(results.get("results", []), 1):
        lines.append(f"{i}. [{item.get('title', 'No title')}]({item.get('url', '#')})")
        if item.get("snippet"):
            lines.append(f"   {item['snippet']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Easy web search without API keys")
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--engine", "-e", default="google", choices=list(ENGINES.keys()),
                        help="Search engine to use (default: google)")
    parser.add_argument("--results", "-r", type=int, default=5,
                        help="Number of results (default: 5)")
    parser.add_argument("--format", "-f", default="json", choices=["json", "md"],
                        help="Output format (default: json)")
    parser.add_argument("--timeout", type=int, default=15,
                        help="Request timeout in seconds (default: 15)")

    args = parser.parse_args()

    # Perform search
    result = search(args.query, args.engine, max_results=args.results)

    # Output
    if args.format == "md":
        sys.stdout.write(format_markdown(result))
    else:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()