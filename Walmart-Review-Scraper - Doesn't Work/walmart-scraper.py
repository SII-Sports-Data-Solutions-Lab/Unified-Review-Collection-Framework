import time
import uuid
import psycopg2
import requests
import random
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse, parse_qs
from webdriver_manager.chrome import ChromeDriverManager
from psycopg2.extras import execute_batch
from fake_useragent import UserAgent

# List of common user agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15"
]

# Browser capabilities to mimic real browsers
BROWSER_CAPABILITIES = {
    "platform": "Windows",
    "browserName": "chrome",
    "version": "110",
    "acceptSslCerts": True
}

DB_CONFIG = {
    'user': 'admin',
    'host': 'raghuserver',
    'database': 'SII',
    'password': 'raghu@123',
    'port': 5432
}

def get_random_user_agent():
    """Get a random user agent from the list or generate one using fake_useragent"""
    try:
        ua = UserAgent()
        return ua.random
    except:
        return random.choice(USER_AGENTS)

def random_delay(min_seconds=1, max_seconds=5):
    """Wait a random amount of time between requests to appear more human-like"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

def create_connection():
    """Create a database connection"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def setup_driver():
    """Configure and return Chrome driver with advanced browser emulation"""
    chrome_options = Options()
    # Uncomment for headless mode in production
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    
    # Set a random user agent
    user_agent = get_random_user_agent()
    chrome_options.add_argument(f"--user-agent={user_agent}")
    
    # Add language and platform to appear more like a real browser
    chrome_options.add_argument("--lang=en-US,en;q=0.9")
    chrome_options.add_argument("--platform=Windows")
    
    # Set browser fingerprinting parameters
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Add browser performance settings
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Add referrer to look more legitimate
    chrome_options.add_argument("--referrer=https://www.google.com/")
    
    # Advanced performance settings
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 1,
        "profile.default_content_setting_values.cookies": 1
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Set window size to a common desktop resolution
    driver.set_window_size(1920, 1080)
    
    # Set an implicit wait for elements to appear
    driver.implicitly_wait(10)
    
    # Execute CDP commands to modify the navigator properties
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {'name': 'Chrome PDF Plugin'},
                    {'name': 'Chrome PDF Viewer'},
                    {'name': 'Native Client'}
                ]
            });
        """
    })
    
    return driver

def load_cookies(driver, domain):
    """Load cookies for a specific domain if they exist"""
    try:
        cookie_file = f"cookies_{domain.replace('.', '_')}.json"
        with open(cookie_file, "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                # Some cookies can cause issues if they're expired or have specific attributes
                try:
                    # Remove problematic cookie attributes
                    if 'expiry' in cookie:
                        del cookie['expiry']
                    
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Error adding cookie: {e}")
        print(f"Loaded cookies for {domain}")
        return True
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"No saved cookies found for {domain}")
        return False

def save_cookies(driver, domain):
    """Save cookies for a specific domain"""
    try:
        cookie_file = f"cookies_{domain.replace('.', '_')}.json"
        cookies = driver.get_cookies()
        with open(cookie_file, "w") as f:
            json.dump(cookies, f)
        print(f"Saved cookies for {domain}")
        return True
    except Exception as e:
        print(f"Error saving cookies: {e}")
        return False

def accept_cookies(driver):
    """Accept cookies on Walmart website using multiple detection methods"""
    try:
        # Try different cookie consent button selectors
        cookie_button_selectors = [
            # Common Walmart cookie banner selectors
            "//button[contains(text(), 'Accept') or contains(text(), 'accept all') or contains(text(), 'Accept All')]",
            "//button[contains(@class, 'cookie-banner') and contains(text(), 'Accept')]",
            "//div[contains(@class, 'cookie-banner')]//button",
            # Common cookie consent selectors
            "//div[contains(@class, 'consent')]//button[contains(text(), 'Accept')]",
            "//div[contains(@id, 'cookie')]//button[contains(text(), 'Accept')]",
            "//button[contains(@id, 'agree')]",
            "//button[contains(@id, 'cookie')]"
        ]
        
        for selector in cookie_button_selectors:
            try:
                cookie_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                cookie_btn.click()
                print(f"Accepted cookies using selector: {selector}")
                
                # Save cookies after accepting
                domain = urlparse(driver.current_url).netloc
                save_cookies(driver, domain)
                
                random_delay(0.5, 1.5)
                return True
            except:
                continue
                
        print("No cookie banner found or already accepted")
        return False
            
    except Exception as e:
        print(f"Error handling cookies: {e}")
        return False

def navigate_with_human_behavior(driver, url):
    """Navigate to a URL with human-like behavior"""
    domain = urlparse(url).netloc
    
    # First load the main domain page
    try:
        main_domain = f"https://{domain}"
        print(f"First navigating to main domain: {main_domain}")
        driver.get(main_domain)
        random_delay(2, 4)
        
        # Try to load cookies
        load_cookies(driver, domain)
        
        # Handle cookies if needed
        accept_cookies(driver)
        
        # Now navigate to the actual URL
        print(f"Now navigating to: {url}")
        driver.get(url)
        
        # Save the cookies after navigation
        save_cookies(driver, domain)
        
        # Random scroll to simulate reading
        scroll_amount = random.randint(300, 700)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        random_delay(1, 3)
        
        return True
    except Exception as e:
        print(f"Error in human-like navigation: {e}")
        # Fallback to direct navigation
        driver.get(url)
        return False

def extract_products_from_category_bs(driver, category_url, total_pages=1):
    """Extract products from a specific Walmart category page using BeautifulSoup with human-like behavior"""
    products = []
    
    try:
        # Navigate with human-like behavior
        print(f"Navigating to category: {category_url}")
        navigate_with_human_behavior(driver, category_url)
        
        # Extract products for specified number of pages
        page = 1
        while page <= total_pages:
            print(f"Extracting products from page {page} using BeautifulSoup...")
            
            # Wait for product grid to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-automation-id='product-grid']"))
            )
            
            # Human-like scrolling behavior
            total_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            scrolls = total_height // viewport_height
            
            for i in range(scrolls):
                driver.execute_script(f"window.scrollTo(0, {viewport_height * (i+1)});")
                random_delay(0.5, 1.5)  # Random delay between scrolls
            
            # Get page source and parse with BeautifulSoup
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all product elements
            product_elements = soup.select("[data-automation-id='product']")
            
            for product_elem in product_elements:
                try:
                    # Extract product details
                    name_elem = product_elem.select_one("[data-automation-id='product-title']")
                    if not name_elem:
                        continue
                    
                    name = name_elem.get_text().strip()
                    
                    # Get product URL
                    link = name_elem.get('href')
                    if not link:
                        link_elem = product_elem.select_one("a")
                        if link_elem:
                            link = link_elem.get('href')
                    
                    # Make sure URL is absolute
                    if link and not link.startswith('http'):
                        link = f"https://www.walmart.com{link}"
                    
                    # Extract product ID from URL
                    if link:
                        parsed_url = urlparse(link)
                        path_segments = parsed_url.path.strip('/').split('/')
                        product_id = path_segments[-1] if path_segments else None
                    else:
                        product_id = None
                    
                    # Try to get price
                    price = "Price not available"
                    price_elem = product_elem.select_one("[data-automation-id='product-price']")
                    if price_elem:
                        price = price_elem.get_text().strip()
                    
                    # Get category info from URL
                    category = "treadmill" if "treadmills" in category_url else "exercise bike"
                    
                    # Create product object
                    if product_id and name:
                        product = {
                            'id': str(uuid.uuid4()),
                            'product_id': product_id,
                            'name': name,
                            'price': price,
                            'url': link,
                            'category': category,
                            'source': 'walmart',
                            'reviews': []
                        }
                        products.append(product)
                        print(f"Found {category}: {name}")
                
                except Exception as e:
                    print(f"Error extracting product with BeautifulSoup: {e}")
                    continue
            
            # Check if there's a next page and we need to go there
            if page < total_pages:
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next Page']"))
                    )
                    
                    # Check if next button is disabled
                    if next_button.get_attribute("disabled") or "disabled" in next_button.get_attribute("class"):
                        print("No more pages available")
                        break
                    
                    # Human-like click with a random delay
                    next_button.click()
                    random_delay(2, 4)  # Longer delay between page navigation
                    page += 1
                except Exception as e:
                    print(f"Error navigating to next page: {e}")
                    break
            else:
                break
                
        print(f"Found {len(products)} products in total using BeautifulSoup")
        return products
        
    except Exception as e:
        print(f"Error during product extraction with BeautifulSoup: {e}")
        return products

def extract_reviews_bs(driver, product):
    """Extract reviews for a given product using BeautifulSoup with human-like behavior"""
    reviews = []
    
    try:
        # Navigate with human-like behavior
        print(f"Extracting reviews for: {product['name']} using BeautifulSoup")
        navigate_with_human_behavior(driver, product['url'])
        
        # Scroll down to reviews section with natural scrolling
        try:
            review_section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#customer-reviews-header"))
            )
            
            # Natural scrolling to the reviews section
            viewport_height = driver.execute_script("return window.innerHeight")
            current_position = driver.execute_script("return window.pageYOffset")
            element_position = review_section.location['y']
            
            # Calculate how many scroll steps we need
            distance = element_position - current_position
            steps = max(5, distance // 300)  # At least 5 steps for short distances
            
            for i in range(steps):
                scroll_to = current_position + (distance * (i+1) / steps)
                driver.execute_script(f"window.scrollTo(0, {scroll_to});")
                random_delay(0.3, 0.7)  # Small random delay between scrolls
                
            random_delay(1, 2)  # Pause when reaching the reviews section
            
        except TimeoutException:
            print("Review section not found")
            return reviews
        
        # Click "See all reviews" button if available
        try:
            see_all_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'See all reviews')]"))
            )
            see_all_button.click()
            random_delay(2, 4)  # Wait for reviews page to load
        except TimeoutException:
            print("No 'See all reviews' button found, continuing with visible reviews")
        
        page = 1
        max_pages = 10  # Limit the number of pages to scrape
        
        while page <= max_pages:
            print(f"Extracting reviews from page {page} using BeautifulSoup...")
            
            # Wait for reviews to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-automation-id='review']"))
            )
            
            # Random scroll to simulate reading reviews
            total_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            scrolls = min(5, total_height // viewport_height)  # Max 5 scrolls
            
            for i in range(scrolls):
                scroll_amount = random.randint(300, 700)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                random_delay(0.5, 1.5)
            
            # Get page source and parse with BeautifulSoup
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract review elements
            review_elements = soup.select("[data-automation-id='review']")
            
            for review_elem in review_elements:
                try:
                    # Extract review details
                    # Rating
                    rating = 0
                    rating_elem = review_elem.select_one("[data-automation-id='review-rating']")
                    if rating_elem:
                        rating_text = rating_elem.get('aria-label')
                        if rating_text:
                            try:
                                rating = int(rating_text.split()[0])
                            except (ValueError, IndexError):
                                pass
                    
                    # Title
                    title = ""
                    title_elem = review_elem.select_one("[data-automation-id='review-title']")
                    if title_elem:
                        title = title_elem.get_text().strip()
                    
                    # Content
                    content = ""
                    content_elem = review_elem.select_one("[data-automation-id='review-text']")
                    if content_elem:
                        content = content_elem.get_text().strip()
                    
                    # Author
                    author = "Anonymous"
                    author_elem = review_elem.select_one("[data-automation-id='review-author']")
                    if author_elem:
                        author = author_elem.get_text().strip()
                    
                    # Date
                    date = ""
                    date_elem = review_elem.select_one("[data-automation-id='review-date']")
                    if date_elem:
                        date = date_elem.get_text().strip()
                    
                    # Create review object
                    review = {
                        'id': str(uuid.uuid4()),
                        'product_id': product['product_id'],
                        'rating': rating,
                        'title': title,
                        'content': content,
                        'author': author,
                        'date': date,
                        'source': 'walmart_bs'
                    }
                    
                    reviews.append(review)
                    
                except Exception as e:
                    print(f"Error extracting review with BeautifulSoup: {e}")
                    continue
            
            # Check if there's a next page button
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-automation-id='next-page']"))
                )
                
                # Check if next button is disabled
                if next_button.get_attribute("disabled") or "disabled" in next_button.get_attribute("class"):
                    print("No more review pages")
                    break
                
                # Human-like click on next button
                next_button.click()
                random_delay(2, 4)  # Longer delay between page navigation
                page += 1
            except Exception as e:
                print(f"No more review pages or error: {e}")
                break
        
        print(f"Extracted {len(reviews)} reviews for {product['name']} using BeautifulSoup")
        return reviews
        
    except Exception as e:
        print(f"Error extracting reviews with BeautifulSoup: {e}")
        return reviews

def fetch_walmart_reviews_api(product_id):
    """Fetch reviews using Walmart's BazaarVoice API with browser emulation"""
    reviews = []
    page = 1
    limit = 100  # Maximum allowed by the API
    
    # Create headers that mimic a real browser
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': f'https://www.walmart.com/ip/{product_id}',
        'Origin': 'https://www.walmart.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    
    try:
        while True:
            # Walmart uses BazaarVoice for reviews
            url = f"https://api.bazaarvoice.com/data/reviews.json?apiversion=5.5&passkey=caR76h9zeB8gQmbi1qDbqMBUy&Filter=ProductId:{product_id}&Include=Products&Stats=Reviews&limit={limit}&offset={limit * (page - 1)}&Sort=SubmissionTime:desc"
            
            print(f"Fetching page {page} from Walmart BazaarVoice API...")
            
            # Add a random delay to simulate human behavior
            random_delay(1, 3)
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Error fetching reviews: HTTP {response.status_code}")
                break
                
            data = response.json()
            current_reviews = data.get('Results', [])
            
            if not current_reviews:
                break
                
            for review in current_reviews:
                review_data = {
                    'id': str(uuid.uuid4()),
                    'product_id': product_id,
                    'rating': review.get('Rating', 0),
                    'title': review.get('Title', ''),
                    'content': review.get('ReviewText', ''),
                    'author': review.get('UserNickname', 'Anonymous'),
                    'date': review.get('SubmissionTime', ''),
                    'source': 'walmart_api'
                }
                reviews.append(review_data)
            
            # Check if there are more reviews to fetch
            total_results = data.get('TotalResults', 0)
            if len(reviews) >= total_results or not current_reviews:
                break
                
            page += 1
            
            # Longer random delay between API pages
            random_delay(2, 5)
            
        print(f"Successfully fetched {len(reviews)} reviews from Walmart API")
        return reviews
        
    except Exception as e:
        print(f"Error fetching Walmart API reviews: {str(e)}")
        return reviews

def save_walmart_api_reviews_to_db(reviews, product_info=None):
    """Save reviews fetched from Walmart API to database"""
    conn = create_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Create table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS walmart_api_reviews (
                    id UUID PRIMARY KEY,
                    product_id TEXT,
                    rating INTEGER,
                    title TEXT,
                    content TEXT,
                    author TEXT,
                    date TEXT,
                    source TEXT,
                    category TEXT
                )
            """)
            
            # Save product info if provided
            if product_info:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS walmart_products (
                        id UUID PRIMARY KEY,
                        product_id TEXT,
                        name TEXT,
                        price TEXT,
                        url TEXT,
                        category TEXT,
                        source TEXT
                    )
                """)
                
                cur.execute("""
                    INSERT INTO walmart_products (id, product_id, name, price, url, category, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        product_id = EXCLUDED.product_id,
                        name = EXCLUDED.name,
                        price = EXCLUDED.price,
                        url = EXCLUDED.url,
                        category = EXCLUDED.category,
                        source = EXCLUDED.source
                """, (
                    str(uuid.uuid4()),
                    product_info['product_id'],
                    product_info['name'],
                    product_info.get('price', 'N/A'),
                    product_info.get('url', ''),
                    product_info.get('category', 'unknown'),
                    product_info['source']
                ))
            
            # Get category from product_info
            category = product_info.get('category', 'unknown') if product_info else 'unknown'
            
            # Insert reviews
            review_data = [
                (
                    review['id'],
                    review['product_id'],
                    review['rating'],
                    review['title'],
                    review['content'],
                    review['author'],
                    review['date'],
                    review['source'],
                    category
                ) for review in reviews
            ]
            
            execute_batch(cur, """
                INSERT INTO walmart_api_reviews (id, product_id, rating, title, content, author, date, source, category)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    product_id = EXCLUDED.product_id,
                    rating = EXCLUDED.rating,
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    author = EXCLUDED.author,
                    date = EXCLUDED.date,
                    source = EXCLUDED.source,
                    category = EXCLUDED.category
            """, review_data)
            
            conn.commit()
            print(f"Saved {len(reviews)} Walmart API reviews to database")
            
    except Exception as e:
        print("Database error:", str(e))
        conn.rollback()
    finally:
        conn.close()

def main():
    """Main function to run the Walmart scraper for treadmills and exercise bikes"""
    driver = setup_driver()
    try:
        print("Starting Walmart scraper with advanced browser emulation...")
        
        # Category URLs provided by the user
        category_urls = {
            "treadmill": "https://www.walmart.com/browse/sports-outdoors/treadmills/4125_4134_1074326?povid=HDL_D9SportingGoods_NUPS_fitness_treadmills_week47",
            "exercise_bike": "https://www.walmart.com/browse/sports-outdoors/exercise-bikes/4125_4134_6143329?povid=HDL_D9SportingGoods_NUPS_fitness_exercisebikes_week47"
        }
        
        all_products = []
        
        # Extract products from each category using BeautifulSoup
        for category_name, category_url in category_urls.items():
            print(f"\n===== Processing {category_name.upper()} category with BeautifulSoup =====\n")
            products = extract_products_from_category_bs(driver, category_url, total_pages=3)
            all_products.extend(products)
            
            # Add a longer random delay between categories
            random_delay(5, 10)
        
        # Extract reviews for each product using BeautifulSoup
        if all_products:
            for i, product in enumerate(all_products):
                print(f"\nExtracting reviews for {product['name']} ({product.get('category', 'unknown')}) with BeautifulSoup")
                product['reviews'] = extract_reviews_bs(driver, product)
                print(f"Found {len(product['reviews'])} reviews")
                
                # Save progress after each product
                if i > 0 and i % 5 == 0:
                    print(f"Saving intermediate progress after {i} products...")
                    save_to_database(all_products[:i])
                
                # Add a longer random delay between product reviews
                random_delay(5, 10)
            
            # Save everything to database
            save_to_database(all_products)
        else:
            print("No products found")
        
        # Method 2: API approach for specific treadmill and exercise bike products
        # These IDs should be actual Walmart product IDs for popular treadmills and exercise bikes
        treadmill_ids = [
            "19864766",  # Example treadmill product ID
            "55503284"   # Another example treadmill ID
        ]
        
        exercise_bike_ids = [
            "15496979",  # Example exercise bike product ID
            "148876345"  # Another example exercise bike ID  
        ]
        
        # Process treadmill reviews
        for product_id in treadmill_ids:
            print(f"\nFetching API reviews for treadmill ID: {product_id}")
            reviews = fetch_walmart_reviews_api(product_id)
            if reviews:
                product_info = {
                    'product_id': product_id,
                    'name': f"Walmart Treadmill {product_id}",
                    'category': 'treadmill',
                    'source': 'walmart_api'
                }
                save_walmart_api_reviews_to_db(reviews, product_info)
            else:
                print(f"No API reviews found for treadmill ID: {product_id}")
            
            # Add a random delay between API calls
            random_delay(3, 7)
        
        # Process exercise bike reviews
        for product_id in exercise_bike_ids:
            print(f"\nFetching API reviews for exercise bike ID: {product_id}")
            reviews = fetch_walmart_reviews_api(product_id)
            if reviews:
                product_info = {
                    'product_id': product_id,
                    'name': f"Walmart Exercise Bike {product_id}",
                    'category': 'exercise_bike',
                    'source': 'walmart_api'
                }
                save_walmart_api_reviews_to_db(reviews, product_info)
            else:
                print(f"No API reviews found for exercise bike ID: {product_id}")
                
            # Add a random delay between API calls
            random_delay(3, 7)
        
    finally:
        print("Scraping completed. Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()
