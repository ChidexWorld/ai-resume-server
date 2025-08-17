"""
Pydantic schemas for authentication endpoints.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from app.models.user import UserType


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    user_type: UserType
    
    # Employer-specific fields
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()
    
    @validator('company_name')
    def validate_company_name(cls, v, values):
        if values.get('user_type') == UserType.EMPLOYER and not v:
            raise ValueError('Company name is required for employers')
        return v


class UserUpdate(BaseModel):
    """Schema for user profile updates."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    
    # Employer-specific fields
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip() if v else v


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str]
    user_type: UserType
    is_active: bool
    is_verified: bool
    
    # Employer-specific fields
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token data."""
    user_id: Optional[int] = None