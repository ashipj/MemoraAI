# 🧠 Memora AI

Memora AI is an AI-powered assistant that automatically extracts key decisions, design changes, and action points from email conversations and updates your project documentation—such as Confluence pages—without manual intervention.

---

## 🚀 Features

- ⛅ **Serverless Architecture** using AWS Lambda & SAM
- 📧 **Email Ingestion** via Microsoft Outlook integration
- 🔍 **Semantic Understanding** using Amazon Bedrock (Claude / Titan)
- 🧠 **RAG Framework** to extract decisions & context
- 🗃️ **DynamoDB Storage** for short-term memory
- 📝 **Confluence API Integration** to update pages automatically
- 📈 **Tracing & Observability** using AWS X-Ray and OpenTelemetry (ADOT)

---

## 📁 Project Structure

```
memora-ai/
├── sam-template.yaml           # AWS SAM template for deploying infrastructure
├── email-reader/              # Lambda to read emails and store in DynamoDB
│   ├── app.js                 # Email fetcher logic using MS Graph API
│   └── utils.js               # Outlook auth and helper methods
├── decision-extractor/        # Lambda for extracting key decisions from email body
│   └── handler.js             # Claude prompt + RAG implementation
├── confluence-updater/        # Lambda to update Confluence pages
│   └── index.js               # REST API integration with Confluence
├── tracing/                   # OpenTelemetry setup
│   └── otel-config.js
├── scripts/                   # Utility scripts for local testing and data import
└── README.md                  # You are here
```

---

## 🛠️ Deployment

> This project uses **AWS SAM CLI** for deployment.

### Prerequisites

- AWS CLI configured (`aws configure`)
- AWS SAM CLI installed
- Microsoft Azure App Registration for Outlook access
- Confluence API token

### Deploy Steps

```bash
git clone https://github.com/ashipj/MemoraAI.git
cd MemoraAI
sam build
sam deploy --guided
```

---

## 🔐 Environment Variables

Each Lambda expects these values via environment variables (defined in `sam-template.yaml`):

### `email-reader`
- `OUTLOOK_CLIENT_ID`
- `OUTLOOK_CLIENT_SECRET`
- `OUTLOOK_TENANT_ID`
- `EMAIL_FOLDER_NAME` (e.g., Inbox)
- `DYNAMODB_TABLE_NAME`

### `decision-extractor`
- `BEDROCK_MODEL_ID` (e.g., `anthropic.claude-v2`)
- `DYNAMODB_TABLE_NAME`

### `confluence-updater`
- `CONFLUENCE_API_TOKEN`
- `CONFLUENCE_BASE_URL`
- `CONFLUENCE_PAGE_ID`

---

## 🧪 Local Testing

Use `sam local invoke` to test individual functions with sample events.

```bash
sam local invoke EmailReaderFunction --event events/sample-email.json
```

---

## 📊 Tracing & Observability

Integrated with AWS X-Ray and OpenTelemetry (ADOT). All Lambda invocations are traced end-to-end.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo and submit a pull request with a clear description of your changes.

---

## 👥 Contributors

- Ashish Joseph
- Anju Joseph

---

## 📄 License

MIT License © 2025 Ashish Joseph
