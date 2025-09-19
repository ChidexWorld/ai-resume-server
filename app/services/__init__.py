"""
Services package initialization.
Provides centralized access to AI and dataset management services.
"""

# Import dataset manager first (no heavy dependencies)
from .dataset_manager import DatasetManager, dataset_manager

# Try to import AI service with graceful fallback
try:
    from .ai_service import AIService, ai_service
    AI_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI service dependencies not available: {e}")
    AI_SERVICE_AVAILABLE = False
    ai_service = None
    AIService = None

__all__ = ["DatasetManager", "dataset_manager", "AIService", "ai_service", "AI_SERVICE_AVAILABLE"]


def initialize_services():
    """Initialize all services and return their status."""
    service_status = {
        "dataset_manager": False,
        "ai_service": False,
        "errors": []
    }

    try:
        # Initialize dataset manager
        stats = dataset_manager.get_dataset_stats()
        service_status["dataset_manager"] = True
        print(f"✓ Dataset manager loaded: {stats['skills']['total_skills']} skills, "
              f"{stats['job_titles']['total_titles']} job titles")

    except Exception as e:
        service_status["errors"].append(f"Dataset manager failed: {str(e)}")
        print(f"✗ Dataset manager initialization failed: {e}")

    if AI_SERVICE_AVAILABLE:
        try:
            # AI service is initialized but models are loaded lazily
            service_status["ai_service"] = True
            print("✓ AI service initialized (models will load on first use)")

        except Exception as e:
            service_status["errors"].append(f"AI service failed: {str(e)}")
            print(f"✗ AI service initialization failed: {e}")
    else:
        service_status["errors"].append("AI service dependencies not installed")
        print("✗ AI service not available (missing dependencies)")

    return service_status


def get_service_status():
    """Get current status of all services."""
    status = {
        "dataset_manager": {
            "status": "ready",
            "stats": dataset_manager.get_dataset_stats()
        }
    }

    if AI_SERVICE_AVAILABLE and ai_service:
        status["ai_service"] = {
            "status": "ready",
            "models_loaded": {
                "whisper": ai_service._whisper_model is not None,
                "sentence_transformer": ai_service._sentence_model is not None,
                "spacy": ai_service._nlp_model is not None
            }
        }
    else:
        status["ai_service"] = {
            "status": "unavailable",
            "reason": "Dependencies not installed"
        }

    return status