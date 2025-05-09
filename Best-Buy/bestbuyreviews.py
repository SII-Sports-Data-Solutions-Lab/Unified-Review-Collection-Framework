import time
import uuid
import psycopg2
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
from webdriver_manager.chrome import ChromeDriverManager
from psycopg2.extras import execute_batch

DB_CONFIG = {
    'user': 'admin',
    'host': 'raghuserver',
    'database': 'SII',
    'password': 'raghu@123',
    'port': 5432
}
# Database configuration for connecting to PostgreSQL database
# Credentials and connection details for the SII database

def create_connection():
    """Create a database connection"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def setup_driver():
    """Configure and return Chrome driver"""
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def accept_cookies(driver):
    """Handle cookie consent dialog"""
    try:
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "sp_message_iframe_764961"))
        )
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
        )
        accept_button.click()
        driver.switch_to.default_content()
        time.sleep(0.2)
    except Exception as e:
        print("Cookie consent handling failed:", str(e))

def extract_products(driver, total_pages=1):
    """Extract products from all pages using URL pagination"""
    base_url = "https://www.bestbuy.com/site/searchpage.jsp?st=exercise+bike&qp=category_facet%3DSAAS%7EExercise+Bikes%7Epcmcat159400050010&id=pcat17071"
    all_products = []
    
    for page in range(1, total_pages + 1):
        print(f"Processing product page {page}/{total_pages}")
        params = {
            "cp": page
        }
        
        driver.get(f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}")
        
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.sku-item"))
            )
            
            items = driver.find_elements(By.CSS_SELECTOR, "li.sku-item")
            # Only get the first item
            if items:
                for item in items:
                    try:
                        # Extract product details
                        sku = item.get_attribute("data-sku-id")
                        name_link = item.find_element(By.CSS_SELECTOR, "h4.sku-title a")
                        name = name_link.text
                        product_url = name_link.get_attribute("href")
                        
                        # Parse product slug from URL
                        path_parts = urlparse(product_url).path.split('/')
                        slug = path_parts[2] if len(path_parts) > 2 else None
                        
                        # Extract price
                        price = item.find_element(By.CSS_SELECTOR, "div.priceView-customer-price span").text
                        
                        # Extract rating
                        rating_element = item.find_elements(By.CSS_SELECTOR, "div.ugc-ratings-reviews")
                        rating = rating_element[0].text.split()[0] if rating_element else None
                        
                        all_products.append({
                            "sku": sku,
                            "name": name,
                            "slug": slug,
                            "price": price,
                            "rating": rating,
                            "reviews": []
                        })
                        print(f"Extracted product: {name}")
                    except Exception as e:
                        print(f"Error extracting product:", str(e))
        
        except Exception as e:
            print(f"Error loading page {page}:", str(e))
            return all_products
        
            
    return all_products

def extract_reviews(driver, product):
    """Extract reviews with pagination using BeautifulSoup"""
    base_url = f"https://www.bestbuy.com/site/reviews/{product['slug']}/{product['sku']}"
    reviews = []
    page = 1
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    
    while True:
        review_url = f"{base_url}?page={page}"
        # Use driver to get the page content (handles JavaScript rendering)
        driver.get(review_url)
        
        # Get the rendered HTML and parse with BeautifulSoup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            # Find the reviews container
            reviews_container = soup.select_one('.reviews-list')
            if not reviews_container:
                print(f"No reviews container found on page {page}")
                break
                
            # Extract all review items
            review_items = reviews_container.select('li.review-item')
            print(f"Page {page} review items: {review_items}")
            if len(review_items) == 0:
                return reviews
                
            for review in review_items:
                try:
                    # Extract author name
                    author_element = review.select_one('button.author-button strong')
                    author = author_element.text.strip() if author_element else "Unknown"

                    # Extract rating
                    rating_element = review.select_one('p.visually-hidden')
                    rating_text = rating_element.text if rating_element else "Rated 0 out of 5 stars"
                    rating = rating_text.split()[1] if len(rating_text.split()) > 1 else "0"

                    # Extract review title
                    title_element = review.select_one('h4.review-title')
                    title = title_element.text.strip() if title_element else "No Title"

                    # Extract review text
                    review_body_element = review.select_one('div.ugc-review-body p')
                    text = review_body_element.text.replace("Read more", "").strip() if review_body_element else "No review text"

                    # Extract review date
                    date_element = review.select_one('time.submission-date')
                    date = date_element.get('title') if date_element else "Unknown Date"

                    # Store extracted data
                    review_data = {
                        "id": str(uuid.uuid4()),
                        "author": author,
                        "rating": rating,
                        "title": title,
                        "text": text,
                        "date": date,
                    }
                    reviews.append(review_data)

                except Exception as e:
                    print(f"Error extracting review: {str(e)}")
                    
            # Check for next page
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'a[title="next Page"]')
                # Check if the button is disabled
                if 'disabled' in next_button.get_attribute('class').split() or not next_button.is_enabled():
                    print("Reached last page - next button is disabled")
                    return reviews
                next_button.click()
                page += 1
            except Exception as e:
                print(f"No next button found or error clicking next: {str(e)}")
                return reviews
                
        except Exception as e:
            print(f"Error loading reviews: {str(e)}")
            break
    
        
def save_to_database(products):
    """Save products and reviews to PostgreSQL in a single table"""
    conn = create_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Create single table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS best_buy_reviews (
                    review_id UUID PRIMARY KEY,
                    product_sku VARCHAR(50),
                    product_name TEXT,
                    product_slug TEXT,
                    product_price TEXT,
                    product_rating TEXT,
                    review_author TEXT,
                    review_rating INTEGER,
                    review_title TEXT,
                    review_text TEXT,
                    review_date TIMESTAMP,
                    review_helpful INTEGER
                )
            """)
            
            # Insert data
            for product in products:
                if product['reviews']:
                    # If product has reviews, create an entry for each review
                    review_data = [
                        (
                            review['id'],
                            product['sku'],
                            product['name'],
                            product['slug'],
                            product['price'],
                            product['rating'],
                            review['author'],
                            int(float(review['rating'])),
                            review['title'],
                            review['text'],
                            review['date'],
                            0  # Default helpful count
                        ) for review in product['reviews']
                    ]
                    
                    execute_batch(cur, """
                        INSERT INTO best_buy_reviews (
                            review_id, product_sku, product_name, product_slug, 
                            product_price, product_rating, review_author, 
                            review_rating, review_title, review_text, 
                            review_date, review_helpful
                        ) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (review_id) DO UPDATE SET
                            product_name = EXCLUDED.product_name,
                            product_slug = EXCLUDED.product_slug,
                            product_price = EXCLUDED.product_price,
                            product_rating = EXCLUDED.product_rating,
                            review_author = EXCLUDED.review_author,
                            review_rating = EXCLUDED.review_rating,
                            review_title = EXCLUDED.review_title,
                            review_text = EXCLUDED.review_text,
                            review_date = EXCLUDED.review_date,
                            review_helpful = EXCLUDED.review_helpful
                    """, review_data)
            
            conn.commit()
            print(f"Saved {len(products)} products with their reviews to the database")
            
    except Exception as e:
        print("Database error:", str(e))
        conn.rollback()
    finally:
        conn.close()

def fetch_turnto_reviews(sku):
    """Fetch reviews from Turnto API for a given SKU"""
    base_url = "https://cdn-ws.turnto.com/v5/sitedata/TXOE2FrZzlhkSdesite"
    reviews = []
    page = 1
    page_size = 25  # API returns 25 reviews per page
    
    try:
        while True:
            url = f"{base_url}/{sku}/d/review/en_US/{page_size}/{page}/%7B%7D/H_RATED/false/false/"
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            if response.status_code != 200:
                print(f"Error fetching reviews: HTTP {response.status_code}")
                break
                
            data = response.json()
            current_reviews = data.get('reviews', [])
            
            if not current_reviews:
                break
                
            for review in current_reviews:
                review_data = {
                    "id": str(uuid.uuid4()),  # Generate unique ID for database
                    "review_id": review.get('id'),
                    "author": review.get('user', {}).get('nickName', 'Anonymous'),
                    "rating": review.get('rating', 0),
                    "title": review.get('title', ''),
                    "text": review.get('text', ''),
                    "date": review.get('dateCreatedFormatted', ''),
                    "helpful_votes": review.get('upVotes', 0),
                    "product_name": review.get('catItem', {}).get('title', ''),
                    "product_sku": review.get('catItem', {}).get('sku', '')
                }
                reviews.append(review_data)
            
            total_reviews = data.get('total', 0)
            if len(reviews) >= total_reviews:
                break
                
            page += 1
            time.sleep(0.2)  # Be nice to the server
            
        print(f"Successfully fetched {len(reviews)} reviews")
        return reviews
        
    except Exception as e:
        print(f"Error fetching reviews: {str(e)}")
        return reviews

def save_turnto_reviews_to_db(reviews):
    """Save Turnto reviews to database"""
    conn = create_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Create table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS turnto_reviews (
                    id UUID PRIMARY KEY,
                    review_id BIGINT,
                    author TEXT,
                    rating INTEGER,
                    title TEXT,
                    review_text TEXT,
                    review_date TEXT,
                    helpful_votes INTEGER,
                    product_name TEXT,
                    product_sku TEXT
                )
            """)
            
            # Insert reviews
            review_data = [
                (
                    review['id'],
                    review['review_id'],
                    review['author'],
                    review['rating'],
                    review['title'],
                    review['text'],
                    review['date'],
                    review['helpful_votes'],
                    review['product_name'],
                    review['product_sku']
                ) for review in reviews
            ]
            
            execute_batch(cur, """
                INSERT INTO turnto_reviews (
                    id, review_id, author, rating, title, review_text,
                    review_date, helpful_votes, product_name, product_sku
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    review_id = EXCLUDED.review_id,
                    author = EXCLUDED.author,
                    rating = EXCLUDED.rating,
                    title = EXCLUDED.title,
                    review_text = EXCLUDED.review_text,
                    review_date = EXCLUDED.review_date,
                    helpful_votes = EXCLUDED.helpful_votes,
                    product_name = EXCLUDED.product_name,
                    product_sku = EXCLUDED.product_sku
            """, review_data)
            
            conn.commit()
            print(f"Saved {len(reviews)} reviews to database")
            
    except Exception as e:
        print("Database error:", str(e))
        conn.rollback()
    finally:
        conn.close()

def scrape_bestbuy_reviews(db_config=None, total_pages=1, search_query="exercise+bike", category_facet="SAAS%7EExercise+Bikes%7Epcmcat159400050010"):
    """
    Scrape BestBuy product reviews with customizable parameters.
    
    Args:
        db_config (dict, optional): Database configuration dictionary. If None, uses default config.
        total_pages (int, optional): Number of product pages to scrape. Defaults to 1.
        search_query (str, optional): Product search query. Defaults to "exercise+bike".
        category_facet (str, optional): Category filter. Defaults to exercise bikes category.
    
    Returns:
        list: List of dictionaries containing product and review data
    """
    if db_config:
        global DB_CONFIG
        DB_CONFIG = db_config

    driver = setup_driver()
    products = []
    
    try:
        driver.get("https://www.bestbuy.com")
        accept_cookies(driver)
        
        # Extract products
        products = extract_products(driver, total_pages)

        if products:
            # Process all products
            for product in products:
                print(f"Found product: {product['name']}")
                
                # Extract reviews for the product
                print(f"Processing reviews for {product['name']}")
                try:
                    product['reviews'] = extract_reviews(driver, product)
                    print(f"Found {len(product['reviews'])} reviews for {product['name']}")
                except Exception as e:
                    print(f"Error extracting reviews for {product['name']}: {str(e)}")
                    product['reviews'] = []
                    
                if not product['reviews']:
                    print(f"No reviews found for {product['name']}")
                    
            # Save to database if config is provided
            if db_config:
                save_to_database(products)
                
    finally:
        driver.quit()
        
    return products

def main():
    products = scrape_bestbuy_reviews()
    print(f"Scraped {len(products)} products with their reviews")

if __name__ == "__main__":
    main()