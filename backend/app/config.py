"""
Configuration managem    # LangChain Settings
    EMBEDDING_PROVIDER: str = "anthropic"  # openai, azure, anthropic
    LLM_PROVIDER: str = "anthropic"  # openai, azure, anthropic
    
    # OpenAI Settings (for embeddings if using openai provider)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_LLM_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    
    # Anthropic Settings (for Claude LLM and embeddings)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    ANTHROPIC_TEMPERATURE: float = 0.7
    ANTHROPIC_MAX_TOKENS: int = 4096oiceRAG backend.
Loads settings from environment variables.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # Apify Settings
    APIFY_TOKEN: Optional[str] = None
    APIFY_ACTOR_NAME: str = "apify/website-content-crawler"
    
    # Target URL
    TARGET_URL: str = "https://www.kamcoinvest.com/fund/kamco-investment-fund"
    
    # LangChain Settings
    EMBEDDING_PROVIDER: str = "azure"  # openai, azure, anthropic
    LLM_PROVIDER: str = "anthropic"  # openai, azure, anthropic
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_LLM_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    
    # Anthropic Settings (for Claude)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    ANTHROPIC_TEMPERATURE: float = 0.7
    ANTHROPIC_MAX_TOKENS: int = 4096
    
    # Azure OpenAI Settings (optional)
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_EMBEDDING_DEPLOYMENT: Optional[str] = None
    AZURE_LLM_DEPLOYMENT: Optional[str] = None
    
    # Vector Store Settings
    VECTOR_STORE_TYPE: str = "chroma"
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    COLLECTION_NAME: str = "voicerag_docs"
    
    # Chunking Settings
    CHUNK_SIZE: int = 200  # Very small chunks for maximum precision
    CHUNK_OVERLAP: int = 50  # Proportional overlap
    
    # RAG Settings
    TOP_K: int = 10  # Increased to get more context with very small chunks
    MAX_CONTEXT_LENGTH: int = 4000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"  # Allow extra fields from .env
    }


# Global settings instance
settings = Settings()
