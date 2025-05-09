import requests
from bs4 import BeautifulSoup
import json
from time import sleep
import psycopg2
from psycopg2.extras import execute_values
import logging
import argparse

# Configure logging
logging.basicConfig(
    filename='error_log.log',
    level=logging.ERROR,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

def log_error(error_message):
    logging.error(error_message)

headers = {
   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
   'accept-encoding': 'gzip, deflate, br, zstd',
   'accept-language': 'en-US,en;q=0.9',
   'cache-control': 'max-age=0',
   'cookie': 'ubid-main=130-4821511-2972805; s_nr=1728658184984-New; s_vnum=2160658184984%26vn%3D1; s_dslv=1728658184985; aws-target-data=%7B%22support%22%3A%221%22%7D; session-id-apay=133-5309301-7114661; session-id=145-5774519-2047817; av-timezone=America/Indianapolis; i18n-prefs=USD; lc-main=en_US; at-main=Atza|IwEBIB2_aL4Lu3U0qvsvvF8DQmp24H-nh0pWZUvulIA-C9WgpCZRNSMpBf44TR3sWIW1-hCTIwZD5P7rDrz9m_EkNj3gyFRpLAAZgmy1oWZon01ul5J9qEzyifCEhGhcJqrNVuiNsG8V8tJNtJFY1Y5bUl70MZhwnNUb9Op54VfZlRypXXnTv5YqztrX4A7LaWwRa6Umy3W96x9OthEIeHf9aqxPEeUW-rvwfE1hbpJ_hOryXQ; sess-at-main="uoctji6YPlOw+US0beYxHURsQC6cCZPbdFsR+eLyDQo="; sst-main=Sst1|PQFq8DE5E30b09zu9JN8Vpr5DHaDV0V-IqB4jHbu8j6pYNunLmtxanX_8Drg8pm1YW05WExpvVOhzNy1X13yT1wFFbu_eKYhegFKNmyCee_KOkRBNDtvAT6ehRjTgnCPj5eY6yIHULGBSDEGChCuI3Z81YFUY1J5-HxPhkumvTRmF6weToNIfxO-9QNXU0goddzdo-0ejdtPFYfzSF_kQLI_XqATapRmrlXIR1Vi253UJFe-ml_MdUvBtpDNVC_cW6pLQcFI7rQT78JC4JuaL0g5EQ6smert6P3ygqXHI1A8VXxB1wB6pf2EEyf2075YZQ9_LR54zkGeBh9mTf3zYp9qih0eCOubDLGl-J3OVDC0l68; session-id-time=2082787201l; aws-target-visitor-id=1729101271148-230921.45_0; AMCV_7742037254C95E840A4C98A6%40AdobeOrg=1585540135%7CMCIDTS%7C20106%7CMCMID%7C57116873832505185390579017089490117009%7CMCAAMLH-1737744417%7C7%7CMCAAMB-1737744417%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1737146817s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0; aws-ubid-main=373-7103873-0578444; regStatus=registered; aws-userInfo-signed=eyJ0eXAiOiJKV1MiLCJrZXlSZWdpb24iOiJ1cy1lYXN0LTEiLCJhbGciOiJFUzM4NCIsImtpZCI6ImE3YWE5NGE4LTBlNDUtNGZkNy05OWMxLWFjMmJlZWYzNTBmOSJ9.eyJzdWIiOiIiLCJzaWduaW5UeXBlIjoiUFVCTElDIiwiaXNzIjoiaHR0cDpcL1wvc2lnbmluLmF3cy5hbWF6b24uY29tXC9zaWduaW4iLCJrZXliYXNlIjoiTERoVGtic0IrS1Vnb0VldDJ4Q2x1eEY0d0twSWs0aFZkMXR0a1RyMkFmOD0iLCJhcm4iOiJhcm46YXdzOmlhbTo6NzA5MjM4NzY1MzU0OnJvb3QiLCJ1c2VybmFtZSI6IlJhZ2h1dmVlciUyMFYifQ.03K0sOfrWbvsOY2CurBB-gkUyHIKXpFR5YDS94675ikKFKb8E9LtOm2aUQ2nIMTD_4Fer4S5sSUnMhOpdXbEMrkTM-6j6-352yu8zuIAnbRPPA8oN1FivSXpsIoX8ADm; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A709238765354%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22Raghuveer%2520V%22%2C%22keybase%22%3A%22LDhTkbsB%2BKUgoEet2xCluxF4wKpIk4hVd1ttkTr2Af8%5Cu003d%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D; noflush_awsccs_sid=cfd6b181fa383740c3dfd4341ea9820698903f62e43803353ca5c3a7ccf7be66; av-profile=cGlkPWFtem4xLmFjdG9yLnBlcnNvbi5vaWQuQUtTR1QyNFJCQUZCRyZ0aW1lc3RhbXA9MTczNzY3NDU4NjE3MiZ2ZXJzaW9uPXYx.g_Vmq3Kf1mkIZwnVNhjk6awcYOfSLCuLONx_0zs7sXdQAAAAAQAAAABnks9acmF3AAAAAPgWC9WfHH8iB-olH_E9xQ; session-token=pdsiZj024OqECzyApDWJdiMosvgTxPnKbgEMIUM5GnGI9P4KbkwrKI9iSqNML7J/QbKCySnoWcuT6GVjEjeWNWpX5rp/yo01vTxqE+zSvYiHEN+2gnKsyDlBPn5wqAdNdkQRVq/4vgBWVdPjLEZ6vsxA9HEsmigcZPhB6O3uQNOJtGBW/spLeYoP8BeRR7JzW/f83ioeomYDRf47CyHN0icAlZDD3ROQ/smpQ5bKCh3ENAR21RJVy68bTqODXyHWJ+AXkoPxByGMP2sxaShIw3QZ3gx7HxT/gJEt4/GfqysP57W5bcZjByzbkjNkFJov1CKQY5zM7XCc8trcraJmiZhPXHSXhzT4DTr6gkapTgixXqAJlrfhDctKpeGN23VK; x-main="3F1k69HAi92hpStrg1skaSk8GWWav2hKDpiFIvNW3nHe?46523HyITrUbykQmQvA"; skin=noskin',
   'device-memory': '8',
   'downlink': '10',
   'dpr': '1.25',
   'ect': '4g',
   'priority': 'u=0, i',
   'rtt': '50',
   'sec-ch-device-memory': '8',
   'sec-ch-dpr': '1.25',
   'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
   'sec-ch-ua-mobile': '?0',
   'sec-ch-ua-platform': '"Windows"',
   'sec-ch-ua-platform-version': '""',
   'sec-ch-viewport-width': '560',
   'sec-fetch-dest': 'document',
   'sec-fetch-mode': 'navigate',
   'sec-fetch-site': 'same-origin',
   'sec-fetch-user': '?1',
   'upgrade-insecure-requests': '1',
   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
   'viewport-width': '560'
}

class AmazonReviewScraper:
    def __init__(self, db_config=None):
        """Initialize the scraper with optional database configuration.
        
        Args:
            db_config (dict): Database configuration with keys:
                - dbname: Database name
                - user: Database user
                - password: Database password
                - host: Database host
                - port: Database port
        """
        self.headers = headers
        self.db_config = db_config or {
            "dbname": "SII",
            "user": "admin",
            "password": "raghu@123",
            "host": "raghuserver",
            "port": "5432"
        }

    def search_amazon_pages(self, name, max_pages=20):
        all_products = []
        
        for page in range(1, max_pages + 1):
            try:
                print(f"Searching page {page} of {max_pages}")
                url = f"https://www.amazon.com/s?k={name}&page={page}"
                response = requests.request("GET", url, headers=self.headers, data={})
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract products from current page
                page_products = []
                for item in soup.find_all("div", {"data-asin": True}):
                    data_asin = item.get("data-asin", None)
                    title_tag = item.find("h2")
                    title = title_tag.get_text(strip=True) if title_tag else None
                    
                    h2_tag = item.find("h2", class_="a-size-medium a-spacing-none a-color-base a-text-normal")
                    aria_label = h2_tag["aria-label"] if h2_tag and "aria-label" in h2_tag.attrs else None
                    
                    if data_asin and title:
                        page_products.append({
                            "data_asin": data_asin, 
                            "title": title.lower() if title else None,
                            "description": aria_label.lower() if aria_label else None
                        })
                
                all_products.extend(page_products) # Add delay between pages to avoid rate limiting
                
            except Exception as e:
                log_error(f"Error processing page {page}: {e}")
                continue
        
        return all_products

    def get_reviews_from_html(self, page_html: str) -> BeautifulSoup:
        try:
            soup = BeautifulSoup(page_html, "lxml")
            reviews = soup.find_all("div", {"class": "a-section celwidget"})
            return reviews
        except Exception as e:
            log_error(f"Error extracting reviews from HTML: {e}")
            return BeautifulSoup("", "lxml")

    def get_review_date(self, soup_object: BeautifulSoup):
        try:
            date_string = soup_object.find("span", {"class": "review-date"}).get_text()
            return date_string.strip()
        except Exception as e:
            log_error(f"Error extracting review date: {e}")
            return ""

    def get_review_text(self, soup_object: BeautifulSoup) -> str:
        try:
            review_text = soup_object.find(
                "span", {"class": "a-size-base review-text review-text-content"}
            ).get_text()
            return review_text.strip()
        except Exception as e:
            log_error(f"Error extracting review text: {e}")
            return ""

    def insert_reviews_to_db(self, reviews, product_asin, product_title, product_description):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            insert_query = """
            INSERT INTO amazon_reviews (
                review_id, data_asin, product_title, product_description, rating, title, review_date, body
            ) VALUES %s
            ON CONFLICT (review_id) DO NOTHING;
            """

            review_values = [
                (
                    review['review_id'],
                    product_asin,
                    product_title,
                    product_description,
                    review['rating'],
                    review['title'],
                    review['date'],
                    review['body']
                )
                for review in reviews
            ]

            execute_values(cursor, insert_query, review_values)
            conn.commit()
        except Exception as e:
            log_error(f"Error inserting reviews into database: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_review_header(self, soup_object: BeautifulSoup) -> str:
        try:
            review_header = soup_object.find(
                "a",
                {
                    "class": "a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold"
                },
            ).get_text()
            return review_header.strip()
        except Exception as e:
            log_error(f"Error extracting review header: {e}")
            return ""

    def get_number_stars(self, soup_object: BeautifulSoup) -> str:
        try:
            stars = soup_object.find("span", {"class": "a-icon-alt"}).get_text()
            return stars.strip()
        except Exception as e:
            log_error(f"Error extracting number of stars: {e}")
            return ""

    def get_product_name(self, soup_object: BeautifulSoup) -> str:
        try:
            product = soup_object.find(
                "a", {"class": "a-size-mini a-link-normal a-color-secondary"}
            ).get_text()
            return product.strip()
        except Exception as e:
            log_error(f"Error extracting product name: {e}")
            return ""

    def get_reviews(self, soup):
        try:
            reviews = self.get_reviews_from_html(str(soup))
            scraped_reviews = []

            for review in reviews:
                try:
                    # Extract each review's details using the helper functions
                    r_title = self.get_review_header(review)
                    r_rating = self.get_number_stars(review)
                    r_content = self.get_review_text(review)
                    r_date = self.get_review_date(review)
                    r_product = self.get_product_name(review)

                    # Organize the review data into a dictionary
                    r = {
                        "product": r_product,
                        "title": r_title,
                        "rating": r_rating,
                        "content": r_content,
                        "date": r_date
                    }

                    # Append the review to the list
                    scraped_reviews.append(r)
                except Exception as e:
                    log_error(f"Error extracting review details: {e}")

            return scraped_reviews
        except Exception as e:
            log_error(f"Error getting reviews: {e}")
            return []

    def get_total_pages(self, soup):
        try:
            # Find the review count div
            review_info = soup.find('div', attrs={'data-hook': 'cr-filter-info-review-rating-count'})
            if review_info:
                # Extract the number of reviews (349 in your example)
                text = review_info.text.strip()
                review_count = int(text.split('with reviews')[0].split(',')[-1].strip())

                # Calculate total pages (10 reviews per page)
                total_pages = -(-review_count // 10)  # Ceiling division
                return total_pages, review_count
            return 1, 0
        except Exception as e:
            log_error(f"Error getting total pages: {e}")
            return 1, 0

    def get_reviews_from_page(self, reviews, soup, star):
        try:
            for review in soup.find_all('li', {'data-hook': 'review'}):
                try:
                    review_data = {
                        'review_id': review.get('id'),
                        'rating': star,
                        'title': review.select_one('[data-hook="review-title"] span').text.strip(),
                        'date': review.find('span', {'data-hook': 'review-date'}).text.split('on ')[-1],
                        'verified_purchase': bool(review.find('span', {'data-hook': 'avp-badge'})),
                        'body': review.find('span', {'data-hook': 'review-body'}).span.text.strip(),
                        'images': [img['src'] for img in review.select('.review-image-tile')],
                        'helpful_votes': review.find('span', {'data-hook': 'helpful-vote-statement'}).text.split()[0] if review.find('span', {'data-hook': 'helpful-vote-statement'}) else '0'
                    }
                    reviews.append(review_data)
                except Exception as e:
                    log_error(f"Error extracting review from page: {e}")
            return reviews
        except Exception as e:
            log_error(f"Error getting reviews from page: {e}")
            return reviews

    def fetch_reviews(self, product_asin, max_pages=5):
        stars = {
            'one_star': 1,
            'two_star': 2,
            'three_star': 3,
            'four_star': 4,
            'five_star': 5
        }
        reviews = []
        for star in stars:
            try:
                url = f"https://www.amazon.com/product-reviews/{product_asin}?filterByStar={star}&reviewerType=avp_only_reviews"

                # Step 3: Send a GET request
                response = requests.get(url, headers=self.headers)
                
                # Sample HTML parsing
                soup = BeautifulSoup(response.text, 'html.parser')

                for script in soup.find_all('script'):
                    script.decompose()

                total_pages, total_reviews = self.get_total_pages(soup)
                page_number = total_pages

                for page in range(1, page_number+1):
                    try:
                        url = f"https://www.amazon.com/product-reviews/{product_asin}?pageNumber={page}&filterByStar={star}&reviewerType=avp_only_reviews"
                        response = requests.get(url, headers=self.headers)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        for script in soup.find_all('script'):
                            script.decompose()
                        reviews = self.get_reviews_from_page(reviews, soup, stars[star])
                    except Exception as e:
                        log_error(f"Error fetching reviews from page {page} for ASIN {product_asin}: {e}")
            except Exception as e:
                log_error(f"Error fetching reviews for star rating {star} for ASIN {product_asin}: {e}")

        return reviews

    def scrape_product_reviews(self, search_term, max_pages=20):
        """Main function to scrape Amazon product reviews.
        
        Args:
            search_term (str): Product to search for on Amazon
            max_pages (int): Maximum number of search result pages to process
            
        Returns:
            list: List of products with their reviews
        """
        products = self.search_amazon_pages(search_term, max_pages)
        
        product_products = [
            product for product in products 
            if product["title"] and product["title"] == search_term.lower() 
            or (product['description'] and search_term.lower() in product['description'])
        ]

        for product in product_products:
            try:
                product_asin = product.get("data_asin")
                if not product_asin:
                    log_error(f"ASIN not found for product: {product}")
                    continue

                print(f"Fetching reviews for ASIN: {product_asin}")
                product["reviews"] = self.fetch_reviews(product_asin)
                self.insert_reviews_to_db(
                    product["reviews"],
                    product_asin,
                    product.get("title"),
                    product.get("description")
                )
            except Exception as e:
                log_error(f"Error processing product {product}: {e}")
        
        return product_products

def scrape_amazon_reviews(search_term, max_pages=20, db_config=None):
    """
    Reusable function to scrape Amazon product reviews.
    Args:
        search_term (str): Product to search for on Amazon
        max_pages (int): Maximum number of search result pages to process
        db_config (dict): Optional database configuration
    Returns:
        list: List of products with their reviews
    """
    scraper = AmazonReviewScraper(db_config=db_config)
    return scraper.scrape_product_reviews(search_term, max_pages)

def main():
    parser = argparse.ArgumentParser(description='Scrape Amazon product reviews')
    parser.add_argument('search_term', help='Product to search for on Amazon')
    parser.add_argument('--max-pages', type=int, default=20, help='Maximum number of search result pages to process')
    parser.add_argument('--db-config', type=json.loads, help='JSON string with database configuration')
    
    args = parser.parse_args()
    
    scraper = AmazonReviewScraper(db_config=args.db_config)
    products = scraper.scrape_product_reviews(args.search_term, args.max_pages)
    
    print(f"Found {len(products)} products")
    for product in products:
        print(f"Product: {product.get('title')} ({product.get('data_asin')})")
        print(f"Number of reviews: {len(product.get('reviews', []))}")

if __name__ == "__main__":
    main()
