"""
Ingestion pipeline for scraping, chunking, and indexing content.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Callable
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config import settings
from app.apify_client import ApifyScraper
from app.brightdata_client import BrightDataScraper
from app.storage import get_vector_store

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Handles the complete ingestion workflow: scrape → chunk → embed → index."""
    
    def __init__(self):
        """Initialize ingestion components."""
        # Select scraper based on configuration
        if settings.SCRAPER_PROVIDER == "brightdata":
            logger.info("Using Bright Data scraper")
            self.scraper = BrightDataScraper()
        else:
            logger.info("Using Apify scraper")
            self.scraper = ApifyScraper()
            
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        logger.info(f"Ingestion pipeline initialized (scraper={settings.SCRAPER_PROVIDER}, chunk_size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP})")
    
    def run(self, url: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Run the complete ingestion pipeline.
        
        Args:
            url: URL to scrape
            progress_callback: Optional callback function for progress updates (takes message: str)
            
        Returns:
            Dict with ingestion statistics
        """
        start_time = time.time()
        logger.info(f"🚀 Starting ingestion pipeline for: {url}")
        
        try:
            # Step 1: Scrape with configured scraper
            if progress_callback:
                progress_callback(f"Starting {settings.SCRAPER_PROVIDER} scrape...")
            
            logger.info(f"📥 Step 1/4: Scraping website with {settings.SCRAPER_PROVIDER}...")
            scraped_docs = self.scraper.scrape_url(url, max_pages=10)
            
            if not scraped_docs:
                raise ValueError(f"No content scraped from {url}")
            
            logger.info(f"✅ Scraped {len(scraped_docs)} pages")
            
            # Step 2: Chunk the documents
            if progress_callback:
                progress_callback(f"Chunking {len(scraped_docs)} documents...")
            
            logger.info("✂️  Step 2/4: Chunking documents...")
            chunks = self._chunk_documents(scraped_docs)
            logger.info(f"✅ Created {len(chunks)} chunks")
            
            # Step 3: Add to vector store (embeds automatically)
            if progress_callback:
                progress_callback(f"Creating embeddings for {len(chunks)} chunks...")
            
            logger.info("🧮 Step 3/4: Creating embeddings...")
            vector_store = get_vector_store()
            
            if progress_callback:
                progress_callback("Indexing into vector store...")
            
            logger.info("💾 Step 4/4: Indexing into vector store...")
            doc_ids = vector_store.add_documents(chunks)
            
            elapsed_time = time.time() - start_time
            
            result = {
                "documents_scraped": len(scraped_docs),
                "chunks_created": len(chunks),
                "chunks_indexed": len(doc_ids),
                "elapsed_time": f"{elapsed_time:.2f}s",
            }
            
            logger.info(f"✨ Ingestion completed successfully!")
            logger.info(f"   📄 Documents scraped: {result['documents_scraped']}")
            logger.info(f"   ✂️  Chunks created: {result['chunks_created']}")
            logger.info(f"   💾 Chunks indexed: {result['chunks_indexed']}")
            logger.info(f"   ⏱️  Time: {result['elapsed_time']}")
            
            return result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"❌ Ingestion failed after {elapsed_time:.2f}s: {str(e)}", exc_info=True)
            raise
    
    def _chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Document]:
        """
        Convert raw scraped documents to LangChain Document chunks.
        
        Args:
            documents: List of scraped documents with 'text', 'url', 'title'
            
        Returns:
            List of LangChain Document objects
        """
        logger.info(f"Chunking {len(documents)} documents...")
        
        all_chunks = []
        
        for doc in documents:
            text = doc.get("text", "")
            if not text or len(text.strip()) < 100:
                continue
            
            # Create a LangChain Document
            langchain_doc = Document(
                page_content=text,
                metadata={
                    "source": doc.get("url", "unknown"),
                    "title": doc.get("title", "Untitled"),
                    "crawled_at": doc.get("crawled_at", ""),
                }
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([langchain_doc])
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks

    
    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing noise and normalizing whitespace.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove common noise patterns
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common navigation text
        noise_patterns = [
            r'cookie (policy|notice|consent)',
            r'accept (all )?cookies',
            r'privacy policy',
            r'terms (of|and) (service|conditions)',
            r'all rights reserved',
            r'copyright \d{4}',
            r'skip to (main )?content',
            r'(sign in|log in|register)',
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace again
        text = ' '.join(text.split())
        
        return text.strip()
