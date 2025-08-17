"""
Router package initialization.
"""
from app.routers import auth, employee, employer, matching, admin

__all__ = ["auth", "employee", "employer", "matching", "admin"]