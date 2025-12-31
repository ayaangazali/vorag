"""
Production-grade Speech services: Speech-to-Text (STT) and Text-to-Speech (TTS).

Safety features:
- Lazy imports (app boots even if deps missing)
- Thread-safe singleton pattern
- Input validation (file size, duration, format)
- Automatic temp file cleanup
- Clear error messages with install instructions
- Timeouts and resource limits

Uses:
- STT: faster-whisper (OpenAI Whisper optimized)
- TTS: Coqui TTS (Mozilla's open-source TTS)
"""

import logging
import os
import tempfile
import threading
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path
from contextlib import contextmanager

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level locks for thread-safe singleton initialization
_stt_lock = threading.Lock()
_tts_lock = threading.Lock()

# Singleton instances
_stt_instance: Optional['SpeechToText'] = None
_tts_instance: Optional['TextToSpeech'] = None


class SpeechServiceError(Exception):
    """Base exception for speech service errors."""
    pass


class DependencyMissingError(SpeechServiceError):
    """Raised when required speech dependencies are not installed."""
    pass


class AudioValidationError(SpeechServiceError):
    """Raised when audio input fails validation."""
    pass


@contextmanager
def safe_temp_file(suffix=".wav", delete=True):
    """
    Context manager for safe temp file handling.
    Always cleans up even on exceptions.
    """
    tmp_file = None
    try:
        tmp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            dir=None  # Use system temp dir
        )
        tmp_path = tmp_file.name
        tmp_file.close()  # Close handle, keep file
        yield tmp_path
    finally:
        if tmp_file and delete and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
                logger.debug(f"Cleaned up temp file: {tmp_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {tmp_path}: {e}")


def validate_audio_file(
    file_path: str,
    max_size_mb: Optional[float] = None,
    max_duration_seconds: Optional[float] = None
) -> Dict[str, Any]:
    """
    Validate audio file before processing.
    
    Args:
        file_path: Path to audio file
        max_size_mb: Maximum file size in MB (defaults to config)
        max_duration_seconds: Maximum audio duration in seconds (defaults to config)
        
    Returns:
        Dict with validation info: {duration, sample_rate, channels}
        
    Raises:
        AudioValidationError: If validation fails
    """
    # Use config defaults if not specified
    if max_size_mb is None:
        max_size_mb = settings.MAX_AUDIO_FILE_SIZE / (1024 * 1024)
    if max_duration_seconds is None:
        max_duration_seconds = settings.MAX_AUDIO_DURATION
    
    # Check file exists
    if not os.path.exists(file_path):
        raise AudioValidationError(f"File not found: {file_path}")
    
    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise AudioValidationError(
            f"File too large: {file_size_mb:.1f}MB (max: {max_size_mb}MB)"
        )
    
    # Try to get audio info (requires soundfile)
    try:
        import soundfile as sf
        with sf.SoundFile(file_path) as audio:
            duration = len(audio) / audio.samplerate
            
            if duration > max_duration_seconds:
                raise AudioValidationError(
                    f"Audio too long: {duration:.1f}s (max: {max_duration_seconds}s)"
                )
            
            return {
                "duration": duration,
                "sample_rate": audio.samplerate,
                "channels": audio.channels,
                "file_size_mb": file_size_mb
            }
    except ImportError:
        # Fallback: just check file size
        logger.warning("soundfile not installed, skipping duration check")
        return {
            "duration": None,
            "sample_rate": None,
            "channels": None,
            "file_size_mb": file_size_mb
        }
    except Exception as e:
        raise AudioValidationError(f"Failed to read audio file: {str(e)}")


class SpeechToText:
    """
    Thread-safe Speech-to-Text service using Faster-Whisper.
    
    Lazy-loads model on first use. Safe to instantiate even if dependencies missing.
    """
    
    def __init__(
        self,
        model_size: Optional[str] = None,
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        Initialize STT service.
        
        Args:
            model_size: Whisper model ("tiny", "base", "small", "medium", "large-v3").
                       Defaults to config setting.
            device: Device to use ("cpu" or "cuda")
            compute_type: Precision ("int8", "float16", "float32")
        """
        self.model_size = model_size or settings.WHISPER_MODEL_SIZE
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy-load the model (called on first transcribe)."""
        if self._initialized:
            return
        
        try:
            from faster_whisper import WhisperModel
        except ImportError as e:
            raise DependencyMissingError(
                "faster-whisper not installed. Install with:\n"
                "  pip install faster-whisper\n"
                "Note: Requires system ffmpeg (brew install ffmpeg / apt install ffmpeg)"
            ) from e
        
        try:
            logger.info(
                f"Loading Whisper model: {self.model_size} "
                f"(device={self.device}, compute_type={self.compute_type})"
            )
            
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=None  # Use default cache (~/.cache/huggingface)
            )
            
            self._initialized = True
            logger.info(f"✅ Whisper model loaded successfully")
            
        except Exception as e:
            raise SpeechServiceError(
                f"Failed to load Whisper model '{self.model_size}': {str(e)}\n"
                f"This may be due to:\n"
                f"  - Missing system dependencies (ffmpeg)\n"
                f"  - Network issues (model download)\n"
                f"  - Insufficient disk space"
            ) from e
    
    def transcribe(
        self,
        audio_file: BinaryIO,
        language: Optional[str] = None,
        max_size_mb: Optional[float] = None,
        max_duration_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.
        
        Args:
            audio_file: Audio file binary stream
            language: Optional language code (e.g., "en", "ar"). Auto-detect if None.
            max_size_mb: Maximum file size in MB (defaults to config)
            max_duration_seconds: Maximum audio duration in seconds (defaults to config)
            
        Returns:
            Dict with:
                - text: Transcribed text
                - language: Detected/specified language
                - language_probability: Confidence score
                - duration: Audio duration in seconds
                - segments: List of segment dicts (text, start, end)
        
        Raises:
            DependencyMissingError: If faster-whisper not installed
            AudioValidationError: If audio validation fails
            SpeechServiceError: If transcription fails
        """
        self._ensure_initialized()
        
        # Handle both file paths (str) and file objects
        if isinstance(audio_file, str):
            # audio_file is already a path - use it directly
            audio_path = audio_file
            cleanup_temp = False
        else:
            # audio_file is a file object - save to temp file
            with safe_temp_file(suffix=".audio") as tmp_path:
                audio_file.seek(0)  # Reset file pointer
                with open(tmp_path, 'wb') as f:
                    f.write(audio_file.read())
                audio_path = tmp_path
                cleanup_temp = True
        
        # Validate audio
        try:
            validation_info = validate_audio_file(
                audio_path,
                max_size_mb=max_size_mb,
                max_duration_seconds=max_duration_seconds
            )
        except AudioValidationError as e:
            raise AudioValidationError(f"Audio validation failed: {str(e)}")
        
        try:
            logger.info(f"Transcribing audio (language={language or 'auto'}, size={validation_info['file_size_mb']:.1f}MB)")
            
            # Transcribe
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                vad_filter=True,  # Remove silence
                vad_parameters=dict(min_silence_duration_ms=500),
                word_timestamps=False  # Faster without word-level timestamps
            )
            
            # Collect segments
            segment_list = []
            text_parts = []
            
            for segment in segments:
                segment_list.append({
                    "text": segment.text.strip(),
                    "start": segment.start,
                    "end": segment.end
                })
                text_parts.append(segment.text.strip())
            
            full_text = " ".join(text_parts)
            
            result = {
                "text": full_text,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": validation_info.get("duration"),
                "segments": segment_list[:10]  # Limit to first 10 segments
            }
            
            logger.info(
                f"✅ Transcription complete: '{full_text[:100]}...' "
                f"(lang={info.language}, confidence={info.language_probability:.2f})"
            )
            
            return result
            
        except Exception as e:
            raise SpeechServiceError(f"Transcription failed: {str(e)}") from e


class TextToSpeech:
    """
    Thread-safe Text-to-Speech service using Coqui TTS.
    
    Lazy-loads model on first use. Safe to instantiate even if dependencies missing.
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        Initialize TTS service.
        
        Args:
            model_name: TTS model name from Coqui TTS model zoo. Defaults to config setting.
            device: Device to use ("cpu" or "cuda")
        """
        self.model_name = model_name or settings.TTS_MODEL
        self.device = device
        self.tts = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy-load the TTS engine (called on first synthesize)."""
        if self._initialized:
            return
        
        # Try Coqui TTS first (better quality but Python <=3.11 only)
        try:
            from TTS.api import TTS
            logger.info(f"Loading Coqui TTS model: {self.model_name} (device={self.device})")
            self.tts = TTS(model_name=self.model_name)
            self.tts.to(self.device)
            self.tts_engine = 'coqui'
            self._initialized = True
            logger.info(f"✅ Coqui TTS model loaded successfully")
            return
        except ImportError:
            logger.warning("Coqui TTS not available (requires Python <=3.11). Falling back to pyttsx3...")
        except Exception as e:
            logger.warning(f"Failed to load Coqui TTS: {e}. Falling back to pyttsx3...")
        
        # Fallback to pyttsx3 (Python 3.12+ compatible, offline)
        try:
            import pyttsx3
            logger.info("Loading pyttsx3 TTS engine...")
            self.tts = pyttsx3.init()
            # Set properties for better quality
            self.tts.setProperty('rate', 175)  # Speed of speech
            self.tts.setProperty('volume', 0.9)  # Volume 0-1
            self.tts_engine = 'pyttsx3'
            self._initialized = True
            logger.info("✅ pyttsx3 TTS engine loaded successfully")
        except ImportError as e:
            raise DependencyMissingError(
                "No TTS library available. Install one of:\n"
                "  pip install TTS (Python <=3.11)\n"
                "  pip install pyttsx3 (Python 3.12+)"
            ) from e
        except Exception as e:
            raise SpeechServiceError(
                f"Failed to initialize TTS engine: {str(e)}"
            ) from e
    
    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None,
        max_chars: Optional[int] = None,
        speaker: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """
        Convert text to speech.
        
        Args:
            text: Text to synthesize
            output_path: Optional output file path. If None, creates temp file.
            max_chars: Maximum text length (defaults to config)
            speaker: Optional speaker name (for multi-speaker models)
            language: Optional language code (for multilingual models)
            
        Returns:
            Path to generated audio file (WAV format)
            
        Raises:
            DependencyMissingError: If TTS not installed
            AudioValidationError: If text too long or empty
            SpeechServiceError: If synthesis fails
        """
        self._ensure_initialized()
        
        # Use config default if not specified
        if max_chars is None:
            max_chars = settings.MAX_TTS_TEXT_LENGTH
        
        # Validate text
        if not text or not text.strip():
            raise AudioValidationError("Text cannot be empty")
        
        text = text.strip()
        
        if len(text) > max_chars:
            raise AudioValidationError(
                f"Text too long: {len(text)} chars (max: {max_chars})"
            )
        
        # Create output path if not provided
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav", dir=None)
        
        try:
            logger.info(f"Synthesizing {len(text)} chars: '{text[:100]}...'")
            
            if self.tts_engine == 'coqui':
                # Use Coqui TTS
                kwargs = {}
                if speaker:
                    kwargs["speaker"] = speaker
                if language:
                    kwargs["language"] = language
                
                # Generate speech
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    **kwargs
                )
            else:
                # Use pyttsx3
                self.tts.save_to_file(text, output_path)
                self.tts.runAndWait()

            
            # Verify file was created
            if not os.path.exists(output_path):
                raise SpeechServiceError("TTS did not create output file")
            
            file_size_kb = os.path.getsize(output_path) / 1024
            logger.info(f"✅ Generated audio: {output_path} ({file_size_kb:.1f} KB)")
            
            return output_path
            
        except Exception as e:
            # Clean up partial file on error
            if output_path and os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except:
                    pass
            
            raise SpeechServiceError(f"TTS synthesis failed: {str(e)}") from e


# ============================================================================
# Public API - Thread-safe singleton getters
# ============================================================================

def get_stt(
    model_size: Optional[str] = None,
    device: str = "cpu",
    compute_type: str = "int8"
) -> SpeechToText:
    """
    Get or create thread-safe STT singleton.
    
    Safe to call even if dependencies not installed (lazy initialization).
    """
    global _stt_instance
    
    if _stt_instance is None:
        with _stt_lock:
            # Double-check inside lock
            if _stt_instance is None:
                _stt_instance = SpeechToText(
                    model_size=model_size,
                    device=device,
                    compute_type=compute_type
                )
    
    return _stt_instance


def get_tts(
    model_name: Optional[str] = None,
    device: str = "cpu"
) -> TextToSpeech:
    """
    Get or create thread-safe TTS singleton.
    
    Safe to call even if dependencies not installed (lazy initialization).
    """
    global _tts_instance
    
    if _tts_instance is None:
        with _tts_lock:
            # Double-check inside lock
            if _tts_instance is None:
                _tts_instance = TextToSpeech(
                    model_name=model_name,
                    device=device
                )
    
    return _tts_instance


def check_speech_dependencies() -> Dict[str, bool]:
    """
    Check which speech dependencies are installed.
    
    Returns:
        Dict with {faster_whisper: bool, TTS: bool, soundfile: bool, pydub: bool}
    """
    deps = {}
    
    try:
        import faster_whisper
        deps["faster_whisper"] = True
    except ImportError:
        deps["faster_whisper"] = False
    
    try:
        import TTS
        deps["TTS"] = True
    except ImportError:
        deps["TTS"] = False
    
    try:
        import soundfile
        deps["soundfile"] = True
    except ImportError:
        deps["soundfile"] = False
    
    try:
        import pydub
        deps["pydub"] = True
    except ImportError:
        deps["pydub"] = False
    
    return deps

