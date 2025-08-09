# headlines_multi_sources.py
# Usage examples:
#   python headlines_multi_sources.py --source pravda
#   python headlines_multi_sources.py --source all --keyword технології --limit 50
#   python headlines_multi_sources.py --url https://censor.net/ua/news/all
#
# Requires: feedparser, requests, beautifulsoup4
# Optional: cloudscraper  (pip install cloudscraper)

from __future__ import annotations
import argparse
import sys
import time
from typing import Iterable, Optional, Tuple, List
from urllib.parse import urljoin, urlsplit
import requests
from bs4 import BeautifulSoup
import feedparser

try:
    from urllib3.util.retry import Retry
except Exception:
    # Fallback if urllib3 path differs
    from requests.packages.urllib3.util.retry import Retry  # type: ignore

from requests.adapters import HTTPAdapter

DEFAULT_SOURCES = {
    # BBC
    "bbc": ["https://feeds.bbci.co.uk/news/rss.xml"],
    # Українська Правда (УП)
    "pravda": [
        "https://www.pravda.com.ua/rss/view_news/",
        "https://www.pravda.com.ua/rss/",
    ],
    # Лівий Берег
    "lb": ["https://lb.ua/rss"],
    # Дзеркало тижня / ZN.ua
    "zn": ["https://zn.ua/rss.xml", "https://zn.ua/ukr/rss"],
    # Цензор.НЕТ (may block scraping; use feed landing)
    "censor": ["https://censor.net/ua/feed", "https://censor.net/en/feed"],
}

UA_HEADERS_XML = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, text/xml;q=0.8,*/*;q=0.1",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

UA_HEADERS_HTML = {
    "User-Agent": UA_HEADERS_XML["User-Agent"],
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": UA_HEADERS_XML["Accept-Language"],
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
}

COMMON_FEED_PATHS = [
    "/rss",
    "/rss.xml",
    "/feed",
    "/feed.xml",
    "/atom.xml",
    "/index.xml",
]


def build_session(
    use_cloudscraper: bool = False, for_xml: bool = False, timeout: int = 20
) -> requests.Session:
    """
    Build a session with retries and strong headers.
    If use_cloudscraper=True and module is installed, returns a Cloudscraper session.
    """
    session: requests.Session
    if use_cloudscraper:
        try:
            import cloudscraper  # type: ignore

            session = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "mac", "mobile": False}
            )
        except Exception:
            session = requests.Session()
    else:
        session = requests.Session()

    headers = UA_HEADERS_XML if for_xml else UA_HEADERS_HTML
    session.headers.update(headers)

    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.5,
        status_forcelist=(403, 429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    # Store default timeout on session for convenience
    session.request = _wrap_request_with_timeout(session.request, timeout)  # type: ignore
    return session


def _wrap_request_with_timeout(request_fn, timeout: int):
    def wrapped(method, url, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout
        return request_fn(method, url, **kwargs)

    return wrapped


def parse_feed_with_session(
    session: requests.Session, url: str
) -> Optional[feedparser.FeedParserDict]:
    try:
        r = session.get(url)
        if r.status_code == 403:
            return None
        r.raise_for_status()
        fp = feedparser.parse(r.content)
        if getattr(fp, "bozo", 0) and not fp.entries:
            return None
        if not fp.entries:
            return None
        return fp
    except Exception:
        return None


def discover_feed(
    session_xml: requests.Session, url: str
) -> Tuple[Optional[str], Optional[feedparser.FeedParserDict]]:
    """
    Try to find a valid RSS/Atom feed URL starting from `url` (which may be a feed or an HTML page).
    """
    # 1) Try as-is
    fp = parse_feed_with_session(session_xml, url)
    if fp:
        return url, fp

    # 2) If HTML, scan for <link rel="alternate"> candidates and common paths
    try:
        r = build_session(for_xml=False).get(url)  # HTML session
    except Exception:
        return None, None

    ctype = (r.headers.get("Content-Type", "") or "").lower()
    if ("xml" in ctype) and ("html" not in ctype):
        # Might be an XML feed that feedparser didn't like; try again after a beat
        time.sleep(0.2)
        fp = parse_feed_with_session(session_xml, url)
        return (url, fp) if fp else (None, None)

    base = f"{urlsplit(url).scheme}://{urlsplit(url).netloc}"
    soup = BeautifulSoup(r.text, "html.parser")
    candidates = set()

    # <link rel="alternate" type="application/rss+xml" href="...">
    for link in soup.find_all("link"):
        rel_list = link.get("rel") or []
        rel = " ".join(rel_list) if isinstance(rel_list, list) else str(rel_list)
        typ = (link.get("type") or "").lower()
        href = link.get("href")
        if href and (
            "rss" in typ
            or "atom" in typ
            or "xml" in href.lower()
            or "rss" in rel.lower()
        ):
            candidates.add(urljoin(base, href))

    # Anchors that look like feeds
    for a in soup.find_all("a", href=True):
        href = a["href"]
        low = href.lower()
        if any(tok in low for tok in (".xml", "/rss", "rss.xml", "atom.xml", "/feed")):
            candidates.add(urljoin(base, href))

    # Common feed paths
    for p in COMMON_FEED_PATHS:
        candidates.add(urljoin(base, p))

    for cand in candidates:
        fp = parse_feed_with_session(session_xml, cand)
        if fp:
            return cand, fp

    return None, None


def get_headlines_from_feed(
    fp: feedparser.FeedParserDict, keyword: Optional[str], limit: int
) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    for e in fp.entries[: max(limit, 0) or 50]:
        title = (e.get("title") or "").strip()
        link = (e.get("link") or "").strip()
        if not title:
            continue
        if keyword and keyword.lower() not in title.lower():
            continue
        items.append((title, link))
    return items


def extract_headlines_from_html(
    session: requests.Session, url: str, keyword: Optional[str], limit: int
) -> List[Tuple[str, str]]:
    """
    Fallback scraping of <h1,h2,h3>. Uses strong headers and tries to avoid 403,
    but if blocked, returns empty.
    """
    try:
        # Set referer to same origin to look more like a browser
        origin = f"{urlsplit(url).scheme}://{urlsplit(url).netloc}"
        headers = {"Referer": origin + "/"}
        r = session.get(url, headers=headers)
        if r.status_code == 403:
            return []
        r.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    seen = set()
    out: List[Tuple[str, str]] = []
    for tag in soup.select("h1, h2, h3"):
        text = tag.get_text(strip=True)
        if not text or len(text) < 5:
            continue
        if text in seen:
            continue
        if keyword and keyword.lower() not in text.lower():
            continue
        seen.add(text)
        out.append((text, ""))
        if len(out) >= (limit or 50):
            break
    return out


def process_single_source(
    name: str,
    seed_urls: Iterable[str],
    keyword: Optional[str],
    limit: int,
    force_cloudscraper: bool = False,
) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Try RSS/Atom first. If no feed found, fallback to HTML headings with bot-block handling.
    Returns (resolved_feed_or_page_url, [(title, link), ...]).
    """
    # Try with requests first; if blocked for feeds, we may try cloudscraper for HTML only.
    sess_xml = build_session(use_cloudscraper=False, for_xml=True)
    feed_url = None
    fp = None
    for u in seed_urls:
        feed_url, fp = discover_feed(sess_xml, u)
        if fp:
            break

    if fp:
        return feed_url or seed_urls[0], get_headlines_from_feed(fp, keyword, limit)

    # Fallback: HTML extraction
    # First with requests
    html_sess = build_session(use_cloudscraper=False, for_xml=False)
    for u in seed_urls:
        items = extract_headlines_from_html(html_sess, u, keyword, limit)
        if items:
            return u, items

    # If still empty and allowed, try cloudscraper for HTML
    if force_cloudscraper:
        html_sess_cs = build_session(use_cloudscraper=True, for_xml=False)
        for u in seed_urls:
            items = extract_headlines_from_html(html_sess_cs, u, keyword, limit)
            if items:
                return u, items

    # Nothing worked
    return seed_urls[0], []


def main():
    ap = argparse.ArgumentParser(
        description="Fetch headlines from Ukrainian/intl sources via RSS first, with anti-bot fallbacks."
    )
    ap.add_argument(
        "--source",
        choices=["bbc", "pravda", "lb", "zn", "censor", "all"],
        default=None,
        help="Predefined source. Use --url for a custom address. If neither is set, defaults to 'pravda'.",
    )
    ap.add_argument(
        "--url",
        type=str,
        default=None,
        help="Custom page or feed URL (takes precedence over --source).",
    )
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument(
        "--keyword",
        type=str,
        default=None,
        help="Optional substring filter (case-insensitive).",
    )
    ap.add_argument(
        "--cloudscraper",
        action="store_true",
        help="Try Cloudscraper fallback for HTML if blocked.",
    )
    ap.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output file to save headlines.",
    )
    args = ap.parse_args()

    # Determine targets
    targets: List[Tuple[str, List[str]]] = []

    if args.url:
        targets = [("custom", [args.url])]
    else:
        src = args.source or "pravda"
        if src == "all":
            for k in ["bbc", "pravda", "lb", "zn", "censor"]:
                targets.append((k, DEFAULT_SOURCES[k]))
        else:
            targets = [(src, DEFAULT_SOURCES[src])]

    total = 0
    all_results = []
    for name, urls in targets:
        resolved, items = process_single_source(
            name=name,
            seed_urls=urls,
            keyword=args.keyword,
            limit=args.limit,
            force_cloudscraper=args.cloudscraper,
        )
        all_results.append((name, resolved, items))
        print(f"=== {name.upper()} [{resolved}] ===")
        if not items:
            print("(no items or blocked)")
        else:
            for i, (title, link) in enumerate(items, 1):
                print(f"{i:02d}. {title}")
                if link:
                    print(f"    {link}")
            total += len(items)
        print()

    # Save to file if requested
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for name, resolved, items in all_results:
                f.write(f"=== {name.upper()} [{resolved}] ===\n")
                if not items:
                    f.write("(no items or blocked)\n\n")
                else:
                    for i, (title, link) in enumerate(items, 1):
                        f.write(f"{i:02d}. {title}\n")
                        if link:
                            f.write(f"    {link}\n")
                    f.write("\n")
        print(f"Saved all results to {args.output}")

    if total == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
