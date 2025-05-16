import boto3
import json
import logging
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Lambda invoked with event: %s", json.dumps(event))

    # Support both standard Lambda and Bedrock Agent action groups
    if "input" in event:
        input_data = event["input"]
        logger.info("Extracted input from event['input']")
    else:
        input_data = event
        logger.info("Using event as input")

    topic_name = "memora-notify-topic"
    page_title = input_data.get("pageTitle", "Untitled Page")
    page_id = input_data.get("pageId", "unknown")
    page_url = input_data.get("url", "")
    email = input_data.get("email", "")

    logger.info("Parsed input data - pageTitle: %s, pageId: %s, url: %s, email: %s",
                page_title, page_id, page_url, email)

    sns = boto3.client("sns")
    try:
        # Create or get SNS topic
        topic_response = sns.create_topic(Name=topic_name)
        topic_arn = topic_response["TopicArn"]
        logger.info("SNS topic created or fetched: %s", topic_arn)

        # Construct message
        message = {
            "pageTitle": page_title,
            "pageId": page_id,
            "url": page_url,
            "email": email
        }
        logger.info("Constructed message: %s", json.dumps(message))

        # Publish to SNS
        publish_response = sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            Subject=f"Confluence Page Created: {page_title}"
        )
        logger.info("SNS publish response: %s", json.dumps(publish_response))

        # Construct Bedrock agent-compatible response
        response_body = {
            'TEXT': {
                'body': "Notification sent successfully"
            }
        }

        function_response = {
            'actionGroup': event.get('actionGroup', 'NotifyPageUpdate'),
            'function': event.get('function', 'lambda_handler'),
            'functionResponse': {
                'responseBody': response_body
            }
        }

        action_response = {
            'messageVersion': '1.0',
            'response': function_response,
            'sessionAttributes': event.get('sessionAttributes', {}),
            'promptSessionAttributes': event.get('promptSessionAttributes', {})
        }

        return action_response

    except Exception as e:
        logger.error("Error occurred: %s", str(e), exc_info=True)

        response_body = {
            'TEXT': {
                'body': f"Failed to publish page '{page_title}'. Error: {str(e)}"
            }
        }

        function_response = {
            'actionGroup': event.get('actionGroup', 'NotifyPageUpdate'),
            'function': event.get('function', 'lambda_handler'),
            'functionResponse': {
                'responseBody': response_body
            }
        }

        action_response = {
            'messageVersion': '1.0',
            'response': function_response,
            'sessionAttributes': event.get('sessionAttributes', {}),
            'promptSessionAttributes': event.get('promptSessionAttributes', {})
        }

        return action_response
