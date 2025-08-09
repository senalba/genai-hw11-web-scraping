# headlines_to_txt.py
# Usage: python headlines_to_txt.py [URL] [OUTPUT_TXT]
# Example: python headlines_to_txt.py https://www.bbc.com/news headlines.txt

import sys
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
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("headlines.txt")
    soup = fetch(url)
    headlines = extract_headlines(soup)
    out_path.write_text("\n".join(headlines), encoding="utf-8")
    print(f"Saved {len(headlines)} headlines to {out_path.resolve()}")

if __name__ == "__main__":
    main()
