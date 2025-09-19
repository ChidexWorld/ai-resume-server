#!/usr/bin/env python3
"""
Enhanced startup script for AI Resume Server.
Initializes both dataset manager and AI service before starting the server.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main startup function."""
    print("=" * 60)
    print("🚀 AI Resume Server - Enhanced Startup")
    print("=" * 60)

    # Initialize services before starting the server
    try:
        from app.services import initialize_services
        print("\n📋 Initializing services...")
        service_status = initialize_services()

        print(f"\n📊 Service Summary:")
        print(f"   Dataset Manager: {'✓' if service_status['dataset_manager'] else '✗'}")
        print(f"   AI Service: {'✓' if service_status['ai_service'] else '✗'}")

        if service_status["errors"]:
            print(f"\n⚠️  Warnings:")
            for error in service_status["errors"]:
                print(f"   - {error}")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        print("The server will start but AI features may not work.")
        print("=" * 60)

    # Import main app after services are initialized
    from main import app

    # Load configuration
    try:
        from app.config import settings
        host = "0.0.0.0"
        port = 8000
        debug = settings.debug
        print(f"🌐 Starting server on http://{host}:{port}")
        print(f"📝 Debug mode: {debug}")
        if debug:
            print("📚 API Documentation: http://localhost:8000/docs")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        host, port, debug = "0.0.0.0", 8000, True

    # Start the server
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if not debug else "debug"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()