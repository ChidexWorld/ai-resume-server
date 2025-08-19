"""
Router package initialization.
Import routers individually to avoid circular imports.
"""
# Individual router imports
from app.routers import auth
from app.routers import employee  
from app.routers import employer
from app.routers import matching
from app.routers import admin

__all__ = ["auth", "employee", "employer", "matching", "admin"]