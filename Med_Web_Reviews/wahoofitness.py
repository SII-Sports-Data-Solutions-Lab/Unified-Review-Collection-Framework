import requests
import uuid
import time
import psycopg2
from psycopg2.extras import execute_batch
import json
import os
from datetime import datetime


DB_CONFIG = {
    'user': 'admin',
    'host': 'raghuserver',
    'database': 'SII',
    'password': 'raghu@123',
    'port': 5432
}


def create_connection():
    """Create a database connection to the PostgreSQL database"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return None

def fetch_wahoo_reviews(product_id, store_id="duEkEw80MrVVjc9AKulYxvFwxOT9DJNf6cIUthrO"):
    """Fetch Wahoo Fitness reviews from Yotpo API for a given product ID"""
    base_url = f"https://api-cdn.yotpo.com/v3/storefront/store/{store_id}/product/{product_id}/reviews"
    reviews = []
    page = 1
    per_page = 50  # Larger page size for efficiency
    
    try:
        # Create directory for raw data if it doesn't exist
        os.makedirs("raw_data", exist_ok=True)
        
        while True:
            url = f"{base_url}?page={page}&perPage={per_page}&sort=smart_optimistic,rating,date,badge,images"
            print(f"Fetching page {page} from Wahoo Fitness Yotpo API...")
            
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            if response.status_code != 200:
                print(f"Error fetching reviews: HTTP {response.status_code}")
                break
                
            data = response.json()
            
            # Save raw data for backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"raw_data/wahoo_{product_id}_page{page}_{timestamp}.json", "w") as f:
                json.dump(data, f, indent=2)
            
            current_reviews = data.get('reviews', [])
            
            if not current_reviews:
                break
                
            for review in current_reviews:
                # Only collect the fields the user is interested in
                review_data = {
                    "id": str(uuid.uuid4()),  # Generate unique ID for database
                    "review_id": review.get('id'),
                    "score": review.get('score', 0),
                    "content": review.get('content', ''),
                    "title": review.get('title', ''),
                    "created_at": review.get('createdAt', ''),
                    "product_name": data.get('products', [{}])[0].get('name', '') if data.get('products') else ''
                }
                reviews.append(review_data)
            
            pagination = data.get('pagination', {})
            total_pages = (pagination.get('total', 0) + per_page - 1) // per_page
            
            print(f"Fetched {len(current_reviews)} reviews (page {page}/{total_pages})")
            
            if page >= total_pages:
                break
                
            page += 1
            time.sleep(0.5)  # Slightly longer delay to be respectful
            
        print(f"Successfully fetched {len(reviews)} Wahoo Fitness reviews")
        return reviews
        
    except Exception as e:
        print(f"Error fetching Wahoo reviews: {str(e)}")
        return reviews

def save_wahoo_reviews_to_db(reviews):
    """Save Wahoo Fitness reviews to database"""
    conn = create_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Create simplified table with only the requested fields
            cur.execute("""
                CREATE TABLE IF NOT EXISTS wahoo_reviews (
                    id UUID PRIMARY KEY,
                    review_id BIGINT,
                    score INTEGER,
                    content TEXT,
                    title TEXT,
                    created_at TEXT,
                    product_name TEXT
                )
            """)
            
            # Insert reviews with only the relevant fields
            review_data = [
                (
                    review['id'],
                    review['review_id'],
                    review['score'],
                    review['content'],
                    review['title'],
                    review['created_at'],
                    review['product_name']
                ) for review in reviews
            ]
            
            execute_batch(cur, """
                INSERT INTO wahoo_reviews (
                    id, review_id, score, content, title, created_at, product_name
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    review_id = EXCLUDED.review_id,
                    score = EXCLUDED.score,
                    content = EXCLUDED.content,
                    title = EXCLUDED.title,
                    created_at = EXCLUDED.created_at,
                    product_name = EXCLUDED.product_name
            """, review_data)
            
            conn.commit()
            print(f"Saved {len(reviews)} Wahoo Fitness reviews to database")
            
    except Exception as e:
        print("Database error:", str(e))
        conn.rollback()
    finally:
        conn.close()

def scrape_and_save_wahoo_reviews(product_ids=None):
    """Reusable function to fetch and save Wahoo Fitness reviews for a list of product IDs."""
    if product_ids is None:
        product_ids = ["548"]
    for product_id in product_ids:
        print(f"\nProcessing Wahoo Fitness product ID: {product_id}")
        reviews = fetch_wahoo_reviews(product_id)
        if reviews:
            save_wahoo_reviews_to_db(reviews)
            print(f"Completed processing for product ID: {product_id}")
        else:
            print(f"No reviews found for product ID: {product_id}")
    print("\nAll Wahoo Fitness products processed successfully!")

def main():
    """Main function to scrape Wahoo Fitness product reviews"""
    # Wahoo Fitness product IDs - expanded list for more comprehensive data collection
    product_ids = [
        "548"
    ]
    
    scrape_and_save_wahoo_reviews(product_ids)

if __name__ == "__main__":
    main()
