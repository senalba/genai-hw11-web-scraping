# headlines_simple.py
# Usage: python headlines_simple.py [URL]
# Example: python headlines_simple.py https://www.bbc.com/news

import sys
import requests
from bs4 import BeautifulSoup

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
    soup = fetch(url)
    headlines = extract_headlines(soup)
    for i, h in enumerate(headlines, 1):
        print(f"{i:02d}. {h}")

if __name__ == "__main__":
    main()
