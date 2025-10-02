"""
NLTK setup configuration - must be imported before any NLTK usage.
This module configures NLTK data paths for production environments.
"""
import os
import sys
import nltk

# Configure NLTK data directory
def setup_nltk_data():
    """Set up NLTK data paths for the application."""
    # Define possible NLTK data directories
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Multiple possible locations for nltk_data
    possible_paths = [
        # Local development
        os.path.join(project_root, 'nltk_data'),
        # Render deployment paths
        '/opt/render/project/src/nltk_data',
        '/opt/render/nltk_data',
        # Heroku/other cloud platforms
        '/app/nltk_data',
        os.path.join(os.getcwd(), 'nltk_data'),
        # Home directory fallback
        os.path.expanduser('~/nltk_data'),
    ]

    # Add all existing paths to NLTK search path
    paths_added = []
    for path in possible_paths:
        if os.path.exists(path) and path not in nltk.data.path:
            nltk.data.path.insert(0, path)
            paths_added.append(path)

    # Print debug info (will appear in deployment logs)
    if paths_added:
        print(f"[NLTK Setup] Added NLTK data paths: {paths_added}", file=sys.stderr)
    else:
        print(f"[NLTK Setup] WARNING: No NLTK data directories found. Searched: {possible_paths}", file=sys.stderr)

    print(f"[NLTK Setup] Current NLTK data path: {nltk.data.path}", file=sys.stderr)

# Run setup immediately when module is imported
setup_nltk_data()
