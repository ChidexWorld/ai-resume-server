#!/usr/bin/env python3
"""Download required NLTK data for the application."""
import nltk
import ssl
import os
import sys

# Handle SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Set NLTK data path to a location that persists on Render
script_dir = os.path.dirname(os.path.abspath(__file__))
nltk_data_dir = os.path.join(script_dir, 'nltk_data')

print(f"Script directory: {script_dir}", file=sys.stderr)
print(f"Target NLTK data directory: {nltk_data_dir}", file=sys.stderr)
print(f"Current working directory: {os.getcwd()}", file=sys.stderr)

# Create directory
os.makedirs(nltk_data_dir, exist_ok=True)
print(f"Created/verified directory: {nltk_data_dir}", file=sys.stderr)

# Add to NLTK path
if nltk_data_dir not in nltk.data.path:
    nltk.data.path.insert(0, nltk_data_dir)
    print(f"Added to NLTK path: {nltk_data_dir}", file=sys.stderr)

# Download required NLTK data to the custom directory
print(f"Downloading NLTK data packages...", file=sys.stderr)

packages = ['stopwords', 'punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
for package in packages:
    print(f"  Downloading {package}...", file=sys.stderr)
    success = nltk.download(package, download_dir=nltk_data_dir, quiet=False)
    if success:
        print(f"  ✓ {package} downloaded successfully", file=sys.stderr)
    else:
        print(f"  ✗ {package} download failed", file=sys.stderr)

# Verify downloads
print(f"\nVerifying NLTK data directory contents:", file=sys.stderr)
for root, dirs, files in os.walk(nltk_data_dir):
    level = root.replace(nltk_data_dir, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/", file=sys.stderr)
    subindent = ' ' * 2 * (level + 1)
    for file in files[:5]:  # Limit to first 5 files per directory
        print(f"{subindent}{file}", file=sys.stderr)

print(f"\nNLTK data setup complete!", file=sys.stderr)
