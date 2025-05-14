# chunker.py

import json
import logging
import boto3
from bs4 import BeautifulSoup
import tiktoken

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
enc = tiktoken.encoding_for_model("text-embedding-3-small")
MAX_TOKENS = 300

def get_token_count(text):
    return len(enc.encode(text))

def clean_text(html):
    return BeautifulSoup(html, "html.parser")

def split_text_by_tokens(text, section_header, base_metadata, chunk_id_base, chunk_counter):
    tokens = enc.encode(text)
    chunks = []
    i = 0
    while i < len(tokens):
        sub_tokens = tokens[i:i + MAX_TOKENS]
        sub_text = enc.decode(sub_tokens)
        chunk_id = f"{chunk_id_base}-{chunk_counter:03d}"
        chunk = {
            "chunkId": chunk_id,
            "pageId": base_metadata["page_id"],
            "pageTitle": base_metadata["title"],
            "sectionHeader": section_header,
            "content": sub_text,
            "tokenCount": len(sub_tokens),
            "url": base_metadata["url"]
        }
        chunks.append(chunk)
        i += MAX_TOKENS
        chunk_counter += 1
    return chunks, chunk_counter

def chunk_html_content(page):
    html = page["text"]
    metadata = page["metadata"]
    soup = clean_text(html)
    logger.info(f"Processing page - clean_text: {clean_text}")

    chunks = []
    chunk_counter = 1
    section_header = ""
    buffer = ""
    chunk_id_base = metadata["page_id"]

    for elem in soup.descendants:
        if elem.name in ["h1", "h2"]:
            if buffer.strip():
                buffer_chunks, chunk_counter = split_text_by_tokens(
                    buffer.strip(), section_header, metadata, chunk_id_base, chunk_counter
                )
                chunks.extend(buffer_chunks)
                buffer = ""
            section_header = elem.get_text(strip=True)
        elif elem.name == "ul":
            list_text = "\n".join(li.get_text(strip=True) for li in elem.find_all("li"))
            buffer += "\n" + list_text + "\n"
        elif elem.name is None and isinstance(elem, str):
            buffer += elem.strip() + " "

    if buffer.strip():
        buffer_chunks, chunk_counter = split_text_by_tokens(
            buffer.strip(), section_header, metadata, chunk_id_base, chunk_counter
        )
        chunks.extend(buffer_chunks)

    return chunks

def chunk_and_store(pages, bucket, prefix):
    for page in pages:
        chunks = chunk_html_content(page)
        filename = f"{prefix.rstrip('/')}/chunks-{page['metadata']['page_id']}.jsonl"
        body = "\n".join(json.dumps(chunk) for chunk in chunks)
        s3.put_object(Bucket=bucket, Key=filename, Body=body.encode("utf-8"))
        logger.info(f"Stored {len(chunks)} chunks for page {page['metadata']['title']}")
