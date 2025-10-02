"""
NLTK setup configuration - must be imported before any NLTK usage.
This module configures NLTK data paths for production environments.
"""
import os
import nltk

# Configure NLTK data directory
def setup_nltk_data():
    """Set up NLTK data paths for the application."""
    # Define possible NLTK data directories
    project_root = os.path.dirname(os.path.abspath(__file__))
    nltk_data_dir = os.path.join(project_root, 'nltk_data')

    # Add custom data directory to NLTK's search path
    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.insert(0, nltk_data_dir)

    # Also check for common deployment paths
    deployment_paths = [
        '/opt/render/project/src/nltk_data',
        '/app/nltk_data',
        os.path.expanduser('~/nltk_data')
    ]

    for path in deployment_paths:
        if os.path.exists(path) and path not in nltk.data.path:
            nltk.data.path.insert(0, path)

# Run setup immediately when module is imported
setup_nltk_data()
