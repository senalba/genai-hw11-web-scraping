# extractors.py

from bs4 import BeautifulSoup


def extract_headlines(html, selector="h3"):
    """
    Extracts headlines from HTML using the given CSS selector (default: 'h3').
    Returns a list of headline strings.
    """
    soup = BeautifulSoup(html, "html.parser")
    return [el.get_text(strip=True) for el in soup.select(selector)]
