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


## Звіт — оцінка результатів та висновки

### Використані промпти
- Generate the three functions (fetch, extract_headlines, main) with the exact logic shown below. Do NOT add other functions, constants. Keep headers={"User-Agent":"Mozilla/5.0"} and timeout=15. Print numbered headlines with f"{i:02d}. {h}" and default URL "https://www.bbc.com/news". Use BeautifulSoup.
- Generate the three functions (fetch, extract_headlines, main) with the exact logic shown below. Do NOT add other functions, constants. Keep headers={"User-Agent":"Mozilla/5.0"} and timeout=15. Use BeautifulSoup  default URL "https://www.bbc.com/news". Save all headlines (one per line, UTF-8) to a text file: if a second CLI argument is provided, use it as the output path; otherwise write to "headlines.txt". Also print Saved {len(headlines)} headlines to <path>.
- Cтворити Python-скрипт, який збирає заголовки новин з певної сторінки сайту та зберігає їх у текстовий файл. додати фільтр по ключовому слову (наприклад, «технології»).

### Оцінка результатів
* **Правильність**: Скрипти працюють: BBC, УП, LB.ua, ZN.ua збирають заголовки стабільно; Censor.NET інколи блокує HTML, але вирішується через RSS або --cloudscraper. Були дрібні неточності, але було просто їх поправити.
* **Повнота**: Усі вимоги покриті: базовий вивід, збереження у файл/CSV, фільтр за ключовим словом, мультиджерельний режим і кастомний url.
* **Читабельність**: Структура функцій іменована ясно, є CLI-параметри, мінімальна логіка дублювання; код легко модифікувати.
* **Ефективність**: Copilot пришвидшив чорнову генерацію (≈50–70% часу економії), але потребував ручних правок: заголовки запитів, retry, anti-bot, feed discovery, CLI. У разі генераціх геть не правильної функції було важко на правти його на істинний шлях.

### Власні висновки (5–7 речень)
Найкращий результат дав деталізований запит із прикладами вводу/виводу та вимогами до бібліотек і параметрів CLI  Copilot у такому разі генерує ближчий до готового каркас. Copilot був корисним для швидкого створення базової структури (аргументи, парсинг, запис у файл), але мережеві нюанси (headers, retries, RSS-fallback) довелося додати вручну. Головні переваги: швидкий старт, узгоджений стиль, зменшення рутини.Водночас потрібно ретельно перевіряти код, особливо роботу з мережею, кодуванням, edge-кейси та обробку помилок. Практика показала, що RSS-підхід надійніший, ніж сирий HTML-парсинг під антиботом. 
Планую й надалі використовувати Copilot для шаблонів, генерації допоміжних функцій і тестів, залишаючи критичну логіку та інтеграції під ручний контроль.