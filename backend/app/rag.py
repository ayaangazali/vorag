"""
RAG (Retrieval-Augmented Generation) query system.
Handles context retrieval and answer generation.
"""

import logging
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document

from app.config import settings
from app.storage import get_vector_store
from app.models import SourceDocument

logger = logging.getLogger(__name__)


class RAGSystem:
    """Handles RAG queries with context retrieval and generation."""
    
    def __init__(self):
        """Initialize RAG components."""
        self.llm = self._initialize_llm()
        self.vector_store = get_vector_store()
        logger.info("RAG system initialized")
    
    def _initialize_llm(self):
        """Initialize LLM based on configuration."""
        if settings.LLM_PROVIDER == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not set")
            
            from langchain_anthropic import ChatAnthropic
            logger.info(f"Initializing Anthropic Claude: {settings.ANTHROPIC_MODEL}")
            return ChatAnthropic(
                model=settings.ANTHROPIC_MODEL,
                temperature=settings.ANTHROPIC_TEMPERATURE,
                max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
            )
        elif settings.LLM_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set")
            
            logger.info(f"Initializing OpenAI LLM: {settings.OPENAI_LLM_MODEL}")
            return ChatOpenAI(
                model=settings.OPENAI_LLM_MODEL,
                temperature=settings.OPENAI_TEMPERATURE,
                openai_api_key=settings.OPENAI_API_KEY,
            )
        elif settings.LLM_PROVIDER == "azure":
            if not settings.AZURE_OPENAI_API_KEY:
                raise ValueError("AZURE_OPENAI_API_KEY not set")
            
            from langchain_openai import AzureChatOpenAI
            logger.info("Initializing Azure OpenAI LLM")
            return AzureChatOpenAI(
                azure_deployment=settings.AZURE_LLM_DEPLOYMENT,
                openai_api_key=settings.AZURE_OPENAI_API_KEY,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                temperature=settings.OPENAI_TEMPERATURE,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
    
    def query(self, question: str, top_k: int = 15) -> Dict[str, Any]:
        """
        Query the RAG system with a question.
        
        Args:
            question: User question
            top_k: Number of context chunks to retrieve (default: 15 for better comparisons)
            
        Returns:
            Dict with answer and sources
        """
        logger.info(f"Processing query: '{question[:100]}...' (top_k={top_k})")
        
        import time
        start_time = time.time()
        
        try:
            # Step 1: Retrieve relevant documents with scores
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query=question,
                k=top_k
            )
            
            if not docs_with_scores:
                logger.warning("No relevant documents found")
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "query_time_ms": (time.time() - start_time) * 1000,
                }
            
            # Step 2: Prepare context
            context_docs = [doc for doc, score in docs_with_scores]
            context = self._prepare_context(context_docs)
            
            # Step 3: Generate answer
            answer = self._generate_answer(question, context)
            
            # Step 4: Format sources
            sources = self._format_sources(docs_with_scores)
            
            query_time = (time.time() - start_time) * 1000
            logger.info(f"Query completed in {query_time:.2f}ms")
            
            return {
                "answer": answer,
                "sources": sources,
                "query_time_ms": query_time,
            }
            
        except Exception as e:
            logger.error(f"Query failed: {str(e)}", exc_info=True)
            raise
    
    def _prepare_context(self, documents: List[Document]) -> str:
        """
        Prepare context string from retrieved documents.
        Groups data by fund for better comparison.
        
        Args:
            documents: Retrieved documents
            
        Returns:
            Formatted context string
        """
        # Group documents by fund name for better organization
        fund_groups = {}
        other_docs = []
        
        for doc in documents:
            fund_name = doc.metadata.get("fund_name", "")
            if fund_name and fund_name != "Unknown":
                if fund_name not in fund_groups:
                    fund_groups[fund_name] = []
                fund_groups[fund_name].append(doc)
            else:
                other_docs.append(doc)
        
        context_parts = []
        
        # Add grouped fund data
        for fund_name, fund_docs in fund_groups.items():
            context_parts.append(f"=== {fund_name} ===")
            for idx, doc in enumerate(fund_docs, 1):
                context_parts.append(f"{doc.page_content}")
            context_parts.append("")  # Empty line between funds
        
        # Add other documents
        if other_docs:
            context_parts.append("=== Additional Information ===")
            for doc in other_docs:
                title = doc.metadata.get("title", "Unknown")
                url = doc.metadata.get("source_url", "")
                context_parts.append(f"Source: {title}")
                if url:
                    context_parts.append(f"URL: {url}")
                context_parts.append(f"{doc.page_content}\n")
        
        full_context = "\n".join(context_parts)
        
        # Truncate if too long
        if len(full_context) > settings.MAX_CONTEXT_LENGTH:
            logger.warning(f"Context too long ({len(full_context)} chars), truncating...")
            full_context = full_context[:settings.MAX_CONTEXT_LENGTH] + "..."
        
        logger.info(f"Prepared context with {len(fund_groups)} funds and {len(other_docs)} other docs")
        return full_context
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using LLM with retrieved context.
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        # Create prompt with enhanced comparison capabilities
        prompt_template = """You are a helpful AI assistant specializing in financial fund analysis. Answer the user's question based ONLY on the provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer the question using only information from the context above
- Be LENIENT with name variations (e.g., "Camp Co" means "Kamco", "camp co-invest" means "Kamco Co-Invest")
- Keep your answer CONCISE and to-the-point (2-3 sentences max for simple questions)
- For voice responses, be brief and conversational
- If the question asks to compare multiple funds, analyze ALL relevant funds found in the context
- When comparing, create clear comparisons using bullet points (not long tables)
- For comparisons, highlight ONLY the most important differences (e.g., top performance numbers)
- If comparing performance, include specific numbers but keep it brief
- If the context doesn't contain enough information to answer fully, say "I don't have enough information to answer that completely"
- Do not make up information not present in the context
- For numerical comparisons, be precise and include units (%, KWD, etc.)

Answer:"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Generate answer
        formatted_prompt = prompt.format(context=context, question=question)
        
        response = self.llm.invoke(formatted_prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        logger.info(f"Generated answer: {answer[:100]}...")
        return answer
    
    def _format_sources(self, docs_with_scores: List[tuple[Document, float]]) -> List[SourceDocument]:
        """
        Format retrieved documents as source citations.
        
        Args:
            docs_with_scores: List of (document, score) tuples
            
        Returns:
            List of SourceDocument objects
        """
        sources = []
        
        for doc, score in docs_with_scores:
            # Normalize score to 0-1 range (Chroma uses distance, lower is better)
            # Convert distance to similarity score
            similarity_score = max(0.0, min(1.0, 1.0 / (1.0 + score)))
            
            source = SourceDocument(
                title=doc.metadata.get("title", "Unknown"),
                url=doc.metadata.get("source_url", ""),
                snippet=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                score=round(similarity_score, 3)
            )
            sources.append(source)
        
        return sources


# Global RAG system instance
rag_system: RAGSystem = None


def get_rag_system() -> RAGSystem:
    """Get or create the global RAG system instance."""
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
    return rag_system
