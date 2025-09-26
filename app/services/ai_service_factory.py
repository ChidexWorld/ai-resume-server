"""
AI Service Factory - Provides easy switching between AI service implementations.
"""

import os
from typing import Union

# Import all AI service implementations
try:
    from .simple_ai_service import SimpleAIService
    SIMPLE_AVAILABLE = True
except ImportError as e:
    print(f"Simple AI Service not available: {e}")
    SIMPLE_AVAILABLE = False

try:
    from .ai_service import AIService
    ORIGINAL_AVAILABLE = True
except ImportError as e:
    print(f"Original AI Service not available: {e}")
    ORIGINAL_AVAILABLE = False

try:
    from .lightweight_ai_service import LightweightAIService
    LIGHTWEIGHT_AVAILABLE = True
except ImportError as e:
    print(f"Lightweight AI Service not available: {e}")
    LIGHTWEIGHT_AVAILABLE = False

try:
    from .enhanced_ai_service import EnhancedAIService
    ENHANCED_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced AI Service not available: {e}")
    ENHANCED_AVAILABLE = False


class AIServiceFactory:
    """
    Factory class for creating AI service instances.
    Allows easy switching between different implementations.
    """

    @staticmethod
    def create_service(service_type: str = "simple") -> Union['SimpleAIService', 'AIService', 'LightweightAIService', 'EnhancedAIService']:
        """
        Create an AI service instance.

        Args:
            service_type: Type of service to create ("simple", "original", "lightweight", or "enhanced")

        Returns:
            AI service instance

        Raises:
            ValueError: If requested service type is not available
        """
        # Check environment variable for override
        env_service_type = os.getenv("AI_SERVICE_TYPE", service_type).lower()

        if env_service_type == "simple":
            if SIMPLE_AVAILABLE:
                print("✓ Using Simple AI Service with dataset_manager.py")
                return SimpleAIService()
            elif ORIGINAL_AVAILABLE:
                print("⚠ Simple AI Service not available, falling back to original")
                return AIService()
            else:
                raise ValueError("No AI service implementations available")

        elif env_service_type == "original":
            if ORIGINAL_AVAILABLE:
                print("✓ Using Original AI Service")
                return AIService()
            elif SIMPLE_AVAILABLE:
                print("⚠ Original AI Service not available, using simple")
                return SimpleAIService()
            else:
                raise ValueError("No AI service implementations available")

        elif env_service_type == "lightweight":
            if LIGHTWEIGHT_AVAILABLE:
                print("✓ Using Lightweight AI Service with enhanced patterns")
                return LightweightAIService()
            elif SIMPLE_AVAILABLE:
                print("⚠ Lightweight AI Service not available, using simple")
                return SimpleAIService()
            elif ORIGINAL_AVAILABLE:
                print("⚠ Lightweight AI Service not available, falling back to original")
                return AIService()
            else:
                raise ValueError("No AI service implementations available")

        elif env_service_type == "enhanced":
            if ENHANCED_AVAILABLE:
                print("✓ Using Enhanced AI Service with Kaggle dataset integration")
                return EnhancedAIService()
            elif SIMPLE_AVAILABLE:
                print("⚠ Enhanced AI Service not available, falling back to simple")
                return SimpleAIService()
            elif ORIGINAL_AVAILABLE:
                print("⚠ Enhanced AI Service not available, falling back to original")
                return AIService()
            else:
                raise ValueError("No AI service implementations available")

        else:
            raise ValueError(f"Unknown service type: {env_service_type}. Available: simple, original, lightweight, enhanced")

    @staticmethod
    def get_available_services() -> list:
        """Get list of available AI service implementations."""
        available = []
        if SIMPLE_AVAILABLE:
            available.append("simple")
        if ORIGINAL_AVAILABLE:
            available.append("original")
        if LIGHTWEIGHT_AVAILABLE:
            available.append("lightweight")
        if ENHANCED_AVAILABLE:
            available.append("enhanced")
        return available

    @staticmethod
    def is_simple_available() -> bool:
        """Check if simple AI service is available."""
        return SIMPLE_AVAILABLE

    @staticmethod
    def is_original_available() -> bool:
        """Check if original AI service is available."""
        return ORIGINAL_AVAILABLE

    @staticmethod
    def is_lightweight_available() -> bool:
        """Check if lightweight AI service is available."""
        return LIGHTWEIGHT_AVAILABLE

    @staticmethod
    def is_enhanced_available() -> bool:
        """Check if enhanced AI service is available."""
        return ENHANCED_AVAILABLE


# Convenience function for easy importing
def get_ai_service(service_type: str = "simple"):
    """Get an AI service instance."""
    return AIServiceFactory.create_service(service_type)


# Default instance for backward compatibility
def create_default_ai_service():
    """Create the default AI service instance."""
    return AIServiceFactory.create_service()