import requests
import json
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

def get_reviews(equipment_type, limit=100, offset=0):
    url = "https://graph.prod.k8s.onepeloton.com/graphql?content=application/json"
    payload = json.dumps({
        "operationName": "UGCReviews",
        "variables": {
            "equipmentType": equipment_type,
            "orderBy": "overallRating_DESC",
            "lang": "en",
            "excludeFamily": True,
            "offset": offset,
            "limit": limit
        },
        "query": "query UGCReviews($equipmentType: ReviewEquipmentTypeUgc!, $lang: LanguageUgc, $excludeFamily: Boolean, $offset: Int, $limit: Int, $orderBy: ReviewsOrderByInputUgc, $minimalRating: Int, $overallRating: Int) {\n  reviewsByCriteria(equipmentType: $equipmentType, lang: $lang, excludeFamily: $excludeFamily, minimalRating: $minimalRating, overallRating: $overallRating) {\n    totalCount\n    nodes(orderBy: $orderBy, offset: $offset, limit: $limit) {\n      id\n      title\n      author {\n        name\n        location\n        verifiedPurchaser\n        __typename\n      }\n      locale\n      overallRating\n      ratingDelivery\n      ratingQuality\n      ratingValue\n      ratingEaseOfUse\n      ratingInstructorsVariety\n      body\n      frequency\n      photoUrl\n      photos\n      mainReason\n      whoUses\n      wouldRecommend\n      response\n      date\n      __typename\n    }\n    __typename\n  }\n}\n"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

def fetch_all_reviews(equipment_type, conn):
    all_reviews = []
    offset = 0
    limit = 100
    total_count = 1  # Initialize with a dummy value to enter the loop

    while offset < total_count:
        response = get_reviews(equipment_type, limit, offset)
        reviews_data = response.get('data', {}).get('reviewsByCriteria', {})
        total_count = reviews_data.get('totalCount', 0)
        reviews = reviews_data.get('nodes', [])
        all_reviews.extend(reviews)
        offset += limit

    insert_reviews_into_db(equipment_type, all_reviews, conn)

def insert_reviews_into_db(equipment_type, reviews, conn):
    insert_query = """
    INSERT INTO reviews (
        id, title, author_name, author_location, author_verified, locale, overall_rating,
        rating_delivery, rating_quality, rating_value, rating_ease_of_use, rating_instructors_variety,
        body, frequency, photo_url, main_reason, who_uses, would_recommend, response, review_date, equipment_type
    ) VALUES %s
    ON CONFLICT (id) DO NOTHING
    """
    values = [
        (
            review['id'], review['title'], review['author']['name'], review['author']['location'],
            review['author']['verifiedPurchaser'], review['locale'], review['overallRating'],
            review['ratingDelivery'], review['ratingQuality'], review['ratingValue'],
            review['ratingEaseOfUse'], review['ratingInstructorsVariety'], review['body'],
            review['frequency'], review['photoUrl'], review['mainReason'], review['whoUses'],
            review['wouldRecommend'], review['response'], datetime.strptime(review['date'], "%Y-%m-%dT%H:%M:%S%z"),
            equipment_type
        )
        for review in reviews
    ]
    execute_values(conn.cursor(), insert_query, values)
    conn.commit()

def scrape_and_save_peloton_reviews(equipment_types=None):
    """Reusable function to fetch and save Peloton reviews for a list of equipment types."""
    if equipment_types is None:
        equipment_types = ["BIKE", "BIKEPLUS", "TREAD", "TREADPLUS", "ROW"]
    conn = psycopg2.connect(
        dbname="cda1f23e499f",
        user="admin",
        password="raghu@123",
        host="raghuserver",
        port="5432"
    )
    for equipment in equipment_types:
        print(f"\nScraping reviews for {equipment}")
        fetch_all_reviews(equipment, conn)
        print(f"Completed scraping for {equipment}")
    conn.close()
    print("\nAll Peloton equipment processed successfully!")

def main():
    equipment_types = ["BIKE", "BIKEPLUS", "TREAD", "TREADPLUS", "ROW"]
    scrape_and_save_peloton_reviews(equipment_types)

if __name__ == "__main__":
    main()