"""
Authentication service for user management.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models import User


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email.lower().strip()).first()
    
    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        """Create a new user."""
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user