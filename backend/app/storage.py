"""
Vector store management using Chroma.
Handles document storage and retrieval.
"""

import os
import logging
from typing import List, Optional

# MUST set this BEFORE importing chromadb to disable telemetry
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

import chromadb

# Monkey patch to completely silence telemetry errors
try:
    import chromadb.telemetry.product.posthog
    original_capture = chromadb.telemetry.product.posthog.Posthog.capture
    def silent_capture(self, *args, **kwargs):
        pass
    chromadb.telemetry.product.posthog.Posthog.capture = silent_capture
except Exception:
    pass  # Silently ignore if structure changed

from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from app.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector storage and retrieval using Chroma."""
    
    def __init__(self):
        """Initialize vector store."""
        self.embeddings = self._initialize_embeddings()
        self.vector_store = None
        self._initialize_vector_store()
    
    def _initialize_embeddings(self):
        """Initialize embedding model based on configuration."""
        if settings.EMBEDDING_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set")
            
            logger.info(f"Initializing OpenAI embeddings: {settings.OPENAI_EMBEDDING_MODEL}")
            return OpenAIEmbeddings(
                model=settings.OPENAI_EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
            )
        elif settings.EMBEDDING_PROVIDER == "azure":
            if not settings.AZURE_OPENAI_API_KEY:
                raise ValueError("AZURE_OPENAI_API_KEY not set")
            
            from langchain_openai import AzureOpenAIEmbeddings
            logger.info(f"Initializing Azure OpenAI embeddings: {settings.AZURE_EMBEDDING_DEPLOYMENT}")
            return AzureOpenAIEmbeddings(
                azure_deployment=settings.AZURE_EMBEDDING_DEPLOYMENT,
                openai_api_key=settings.AZURE_OPENAI_API_KEY,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_version=settings.AZURE_OPENAI_API_VERSION,
            )
        elif settings.EMBEDDING_PROVIDER == "huggingface":
            # Use free local HuggingFace embeddings
            from langchain_huggingface import HuggingFaceEmbeddings
            logger.info("Initializing HuggingFace embeddings (sentence-transformers/all-MiniLM-L6-v2)")
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {settings.EMBEDDING_PROVIDER}")
    
    def _initialize_vector_store(self):
        """Initialize or load existing vector store."""
        logger.info(f"Initializing Chroma vector store at: {settings.CHROMA_PERSIST_DIRECTORY}")
        
        # Create settings to disable telemetry
        chroma_settings = ChromaSettings(
            anonymized_telemetry=False,
            allow_reset=True,
        )
        
        # Create persistent Chroma client with telemetry disabled
        chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=chroma_settings,
        )
        
        # Initialize LangChain Chroma wrapper
        self.vector_store = Chroma(
            client=chroma_client,
            collection_name=settings.COLLECTION_NAME,
            embedding_function=self.embeddings,
        )
        
        logger.info("Vector store initialized successfully")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            List of document IDs
        """
        if not documents:
            logger.warning("No documents to add")
            return []
        
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        # Add documents (Chroma handles deduplication by ID)
        ids = self.vector_store.add_documents(documents)
        
        logger.info(f"Successfully added {len(ids)} documents")
        return ids
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[dict] = None
    ) -> List[Document]:
        """
        Perform similarity search.
        
        Args:
            query: Query text
            k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of similar documents
        """
        logger.info(f"Performing similarity search for query: '{query[:100]}...'")
        
        results = self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter_dict,
        )
        
        logger.info(f"Retrieved {len(results)} similar documents")
        return results
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[dict] = None
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores.
        
        Args:
            query: Query text
            k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of (document, score) tuples
        """
        logger.info(f"Performing similarity search with scores for query: '{query[:100]}...'")
        
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter_dict,
        )
        
        logger.info(f"Retrieved {len(results)} documents with scores")
        return results
    
    def get_document_count(self) -> int:
        """Get total number of documents in the vector store."""
        try:
            collection = self.vector_store._collection
            count = collection.count()
            return count
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def delete_collection(self):
        """Delete the entire collection."""
        logger.warning(f"Deleting collection: {settings.COLLECTION_NAME}")
        self.vector_store.delete_collection()
        self._initialize_vector_store()


# Global vector store instance
vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create the global vector store instance."""
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store
