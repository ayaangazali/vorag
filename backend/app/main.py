"""
FastAPI application for RAG backend.
Provides endpoints for ingestion, querying, and health checks.
"""

import logging
import uuid
import os
import tempfile
from typing import Dict
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

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


@app.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Convert speech audio to text using Whisper.
    
    **Requires optional dependencies:** `pip install faster-whisper soundfile`
    
    Args:
        audio: Audio file (WAV, MP3, M4A, OGG, FLAC, etc.)
               Max size: 25MB, Max duration: 5 minutes
        
    Returns:
        {
            "text": "transcribed text",
            "filename": "original_filename.wav",
            "duration": 12.5,
            "language": "en"
        }
        
    Raises:
        503: Speech dependencies not installed
        400: Invalid audio file
        500: Transcription error
    """
    try:
        from app.speech import get_stt, DependencyMissingError, AudioValidationError, safe_temp_file
        
        logger.info(f"📥 STT request: {audio.filename}")
        
        # Save uploaded file to temp location
        with safe_temp_file(suffix=os.path.splitext(audio.filename or ".wav")[1]) as temp_path:
            # Write uploaded content
            content = await audio.read()
            with open(temp_path, "wb") as f:
                f.write(content)
            
            # Get STT service (lazy-loaded)
            stt = get_stt()
            
            # Transcribe (includes validation)
            result = stt.transcribe(temp_path)
        
        logger.info(f"✅ STT success: '{result['text'][:100]}...'")
        
        return {
            "text": result["text"],
            "filename": audio.filename,
            "duration": result.get("duration"),
            "language": result.get("language", "unknown")
        }
        
    except DependencyMissingError as e:
        logger.warning(f"Speech deps missing: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "speech_dependencies_missing",
                "message": str(e),
                "install_command": "pip install faster-whisper soundfile pydub",
                "docs": "See VOICE_FEATURES.md for full setup instructions"
            }
        )
    except AudioValidationError as e:
        logger.warning(f"Audio validation failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_audio",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"STT failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Speech-to-text failed: {str(e)}"
        )


@app.post("/text-to-speech")
async def text_to_speech(request: Dict[str, str]):
    """
    Convert text to speech audio.
    
    **Requires optional dependencies:** `pip install TTS soundfile`
    
    Args:
        request: {"text": "text to synthesize"}
                 Max length: 5000 characters
        
    Returns:
        WAV audio file
        
    Raises:
        503: Speech dependencies not installed
        400: Text validation failed
        500: Synthesis error
    """
    try:
        from app.speech import get_tts, DependencyMissingError, SpeechServiceError, safe_temp_file
        
        text = request.get("text", "")
        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text field is required and cannot be empty"
            )
        
        if len(text) > 5000:
            raise HTTPException(
                status_code=400,
                detail=f"Text too long ({len(text)} chars). Maximum is 5000 characters."
            )
        
        logger.info(f"🔊 TTS request: '{text[:100]}...'")
        
        # Get TTS service (lazy-loaded)
        tts = get_tts()
        
        # Generate speech to temp file
        with safe_temp_file(suffix=".wav") as temp_path:
            output_path = tts.synthesize(text, output_path=temp_path)
            
            # Return audio file
            response = FileResponse(
                output_path,
                media_type="audio/wav",
                filename="speech.wav",
                headers={"Content-Disposition": "attachment; filename=speech.wav"}
            )
            
            logger.info(f"✅ TTS success: {output_path}")
            return response
        
    except DependencyMissingError as e:
        logger.warning(f"Speech deps missing: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "speech_dependencies_missing",
                "message": str(e),
                "install_command": "pip install TTS soundfile",
                "docs": "See VOICE_FEATURES.md for full setup instructions"
            }
        )
    except HTTPException:
        raise  # Re-raise validation errors
    except Exception as e:
        logger.error(f"TTS failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Text-to-speech failed: {str(e)}"
        )


@app.post("/voice-query")
async def voice_query(audio: UploadFile = File(...)):
    """
    🎤 Voice RAG Pipeline: Speak a question → Get a spoken answer
    
    Combines STT → RAG → TTS pipeline for full voice interaction.
    
    **Requires optional dependencies:** `pip install faster-whisper TTS soundfile pydub`
    
    Args:
        audio: Audio file with spoken question
               Max size: 25MB, Max duration: 5 minutes
        
    Returns:
        Audio file with spoken answer (WAV format)
        Headers include transcribed question and answer text
        
    Raises:
        503: Speech dependencies not installed
        400: Invalid audio file
        500: Pipeline error
    """
    try:
        from app.speech import (
            get_stt, get_tts,
            DependencyMissingError,
            AudioValidationError,
            SpeechServiceError,
            safe_temp_file
        )
        
        logger.info(f"🎤 Voice query: {audio.filename}")
        
        # Step 1: Speech-to-Text
        with safe_temp_file(suffix=os.path.splitext(audio.filename or ".wav")[1]) as input_path:
            # Save uploaded audio
            content = await audio.read()
            with open(input_path, "wb") as f:
                f.write(content)
            
            # Convert webm to wav if needed
            if input_path.endswith('.webm') or input_path.endswith('.ogg'):
                try:
                    logger.info("Converting webm/ogg to wav using ffmpeg...")
                    
                    # Use ffmpeg directly (more reliable than pydub for Python 3.13)
                    import subprocess
                    
                    # Create a new temp file for wav
                    with safe_temp_file(suffix=".wav") as wav_path:
                        # Use ffmpeg to convert: mono, 16kHz, 16-bit PCM
                        cmd = [
                            'ffmpeg',
                            '-i', input_path,
                            '-ar', '16000',  # Sample rate: 16kHz
                            '-ac', '1',      # Channels: mono
                            '-sample_fmt', 's16',  # 16-bit PCM
                            '-y',            # Overwrite output
                            wav_path
                        ]
                        
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        if result.returncode != 0:
                            logger.error(f"ffmpeg error: {result.stderr}")
                            raise Exception(f"ffmpeg conversion failed: {result.stderr[:200]}")
                        
                        logger.info("✅ Audio converted successfully")
                        
                        # Transcribe the converted audio
                        stt = get_stt()
                        stt_result = stt.transcribe(wav_path)
                        question = stt_result["text"]
                        
                except subprocess.TimeoutExpired:
                    logger.error("Audio conversion timeout")
                    raise HTTPException(
                        status_code=400,
                        detail="Audio conversion timed out. File may be too large."
                    )
                except FileNotFoundError:
                    logger.error("ffmpeg not found")
                    raise HTTPException(
                        status_code=500,
                        detail="ffmpeg is not installed. Please install it: brew install ffmpeg"
                    )
                except Exception as e:
                    logger.error(f"Audio conversion failed: {e}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to convert audio: {str(e)}"
                    )
            else:
                # Transcribe directly
                stt = get_stt()
                stt_result = stt.transcribe(input_path)
                question = stt_result["text"]
            
            logger.info(f"📝 Transcribed: '{question}'")
        
        # Step 1.5: Use Claude to clean up grammar and fix transcription errors
        from anthropic import Anthropic
        anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        correction_prompt = f"""Fix any grammar mistakes and correct common transcription errors in this voice query. 
Common errors: "camp co" should be "Kamco", "camco" should be "Kamco", "camp go" should be "Kamco", "camcuin" should be "Kamco".
Keep it natural and conversational. Only return the corrected text, nothing else.

Original: {question}"""

        correction_response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",  # Fast model for quick correction
            max_tokens=200,
            messages=[{"role": "user", "content": correction_prompt}]
        )
        
        question_cleaned = correction_response.content[0].text.strip()
        logger.info(f"✨ Claude corrected: '{question}' → '{question_cleaned}'")
        
        # Step 2: RAG Query
        rag = get_rag_system()
        rag_result = rag.query(question=question_cleaned, top_k=15)
        answer = rag_result["answer"]
        
        logger.info(f"🤖 Generated answer: '{answer[:100]}...'")
        
        # Step 3: Text-to-Speech (Edge TTS)
        tts = get_tts()
        
        # Create temp file for audio output
        with safe_temp_file(suffix=".mp3") as output_path:
            audio_path = await tts.synthesize(answer, output_path=output_path)
            
            logger.info(f"🔊 Synthesized audio with Edge TTS")
            
            # Read audio file to memory so we can delete temp file
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # Sanitize headers to prevent HTTP errors (remove newlines, special chars)
            def sanitize_header(text: str) -> str:
                """Remove problematic characters from HTTP headers."""
                import re
                # Remove newlines, carriage returns, and non-ASCII
                text = text.replace('\n', ' ').replace('\r', ' ')
                # Remove control characters
                text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
                return text.strip()
            
            # Return audio response with the Claude-corrected question
            return Response(
                content=audio_data,
                media_type="audio/mpeg",
                headers={
                    "X-Transcribed-Question": sanitize_header(question_cleaned[:1000]),  # Claude corrected version
                    "X-Raw-Transcription": sanitize_header(question[:1000]),  # Original for debugging
                    "X-Answer-Text": sanitize_header(answer[:2000]),  # Show more of the answer
                    "X-Source-Count": str(len(rag_result.get("sources", []))),
                    "X-Voice": "en-US-AriaNeural"
                }
            )
        
    except DependencyMissingError as e:
        logger.warning(f"Speech deps missing: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "speech_dependencies_missing",
                "message": str(e),
                "install_command": "pip install faster-whisper TTS soundfile pydub",
                "docs": "See VOICE_FEATURES.md for full setup instructions"
            }
        )
    except AudioValidationError as e:
        logger.warning(f"Audio validation failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_audio",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Voice query failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Voice query failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
