#!/usr/bin/env python3
"""Download required NLTK data for the application."""
import nltk
import ssl
import os

# Handle SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Set NLTK data path to a location that persists on Render
nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)

# Download required NLTK data to the custom directory
print(f"Downloading NLTK data to {nltk_data_dir}...")
nltk.download('stopwords', download_dir=nltk_data_dir, quiet=True)
nltk.download('punkt', download_dir=nltk_data_dir, quiet=True)
nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_dir, quiet=True)
nltk.download('maxent_ne_chunker', download_dir=nltk_data_dir, quiet=True)
nltk.download('words', download_dir=nltk_data_dir, quiet=True)
print("NLTK data downloaded successfully!")
