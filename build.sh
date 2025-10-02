#!/usr/bin/env bash
# Render build script

set -o errexit

echo "=== Starting build process ==="

# Install Python dependencies
echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

# Download NLTK data
echo "=== Downloading NLTK data ==="
python download_nltk_data.py || {
    echo "WARNING: NLTK data download failed, but continuing..."
}

# Download spaCy model
echo "=== Downloading spaCy model ==="
python -m spacy download en_core_web_sm || {
    echo "WARNING: spaCy model download failed, but continuing..."
}

echo "=== Verifying NLTK data location ==="
ls -la nltk_data 2>/dev/null || echo "nltk_data directory not found"

echo "=== Build completed successfully! ==="
