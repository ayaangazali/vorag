"""
Configuration management for VoiceRAG backend.
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
    
    # Bright Data Settings (alternative to Apify)
    BRIGHTDATA_API_TOKEN: Optional[str] = None
    BRIGHTDATA_COLLECTOR_ID: str = "c_mjsgl9011x823pu93h"
    
    # Scraper Selection
    SCRAPER_PROVIDER: str = "brightdata"  # apify or brightdata
    
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
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"
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
    TOP_K: int = 15  # Increased for better fund comparisons
    MAX_CONTEXT_LENGTH: int = 8000  # Increased to hold more fund data for comparisons
    
    # ==========================================
    # Speech Settings (Optional Dependencies)
    # ==========================================
    
    # Whisper STT Model Size
    # Options: tiny, base, small, medium, large-v3
    # Larger = more accurate but slower
    WHISPER_MODEL_SIZE: str = "base"
    
    # Coqui TTS Model
    # Fast English: "tts_models/en/ljspeech/tacotron2-DDC"
    # Multilingual (17 langs): "tts_models/multilingual/multi-dataset/xtts_v2"
    TTS_MODEL: str = "tts_models/en/ljspeech/tacotron2-DDC"
    
    # Speech File Size Limits (bytes)
    MAX_AUDIO_FILE_SIZE: int = 25 * 1024 * 1024  # 25MB
    
    # Speech Duration Limits (seconds)
    MAX_AUDIO_DURATION: int = 300  # 5 minutes
    
    # TTS Text Length Limit (characters)
    MAX_TTS_TEXT_LENGTH: int = 5000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"  # Allow extra fields from .env
    }


# Global settings instance
settings = Settings()
