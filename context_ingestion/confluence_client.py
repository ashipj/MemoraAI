import requests

def get_all_pages(base_url, email, token):
    auth = (email, token)
    headers = { "Accept": "application/json" }
    pages = []
    start = 0

    while True:
        url = f"{base_url}/rest/api/content?limit=25&start={start}&expand=body.storage"
        response = requests.get(url, auth=auth, headers=headers)
        data = response.json()
        results = data.get("results", [])

        for page in results:
            pages.append({
                "title": page["title"],
                "body": page["body"]["storage"]["value"],
                "page_id": page["id"],
                "url": f"{base_url}/pages/viewpage.action?pageId={page['id']}"
            })

        if "_links" in data and "next" in data["_links"]:
            start += 25
        else:
            break
    return pages
