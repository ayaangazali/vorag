#!/bin/bash

# ============================================
# VoiceRAG Speech Dependencies Installer
# ============================================
# Installs and verifies speech-to-text and text-to-speech dependencies
# for production-grade Voice RAG functionality.

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  VoiceRAG Speech Dependencies Installer${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check Python version
echo -e "${BLUE}🐍 Checking Python version...${NC}"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}❌ Error: Python 3.8+ required, found $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
echo ""

# Check for ffmpeg (required for audio processing)
echo -e "${BLUE}� Checking for ffmpeg...${NC}"
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}❌ ffmpeg not found${NC}"
    echo ""
    echo -e "${YELLOW}ffmpeg is required for audio processing.${NC}"
    echo -e "${YELLOW}Install it with:${NC}"
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "  ${GREEN}brew install ffmpeg${NC}"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo -e "  ${GREEN}sudo apt-get install ffmpeg${NC}  # Debian/Ubuntu"
        echo -e "  ${GREEN}sudo yum install ffmpeg${NC}      # CentOS/RHEL"
    fi
    echo ""
    echo -e "${YELLOW}After installing ffmpeg, run this script again.${NC}"
    exit 1
fi
FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1 | awk '{print $3}')
echo -e "${GREEN}✅ ffmpeg $FFMPEG_VERSION${NC}"
echo ""

# Install Python packages
echo -e "${BLUE}📦 Installing Python packages...${NC}"
echo ""

echo -e "${BLUE}🎤 [1/5] Installing faster-whisper (Speech-to-Text)...${NC}"
pip install --quiet faster-whisper==0.10.0
echo -e "${GREEN}✅ faster-whisper installed${NC}"

echo -e "${BLUE}🔊 [2/5] Installing Coqui TTS (Text-to-Speech)...${NC}"
pip install --quiet TTS==0.21.3
echo -e "${GREEN}✅ Coqui TTS installed${NC}"

echo -e "${BLUE}🎵 [3/5] Installing pydub (Audio manipulation)...${NC}"
pip install --quiet pydub==0.25.1
echo -e "${GREEN}✅ pydub installed${NC}"

echo -e "${BLUE}🔉 [4/5] Installing soundfile (Audio I/O)...${NC}"
pip install --quiet soundfile==0.12.1
echo -e "${GREEN}✅ soundfile installed${NC}"

echo -e "${BLUE}📄 [5/5] Installing python-magic (File validation)...${NC}"
pip install --quiet python-magic==0.4.27
echo -e "${GREEN}✅ python-magic installed${NC}"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  ✅ Installation Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${YELLOW}📝 Important Notes:${NC}"
echo ""
echo -e "  ${BLUE}1.${NC} On first use, models will auto-download (~500MB total):"
echo -e "     • Whisper 'base' model: ~140MB"
echo -e "     • TTS model: ~200MB"
echo ""
echo -e "  ${BLUE}2.${NC} Test speech features:"
echo -e "     ${GREEN}python -c 'from app.speech import check_speech_dependencies; print(check_speech_dependencies())'${NC}"
echo ""
echo -e "  ${BLUE}3.${NC} API endpoints available:"
echo -e "     • POST /speech-to-text"
echo -e "     • POST /text-to-speech"
echo -e "     • POST /voice-query (full STT→RAG→TTS pipeline)"
echo ""
echo -e "  ${BLUE}4.${NC} Full documentation:"
echo -e "     See ${GREEN}VOICE_FEATURES.md${NC} for setup and usage examples"
echo ""
echo -e "${GREEN}🚀 Voice RAG is ready to use!${NC}"
