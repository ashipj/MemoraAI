import boto3
import json

def lambda_handler(event, context):
    # Support both standard Lambda and Bedrock Agent action groups
    if "input" in event:
        input_data = event["input"]
    else:
        input_data = event

    topic_name = input_data.get("topicName", "memora-notify-topic")
    page_title = input_data.get("pageTitle", "Untitled Page")
    page_id = input_data.get("pageId", "unknown")
    page_url = input_data.get("url", "")
    email = input_data.get("email", "")

    sns = boto3.client("sns")
    try:
        # Create or get SNS topic
        topic_response = sns.create_topic(Name=topic_name)
        topic_arn = topic_response["TopicArn"]

        # Construct message
        message = {
            "pageTitle": page_title,
            "pageId": page_id,
            "url": page_url,
            "email": email
        }

        # Publish to SNS
        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            Subject=f"Confluence Page Created: {page_title}"
        )

        return {
            "status": "success",
            "topicArn": topic_arn,
            "messageSent": message
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
