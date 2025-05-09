# Peloton Site Review Scraper

This folder contains a scraper for Peloton product reviews.

## Requirements

- Python 3.7+
- requests
- psycopg2-binary

Install dependencies:

```bash
pip install requests psycopg2-binary
```

## Usage

Import and use the reusable function:

```python
from main import scrape_and_save_peloton_reviews

# Scrape default equipment types
scrape_and_save_peloton_reviews()

# Or specify a list of equipment types
scrape_and_save_peloton_reviews(["BIKE", "TREAD"])
```

## Output

- Reviews are saved to the PostgreSQL database as defined in the script.

## Note

- You can still run the script directly as a standalone program.
- The reusable function allows you to import and trigger scraping from other Python scripts or notebooks.
