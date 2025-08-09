# headlines_keyword_csv.py
# Usage: python headlines_keyword_csv.py [URL] [KEYWORD] [OUTPUT_CSV]
# Example: python headlines_keyword_csv.py https://www.bbc.com/news technology tech_headlines.csv

import sys
import csv
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from pathlib import Path

def fetch(url: str) -> BeautifulSoup:
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def extract_headlines(soup: BeautifulSoup) -> list[str]:
    seen = set()
    out = []
    for tag in soup.select("h1, h2, h3"):
        text = tag.get_text(strip=True)
        if text and text not in seen and len(text) > 4:
            seen.add(text)
            out.append(text)
    return out

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.bbc.com/news"
    keyword = (sys.argv[2] if len(sys.argv) > 2 else "technology").strip()
    out_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("filtered_headlines.csv")

    soup = fetch(url)
    headlines = extract_headlines(soup)

    ts = datetime.now(timezone.utc).isoformat()
    kw = keyword.lower()
    filtered = [h for h in headlines if kw in h.lower()]

    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp_utc", "keyword", "headline", "source_url"])
        for h in filtered:
            w.writerow([ts, keyword, h, url])

    print(f"Saved {len(filtered)} '{keyword}' headlines to {out_path.resolve()} (from {len(headlines)} total)")

if __name__ == "__main__":
    main()
