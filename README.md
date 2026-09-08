# lead-list-builder

Scrapes a paginated directory into leads.csv + leads.xlsx. Dedupes, trims whitespace, adds validation columns you can filter on.

parse_page() is the only part that changes per site - everything else (pagination, retries, rate limiting, output) stays the same. Demo runs against quotes.toscrape.com.

```
pip install requests beautifulsoup4 pandas openpyxl
python build_leads.py
```
