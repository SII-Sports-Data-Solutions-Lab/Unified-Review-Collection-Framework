import requests
import uuid
import time
import psycopg2
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

def scrape_and_save_turnto_reviews(sku_list=None):
    """Reusable function to fetch and save Turnto reviews for a list of SKUs."""
    if sku_list is None:
        sku_list = ["43619-NTL19124"]
    for sku in sku_list:
        reviews = fetch_turnto_reviews(sku)
        if reviews:
            save_turnto_reviews_to_db(reviews)

# Example usage in main:
def main():
    # Example SKU for Bowflex T22 Treadmill
    sku = "43619-NTL19124"
    scrape_and_save_turnto_reviews([sku])

if __name__ == "__main__":
    main()

