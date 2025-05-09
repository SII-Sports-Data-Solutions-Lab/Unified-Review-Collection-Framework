import requests
import psycopg2
from psycopg2.extras import execute_batch
import json
import uuid

def ensure_uuid(value):
    if isinstance(value, str) and len(value) == 36:
        return value  # Assume it's already a UUID
    elif value and isinstance(value, int):  
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(value)))  # Convert integer to UUID
    return None  # Return None if invalid

DB_CONFIG = {
    'user': 'admin',
    'host': 'raghuserver',
    'database': 'SII',
    'password': 'raghu@123',
    'port': 5432
}


def create_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None
    

def get_product_data():
    # Setup session and headers
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    
    # Get visitorId from initial page visit
    main_url = 'https://www.target.com/c/exercise-bikes-fitness-sports-outdoors/-/N-56fdb'
    response = session.get(main_url, headers=headers)
    visitor_id = session.cookies.get('visitorId')
    
    if not visitor_id:
        return []
    
    # API parameters
    base_api_url = 'https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2'
    params = {
        'key': '9f36aeafbe60771e321a7cc95a78140772ab3e96',
        'category': '56fdb',
        'channel': 'WEB',
        'count': '24',
        'default_purchasability_filter': 'false',
        'include_sponsored': 'true',
        'offset': 0,
        'page': '/c/56fdb',
        'platform': 'desktop',
        'pricing_store_id': '2391',
        'useragent': headers['User-Agent'],
        'visitor_id': visitor_id
    }
    
    all_products = []
    offset = 0
    
    while True:
        params['offset'] = offset
        response = session.get(base_api_url, params=params, headers=headers)
        
        if response.status_code != 200:
            break
        
        data = response.json()
        products = data.get('data', {}).get('search', {}).get('products', [])
        
        if not products:
            break
        
        all_products.extend(products)
        
        offset += 24
    
    return all_products


def get_all_reviews(reviewed_id, delay=1):
    reviews = []
    page = 0  # Adjust to 1 if the API starts counting from 1
    has_more = True
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
    
    while has_more:
        url = "https://r2d2.target.com/ggc/v2/summary"
        params = {
            'key': 'c6b68aaef0eac4df4931aae70500b7056531cb37',
            'reviewedId': reviewed_id,
            'page': page,
            'size': 3,  # Max allowed per page (adjust if needed)
            'sortBy': 'most_recent',
            'verifiedOnly': 'false',
            'hasOnlyPhotos': 'false',
            'includes': 'reviews,reviewsWithPhotos,entities,metadata,statistics'
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch reviews for TCIN {reviewed_id}, page {page}")
            break
        
        data = response.json()
        batch = data.get('reviews', [])
        if not batch:
            has_more = False  # Exit loop if no reviews
        else:
            reviews.extend(batch['results'])
            page += 1
    
    return reviews


def save_reviews_to_db(reviews, product_name):
    """Save reviews to the database."""
    data_to_insert = [
        (
            ensure_uuid(review.get("id")),
            ensure_uuid(review.get("external_id")),
            review.get("channel"),
            review.get("tcin"),  # Common tcin
            product_name,  # Common product name
            review.get("Rating"),
            review.get("RatingRange"),
            json.dumps(review.get("SecondaryRatingsOrder", [])),  # Serialize list to JSON, default to empty list
            json.dumps(review.get("SecondaryRatings", {})),  # Serialize dict to JSON, default to empty dict
            review.get("title"),
            review.get("text"),
            review.get("is_recommended"),  # Use .get() to handle missing key
            review.get("is_verified"),
            review.get("status"),
            json.dumps(review.get("photos", [])),  # Serialize list to JSON, default to empty list
            json.dumps(review.get("BadgesOrder", [])),  # Serialize list to JSON, default to empty list
            json.dumps(review.get("Badges", {})),  # Serialize dict to JSON, default to empty dict
            review.get("SourceClient"),
            review.get("IsRatingsOnly"),
            review.get("ClientResponseCount"),
            json.dumps(review.get("ClientResponses", [])),  # Serialize list to JSON, default to empty list
            json.dumps(review.get("Entities", [])),  # Serialize list to JSON, default to empty list
            json.dumps(review.get("tags", [])),  # Serialize list to JSON, default to empty list
            json.dumps(review.get("author", {})),  # Serialize dict to JSON, default to empty dict
            review.get("is_syndicated"),
            json.dumps(review.get("feedback", {})),  # Serialize dict to JSON, default to empty dict
            review.get("submitted_at"),
            review.get("modified_at"),
            json.dumps(review.get("reviewer_attributes", [])),  # Serialize list to JSON, default to empty list
            review.get("is_incentivized")
        )
        for review in reviews
    ]

    conn = create_connection()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Batch insert query
                query = """
                    INSERT INTO target_reviews (
                        id, external_id, channel, tcin, product_name, rating, rating_range,
                        secondary_ratings_order, secondary_ratings, title, review_text,
                        is_recommended, is_verified, status, photos, badges_order, badges,
                        source_client, is_ratings_only, client_response_count, client_responses,
                        entities, tags, author, is_syndicated, feedback, submitted_at, modified_at,
                        reviewer_attributes, is_incentivized
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        external_id = EXCLUDED.external_id,
                        channel = EXCLUDED.channel,
                        tcin = EXCLUDED.tcin,
                        product_name = EXCLUDED.product_name,
                        rating = EXCLUDED.rating,
                        rating_range = EXCLUDED.rating_range,
                        secondary_ratings_order = EXCLUDED.secondary_ratings_order,
                        secondary_ratings = EXCLUDED.secondary_ratings,
                        title = EXCLUDED.title,
                        review_text = EXCLUDED.review_text,
                        is_recommended = EXCLUDED.is_recommended,
                        is_verified = EXCLUDED.is_verified,
                        status = EXCLUDED.status,
                        photos = EXCLUDED.photos,
                        badges_order = EXCLUDED.badges_order,
                        badges = EXCLUDED.badges,
                        source_client = EXCLUDED.source_client,
                        is_ratings_only = EXCLUDED.is_ratings_only,
                        client_response_count = EXCLUDED.client_response_count,
                        client_responses = EXCLUDED.client_responses,
                        entities = EXCLUDED.entities,
                        tags = EXCLUDED.tags,
                        author = EXCLUDED.author,
                        is_syndicated = EXCLUDED.is_syndicated,
                        feedback = EXCLUDED.feedback,
                        submitted_at = EXCLUDED.submitted_at,
                        modified_at = EXCLUDED.modified_at,
                        reviewer_attributes = EXCLUDED.reviewer_attributes,
                        is_incentivized = EXCLUDED.is_incentivized;
                """
                
                # Execute batch insert
                execute_batch(cur, query, data_to_insert)
                
    finally:
        conn.close()


def scrape_and_save_target_reviews(product_list=None):
    """Reusable function to fetch and save Target reviews for a list of products."""
    if product_list is None:
        product_list = get_product_data()
    for product in product_list:
        tcin = product.get('tcin')
        name = product.get('title', '').strip()
        print(f"\nScraping reviews for {name} (TCIN: {tcin})")
        reviews = get_all_reviews(tcin)
        if reviews:
            save_reviews_to_db(reviews, name)
            print(f"Completed scraping for {name}")
        else:
            print(f"No reviews found for {name}")
    print("\nAll Target products processed successfully!")


if __name__ == "__main__":
    products = get_product_data()
    scrape_and_save_target_reviews(products)
