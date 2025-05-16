Memora AI

Memora AI is an agentic, serverless AI system that automatically processes Gmail conversations related to projects, classifies the content, summarizes it, and updates relevant Confluence pages. The system is designed for teams that want to keep documentation current with minimal manual effort.

Key Features

🧠 Agentic Intelligence: Powered by AWS Bedrock agents using Claude 3.5 Haiku, it performs task chaining such as classification, summarization, and documentation.

📥 Email Integration: Ingests emails from Gmail using the Gmail API.

🧾 Content Relevance & Classification: The agent identifies if a thread is relevant to a project. If it is, classifies it as BRD, Release Notes, Action Items, or Other.

📝 Confluence Updater: Formats summaries based on matching templates  and creates new confluence pages under the relavent Confluence pages.

📚 Knowledge Base (KB): Uses Confluence content and project-specific rules for contextual decision-making. Uses AWS Bedrock KB with Aurora serverless.

🛠 Fully Serverless and Infrastructure as Code (IaC) : Built using AWS SAM, with Lambda, DynamoDB, Aurora, S3, and Bedrock.

Architecture Overview

Gmail → Email Reader Lambda → DynamoDB → Email Orchestrator Lambda
                                            ↓
                                     Bedrock Agent ←→ Aurora DB (RAG Vector store)
                                            ↓
                               confluence-writer-function → Confluence Cloud

Repository Structure

MemoraAI/
├── confluence_content_ingestion/ # Lambda: Pushes KB content to S3
│   ├── src/
│   └── template.yaml
├── memora_core/                  # Core logic: RAG engine, Bedrock clients, utilities
│   └── email_reader/
|   └── email_orchestrator/
|   └── lambda_confluence_writer/
│   └── template.yaml
├── .gitignore                    # Specifies files to ignore in version control
└── README.md                     # Project documentation

Deployment

Make sure you have AWS SAM CLI installed and configured.

sam build
sam deploy --guided

memora_core and confluence_content_ingestion are to be deployed independently.

Environment Variables

Each Lambda expects certain environment variables like :

DDB_TABLE_NAME

CONFLUENCE_TOKEN_SECRET

GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, etc.

KB_ID, BEDROCK_AGENT_ID, etc.

AURORA_CONNECTION_STRING

Contributors

Ashish Palamkunnel Joseph

Anju Sebastian

License

This project is licensed under the MIT License.