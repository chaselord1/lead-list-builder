"""Lead list builder: scrapes a paginated directory into a clean, deduped
spreadsheet with basic validation columns.

Setup:
  pip install requests beautifulsoup4 pandas openpyxl

Run:
  python build_leads.py            -> leads.xlsx + leads.csv

Demo target is quotes.toscrape.com (a practice site), standing in for any
directory: business listings, member pages, supplier catalogs, etc. For a real
job I swap the parse_page() function to match the client's target site.
"""
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = "https://quotes.toscrape.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (lead-list demo)"}
DELAY_S = 1.0            # be polite: one page per second


def parse_page(html):
    """Pull one directory page into rows. This is the part I customize per site."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for card in soup.select("div.quote"):
        name = card.select_one("small.author")
        tags = [t.get_text(strip=True) for t in card.select("a.tag")]
        link = card.select_one("a[href*='/author/']")
        rows.append({
            "name": name.get_text(strip=True) if name else "",
            "categories": ", ".join(tags),
            "profile_url": BASE + link["href"] if link else "",
        })
    next_link = soup.select_one("li.next a")
    return rows, (BASE + next_link["href"] if next_link else None)


def looks_like_email(s):
    return bool(re.match(r"^[\w.+-]+@[\w-]+\.[\w.]+$", str(s or "")))


def main():
    url = BASE
    all_rows = []
    page = 0
    while url:
        page += 1
        print(f"page {page}: {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"  page failed ({e}), stopping here with what we have")
            break
        rows, url = parse_page(r.text)
        all_rows.extend(rows)
        time.sleep(DELAY_S)

    df = pd.DataFrame(all_rows)
    before = len(df)
    df = df.drop_duplicates(subset=["name"]).reset_index(drop=True)
    df["name"] = df["name"].str.strip()
    # validation columns the client can filter on
    df["has_profile"] = df["profile_url"].str.len() > 0
    if "email" in df.columns:
        df["email_valid"] = df["email"].map(looks_like_email)

    df.to_csv("leads.csv", index=False)
    df.to_excel("leads.xlsx", index=False)
    print(f"\ndone: {len(df)} unique rows ({before - len(df)} duplicates removed)")
    print("wrote leads.csv and leads.xlsx")


if __name__ == "__main__":
    main()
