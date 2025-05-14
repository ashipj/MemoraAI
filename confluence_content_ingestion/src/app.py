import json
import os
import logging
from confluence_client import get_all_pages
from kb_formatter import chunk_and_store

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    confluence_base_url = os.environ.get("confluence_base_url")
    confluence_email = os.environ.get("confluence_email")
    s3_bucket = os.environ.get("S3_BUCKET")
    s3_prefix = os.environ.get("S3_PREFIX")
    confluence_token = os.environ.get("CONFLUENCE_TOKEN")

    logger.info(f"Confluence base URL: {confluence_base_url}") 
    logger.info(f"S3 bucket: {s3_bucket}")
    logger.info(f"S3 prefix: {s3_prefix}")
    logger.info(f"Confluence email: {confluence_email}")

    pages = get_all_pages(confluence_base_url, confluence_email, confluence_token)
    chunk_and_store(pages, s3_bucket, s3_prefix)

    return {
        "statusCode": 200,
        "body": json.dumps(f"Ingested {len(pages)} pages into S3 for Bedrock KB.")
    }
