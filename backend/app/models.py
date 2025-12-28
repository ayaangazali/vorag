"""
Pydantic models for API requests and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    SCRAPING = "scraping"
    PROCESSING = "processing"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestRequest(BaseModel):
    """Request to start ingestion job."""
    url: Optional[str] = Field(None, description="URL to scrape (uses default if not provided)")
    force_refresh: bool = Field(False, description="Force re-scraping even if URL already indexed")


class IngestResponse(BaseModel):
    """Response from starting ingestion."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Human-readable message")


class JobStatusResponse(BaseModel):
    """Job status response."""
    job_id: str
    status: JobStatus
    step: str = Field(..., description="Current processing step")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    error: Optional[str] = Field(None, description="Error message if failed")
    started_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    """Request to query the RAG system."""
    question: str = Field(..., min_length=1, description="Question to answer")
    top_k: int = Field(5, ge=1, le=20, description="Number of context chunks to retrieve")


class SourceDocument(BaseModel):
    """Retrieved source document."""
    title: str = Field(..., description="Document title")
    url: str = Field(..., description="Source URL")
    snippet: str = Field(..., description="Relevant text snippet")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")


class QueryResponse(BaseModel):
    """Response from RAG query."""
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents used")
    query_time_ms: float = Field(..., description="Query processing time in milliseconds")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    vector_store_initialized: bool = Field(..., description="Whether vector store is ready")
    document_count: int = Field(..., description="Number of indexed documents")
