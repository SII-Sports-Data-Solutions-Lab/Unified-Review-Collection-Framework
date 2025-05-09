# Target Review Scraper

This folder contains a scraper for Target product reviews.

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
from target_scraper import scrape_and_save_target_reviews

# Scrape reviews for all products in the product data
scrape_and_save_target_reviews()

# Or specify a custom product list
# product_list = [{"tcin": "12345", "title": "Product Name"}, ...]
scrape_and_save_target_reviews(product_list)
```

## Output

- Reviews are saved to the PostgreSQL database as defined in the script.

## Note

- You can still run the script directly as a standalone program.
- The reusable function allows you to import and trigger scraping from other Python scripts or notebooks.
