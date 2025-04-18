# SII Sentiment Analysis Project

This project is a comprehensive web scraping and analysis solution designed to collect and analyze product reviews from multiple fitness equipment retailers. It stores the data in a PostgreSQL database and provides visualization through a Streamlit web application.

## Project Structure

### Web Scrapers
- **Amazon-Review-Scraper/**
  - `main.py`: Scrapes Amazon product reviews with pagination support (up to 20 pages)
  - Support for product search, review extraction, and database storage
  
- **Peleton-Site-Review-Scraper/**
  - `main.py`: Scrapes reviews from Peloton's website for different equipment types (BIKE, BIKEPLUS, TREAD, TREADPLUS, ROW)
  
- **Best-Buy/**
  - `bestbuyreviews.py`: Scrapes Best Buy product reviews with pagination support
  
- **Dick's Sporting Goods/**
  - `product_get.js`: Product information scraper
  - `review_getter.js`: Review scraper with API integration
  
- **Bowflex/**
  - `review_scraper.py`: Scrapes Bowflex product reviews using their API
  
- **Horizon-Reviews/**
  - Node.js-based scraper for Horizon Fitness reviews using Puppeteer
  
- **Med_Web_Reviews/**
  - `wahoofitness.py`: Wahoo Fitness review scraper
  - `scheel_scrapper.py`: Scheel's review scraper

### Core Components
- `webapp.py`: Streamlit web application for visualizing review data
- `requirements.txt`: Python package dependencies

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Node.js (for Dick's Sporting Goods and Horizon Fitness scrapers)
- Required Python packages (listed in `requirements.txt`)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/SII-Sentiment-Analysis-Project.git
    cd SII-Sentiment-Analysis-Project
    ```

2. Install Python dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. For Node.js scrapers, install dependencies:
    ```sh
    cd Horizon-Reviews
    npm install
    cd ../Dick\'s\ Sporting\ Goods
    npm install
    ```

## Usage

### Running the Scrapers

1. Amazon Reviews:
    ```sh
    cd Amazon-Review-Scraper
    python main.py
    ```

2. Peloton Reviews:
    ```sh
    cd Peleton-Site-Review-Scraper
    python main.py
    ```

3. Horizon Fitness Reviews:
    ```sh
    cd Horizon-Reviews
    node index.js
    ```

### Visualization Dashboard

Launch the Streamlit web application:
```sh
streamlit run webapp.py
```

The dashboard provides:
- Review filtering by retailer, rating, and date range
- Equipment type filtering
- Rating distribution visualization
- Detailed review content display

## Features

- Multi-platform review collection (Amazon, Peloton, Best Buy, Dick's, etc.)
- Automated pagination handling
- Rate limiting and request management
- Error logging and handling
- PostgreSQL database integration
- Interactive data visualization
- Support for various review metrics (rating, verified purchase, helpful votes, etc.)

## Database Schema

The project uses multiple tables to store reviews from different sources:
- amazon_reviews
- peloton_reviews
- bestbuy_reviews
- dicks_reviews
- horizon_reviews
- wahoo_reviews

Each table includes fields for:
- Review ID
- Product information
- Rating
- Review content
- Author information
- Review date
- Additional metadata specific to each platform

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- BeautifulSoup4 for web scraping
- Streamlit for the web application
- PostgreSQL for the database
- Pandas for data manipulation
- Puppeteer for JavaScript-based scraping
- Various retailer APIs for data access

Feel free to contribute to this project by submitting issues or pull requests.
