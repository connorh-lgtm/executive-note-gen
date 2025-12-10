#!/bin/bash

# Executive Note Generator - Run Script

echo "🚀 Starting Executive Note Generator..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! pip show fastapi > /dev/null 2>&1; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API key before the server starts!"
    echo "   - For OpenAI: Add OPENAI_API_KEY"
    echo "   - For Anthropic: Add ANTHROPIC_API_KEY"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the server
echo "✅ Starting FastAPI server..."
echo "🌐 Open http://localhost:8000 in your browser"
echo ""
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
