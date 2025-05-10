import os
import boto3
import base64
import email
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta, timezone

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DDB_TABLE_NAME'])

def lambda_handler(event, context):
    service = get_gmail_service()
    messages = fetch_recent_emails(service)

    for m in messages:
        msg = service.users().messages().get(userId='me', id=m['id'], format='full').execute()
        headers = msg.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        body = get_email_body(msg.get('payload', {}))

        item = {
            'id': msg['id'],
            'threadId': msg['threadId'],
            'subject': subject,
            'fromAddress': from_addr,
            'receivedDateTime': date,
            'bodyPreview': body,
            'processed': False
        }
        table.put_item(Item=item)

    return {"statusCode": 200, "message": f"{len(messages)} emails stored."}


# Gmail service auth using OAuth2
def get_gmail_service():
    creds = Credentials(
        token=os.environ['ACCESS_TOKEN'],
        refresh_token=os.environ['REFRESH_TOKEN'],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ['CLIENT_ID'],
        client_secret=os.environ['CLIENT_SECRET'],
        scopes=['https://www.googleapis.com/auth/gmail.readonly']
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('gmail', 'v1', credentials=creds)

# Fetch emails received in the past hour
def fetch_recent_emails(service):
    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=1)
    query = f"after:{int(past.timestamp())}"  # Gmail API expects epoch seconds
    result = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
    return result.get('messages', [])

# Extract email body from the payload
# Handles both multipart and single-part emails
def get_email_body(payload):
    parts = payload.get('parts', [])
    if parts:
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    else:
        # For single-part emails
        body_data = payload.get('body', {}).get('data', '')
        if body_data:
            return base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
    return ''
