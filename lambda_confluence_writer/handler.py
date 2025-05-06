# lambda_confluence_writer/handler.py
import os
import json
import requests

def lambda_handler(event, context):
    CONFLUENCE_URL = os.environ['CONFLUENCE_URL']
    API_USER = os.environ['CONFLUENCE_USER']
    API_TOKEN = os.environ['CONFLUENCE_TOKEN']

    headers = {
        "Content-Type": "application/json"
    }

    auth = (API_USER, API_TOKEN)
    title = event['title']
    space = event['spaceKey']
    content = event['content']

    # Check if page exists
    search_url = f"{CONFLUENCE_URL}/rest/api/content?title={title}&spaceKey={space}&expand=version"
    response = requests.get(search_url, auth=auth, headers=headers)
    data = response.json()

    if data.get('results'):
        # Page exists, update
        page_id = data['results'][0]['id']
        version = data['results'][0]['version']['number'] + 1

        update_url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}"
        payload = {
            "id": page_id,
            "type": "page",
            "title": title,
            "space": {"key": space},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            },
            "version": {"number": version}
        }
        result = requests.put(update_url, data=json.dumps(payload), auth=auth, headers=headers)
    else:
        # Page doesn't exist, create new
        create_url = f"{CONFLUENCE_URL}/rest/api/content"
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        result = requests.post(create_url, data=json.dumps(payload), auth=auth, headers=headers)

    return {
        'statusCode': result.status_code,
        'body': result.text
    }
