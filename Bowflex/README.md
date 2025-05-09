# Bowflex Review Scraper

This module provides functionality to scrape product reviews from Bowflex's website using their PowerReviews API.

## Features

- Scrape reviews for specific Bowflex products
- Save reviews to PostgreSQL database
- Configurable database settings
- Handles pagination automatically
- Rate limiting to prevent API overload

## Prerequisites

```bash
pip install requests psycopg2-binary
```

## Database Configuration

Update the `DB_CONFIG` dictionary in `review_scraper.py` with your PostgreSQL database credentials:

```python
DB_CONFIG = {
    'user': 'your_username',
    'host': 'your_host',
    'database': 'your_database',
    'password': 'your_password',
    'port': 5432
}
```

## Usage

### As a Module

```python
from review_scraper import scrape_bowflex_reviews

# Scrape reviews for a specific product
product_id = '100894'  # BowFlex C6 Bike
product_name = 'BowFlex C6 Bike'

# To save to database (default behavior)
reviews = scrape_bowflex_reviews(product_id, product_name)

# To only get reviews without saving to database
reviews = scrape_bowflex_reviews(product_id, product_name, save_to_db=False)
```

### Command Line Usage

To scrape reviews for all predefined Bowflex products:

```bash
python review_scraper.py
```

## Predefined Products

The script includes several predefined products:
- BowFlex IC Bike SE (101012)
- BowFlex C6 Bike (100894)
- BowFlex Treadmill 22 (100910)
- BowFlex Treadmill 10 (100909)
- BowFlex BXT8J Treadmill (100998)
- BowFlex T9 Treadmill (HTM1439-01)
- BowFlex VeloCore Bike - 22 (velocore)

## Return Data Structure

The scraper returns a list of review objects. Each review contains:
- Rating
- Title
- Details/Comments
- Author information
- Creation and update dates
- Helpful votes count
- Verification status
- Custom fields
- Photo attachments (if any)

## Error Handling

The script includes basic error handling for:
- Failed HTTP requests
- JSON parsing errors
- Database connection issues

## Rate Limiting

The script includes a 0.1-second delay between requests to avoid overwhelming the API.