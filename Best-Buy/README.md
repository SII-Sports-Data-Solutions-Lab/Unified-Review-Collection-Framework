# Best Buy Review Scraper

A Python scraper for extracting product and review data from Best Buy's website.

## Features

- Scrapes product information and customer reviews from Best Buy
- Customizable search queries and categories
- Optional database storage (PostgreSQL)
- Handles pagination automatically
- Includes both web scraping and API-based review collection

## Prerequisites

```bash
pip install selenium beautifulsoup4 psycopg2-binary requests webdriver-manager
```

## Usage

You can use this scraper in two ways:

### 1. As a standalone script

Simply run the script directly:

```bash
python bestbuyreviews.py
```

This will use the default configuration to scrape exercise bike products and their reviews.

### 2. As an imported module

```python
from bestbuyreviews import scrape_bestbuy_reviews

# Optional: Custom database configuration
db_config = {
    'user': 'your_user',
    'host': 'your_host',
    'database': 'your_db',
    'password': 'your_password',
    'port': 5432
}

# Example usage with custom parameters
products = scrape_bestbuy_reviews(
    db_config=db_config,           # Optional: database configuration
    total_pages=3,                 # Number of product pages to scrape
    search_query="treadmill",      # Custom search query
    category_facet="SAAS~Treadmills~pcmcat326200050005"  # Custom category
)

# Process the scraped data
for product in products:
    print(f"Product: {product['name']}")
    print(f"Number of reviews: {len(product['reviews'])}")
```

## Data Structure

The scraper returns a list of product dictionaries with the following structure:

```python
{
    "sku": "1234567",
    "name": "Product Name",
    "slug": "product-url-slug",
    "price": "$999.99",
    "rating": "4.5",
    "reviews": [
        {
            "id": "uuid",
            "author": "Reviewer Name",
            "rating": "5",
            "title": "Review Title",
            "text": "Review Content",
            "date": "Review Date"
        },
        # ... more reviews
    ]
}
```

## Database Schema

If using database storage, the scraper creates two tables:

1. `best_buy_reviews`: Stores web-scraped reviews
2. `turnto_reviews`: Stores reviews from the TurnTo API

## Notes

- The scraper respects website policies and includes appropriate delays between requests
- Selenium WebDriver is used for JavaScript-rendered content
- Make sure you have Chrome browser installed as the scraper uses ChromeDriver