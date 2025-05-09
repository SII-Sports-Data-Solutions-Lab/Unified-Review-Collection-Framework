# Unified Review Collection Framework for Major E-commerce sites

This project is a comprehensive web scraping and analysis solution designed to collect and analyze product reviews from multiple fitness equipment retailers.

## Project Structure

### Web Scrapers
- [Amazon-Review-Scraper/README.md](Amazon-Review-Scraper/README.md): Python tool for scraping Amazon product reviews with CLI and library support. Features product search, review extraction, PostgreSQL storage, and error logging.
- [Peleton-Site-Review-Scraper/README.md](Peleton-Site-Review-Scraper/README.md): Python scraper for Peloton reviews. Supports scraping by equipment type, reusable as a function or script, and saves to PostgreSQL.
- [Best-Buy/README.md](Best-Buy/README.md): Python scraper for Best Buy product reviews. Handles pagination, supports custom queries, and can store data in PostgreSQL.
- [Dick's Sporting Goods/README.md](Dick's Sporting Goods/README.md): Node.js scraper for Dick's Sporting Goods reviews. Supports CLI and module usage, automatic pagination, and PostgreSQL integration.
- [Bowflex/README.md](Bowflex/README.md): Python scraper for Bowflex reviews using their API. Supports multiple products, pagination, and PostgreSQL storage.
- [Horizon-Reviews/README.md](Horizon-Reviews/README.md): Node.js Puppeteer-based scraper for Yotpo-powered reviews (e.g., Horizon Fitness). Handles dynamic content, popups, and PostgreSQL storage.
- [Med_Web_Reviews/README.md](Med_Web_Reviews/README.md): Python scrapers for Wahoo Fitness (Yotpo API) and Scheel's (Turnto API). Reusable as functions or scripts, saves to PostgreSQL.
- [Target/README.md](Target/README.md): Python scraper for Target reviews. Reusable as a function or script, saves to PostgreSQL.
- [split_reviews_by_sentence/README.MD](split_reviews_by_sentence/README.MD): Python module to split reviews into sentences and store them in a database for further analysis.


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
    cd ../Dick's Sporting Goods
    npm install
    ```

## Usage

### Running the Scrapers

- See each scraper's README for detailed usage and configuration instructions:
    - [Amazon-Review-Scraper/README.md](Amazon-Review-Scraper/README.md)
    - [Peleton-Site-Review-Scraper/README.md](Peleton-Site-Review-Scraper/README.md)
    - [Best-Buy/README.md](Best-Buy/README.md)
    - [Dick's Sporting Goods/README.md](Dick's Sporting Goods/README.md)
    - [Bowflex/README.md](Bowflex/README.md)
    - [Horizon-Reviews/README.md](Horizon-Reviews/README.md)
    - [Med_Web_Reviews/README.md](Med_Web_Reviews/README.md)
    - [Target/README.md](Target/README.md)
    - [split_reviews_by_sentence/README.MD](split_reviews_by_sentence/README.MD)


## Features

- Multi-platform review collection (Amazon, Peloton, Best Buy, Dick's, Bowflex, Horizon, Wahoo, Scheel's, Target, etc.)
- Automated pagination handling
- Rate limiting and request management
- Error logging and handling
- PostgreSQL database integration
- Interactive data visualization
- Support for various review metrics (rating, verified purchase, helpful votes, etc.)
- Modular and reusable scraping functions

## Database Schema

The project uses multiple tables to store reviews from different sources:
- amazon_reviews
- peloton_reviews
- bestbuy_reviews
- dicks_reviews
- horizon_reviews
- wahoo_reviews
- Additional tables for sentence splitting and raw data as needed

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

---

For detailed instructions, features, and usage examples for each scraper, see the linked README files in each subfolder.
