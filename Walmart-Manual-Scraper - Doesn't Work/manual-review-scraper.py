import time
import json
import random
import requests
import re
import os
from urllib.parse import urlparse, parse_qs
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

def extract_product_id(product_url):
    """Extract the product ID from a Walmart product URL"""
    # Try to extract using URL parsing
    try:
        # First try extracting from the pathname
        parsed_url = urlparse(product_url)
        path_segments = parsed_url.path.strip('/').split('/')
        
        # The product ID is typically the last segment in the URL path
        # For review URLs like https://www.walmart.com/reviews/product/459455734
        if 'reviews' in parsed_url.path:
            product_id = path_segments[-1]
        # For product URLs like https://www.walmart.com/ip/product-name/459455734
        elif 'ip' in parsed_url.path:
            product_id = path_segments[-1]
        else:
            # Try to find the number at the end of URL
            match = re.search(r'/(\d+)(?:\?|$)', product_url)
            if match:
                product_id = match.group(1)
            else:
                # Fallback: extract from query parameters if present
                query_params = parse_qs(parsed_url.query)
                product_id = query_params.get('id', [None])[0]
        
        return product_id
    except Exception as e:
        print(f"Error extracting product ID from URL: {e}")
        return None

def fetch_reviews_graphql(product_url, limit_per_page=10, max_pages=100, output_file=None):
    """
    Fetch product reviews using Walmart's GraphQL API
    
    Args:
        product_url: URL of the product or product review page
        limit_per_page: Number of reviews to fetch per page
        max_pages: Maximum number of pages to fetch
        output_file: Path to save the JSON output file
    
    Returns:
        List of review objects
    """
    # Extract product ID from URL
    product_id = extract_product_id(product_url)
    if not product_id:
        print("Could not extract product ID from URL")
        return []
    
    print(f"Extracted product ID: {product_id}")
    
    # GraphQL endpoint
    graphql_url = "https://www.walmart.com/orchestra/home/graphql/ReviewsById/2a57e2551087b5ca4379fd99b25e5deffc25f97f389a87c2f17d2a45daefb031"
    
    # Initialize variables
    all_reviews = []
    current_page = 1
    total_pages = 1  # Will be updated from the first response
    
    # Track product info from first response
    product_info = None
    
    try:
        while current_page <= max_pages and current_page <= total_pages:
            print(f"Fetching page {current_page} of reviews...")
            
            # Build variables for GraphQL query
            variables = {
                "itemId": product_id,
                "page": current_page,
                "sort": "relevancy",  # Options: relevancy, submission-desc, submission-asc, rating-desc, rating-asc
                "limit": limit_per_page,
                "filters": [],
                "aspect": None,
                "filterCriteria": {
                    "rating": [],
                    "reviewAttributes": [],
                    "aspectId": None
                }
            }
            
            # Convert variables to URL-encoded JSON string
            variables_str = json.dumps(variables).replace(" ", "")
            
            # Build the full URL with parameters
            url = f"{graphql_url}?variables={variables_str}"
            
            # Create headers that mimic a real browser
            headers = {
                'authority': 'www.walmart.com',
                'scheme': 'https',
                'Baggage': 'trafficType=customer,deviceType=desktop,renderScope=CSR,webRequestSource=Browser,pageName=seeAllReviews,isomorphicSessionId=yWKIaAPm6CQc5PhHMh5Ye,renderViewId=749b87eb-04ee-4e95-a848-efa6e63fdd39',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': f'https://www.walmart.com/reviews/product/{product_id}',
                'Origin': 'https://www.walmart.com',
                'Connection': 'keep-alive',
                'Wm_page_url': f'https://www.walmart.com/reviews/product/{product_id}',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                # Additional headers to look more like a browser
                'X-APOLLO-OPERATION-NAME': 'ReviewsById',
                'content-type': 'application/json',
                'Cookie': 'ACID=031effb5-04fd-47b5-811b-6b790f667161; _m=9; hasACID=true; abqme=true; vtc=cA6sgtm-suK_ePxmix3-9k; _pxhd=4dcd3a05879037ee56ace989e5da9ce8d5e0d7e931d7330ffc0d9104ea01147f:5d770349-ac6c-11ef-8ebe-bdeb87c1ddef; _pxvid=5d770349-ac6c-11ef-8ebe-bdeb87c1ddef; io_id=0edccb2c-aa6b-4bf6-9037-ab04752ded5f; brwsr=d4d6b41e-e89b-11ef-948e-f765dacfa8a5; salsify_session_id=7b22b42e-7a30-43c0-a78d-38eac401fa07; hasLocData=1; adblocked=true; assortmentStoreId=4053; dimensionData=695; _sp_id.ad94=be84994e-0139-45bd-8890-977a593b1424.1740435293.1.1740435314.1740435293.7c456a54-6cb5-4b11-8d53-2b10d38d6e6a; pxcts=ba5a2d5a-fab3-11ef-9137-821a588fe493; _intlbu=false; _shcc=US; userAppVersion=us-web-1.186.0-bf6bd5dbc910944137dd6b81b3e6715bf0ce409b-030519; ak_bmsc=E7CA5447896ED2E25CE7C040D7CD05B9~000000000000000000000000000000~YAAQ7RjQF+IFvWSVAQAAhkdLcRuB/ERlvDVq1oIAI06qeBmRILxWchkGmo3Q9KAvRIiIWEEgE7Ep1TaFwlngg1LgBwzDP5WFq6BfhDo/ViG5M36GanI2+AlnOgLxj7HR2/M4dPn0gADKArhr1d1qOuz6mJ6xqNZk1asVQiCvrGXY1pOgfZEe+T71ntTBpw5Pe2Ze1iQ9TpMoscFQeR2/xHGL3GyqGfga9ykFYBzRCuPMV+u3WhlS6k/v5rxLW2ef+svH57RJ2I8lMJawwjMFmW2RlO1OWj9B4DGNMsTJj6V2Y2diDRnR9rMs1B2WyYfFI9U95kyX43llI3j94oK21dJwa/TTd3vbKNoLMSgc3hftQAILAeE6CS30ctLRo8C/FJmJD4krW/O06Xs=; AID=wmlspartner=wlpa:reflectorid=dsn_ad_0623da05-c5bf-4a48-9486-39a354348052:lastupd=1741364424326; auth=MTAyOTYyMDE4sae8%2FjrJIJE6cUq3dx9Z%2BREstNbcQ67w40H2TXOj7zVFH8J%2FD8TQkVK4xabJ9UqDhAKqwgH1guqZAQklM6KA8BxiS8N7H7F79cb97Z2CgDP%2FXPMmgPeFng0wBtZ4uW09767wuZloTfhm7Wk2Kcjygi5k0VvBM%2FJjwcKWWhCnBS9vrjzZsi9mFn%2B1kiLGXqDpU2UzQXiTDqwT042701%2F4eCJcAOifmXhHdGm3KTyUNMcUMk70P8glgOEpLOprhDfMWpzMbgzyqWg6MoSOREDGWrRY8LMzZ5qgi9gS949kQSjrBMuglCHA5wr4%2BivNIn2i%2Fmg22YPpoETrtTxh2SepEI8YUH63MxlKOZsIAxXj9iC5Zr7swXozMeaLkJeo6%2FhtLzQgD1SdHnl4RL8G5HqeHkjyrOXbKKhH072NS%2FW0j%2FU%3D; bstc=dcvEPmNRy39xTXYHezGhgs; mobileweb=0; xpth=x-o-mart%2BB2C~x-o-mverified%2Bfalse; xpa=21b5p|6LaVA|79dea|7xMaT|8TFb0|9wpmY|IpnX6|NC__g|OQe8n|PzMdd|RUIbZ|TuvkI|ZijSx|fdm-7|fiMHA|jL4sb|jM1ax|jQ0HQ|kGLhR|n7hlw|pXvSG|q92Hs|sXfD6|u4KO1|uYSVU|w6NXd|xf36q|yAoIi; exp-ck=21b5p16LaVA279dea19wpmY1NC__g1OQe8n2PzMdd2RUIbZ1TuvkI1ZijSx1fdm-71fiMHA1jL4sb3jQ0HQ1kGLhR3pXvSG1sXfD61u4KO11uYSVU1w6NXd3xf36q2yAoIi3; _astc=bcd702e2b84f3b87653150b9f0e61112; locDataV3=eyJpc0RlZmF1bHRlZCI6ZmFsc2UsImlzRXhwbGljaXQiOnRydWUsImludGVudCI6IlNISVBQSU5HIiwicGlja3VwIjpbeyJub2RlSWQiOiI0MDUzIiwiZGlzcGxheU5hbWUiOiJJbmRpYW5hcG9saXMgTmVpZ2hib3Job29kIE1hcmtldCIsImFkZHJlc3MiOnsicG9zdGFsQ29kZSI6IjQ2MjI4IiwiYWRkcmVzc0xpbmUxIjoiNTU1NSBNSUNISUdBTiBSRCIsImNpdHkiOiJJbmRpYW5hcG9saXMiLCJzdGF0ZSI6IklOIiwiY291bnRyeSI6IlVTIn0sImdlb1BvaW50Ijp7ImxhdGl0dWRlIjozOS44NTMzNzEsImxvbmdpdHVkZSI6LTg2LjE5MjUxMX0sInNjaGVkdWxlZEVuYWJsZWQiOnRydWUsInVuU2NoZWR1bGVkRW5hYmxlZCI6dHJ1ZSwic3RvcmVIcnMiOiIwNjowMC0yMzowMCIsImFsbG93ZWRXSUNBZ2VuY2llcyI6WyJJTiJdLCJzdXBwb3J0ZWRBY2Nlc3NUeXBlcyI6WyJQSUNLVVBfSU5TVE9SRSIsIlBJQ0tVUF9DVVJCU0lERSJdLCJ0aW1lWm9uZSI6IkFtZXJpY2EvSW5kaWFuYS9JbmRpYW5hcG9saXMiLCJzdG9yZUJyYW5kRm9ybWF0IjoiTmVpZ2hib3Job29kIE1hcmtldCIsInNlbGVjdGlvblR5cGUiOiJDVVNUT01FUl9TRUxFQ1RFRCJ9LHsibm9kZUlkIjoiMzc4MSJ9LHsibm9kZUlkIjoiMTUxOCJ9LHsibm9kZUlkIjoiMjc4NyJ9LHsibm9kZUlkIjoiMjc4NiJ9LHsibm9kZUlkIjoiNTgwNCJ9LHsibm9kZUlkIjoiNjM5MCJ9LHsibm9kZUlkIjoiMjc4OCJ9LHsibm9kZUlkIjoiNTQwOCJ9XSwic2hpcHBpbmdBZGRyZXNzIjp7ImxhdGl0dWRlIjozOS44NDYxLCJsb25naXR1ZGUiOi04Ni4yMDI5LCJwb3N0YWxDb2RlIjoiNDYyMjgiLCJjaXR5IjoiSW5kaWFuYXBvbGlzIiwic3RhdGUiOiJJTiIsImNvdW50cnlDb2RlIjoiVVNBIiwiZ2lmdEFkZHJlc3MiOmZhbHNlLCJ0aW1lWm9uZSI6IkFtZXJpY2EvTmV3X1lvcmsiLCJhbGxvd2VkV0lDQWdlbmNpZXMiOlsiSU4iXX0sImFzc29ydG1lbnQiOnsibm9kZUlkIjoiNDA1MyIsImRpc3BsYXlOYW1lIjoiSW5kaWFuYXBvbGlzIE5laWdoYm9yaG9vZCBNYXJrZXQiLCJpbnRlbnQiOiJQSUNLVVAifSwiaW50ZW50U291cmNlIjoiR0lDX0Z1bGZpbGxtZW50X1ByZWZlcmVuY2UiLCJpbnN0b3JlIjpmYWxzZSwiZGVsaXZlcnkiOnsibm9kZUlkIjoiNDA1MyIsImRpc3BsYXlOYW1lIjoiSW5kaWFuYXBvbGlzIE5laWdoYm9yaG9vZCBNYXJrZXQiLCJhZGRyZXNzIjp7InBvc3RhbENvZGUiOiI0NjIyOCIsImFkZHJlc3NMaW5lMSI6IjU1NTUgTUlDSElHQU4gUkQiLCJjaXR5IjoiSW5kaWFuYXBvbGlzIiwic3RhdGUiOiJJTiIsImNvdW50cnkiOiJVUyJ9LCJnZW9Qb2ludCI6eyJsYXRpdHVkZSI6MzkuODUzMzcxLCJsb25naXR1ZGUiOi04Ni4xOTI1MTF9LCJ0eXBlIjoiREVMSVZFUlkiLCJzY2hlZHVsZWRFbmFibGVkIjpmYWxzZSwidW5TY2hlZHVsZWRFbmFibGVkIjpmYWxzZSwiYWNjZXNzUG9pbnRzIjpbeyJhY2Nlc3NUeXBlIjoiREVMSVZFUllfQUREUkVTUyJ9XSwiaXNFeHByZXNzRGVsaXZlcnlPbmx5IjpmYWxzZSwiYWxsb3dlZFdJQ0FnZW5jaWVzIjpbIklOIl0sInN1cHBvcnRlZEFjY2Vzc1R5cGVzIjpbIkRFTElWRVJZX0FERFJFU1MiXSwidGltZVpvbmUiOiJBbWVyaWNhL0luZGlhbmEvSW5kaWFuYXBvbGlzIiwic3RvcmVCcmFuZEZvcm1hdCI6Ik5laWdoYm9yaG9vZCBNYXJrZXQiLCJzZWxlY3Rpb25UeXBlIjoiTFNfU0VMRUNURUQifSwiaXNnZW9JbnRsVXNlciI6ZmFsc2UsIm1wRGVsU3RvcmVDb3VudCI6MCwicmVmcmVzaEF0IjoxNzQxMzg0MTExODQ0LCJ2YWxpZGF0ZUtleSI6InByb2Q6djI6MDMxZWZmYjUtMDRmZC00N2I1LTgxMWItNmI3OTBmNjY3MTYxIn0%3D; locGuestData=eyJpbnRlbnQiOiJTSElQUElORyIsImludGVudFNvdXJjZSI6IkdJQ19GdWxmaWxsbWVudF9QcmVmZXJlbmNlIiwiaXNFeHBsaWNpdCI6dHJ1ZSwic3RvcmVJbnRlbnQiOiJQSUNLVVAiLCJtZXJnZUZsYWciOnRydWUsImlzRGVmYXVsdGVkIjpmYWxzZSwicGlja3VwIjp7Im5vZGVJZCI6IjQwNTMiLCJ0aW1lc3RhbXAiOjE3MzI2NzY2ODk3MjQsInNlbGVjdGlvblR5cGUiOiJDVVNUT01FUl9TRUxFQ1RFRCIsInNlbGVjdGlvblNvdXJjZSI6IlBpY2t1cCBTdG9yZSBTZWxlY3RvciJ9LCJzaGlwcGluZ0FkZHJlc3MiOnsidGltZXN0YW1wIjoxNzMyNjc2Njg5NzI0LCJ0eXBlIjoicGFydGlhbC1sb2NhdGlvbiIsImdpZnRBZGRyZXNzIjpmYWxzZSwicG9zdGFsQ29kZSI6IjQ2MjI4IiwiZGVsaXZlcnlTdG9yZUxpc3QiOlt7Im5vZGVJZCI6IjQwNTMiLCJ0eXBlIjoiREVMSVZFUlkiLCJ0aW1lc3RhbXAiOjE3NDA4Nzc3OTM2OTUsImRlbGl2ZXJ5VGllciI6bnVsbCwic2VsZWN0aW9uVHlwZSI6IkxTX1NFTEVDVEVEIiwic2VsZWN0aW9uU291cmNlIjpudWxsfV0sImNpdHkiOiJJbmRpYW5hcG9saXMiLCJzdGF0ZSI6IklOIn0sInBvc3RhbENvZGUiOnsidGltZXN0YW1wIjoxNzMyNjc2Njg5NzI0LCJiYXNlIjoiNDYyMjgifSwibXAiOltdLCJtc3AiOnsibm9kZUlkcyI6WyIzNzgxIiwiMTUxOCIsIjI3ODciLCIyNzg2IiwiNTgwNCIsIjYzOTAiLCIyNzg4IiwiNTQwOCJdLCJ0aW1lc3RhbXAiOjE3NDA4Nzc3OTM2NTF9LCJtcERlbFN0b3JlQ291bnQiOjAsInZhbGlkYXRlS2V5IjoicHJvZDp2MjowMzFlZmZiNS0wNGZkLTQ3YjUtODExYi02Yjc5MGY2NjcxNjEifQ%3D%3D; xpm=1%2B1741364424%2BcA6sgtm-suK_ePxmix3-9k~%2B0; _px3=7ba5bfbfb13f014a19cd2dbbe0a44b9f4327f69ce00f05fcfdc93c3e3bfefd3d:IAz3f63t7kbLQc5BEPXJPSd977EU/wI3Ab6p6LEof7ejk0GsduLUReQBhPhk2TFOE2YdXCt+DNlgt1CxrmVxRA==:1000:gAN3brtAHSyXmywz5slK68G7x+3+9reziCKoqf66VHhvakZj5y/DbIXusbGgxiewdG5WQkKxU5Rd6Pso7mSxTHQ3wTVfdeG51bkSawQnId088FYKDO0dethhTmcsR5jZBV4WmPs1K5ef1QJWHDeKa2ITP16VvvYrXQ4eshSXIiL1RsM3KwwBXYZU59vy3EzvRhmkq1PeYHBlvA3wzi/8rG8uaiYHYlfFJqa+mJgA3SI=; if_id=FMEZARSFGiiBuZIBr9mWI5m+RwkFtQR3Pfxx3dxtGI4LpzD4yWvuubmPgRG6e3lKDQ8TZ8v3VsdYKvJvj0vLFMijt7fuMYOzOxdIt2xVn957s5sqRmeWn5YzeLnehHmVnUkdb3Hfiaqf4spzyQJSZIqKkBfvH8C4fH+oL9/3jDNbe1h/p3KxknZAngLNqDXLttpL6pT8LPVhxlIrvecZFP28meZQjLlZwD0ew/XmBjtHdUeW2BZxYaTtlkJJa66Q9TXqUIdRlI18vXBUMS/3I6Giher8/AKb+VvDPyzNjOsAA1n6YK+6ABFcHTOTCy7fgr/Gknur8NKOTKoOk/nseywDoDbLky0=; TS016ef4c8=015aee3de23c5a5f51de07f8ee411331628660463df24c8b968890ebd3dcf8e6467da3248b463d85bdfcd7a9ffbfc3615b321f23b5; TS01f89308=015aee3de23c5a5f51de07f8ee411331628660463df24c8b968890ebd3dcf8e6467da3248b463d85bdfcd7a9ffbfc3615b321f23b5; TS8cb5a80e027=0832e887dfab2000be9884b2b7dc7f9594a25d3e3f0fbdcc4c5a53cbea28f73542b34ac9ee437fbc08caed488a113000abceff4c31609aed6362415d86d6cba779570b89760377c66c6f302f19ed848e1ecc7a3c12a2c1372a11f188a9705d46; ipSessionTrafficType=Internal; bm_mi=654B697FA7CDE6FDAA26ED5BE5333DBC~YAAQ5xjQFxGYU1aVAQAAitBpcRuXU7FvLV0d+qfeSHRIwFZM5yV1GuB9DLyW2swsFKRUEKLmQ0nSiRuQkc0b7xRePpOVDbiwi4P/GL+9+8jH6ks6v09yaUeChdCKZ1rDZ2QP7QsierZDyGPx5UjOmQqheHWyjwO5SrOjuV6goQimGfPEAXogDKnfTPCXpfVw2WGnevybZg2RZbgIeFqKer8FqRpsjW/mJfdcfsKRK7akuJOqHGxJtNy2MLOzUDoFQSlc7BUbChcx6Yzu76SAaaRQXLRKR6vWoKwtFSl8gIwAvJGrmnn8Yxjrl9SyJLE49c5GbmE7qRnXcLBW+OuT/u3TTpwp4e25o4ip4fJcCldoI8IudVd5Bm8GP7Rk8ksz/i9Dvjo/bYxEgsCaxdLN9DATpYhqogHC4cbKRxCqm44K+VBx0yz10467P6FfmX2Z+nxiYX1URKsQN1XEbhFUtuFXrJkRXgezpQ==~1; xptwj=uz:a49f482029c69f429bcd:Qo9UK7fqDR6nQNPBUNaVfBrlJNRmvT/NrwA6a6/3Tvw3TNCGrhTq0UOFV6uurvmtJ8MV6n8DOJhP4j0l1G5YJqZ2NSz9Do3U7QojPuNnarCqRpLR7PYVyuNhBudfs9+7hRUU5uY2dEz6IDolqyMB7AM9zD94Y1wHg8auhcJUFRoB1tij94bnEQuRZGkeQbzul9y1P1Lj/B0U7LSVl/jL6K8=; _pxde=b3af41448c6db9214a157db9e09b26982871b391294f6d95ae246983dffda409:eyJ0aW1lc3RhbXAiOjE3NDEzNjQ1MTU0ODV9; xptc=_m%2B9~assortmentStoreId%2B4053; com.wm.reflector="reflectorid:dsn_ad_0623da05-c5bf-4a48-9486-39a354348052@lastupd:1741364516000@firstcreate:1740877793529"; xptwg=1846086198:179DB6419FD71D0:3A3F5F6:824C4F64:E49A9BC7:9DFE3780:; TS012768cf=017eb508c68456aba0bf8159db56debbac1a6a0d114b2b0fd8bfe512e3d964a5fb1fdf51b1285d152872dc8ff216aee83290931487; TS01a90220=017eb508c68456aba0bf8159db56debbac1a6a0d114b2b0fd8bfe512e3d964a5fb1fdf51b1285d152872dc8ff216aee83290931487; TS2a5e0c5c027=0882a69f92ab2000a0c26ae68479e72b9ef99cf9b5400fb2a8157bc86fc6ba29e219e89158d8168208f06b644d113000cb6531e84a61d7baa2bf624cd66e37693c1a8a20f00b3ee8d20abd5bc641bf5afa955f44563a3c9aaba0a4027d6f9fc2; akavpau_p2=1741365116~id=d0b684a46b8dec059b2b33076e97309d; bm_sv=D4AF1C73EA61B464AB0C68B41573C360~YAAQ5xjQF3CcU1aVAQAAgtZpcRswBtLmVAVXjtTYRNVMjoIMGYWVrkWVjfvPa4a8Mq9/gw4L5juHqdtxa7DTVRHgdZHhDYmhNlioA/Ah+VlabDibbY+JMqFMq0V4z/gG1yIRJsyDLW7173tuVrUgnQO9gKDAE/HumWEKg1JptGCpPt5SbMCpYssljk+V/D3zRIFwfUfzs8D+uS7i02p4dgDhT5zfztXuZpK3YhQXIzDEYWCAmnGzrz4QrPWbSWrNsY8=~1'
            }
            
            # Add a random delay before each request
            random_delay(2, 5)
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Error fetching reviews: HTTP {response.status_code}")
                print(response.text[:200])  # Print first 200 chars of response for debugging
                break
            
            try:
                data = response.json()
                
                # Extract the data from the GraphQL response
                review_data = data.get('data', {}).get('reviews', {})
                
                # Get overall product info from first page
                if current_page == 1 and not product_info:
                    product_info = {
                        'product_id': product_id,
                        'name': review_data.get('product', {}).get('name', ''),
                        'average_rating': review_data.get('summaryState', {}).get('overallRating', {}).get('average', 0),
                        'total_reviews': review_data.get('pagination', {}).get('total', 0)
                    }
                    print(f"Product: {product_info['name']}")
                    print(f"Average Rating: {product_info['average_rating']}")
                    print(f"Total Reviews: {product_info['total_reviews']}")
                
                # Extract reviews from the current page
                reviews = review_data.get('reviews', [])
                
                if not reviews:
                    print("No more reviews found")
                    break
                
                # Process each review
                for review in reviews:
                    review_obj = {
                        'review_id': review.get('id'),
                        'title': review.get('title', ''),
                        'text': review.get('text', ''),
                        'rating': review.get('rating', 0),
                        'reviewer_name': review.get('userNickname', 'Anonymous'),
                        'submission_date': review.get('submissionDate', ''),
                        'helpful_votes': review.get('helpfulness', {}).get('helpfulVoteCount', 0),
                        'not_helpful_votes': review.get('helpfulness', {}).get('unhelpfulVoteCount', 0),
                        'verified_purchase': review.get('verifiedPurchase', False),
                        'product_id': product_id
                    }
                    
                    # Extract review photos if available
                    if 'photos' in review and review['photos']:
                        review_obj['photos'] = [photo.get('url') for photo in review['photos']]
                    
                    all_reviews.append(review_obj)
                
                # Update pagination information
                pagination = review_data.get('pagination', {})
                total_pages = pagination.get('pages', 0)
                
                print(f"Fetched {len(reviews)} reviews (Page {current_page}/{total_pages})")
                
                # Move to next page
                current_page += 1
                
                # Add a longer random delay between pages
                random_delay(3, 7)
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                break
                
        # Save all reviews to file if requested
        if output_file and all_reviews:
            output_data = {
                'product': product_info,
                'reviews': all_reviews,
                'total_reviews_fetched': len(all_reviews),
                'date_fetched': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(all_reviews)} reviews to {output_file}")
        
        return all_reviews
        
    except Exception as e:
        print(f"Error fetching reviews: {str(e)}")
        
        # Save whatever we have if there's an error
        if output_file and all_reviews:
            output_data = {
                'product': product_info,
                'reviews': all_reviews,
                'total_reviews_fetched': len(all_reviews),
                'date_fetched': time.strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(e)
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(all_reviews)} reviews to {output_file} (with error)")
            
        return all_reviews

def main():
    """Main function to run the Walmart GraphQL API review scraper"""
    print("Walmart GraphQL API Review Scraper")
    print("----------------------------------")
    
    # Example product URL
    product_url = "https://www.walmart.com/reviews/product/459455734"
    
    # Output file path
    output_file = "reviews_output.json"
    
    # Fetch reviews
    reviews = fetch_reviews_graphql(
        product_url=product_url, 
        limit_per_page=10,      # 20 reviews per page
        max_pages=50,           # Up to 50 pages (1000 reviews max)
        output_file=output_file
    )
    
    print(f"Scraping completed with {len(reviews)} reviews.")

if __name__ == "__main__":
    main()