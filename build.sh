#!/usr/bin/env bash
# Render build script

set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Download NLTK data
python download_nltk_data.py

# Download spaCy model
python -m spacy download en_core_web_sm

echo "Build completed successfully!"
