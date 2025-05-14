# 🧠 ConfluenceContentIngestionFunction

This AWS Lambda function ingests Confluence pages, chunks them intelligently, and stores the structured data in an S3 bucket for use in downstream AI pipelines like **MemoraAI**.

---

## 📌 Features

- Connects to Confluence Cloud using API token
- Fetches all pages and extracts rich HTML content
- Chunks content by logical HTML tags (`<h1>`, `<h2>`, `<ul>`)
- Retains section headers and page metadata (title, pageId, URL)
- Token-limits each chunk for compatibility with LLM embeddings
- Uploads `.jsonl` chunks to the specified S3 bucket

---

## 🛠️ Technologies

- AWS Lambda (Python 3.11)
- AWS SAM (for packaging & deployment)
- Boto3
- BeautifulSoup4
- `tiktoken` for token-aware chunking
- Confluence REST API

---

## 🚀 Deployment (via AWS SAM)

### 1. Install dependencies

```bash
pip install -r requirements.txt -t src/
```

### 2. Build the project

```bash
sam build
```

*(Optional for Linux dependencies like `tiktoken`:)*  
```bash
sam build --use-container
```

### 3. Deploy to AWS

```bash
sam deploy --guided
```

Follow the prompts to set stack name, region, and environment variables.

---

## ⚙️ Required Environment Variables

Set these in `template.yaml` or AWS Console:

| Variable              | Description                         |
|-----------------------|-------------------------------------|
| `confluence_base_url` | Base URL with `/wiki`, e.g. `https://yourdomain.atlassian.net/wiki` |
| `confluence_email`    | Atlassian account email             |
| `CONFLUENCE_TOKEN`    | Confluence API token                |
| `S3_BUCKET`           | Target S3 bucket for storing chunks |
| `S3_PREFIX`           | Prefix (folder) in S3 to store `.jsonl` files |

---

## 🧪 Sample Output (S3 JSONL)

Each chunk will look like:

```json
{
  "chunkId": "123456-001",
  "pageId": "123456",
  "pageTitle": "Release Notes – Memora AI",
  "sectionHeader": "1. Overview",
  "content": "Memora AI is a serverless platform...",
  "tokenCount": 87,
  "url": "https://yourdomain.atlassian.net/wiki/pages/viewpage.action?pageId=123456"
}
```

---

## 🐛 Troubleshooting

- **403 from Confluence**: Check if API token is valid and email matches Atlassian ID.
- **Token limit errors**: Chunk size is capped at 300 tokens using `tiktoken`.
- **Docker issues on Windows**: Use `sam build` without `--use-container`, or build layers separately.

---

## 📂 Project Structure

```
src/
├── app.py                # Lambda handler
├── confluence_client.py  # Fetches pages from Confluence
├── kb_formatter.py       # HTML cleaner, chunker, and S3 writer
├── requirements.txt
template.yaml             # SAM template
README.md
```

---

## 📄 License

MIT License

---

## 👥 Maintainers

Ashish Joseph  
[https://github.com/ashipj](https://github.com/ashipj)
