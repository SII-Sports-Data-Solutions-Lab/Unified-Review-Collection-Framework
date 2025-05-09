# Amazon Review Scraper

A Python-based tool for scraping Amazon product reviews with support for both command-line usage and programmatic integration.

## Features

- Search for products on Amazon
- Scrape reviews filtered by star rating
- Save reviews to a PostgreSQL database
- Support for verified purchase reviews
- Extract review metadata (rating, title, date, helpful votes, etc.)
- Error logging and handling

## Prerequisites

```bash
pip install requests beautifulsoup4 psycopg2-binary lxml
```

## Usage

### Command Line Interface

```bash
python main.py "Product Name" --max-pages 20 --db-config '{"dbname":"your_db","user":"your_user","password":"your_pass","host":"your_host","port":"5432"}'
```

Arguments:
- `search_term`: Product name to search for (required)
- `--max-pages`: Maximum number of search result pages to process (default: 20)
- `--db-config`: JSON string with database configuration (optional)

### As a Library

```python
from main import AmazonReviewScraper

# Initialize scraper with custom database config (optional)
db_config = {
    "dbname": "your_db",
    "user": "your_user",
    "password": "your_pass",
    "host": "your_host",
    "port": "5432"
}

scraper = AmazonReviewScraper(db_config=db_config)

# Scrape reviews
products = scraper.scrape_product_reviews("Product Name", max_pages=20)

# Process results
for product in products:
    print(f"Product: {product.get('title')}")
    print(f"ASIN: {product.get('data_asin')}")
    print(f"Number of reviews: {len(product.get('reviews', []))}")
```

## Database Schema

The scraper expects a PostgreSQL database with the following table:

```sql
CREATE TABLE amazon_reviews (
    review_id TEXT PRIMARY KEY,
    data_asin TEXT,
    product_title TEXT,
    product_description TEXT,
    rating INTEGER,
    title TEXT,
    review_date TEXT,
    body TEXT
);
```

## Error Handling

Errors are logged to `error_log.log` in the same directory as the script. Check this file for debugging information if issues occur.

## Note

This scraper is for educational purposes only. Make sure to follow Amazon's terms of service and robots.txt when using this tool.