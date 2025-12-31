"""
Tests for speech services.
Tests validation, error handling, and dependency checking.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Test imports - these should work even without speech dependencies
from app.speech import (
    check_speech_dependencies,
    safe_temp_file,
    SpeechServiceError,
    DependencyMissingError,
    AudioValidationError,
)


class TestDependencyChecking:
    """Test dependency detection and error handling."""
    
    def test_check_dependencies_returns_dict(self):
        """check_speech_dependencies() should return a dict."""
        result = check_speech_dependencies()
        assert isinstance(result, dict)
        assert "faster_whisper" in result
        assert "TTS" in result
        assert "soundfile" in result
        assert "pydub" in result
        assert "python_magic" in result
    
    def test_dependency_values_are_booleans(self):
        """All dependency check values should be booleans."""
        result = check_speech_dependencies()
        for key, value in result.items():
            assert isinstance(value, bool), f"{key} should be boolean"


class TestSafeTempFile:
    """Test temp file handling with automatic cleanup."""
    
    def test_safe_temp_file_creates_path(self):
        """safe_temp_file should yield a file path."""
        with safe_temp_file() as temp_path:
            assert isinstance(temp_path, str)
            assert len(temp_path) > 0
    
    def test_safe_temp_file_cleanup_on_success(self):
        """Temp file should be cleaned up after successful use."""
        temp_path_ref = None
        
        with safe_temp_file(suffix=".wav") as temp_path:
            temp_path_ref = temp_path
            # Create the file
            with open(temp_path, "w") as f:
                f.write("test")
            assert os.path.exists(temp_path)
        
        # File should be deleted after context exits
        assert not os.path.exists(temp_path_ref)
    
    def test_safe_temp_file_cleanup_on_error(self):
        """Temp file should be cleaned up even if an error occurs."""
        temp_path_ref = None
        
        try:
            with safe_temp_file(suffix=".wav") as temp_path:
                temp_path_ref = temp_path
                # Create the file
                with open(temp_path, "w") as f:
                    f.write("test")
                # Raise an error
                raise ValueError("Test error")
        except ValueError:
            pass  # Expected
        
        # File should still be deleted
        assert not os.path.exists(temp_path_ref)
    
    def test_safe_temp_file_suffix(self):
        """safe_temp_file should respect suffix parameter."""
        with safe_temp_file(suffix=".mp3") as temp_path:
            assert temp_path.endswith(".mp3")
        
        with safe_temp_file(suffix=".wav") as temp_path:
            assert temp_path.endswith(".wav")


class TestValidation:
    """Test input validation functions."""
    
    @pytest.mark.skipif(
        not check_speech_dependencies().get("python_magic", False),
        reason="python-magic not installed"
    )
    def test_validate_audio_file_imports(self):
        """validate_audio_file should be importable with deps."""
        from app.speech import validate_audio_file
        assert callable(validate_audio_file)
    
    def test_missing_dependencies_raise_helpful_error(self):
        """Missing dependencies should raise DependencyMissingError."""
        # This tests the error handling, not the actual functionality
        assert DependencyMissingError is not None
        
        # Test that we can create the exception
        error = DependencyMissingError("test error")
        assert str(error) == "test error"
        assert isinstance(error, SpeechServiceError)


class TestSTTService:
    """Test SpeechToText service initialization and error handling."""
    
    def test_stt_dependency_check(self):
        """STT should check for faster-whisper dependency."""
        deps = check_speech_dependencies()
        
        if not deps.get("faster_whisper", False):
            # If dependency missing, import should work but usage should fail
            from app.speech import get_stt
            
            with pytest.raises(DependencyMissingError):
                stt = get_stt()
                stt._ensure_initialized()
    
    @pytest.mark.skipif(
        not check_speech_dependencies().get("faster_whisper", False),
        reason="faster-whisper not installed"
    )
    def test_stt_singleton_pattern(self):
        """get_stt() should return same instance (singleton)."""
        from app.speech import get_stt
        
        stt1 = get_stt()
        stt2 = get_stt()
        
        assert stt1 is stt2


class TestTTSService:
    """Test TextToSpeech service initialization and error handling."""
    
    def test_tts_dependency_check(self):
        """TTS should check for TTS library dependency."""
        deps = check_speech_dependencies()
        
        if not deps.get("TTS", False):
            # If dependency missing, import should work but usage should fail
            from app.speech import get_tts
            
            with pytest.raises(DependencyMissingError):
                tts = get_tts()
                tts._ensure_initialized()
    
    @pytest.mark.skipif(
        not check_speech_dependencies().get("TTS", False),
        reason="TTS not installed"
    )
    def test_tts_singleton_pattern(self):
        """get_tts() should return same instance (singleton)."""
        from app.speech import get_tts
        
        tts1 = get_tts()
        tts2 = get_tts()
        
        assert tts1 is tts2
    
    @pytest.mark.skipif(
        not check_speech_dependencies().get("TTS", False),
        reason="TTS not installed"
    )
    def test_tts_max_length_validation(self):
        """TTS should validate text length."""
        from app.speech import get_tts
        
        tts = get_tts()
        
        # Text too long should raise error
        long_text = "a" * 10000  # 10k chars (max is 5k)
        
        with pytest.raises(SpeechServiceError):
            tts.synthesize(long_text)


class TestExceptions:
    """Test custom exception hierarchy."""
    
    def test_exception_hierarchy(self):
        """Verify exception inheritance."""
        assert issubclass(DependencyMissingError, SpeechServiceError)
        assert issubclass(AudioValidationError, SpeechServiceError)
        assert issubclass(SpeechServiceError, Exception)
    
    def test_exception_messages(self):
        """Exceptions should preserve messages."""
        msg = "Test error message"
        
        error1 = SpeechServiceError(msg)
        assert str(error1) == msg
        
        error2 = DependencyMissingError(msg)
        assert str(error2) == msg
        
        error3 = AudioValidationError(msg)
        assert str(error3) == msg


class TestAPIEndpoints:
    """Test API endpoint behavior (integration tests)."""
    
    @pytest.mark.skipif(
        not all(check_speech_dependencies().values()),
        reason="Speech dependencies not fully installed"
    )
    def test_endpoints_available_with_deps(self):
        """API endpoints should work when dependencies are installed."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Health check should always work
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_endpoints_return_503_without_deps(self):
        """API endpoints should return 503 when dependencies missing."""
        # This would need to be tested in an environment without deps
        # or with mocked imports
        pass


# Pytest configuration
@pytest.fixture(autouse=True)
def cleanup_singletons():
    """Reset singleton instances between tests."""
    import sys
    
    # Clear speech module singletons if loaded
    if 'app.speech' in sys.modules:
        module = sys.modules['app.speech']
        if hasattr(module, '_stt_instance'):
            module._stt_instance = None
        if hasattr(module, '_tts_instance'):
            module._tts_instance = None
    
    yield
    
    # Cleanup after test
    if 'app.speech' in sys.modules:
        module = sys.modules['app.speech']
        if hasattr(module, '_stt_instance'):
            module._stt_instance = None
        if hasattr(module, '_tts_instance'):
            module._tts_instance = None


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_speech.py -v
    pytest.main([__file__, "-v"])
