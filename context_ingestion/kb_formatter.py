import json
import boto3

s3 = boto3.client("s3")

def chunk_and_store(pages, bucket, prefix):
    for page in pages:
        text = page["body"]
        chunks = [text[i:i+800] for i in range(0, len(text), 800)]

        records = []
        for chunk in chunks:
            records.append({
                "text": chunk,
                "metadata": {
                    "url": page["url"],
                    "page_id": page["page_id"],
                    "title": page["title"]
                }
            })

        filename = f"{prefix}/page-{page['page_id']}.jsonl"
        file_content = "\n".join([json.dumps(r) for r in records])
        s3.put_object(Bucket=bucket, Key=filename, Body=file_content.encode("utf-8"))
