import requests
import time
import json
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_batch
from datetime import datetime


# Database configuration
DB_CONFIG = {
    'user': 'admin',
    'host': 'raghuserver',
    'database': 'SII',
    'password': 'raghu@123',
    'port': 5432
}

# Create reviews table if not exists
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS velocore_reviews (
    id SERIAL PRIMARY KEY,
    ugc_id BIGINT,
    legacy_id BIGINT,
    review_id BIGINT,
    internal_review_id BIGINT,
    rating INTEGER,
    title TEXT,
    type TEXT,
    details TEXT,
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    helpful_votes INTEGER,
    verified_buyer BOOLEAN,
    client_id TEXT,
    locale TEXT,
    author_name TEXT,
    author_location TEXT,
    badges JSONB,
    custom_fields JSONB,
    photos JSONB
);
"""

def create_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def create_table(conn):
    """Create reviews table"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
        conn.rollback()


def insert_reviews(conn, reviews):
    """Insert reviews into the database"""
    insert_sql = """
    INSERT INTO velocore_reviews (
        ugc_id, legacy_id, review_id, internal_review_id, rating, title, type, details,
        created_date, updated_date, helpful_votes, verified_buyer, client_id,
        locale, author_name, author_location, badges, custom_fields, photos
    ) VALUES (
        %(ugc_id)s, %(legacy_id)s, %(review_id)s, %(internal_review_id)s, %(rating)s,
        %(title)s, %(type)s, %(details)s, %(created_date)s, %(updated_date)s,
        %(helpful_votes)s, %(verified_buyer)s, %(client_id)s, %(locale)s,
        %(author_name)s, %(author_location)s, %(badges)s, %(custom_fields)s, %(photos)s
    )
    """
    try:
        with conn.cursor() as cursor:
            # Prepare review data for insertion
            prepared_reviews = []
            for review in reviews:
                details = review.get('details', {})
                badges = review.get('badges', {})
                metrics = review.get('metrics', {})

                created_date = datetime.utcfromtimestamp(details.get('created_date')/ 1000) if details.get('created_date') else None
                updated_date = datetime.utcfromtimestamp(details.get('updated_date') / 1000) if details.get('updated_date')else None

                prepared = {
                    'ugc_id': review.get('ugc_id'),
                    'legacy_id': review.get('legacy_id'),
                    'review_id': review.get('review_id'),
                    'internal_review_id': review.get('internal_review_id'),
                    'rating': metrics.get('rating'),  
                    'title': details.get('headline'),
                    'type': review.get('type'),
                    'details': details.get('comments'),  
                    'created_date': created_date, 
                    'updated_date': updated_date, 
                    'helpful_votes': details.get('helpful_votes'), 
                    'verified_buyer': badges.get('is_verified_buyer', False),
                    'client_id': details.get('product_page_id'),  
                    'locale': details.get('locale'),  
                    'author_name': details.get('nickname'),  
                    'author_location': details.get('location'),  
                    'badges': json.dumps(badges),  
                    'custom_fields': json.dumps(details.get('properties', [])), 
                    'photos': json.dumps(review.get('photos', []))
                }
                prepared_reviews.append(prepared)
            
            # Batch insert
            execute_batch(cursor, insert_sql, prepared_reviews)
        conn.commit()
        print(f"Successfully inserted {len(reviews)} reviews")
    except Exception as e:
        print(f"Error inserting reviews: {e}")
        conn.rollback()


def scrape_all_reviews(product):
    base_url = 'https://display.powerreviews.com'
    api_key = '61c24da0-253d-432e-b5a5-77e18cf226d9'
    initial_url = f'{base_url}/m/710199/l/en_US/product/{product}/reviews?paging.from=0&paging.size=5&sort=Newest&image_only=false&page_locale=en_US&_noconfig=true&apikey={api_key}'
    
    all_reviews = []
    current_url = initial_url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    while current_url:
        try:
            response = requests.get(current_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Extract reviews
            if data.get('results'):
                reviews = data['results'][0].get('reviews', [])
                all_reviews.extend(reviews)
                print(f'Collected {len(reviews)} reviews. Total: {len(all_reviews)}')

            # Get next page URL
            paging = data.get('paging', {})
            next_page_path = paging.get('next_page_url')

            if next_page_path:
                # Add API key to next page URL
                if '?' in next_page_path:
                    current_url = f"{base_url}{next_page_path}&apikey={api_key}"
                else:
                    current_url = f"{base_url}{next_page_path}?apikey={api_key}"
            else:
                current_url = None

            # Respectful delay
            time.sleep(0.1)

        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}')
            break
        except json.JSONDecodeError as e:
            print(f'Failed to parse JSON: {e}')
            break

    for review in all_reviews:
        review["type"] = products[product]
    
    # Save results
    conn = create_connection()
    if conn:
        create_table(conn)
        insert_reviews(conn, all_reviews)
        conn.close()
        print('Review insertion completed')

if __name__ == '__main__':
    
    products = {101012:'BowFlex IC Bike SE',
            100894:'BowFlex C6 Bike',
            100910:'BowFlex Treadmill 22',
            100909:'BowFlex Treadmill 10',
            100998:'BowFlex BXT8J Treadmill',
            'HTM1439-01':'BowFlex T9 Treadmill',
            'velocore':'BowFlex VeloCore Bike - 22'}
    
    for product in products:
        scrape_all_reviews(product)
