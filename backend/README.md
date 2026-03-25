# Leadership Insights Agent - Backend

Backend API for the Leadership Insights AI Agent, built with FastAPI and Microsoft Agent Framework.

## 📋 Overview

This backend service provides AI-powered leadership insights through document processing and intelligent chat capabilities. It uses Azure OpenAI for embeddings and agent-based interactions, with support for PDF document parsing.

## ✨ Features

- **Document Processing**: Upload and parse PDF
- **AI-Powered Chat**: Interact with an intelligent agent for leadership insights
- **Embeddings Generation**: Create vector embeddings for document chunks

## 🛠️ Prerequisites

- **Python 3.12** (Required - the `unstructured` package for PDF parsing only supports Python 3.12, not the LTS version)
- pip (Python package manager)
- Azure OpenAI account with API access

> ⚠️ **Important**: This project requires Python 3.12 specifically due to compatibility requirements with the `unstructured[pdf]` package used for document parsing. Other Python versions are not supported.

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
cd c:\Users\Dharahas H\Kicks\Projects\LeadershipInsightsAgent\backend
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install fastapi uvicorn pypdf2 python-docx opentelemetry-exporter-otlp-proto-grpc numpy httpx agent-framework-core "unstructured[pdf]"
```

Or install from the requirements file (if you create one):
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Then edit `.env` with your configuration:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Azure AI Model Configuration
AZURE_OPENAI_KEY=your-azure-key-here
AZURE_OPENAI_BASE_URL=your-azure-endpoint-here
AZURE_API_VERSION=your-azure-api-version

# OR (Either Use Azure or OpenAI for base models)

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=your-openai-base-url (optional)

# Model Configuration (Required for both Azure and OpenAI)
OPENAI_MODEL_NAME=gpt-4
EMBEDDING_MODEL_NAME=text-embedding-3-small
```

**Configuration Options:**

You can use **either Azure OpenAI or OpenAI** (not both):

**Option 1: Azure OpenAI** (Required variables)
- `AZURE_OPENAI_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_BASE_URL`: Your Azure OpenAI endpoint URL (e.g., https://your-resource.openai.azure.com)
- `AZURE_API_VERSION`: API version (optional, e.g., 2024-02-15-preview)

**Option 2: OpenAI** (Required variables)
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_BASE_URL`: Custom OpenAI base URL (optional, for proxies or compatible services)

**Common Configuration** (Required for both)
- `OPENAI_MODEL_NAME`: Model name or deployment name for chat (e.g., gpt-4, gpt-3.5-turbo)
- `EMBEDDING_MODEL_NAME`: Model name for embeddings (e.g., text-embedding-3-small, text-embedding-ada-002)

**API Configuration** (Optional)
- `API_HOST`: Host to bind the API server (default: 0.0.0.0)
- `API_PORT`: Port for the API server (default: 8000)
## 🏃 Running the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Document Management

- `POST /api/document/upload` - Upload and process documents
- `GET /api/document/list` - List all uploaded documents
- `GET /api/document/{document_id}` - Get document details
- `DELETE /api/document/{document_id}` - Delete a document

### Chat

- `POST /api/chat` - Send a message to the AI agent
- `GET /api/chat/history` - Retrieve chat history

## 📁 Project Structure

```
backend/
├── app/
│   ├── agent/
│   │   ├── insights_agent.py    # AI agent implementation
│   │   └── tools.py              # Agent tools and utilities
│   ├── routers/
│   │   ├── chat.py               # Chat endpoints
│   │   └── document.py           # Document endpoints
│   ├── services/
│   │   ├── chunkingService.py    # Document chunking logic
│   │   ├── documentService.py    # Document management
│   │   ├── embeddingService.py   # Embedding generation
│   │   └── parsingService.py     # PDF/DOCX parsing
│   ├── clients.py                # External API clients
│   ├── config.py                 # Configuration settings
│   └── constants.py              # Application constants
├── uploads/                      # Uploaded files storage
├── main.py                       # Application entry point
├── pyproject.toml               # Project dependencies
└── README.md                     # This file
```


## 🐛 Troubleshooting

### Common Issues

**1. Python Version Error**
```
Error: Package 'unstructured' requires Python 3.12
```
**Solution:** Ensure you're using Python 3.12 specifically. Check your version:
```bash
python --version  # Should show Python 3.12.x
```
If you have multiple Python versions installed, use:
```bash
py -3.12 -m venv venv  # Windows
python3.12 -m venv venv  # macOS/Linux
```

**2. Import Errors**
```bash
# Ensure all dependencies are installed
pip install --upgrade pip
pip install -r requirements.txt
```

**3. Azure OpenAI or OpenAI Connection Issues**
- Verify your `.env` file has correct credentials
- Ensure you've configured either Azure OpenAI OR OpenAI (not both)
- For Azure: Check that your Azure OpenAI resource is active and API key has proper permissions
- For OpenAI: Verify your API key is valid and has sufficient credits

**4. File Upload Issues**
- Ensure the `uploads` directory exists and has write permissions
- Check file size limits (default: 10MB)

**5. Port Already in Use**
```bash
# Change the API_PORT in .env or run with a different port
API_PORT="8001"
```

**6. Model Configuration Issues**
- Ensure `OPENAI_MODEL_NAME` and `EMBEDDING_MODEL_NAME` are set correctly
- For Azure: Use your deployment names (not model names)
- For OpenAI: Use model names like `gpt-4`, `gpt-3.5-turbo`, `text-embedding-3-small`

## 📦 Dependencies

Core dependencies:
- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Agent Framework**: Microsoft Agent Framework for AI agents
- **OpenAI**: Azure OpenAI integration
- **Unstructured**: Document parsing
- **PyPDF2**: PDF processing
- **python-docx**: DOCX processing
- **OpenTelemetry**: Observability and tracing

## 👥 Contributors

- Dharahas
