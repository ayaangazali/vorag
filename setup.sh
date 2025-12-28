#!/bin/bash
# VoiceRAG - Quick Setup Script

echo "🎙️ VoiceRAG Setup"
echo "=================="
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  backend/.env not found!"
    echo "📝 Creating from .env.example..."
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env"
    echo ""
    echo "🔑 Please edit backend/.env and add your API keys:"
    echo "   - APIFY_TOKEN"
    echo "   - ANTHROPIC_API_KEY"  
    echo "   - AZURE_OPENAI_API_KEY"
    echo "   - AZURE_OPENAI_ENDPOINT"
    echo ""
    echo "Press Enter after you've added your keys..."
    read
fi

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "../.venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv ../.venv
fi

# Activate virtual environment
source ../.venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

cd ..

# Setup frontend
echo ""
echo "📦 Setting up Node.js frontend..."
cd frontend

# Install Node dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source ../.venv/bin/activate"
echo "  python3 main.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3001"
