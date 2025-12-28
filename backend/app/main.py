"""
FastAPI application for RAG backend.
Provides endpoints for ingestion, querying, and health checks.
"""

import logging
import uuid
from typing import Dict
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import (
    IngestRequest,
    IngestResponse,
    JobStatusResponse,
    JobStatus,
    QueryRequest,
    QueryResponse,
    HealthResponse,
)
from app.ingest import IngestionPipeline
from app.rag import get_rag_system

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Job tracking (in-memory store)
# In production, use Redis or a database
jobs: Dict[str, Dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Starting VoRAG backend...")
    logger.info(f"Apify Actor: {settings.APIFY_ACTOR_NAME}")
    logger.info(f"Embedding Provider: {settings.EMBEDDING_PROVIDER}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    
    # Initialize RAG system on startup
    try:
        get_rag_system()
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {str(e)}")
    
    yield
    
    logger.info("Shutting down VoRAG backend...")


# Create FastAPI app
app = FastAPI(
    title="VoRAG Backend",
    description="Backend API for Voice RAG with Apify scraping and LangChain",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],  # Next.js frontend (multiple ports)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from app.storage import get_vector_store
    
    try:
        vector_store = get_vector_store()
        doc_count = vector_store.get_document_count()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            vector_store_initialized=True,
            document_count=doc_count,
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            vector_store_initialized=False,
            document_count=0,
        )


def run_ingestion_job(job_id: str, url: str):
    """
    Run ingestion job in background.
    
    Args:
        job_id: Job identifier
        url: URL to scrape
    """
    logger.info(f"Starting ingestion job {job_id} for URL: {url}")
    
    # Update job status
    jobs[job_id]["status"] = JobStatus.PROCESSING
    jobs[job_id]["message"] = "Scraping content..."
    
    def update_progress(message: str):
        """Update job progress."""
        jobs[job_id]["message"] = message
        logger.info(f"Job {job_id}: {message}")
    
    try:
        # Run ingestion pipeline
        pipeline = IngestionPipeline()
        result = pipeline.run(url, progress_callback=update_progress)
        
        # Update job with results
        jobs[job_id]["status"] = JobStatus.COMPLETED
        jobs[job_id]["message"] = "Ingestion completed successfully"
        jobs[job_id]["result"] = {
            "documents_scraped": result["documents_scraped"],
            "chunks_created": result["chunks_created"],
            "chunks_indexed": result["chunks_indexed"],
            "elapsed_time": result["elapsed_time"],
        }
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Job {job_id} completed: {result['chunks_indexed']} chunks indexed")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}", exc_info=True)
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()


@app.post("/ingest", response_model=IngestResponse)
async def ingest_url(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Start ingestion job to scrape and index content from URL.
    
    Args:
        request: Ingestion request with URL
        background_tasks: FastAPI background tasks
        
    Returns:
        Job ID for tracking status
    """
    logger.info(f"Received ingestion request for URL: {request.url}")
    
    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "message": "Job queued",
        "url": request.url,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "result": None,
    }
    
    # Start background job
    background_tasks.add_task(run_ingestion_job, job_id, request.url)
    
    return IngestResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Ingestion job started",
    )


@app.get("/ingest/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of an ingestion job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status information
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = jobs[job_id]
    
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        step=job.get("step", "initializing"),
        progress=job.get("progress", 0.0),
        error=job.get("error"),
        started_at=job["created_at"],
        completed_at=job.get("completed_at"),
        metadata=job.get("metadata", {}),
    )


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system with a question.
    
    Args:
        request: Query request with question
        
    Returns:
        Answer and source documents
    """
    logger.info(f"Received query: '{request.question}'")
    
    try:
        # Get RAG system
        rag = get_rag_system()
        
        # Query
        result = rag.query(
            question=request.question,
            top_k=request.top_k or 5,
        )
        
        return QueryResponse(
            query=request.question,
            answer=result["answer"],
            sources=result["sources"],
            query_time_ms=result["query_time_ms"],
        )
        
    except Exception as e:
        logger.error(f"Query failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
