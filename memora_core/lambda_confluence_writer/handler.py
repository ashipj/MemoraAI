# lambda_confluence_writer/handler.py
import os
import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        CONFLUENCE_URL = os.environ['CONFLUENCE_URL']
        API_USER = os.environ['CONFLUENCE_USER']
        API_TOKEN = os.environ['CONFLUENCE_TOKEN']

        headers = {
            "Content-Type": "application/json"
        }

        auth = (API_USER, API_TOKEN)

        logger.info("Event received: %s", json.dumps(event))

        # For Bedrock-style payloads
        if 'parameters' in event:
            params = {p['name']: p['value'] for p in event['parameters']}
        else:
            params = event  # Direct JSON

        space = params.get('spaceKey')
        title = params.get('title')
        content = params.get('content')
        parent_page_id = params.get('parentPageId')

        # Just log the inputs for now
        logger.info(f"Title: {title}")
        logger.info(f"Space: {space}")
        logger.info(f"Parent ID: {parent_page_id}")
        logger.info(f"Content: {content}")

        # Check if page exists
        search_url = f"{CONFLUENCE_URL}/rest/api/content?title={title}&spaceKey={space}&expand=version"
        response = requests.get(search_url, auth=auth, headers=headers)
        data = response.json()

        action_taken = "created"
        if data.get('results'):
            action_taken = "updated"
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
            if parent_page_id:
                payload["ancestors"] = [{"id": str(parent_page_id)}]
            result = requests.post(create_url, data=json.dumps(payload), auth=auth, headers=headers)
            
        logger.info(f"Output: {result.json()}")
        new_page_url = f"{CONFLUENCE_URL}/spaces/{space}/pages/{result.json().get('id')}"
        logger.info(f"New page URL: {new_page_url}")

        response_body = {
            'TEXT': {
                'body': f"Page with title '{title}' was {action_taken} at url {new_page_url}."
            }
        }
        
        function_response = {
            'actionGroup': event['actionGroup'],
            'function': event['function'],
            'functionResponse': {
                'responseBody': response_body
            }
        }
    
        session_attributes = event['sessionAttributes']
        prompt_session_attributes = event['promptSessionAttributes']

        action_response = {
            'messageVersion': '1.0', 
            'response': function_response,
            'sessionAttributes': session_attributes,
            'promptSessionAttributes': prompt_session_attributes
        }
        return action_response
    except Exception as e:
        logger.error("Exception occurred: %s", str(e))
        return {
            "messageVersion": "1.0",
            "functionResponse": {
                "output": {
                    "status": "ERROR",
                    "message": f"Exception occurred: {str(e)}"
                }
            }
        }