import os
import boto3
import base64
import re
import logging
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from boto3.dynamodb.conditions import Key

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DDB_TABLE_NAME'])

def lambda_handler(event, context):
    service = get_gmail_service()
    messages = fetch_recent_emails(service)
    saved_count = 0

    for m in messages:
        msg = service.users().messages().get(userId='me', id=m['id'], format='full').execute()
        headers = msg.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        body = get_email_body(msg.get('payload', {}))
        thread_id = msg['threadId']

        # Check if thread already exists
        response = table.query(
            IndexName='threadId-index',
            KeyConditionExpression=Key('threadId').eq(thread_id)
        )
        items = response.get('Items', [])
        # existing = table.get_item(Key={'threadId': thread_id}).get('Item')

        if len(items) > 0:
            # If thread exists, strip quoted text from body
            body = strip_quoted_text(body)
        else:
            # If new thread, save full body
            body = body.strip()

        item = {
            'id': msg['id'],
            'threadId': thread_id,
            'subject': subject,
            'fromAddress': from_addr,
            'receivedDateTime': date,
            'bodyPreview': body,
            'processed': False
        }
        table.put_item(Item=item)
        saved_count += 1

    return {"statusCode": 200, "message": f"{saved_count} emails stored."}


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


def fetch_recent_emails(service):
    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=24)
    query = f"after:{int(past.timestamp())}"
    result = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
    return result.get('messages', [])


def get_email_body(payload):
    parts = payload.get('parts', [])
    if parts:
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    else:
        body_data = payload.get('body', {}).get('data', '')
        if body_data:
            return base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
    return ''


def strip_quoted_text(body):
    lines = body.splitlines()
    cleaned_lines = []
    logger.info(f"Original body: {body}")
    for line in lines:
        # Remove the specific "On ... wrote:" line
        if re.match(r'\n?On\s.+?wrote:\s*\n?', line.strip()):
            continue
        # Remove quoted lines starting with '>'
        if line.strip().startswith('>'):
            continue
        cleaned_lines.append(line)
    clean_body = '\n'.join(cleaned_lines).strip()
    logger.info(f"After removing quoted lines: {clean_body}")
    return clean_body