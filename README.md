# GenAI — HW11: Copilot News Headlines Scraper

## What is here
- `headlines_simple.py` — collects headlines and prints them to the console.
- `headlines_to_txt.py` — collects headlines and saves them to a TXT file.
- `headlines_keyword_csv.py` — filters by keyword and saves to CSV with UTC timestamp.
- `report_template.md` — short report template.

## Requirements
- Python 3.10+
- Packages: `requests`, `beautifulsoup4`

```bash
pip install requests beautifulsoup4
```

## Example usage
```bash
# 1) Simple output
python headlines_simple.py https://www.bbc.com/news

# 2) Save to text file
python headlines_to_txt.py https://www.bbc.com/news headlines.txt

# 3) Filter by keyword -> CSV with timestamp
python headlines_keyword_csv.py https://www.bbc.com/news technology tech_headlines.csv
```

> Tip: The URL can be any news site (for example, “Ukrainian Pravda”). If the page layout is different, you may need to update the CSS selectors in the `extract_headlines` function.

## Copilot prompts (examples)
- *Get all headlines from the main page of BBC News*
- *Get headlines from BBC News and save them to a text file*
- *Get headlines from BBC News related to technology and save them to a CSV file with timestamp*

## Evaluation checklist
- **Correctness:** scripts run without errors and collect headlines.
- **Completeness:** meets requirements (output/save/filter).
- **Readability:** clear function names, no duplication.
- **Efficiency:** did Copilot save you time.

## Report (what to submit)
- Code (`.py` or `.ipynb`).
- Short report using the `report_template.md`:
  - chosen task; prompts used; comparative evaluation; 5–7 conclusions.

---
*Optional:* you can rename the repository, e.g., `genai-hw11-copilot-news-scraper`.
