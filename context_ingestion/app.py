import json
import os
from confluence_client import get_all_pages
from kb_formatter import chunk_and_store

def lambda_handler(event, context):
    confluence_base_url = os.environ.get("confluence_base_url")
    confluence_email = os.environ.get("email")
    s3_bucket = os.environ.get("S3_BUCKET")
    s3_prefix = os.environ.get("S3_PREFIX")

    confluence_token = event.get("token")
    
    pages = get_all_pages(confluence_base_url, confluence_email, confluence_token)
    chunk_and_store(pages, s3_bucket, s3_prefix)

    return {
        "statusCode": 200,
        "body": json.dumps(f"Ingested {len(pages)} pages into S3 for Bedrock KB.")
    }
