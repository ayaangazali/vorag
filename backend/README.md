# VoRAG Backend

FastAPI backend for Voice RAG system with Apify web scraping, LangChain RAG, and Chroma vector storage.

## Features

- 🌐 **Web Scraping**: Uses Apify actors to scrape content from any URL
- 🔍 **Vector Search**: Chroma vector store with embeddings
- 🤖 **RAG Pipeline**: LangChain-powered retrieval with Claude (Anthropic) for generation
- 🚀 **FastAPI**: High-performance async API with automatic docs
- 📊 **Job Tracking**: Background ingestion with status tracking

**Note**: Currently uses OpenAI for embeddings (as Anthropic doesn't provide embeddings API yet) and Claude for LLM.

## Architecture

```
┌─────────────┐
│  Frontend   │
│  (Next.js)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌────────────────────────────────┐ │
│  │  POST /ingest                  │ │
│  │  GET  /ingest/{id}/status      │ │
│  │  POST /query                   │ │
│  │  GET  /health                  │ │
│  └────────────────────────────────┘ │
└───┬─────────────────────────────┬───┘
    │                             │
    ▼                             ▼
┌───────────┐              ┌──────────────┐
│   Apify   │              │   Chroma     │
│  Scraper  │              │ Vector Store │
└───────────┘              └──────────────┘
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys:
# - APIFY_TOKEN: Get from https://console.apify.com/account/integrations
# - ANTHROPIC_API_KEY: Get from https://console.anthropic.com/settings/keys (for Claude)
# - AZURE_OPENAI_API_KEY: Get from Azure Portal -> Your OpenAI Resource
# - AZURE_OPENAI_ENDPOINT: Your Azure OpenAI endpoint URL
# - AZURE_EMBEDDING_DEPLOYMENT: Your embedding model deployment name (e.g., text-embedding-ada-002)
```

### 3. Run Server

```bash
# Easy way - just run main.py
python3 main.py

# Or use uvicorn directly
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 📥 POST /ingest

Start a background job to scrape and index content from a URL.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Ingestion job started"
}
```

### 📊 GET /ingest/{job_id}/status

Get the status of an ingestion job.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "message": "Ingestion completed successfully",
  "created_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:32:15",
  "result": {
    "documents_scraped": 45,
    "chunks_created": 230,
    "chunks_indexed": 230,
    "elapsed_time": 135.2
  }
}
```

Job statuses: `pending` → `processing` → `completed` / `failed`

### 💬 POST /query

Query the RAG system with a question.

**Request:**
```json
{
  "query": "What is the investment strategy?",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "What is the investment strategy?",
  "answer": "Based on the documents, the investment strategy focuses on...",
  "sources": [
    {
      "title": "Investment Strategy",
      "url": "https://example.com/strategy",
      "snippet": "Our investment approach...",
      "score": 0.89
    }
  ],
  "query_time_ms": 1250.5
}
```

### 🏥 GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "vector_store_docs": 230
}
```

## Configuration

All configuration is done via environment variables in `.env`:

### Apify Settings

- `APIFY_TOKEN`: Your Apify API token (required)
- `APIFY_ACTOR_NAME`: Actor to use for scraping (default: `apify/website-content-crawler`)
  - Options: `apify/website-content-crawler`, `apify/web-scraper`

### Azure OpenAI Settings (Recommended)

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI key (required)
- `AZURE_OPENAI_ENDPOINT`: Your Azure endpoint (e.g., `https://your-resource.openai.azure.com/`)
- `AZURE_OPENAI_API_VERSION`: API version (default: `2024-02-15-preview`)
- `AZURE_EMBEDDING_DEPLOYMENT`: Your embedding deployment name (e.g., `text-embedding-ada-002`)
- `AZURE_LLM_DEPLOYMENT`: Your LLM deployment name if using Azure for LLM (e.g., `gpt-4`)

Set `EMBEDDING_PROVIDER=azure` to use Azure OpenAI for embeddings.

### OpenAI Settings (Alternative)

If you prefer regular OpenAI instead of Azure:

```bash
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-...your_key...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### Anthropic Settings

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required for Claude LLM)
- `ANTHROPIC_MODEL`: Claude model (default: `claude-3-5-sonnet-20241022`)
  - Options: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`
- `ANTHROPIC_TEMPERATURE`: LLM temperature (default: `0.7`)
- `ANTHROPIC_MAX_TOKENS`: Max tokens to generate (default: `4096`)

### Alternative LLM Providers

If you prefer Azure OpenAI or OpenAI instead of Claude for the LLM:

**Azure OpenAI:**
```bash
LLM_PROVIDER=azure
AZURE_LLM_DEPLOYMENT=gpt-4
```

**OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_LLM_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
```

### Azure OpenAI (Optional)

If using Azure instead of OpenAI:

```bash
EMBEDDING_PROVIDER=azure
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_LLM_DEPLOYMENT=gpt-35-turbo
```

### Chunking Settings

- `CHUNK_SIZE`: Text chunk size in characters (default: `1000`)
- `CHUNK_OVERLAP`: Overlap between chunks (default: `200`)
- `MAX_CONTEXT_LENGTH`: Max context length for LLM (default: `8000`)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and endpoints
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic models
│   ├── apify_client.py      # Apify scraping client
│   ├── storage.py           # Vector store wrapper
│   ├── ingest.py            # Ingestion pipeline
│   └── rag.py               # RAG query system
├── data/
│   └── chroma/              # Chroma vector store (auto-created)
├── requirements.txt
├── .env.example
└── README.md
```

## Development

### View Logs

The application logs all operations:

```bash
# Run with logs
uvicorn app.main:app --reload --log-level info
```

### Test API

Use the interactive docs:
1. Go to http://localhost:8000/docs
2. Try the endpoints with the "Try it out" button

Or use curl:

```bash
# Health check
curl http://localhost:8000/health

# Start ingestion
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.kamcoinvest.com/fund/kamco-investment-fund"}'

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this fund about?"}'
```

### Clear Vector Store

To reset the vector store:

```bash
rm -rf backend/data/chroma
```

## Troubleshooting

### "APIFY_TOKEN not set" Error

Make sure you've created a `.env` file and added your Apify token:

```bash
cp .env.example .env
# Edit .env and add APIFY_TOKEN=your_token_here
```

### "OPENAI_API_KEY not set" Error

Add your OpenAI API key to `.env` (needed for embeddings):

```bash
OPENAI_API_KEY=sk-...your_key_here...
```

### "ANTHROPIC_API_KEY not set" Error

Add your Anthropic API key to `.env` (needed for Claude LLM):

```bash
ANTHROPIC_API_KEY=sk-ant-...your_key_here...
```

### Import Errors

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Port Already in Use

If port 8000 is already in use, run on a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

## Production Deployment

For production:

1. **Use a proper database** for job tracking (replace in-memory dict)
2. **Add authentication** to protect endpoints
3. **Set up Redis** for caching and job queues
4. **Use environment-specific configs**
5. **Add monitoring** (e.g., Sentry, Datadog)
6. **Deploy with Docker**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## License

MIT
