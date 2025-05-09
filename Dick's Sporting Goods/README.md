# Dick's Sporting Goods Review Scraper

A Node.js based scraper for collecting product reviews from Dick's Sporting Goods website.

## Prerequisites

- Node.js (v12 or higher)
- PostgreSQL database
- npm packages:
  - axios
  - pg
  - pg-format

## Installation

1. Install the required dependencies:
```bash
npm install axios pg pg-format
```

2. Configure your database settings in the code by modifying the `DB_CONFIG` object:
```javascript
const DB_CONFIG = {
  user: 'your_username',
  host: 'your_host',
  database: 'your_database',
  password: 'your_password',
  port: 5432
};
```

## Usage

### As a module

```javascript
const { scrapeReviewsBySearchTerm, scrapeAllReviews } = require('./review_getter');

// Scrape reviews by search term
async function example1() {
  const results = await scrapeReviewsBySearchTerm('exercise bike');
  console.log(results);
}

// Scrape reviews for a specific product
async function example2() {
  await scrapeAllReviews('productId', 'Product Name');
}
```

### As a standalone script

Simply run the script directly:

```bash
node review_getter.js
```

This will scrape reviews for exercise bikes by default.

## Features

- Automatic pagination handling
- Database storage with duplicate prevention
- Error handling and retry logic
- Configurable search terms
- Exports reusable functions for integration into other projects

## Database Schema

The scraper expects a PostgreSQL table with the following structure:

```sql
CREATE TABLE dicks_reviews (
    id TEXT PRIMARY KEY,
    device TEXT,
    rating INTEGER,
    title TEXT,
    type TEXT,
    review_text TEXT,
    author TEXT,
    location TEXT,
    submission_time TIMESTAMP,
    is_recommended BOOLEAN,
    secondary_ratings JSONB,
    context_data JSONB,
    badges JSONB,
    photos JSONB,
    pros TEXT,
    cons TEXT
);
```

## Exported Functions

- `scrapeReviewsBySearchTerm(searchTerm)`: Scrapes all reviews for products matching the search term
- `scrapeAllReviews(productId, productName)`: Scrapes all reviews for a specific product
- `fetchReviews(offset, productId)`: Fetches a single page of reviews
- `parseReview(review)`: Parses a single review into the correct format
- `DB_CONFIG`: Database configuration object

## Rate Limiting

Be mindful of rate limiting and consider adding delays between requests when scraping large amounts of data.