import requests
import logging

from requests.auth import HTTPBasicAuth

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_all_pages(base_url, email, token):
    logger.info(f"token: {len(token)}")
    auth = (email.strip(), token.strip())
    # auth = HTTPBasicAuth(email.strip(), token.strip())
    headers = { "Accept": "application/json" }
    pages = []
    start = 0

    while True:
        # Fetch pages from Confluence API
        url = f"{base_url}/rest/api/content?limit=25&start={start}&expand=body.storage"
        logger.info(f"Auth {auth}, headers: {headers}, url: {url}")
        response = requests.get(url, auth=auth, headers=headers)
        data = response.json()
        logger.info(f"Response data: {response.status_code} : {data}")
        results = data.get("results", [])

        logger.info(f"URL: {url}")
        logger.info(f"Fetched {len(results)} pages from Confluence.")

        for page in results:
            logger.info(f"Processing page: {page['title']}")
            pages.append({
                "body": page["body"]["storage"]["value"],
                "metadata": {
                    "title": page["title"],
                    "page_id": page["id"],
                    "url": f"{base_url}/pages/viewpage.action?pageId={page['id']}"
                }
            })

        if "_links" in data and "next" in data["_links"]:
            start += 25
        else:
            break
    return pages
