#!/usr/bin/env python3
"""
Service status checker for AI Resume Server.
"""

import sys
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Check and display service status."""
    print("🔍 AI Resume Server - Service Status Check")
    print("=" * 50)

    try:
        from app.services import get_service_status
        status = get_service_status()

        print("📊 Service Status:")
        print(json.dumps(status, indent=2))

        # Summary
        print("\n📋 Summary:")
        dm_status = status["dataset_manager"]["status"]
        ai_status = status["ai_service"]["status"]

        print(f"   Dataset Manager: {'✅' if dm_status == 'ready' else '❌'} {dm_status}")
        print(f"   AI Service: {'✅' if ai_status == 'ready' else '❌'} {ai_status}")

        if dm_status == "ready":
            stats = status["dataset_manager"]["stats"]
            print(f"\n📈 Dataset Statistics:")
            print(f"   Skills: {stats['skills']['total_skills']} across {stats['skills']['total_industries']} industries")
            print(f"   Job Titles: {stats['job_titles']['total_titles']} across {stats['job_titles']['total_industries']} industries")
            print(f"   Certifications: {stats['certifications']['total_certifications']} across {stats['certifications']['total_industries']} industries")

        if ai_status == "ready":
            models = status["ai_service"]["models_loaded"]
            print(f"\n🤖 AI Models Status:")
            print(f"   Whisper: {'✅ Loaded' if models['whisper'] else '💤 Not loaded (lazy)'}")
            print(f"   Sentence Transformer: {'✅ Loaded' if models['sentence_transformer'] else '💤 Not loaded (lazy)'}")
            print(f"   spaCy NLP: {'✅ Loaded' if models['spacy'] else '💤 Not loaded (lazy)'}")

    except Exception as e:
        print(f"❌ Error checking services: {e}")
        sys.exit(1)

    print("=" * 50)

if __name__ == "__main__":
    main()