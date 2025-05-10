import json
import boto3
import logging
from boto3.dynamodb.conditions import Attr, Key
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('EmailStorage')

bedrock_runtime = boto3.client("bedrock-agent-runtime")
AGENT_ID = "GCUHPGWEWO"
# AGENT_ALIAS_ID = "60HGQN0VKA" Cloude sonnet
# AGENT_ALIAS_ID = "9ZSGMXEBKU"  # Nova lite
AGENT_ALIAS_ID = "A98JF2T472"  # Claude 3.5 Haiku

def lambda_handler(event, context):
    logger.info("Starting email thread summarization process.")
    
    thread_ids = get_unique_unprocessed_thread_ids()
    logger.info(f"Found {len(thread_ids)} unique unprocessed threadIds.")

    results = []

    for thread_id in thread_ids:
        logger.info(f"Processing threadId: {thread_id}")
        thread_emails = get_emails_by_thread(thread_id)
        # thread_emails.sort(key=lambda e: e['timestamp'])
        thread_emails.sort(key=lambda e: parse_datetime_safe(e.get('receivedDateTime', '')))
        full_thread_text = "\n\n".join(email.get('bodyPreview', '') for email in thread_emails)
        logger.info(f"full_thread_text: {full_thread_text}")

        if not full_thread_text.strip():
            logger.warning(f"Thread {thread_id} has no content.")
            continue

        agent_response = invoke_bedrock_agent(full_thread_text)
        logger.info(f"Agent response for thread {thread_id}: {agent_response}")

        if not agent_response or "not relevant" in agent_response.lower():
            logger.info(f"Thread {thread_id} marked as not relevant. Skipping.")
            continue

        # mark_emails_processed(thread_emails)
        # logger.info(f"Marked thread {thread_id} emails as processed.")

        results.append({
            "thread_id": thread_id,
            "agent_response": agent_response
        })

    logger.info(f"Completed processing. Total relevant threads: {len(results)}")
    return {
        "status": "completed",
        "processed_threads": len(results),
        "details": results
    }

def get_unique_unprocessed_thread_ids():
    response = table.scan(
        FilterExpression=Attr('processed').eq(False),
        ProjectionExpression='threadId'
    )
    thread_ids = {item['threadId'] for item in response['Items'] if 'threadId' in item}
    return list(thread_ids)

def get_emails_by_thread(thread_id):
    response = table.query(
        IndexName='threadId-index',  # Ensure GSI exists
        KeyConditionExpression=Key('threadId').eq(thread_id)
    )
    return response['Items']

def invoke_bedrock_agent(email_thread_text):
    try:
        logger.info("Invoking Bedrock agent...")
        response = bedrock_runtime.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId="email-session",
            inputText=(
                f"Here is an email thread. Identify if this is relevant to any known project. "
                f"If relevant, summarize it in a document-style format and update the Confluence page.\n\n"
                f"{email_thread_text}"
            )
        )
        # Response is a streaming object; you must read the text chunks
        full_response = ""
        for event in response['completion']:
            if "chunk" in event and "bytes" in event["chunk"]:
                full_response += event["chunk"]["bytes"].decode("utf-8")

        return full_response or "No text response from agent"
    except Exception as e:
        logger.error(f"Agent invocation failed: {str(e)}")
        return None

def mark_emails_processed(emails):
    for email in emails:
        try:
            table.update_item(
                Key={'email_id': email['email_id']},
                UpdateExpression="SET processed = :val",
                ExpressionAttributeValues={':val': True}
            )
        except Exception as e:
            logger.error(f"Failed to mark email {email['email_id']} as processed: {str(e)}")

def parse_datetime_safe(date_str):
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    except Exception as e:
        logger.warning(f"Could not parse date: {date_str} — {str(e)}")
        return datetime.min  # fallback for sorting