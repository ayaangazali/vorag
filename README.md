# VoRAG - Voice RAG Web Application

A full-stack Voice RAG (Retrieval-Augmented Generation) application with web scraping, vector storage, and AI-powered question answering.

## 🏗️ Project Structure

```
vorag/
├── frontend/          # Next.js frontend application
│   ├── app/          # Next.js app directory
│   ├── components/   # React components
│   ├── package.json  # Frontend dependencies
│   └── COMPONENTS.md # Frontend documentation
│
├── backend/          # FastAPI backend application
│   ├── app/         # Python application code
│   ├── data/        # Vector store data (auto-generated)
│   ├── requirements.txt
│   └── README.md    # Backend API documentation
│
├── .venv/           # Python virtual environment (shared)
└── README.md        # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **API Keys**:
  - Apify (for web scraping)
  - Anthropic (for Claude LLM)
  - Azure OpenAI (for embeddings)

### 1. Setup Backend

```bash
# Navigate to backend
cd backend

# Install dependencies (uses .venv in root)
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Backend will run at: **http://localhost:8000**
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. Setup Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at: **http://localhost:3000**

## 📚 Documentation

- **Backend**: See [backend/README.md](backend/README.md) for API documentation
- **Frontend**: See [frontend/COMPONENTS.md](frontend/COMPONENTS.md) for component documentation

## 🔑 Environment Variables

### Backend (.env in backend/)

```bash
# Required
APIFY_TOKEN=your_apify_token
ANTHROPIC_API_KEY=your_anthropic_key
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# Optional (has defaults)
EMBEDDING_PROVIDER=azure
LLM_PROVIDER=anthropic
```

## 🛠️ Development Workflow

### Running Both Services

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Making Changes

- **Frontend changes**: Hot reload is automatic
- **Backend changes**: Uvicorn auto-reloads on file changes

## 📖 Usage

1. **Start both servers** (backend and frontend)
2. **Open frontend** at http://localhost:3000
3. **Ingest content**:
   - Use the `/ingest` API endpoint to scrape a URL
   - Backend will scrape, chunk, and index the content
4. **Ask questions**:
   - Type questions in the chat interface
   - Get AI-powered answers from Claude with sources

## 🎨 Features

### Frontend
- 🎨 **Glassmorphic UI**: Modern light mode with glass effects
- 💬 **Chat Interface**: Dynamic bubble textarea with animations
- ⚡ **Real-time**: Smooth animations and transitions
- 📱 **Responsive**: Works on all devices

### Backend
- 🌐 **Web Scraping**: Apify integration for content extraction
- 🔍 **Vector Search**: Chroma for semantic search
- 🤖 **RAG Pipeline**: Claude + Azure OpenAI embeddings
- 🚀 **FastAPI**: High-performance async API
- 📊 **Job Tracking**: Background ingestion with status updates

## 🏭 Production Deployment

### Backend

```bash
# Use gunicorn with uvicorn workers
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
# Build for production
cd frontend
npm run build
npm start
```

## 📄 License

MIT

## 🔗 Quick Links

- **Apify Console**: https://console.apify.com
- **Anthropic Console**: https://console.anthropic.com
- **Azure Portal**: https://portal.azure.com
