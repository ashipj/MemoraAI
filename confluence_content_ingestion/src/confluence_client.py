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
        url = f"{base_url}/rest/api/content?limit=25&start={start}&expand=body.storage,ancestors"
        logger.info(f"Auth {auth}, headers: {headers}, url: {url}")
        response = requests.get(url, auth=auth, headers=headers)
        data = response.json()
        logger.info(f"Response data: {response.status_code} : {data}")
        results = data.get("results", [])

        logger.info(f"URL: {url}")
        logger.info(f"Fetched {len(results)} pages from Confluence.")

        for page in results:
            logger.info(f"Processing page: {page['title']}")
            ancestors = page.get("ancestors", [])
            if ancestors:
                immediate_parent = ancestors[-1]
                parent_page_id = immediate_parent.get("id")
                parent_page_title = immediate_parent.get("title")
            else:
                parent_page_id = None
                parent_page_title = None
            pages.append({
                "body": page["body"]["storage"]["value"],
                "metadata": {
                    "title": page["title"],
                    "page_id": page["id"],
                    "url": f"{base_url}/pages/viewpage.action?pageId={page['id']}",
                    "parent_page_id": parent_page_id,
                    "parent_page_title": parent_page_title
                }
            })

        if "_links" in data and "next" in data["_links"]:
            start += 25
        else:
            break
    return pages
