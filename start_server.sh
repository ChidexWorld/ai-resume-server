
#!/bin/bash

# AI Resume Server Startup Script
# This script ensures clean environment variables and starts the server

echo "🚀 Starting AI Resume Server..."

# Clean problematic environment variables that might have comments
unset MAX_FILE_SIZE
unset MAX_AUDIO_DURATION  
unset SIMILARITY_THRESHOLD
unset MINIMUM_MATCH_SCORE

echo "✅ Cleaned environment variables"

# Verify .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.example to .env and configure your settings:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

echo "✅ Environment file found"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Start the server
echo "🔥 Starting uvicorn server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload