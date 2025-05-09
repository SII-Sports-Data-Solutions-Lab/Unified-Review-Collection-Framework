# Med_Web_Reviews Scrapers

This folder contains two review scrapers:
- Wahoo Fitness (Yotpo API)
- Scheel's (Turnto API)

## Requirements

- Python 3.7+
- requests
- psycopg2-binary

Install dependencies:

```bash
pip install requests psycopg2-binary
```

## Usage

### Wahoo Fitness Scraper

Import and use the reusable function:

```python
from wahoofitness import scrape_and_save_wahoo_reviews

# Scrape default product(s)
scrape_and_save_wahoo_reviews()

# Or specify a list of product IDs
scrape_and_save_wahoo_reviews(["548", "1234"])
```

### Scheel's (Turnto) Scraper

Import and use the reusable function:

```python
from scheel_scrapper import scrape_and_save_turnto_reviews

# Scrape default SKU(s)
scrape_and_save_turnto_reviews()

# Or specify a list of SKUs
scrape_and_save_turnto_reviews(["43619-NTL19124", "ANOTHER-SKU"])
```

## Output

- Reviews are saved to the PostgreSQL database as defined in each script.
- Raw data for Wahoo Fitness is also saved in the `raw_data/` folder.

## Note

- You can still run each script directly as a standalone program.
- The reusable functions allow you to import and trigger scraping from other Python scripts or notebooks.
