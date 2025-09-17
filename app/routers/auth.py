"""
Authentication router for user registration, login, and profile management.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.database import get_db
from app.models import User, UserType
from app.config import settings
from app.schemas.auth import UserCreate, UserResponse, Token, UserUpdate, UserLogin
from app.services.auth_service import AuthService

# Create router
router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# HTTP Bearer scheme for Swagger UI authorization
security = HTTPBearer()

# Auth service
auth_service = AuthService()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

    user = auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post(
    "/register",
    response_model=UserResponse,
    summary="Register New User",
    description="Register a new user account as either an employee or employer. Employers must provide company information.",
    response_description="User profile information with unique ID and authentication details",
)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user (employee or employer).

    - **user_type**: Choose 'employee' or 'employer'
    - **email**: Must be unique and valid email address
    - **password**: Must be at least 8 characters long
    - **company_name**: Required for employers, ignored for employees

    Returns the created user profile with unique ID.
    """
    # Check if user already exists
    existing_user = auth_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create user
        user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            user_type=user_data.user_type,
            company_name=user_data.company_name,
            company_website=user_data.company_website,
            company_size=user_data.company_size,
        )

        # Save to database
        db.add(user)
        db.commit()
        db.refresh(user)

        return UserResponse.model_validate(user.to_dict())

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post(
    "/login",
    response_model=Token,
    summary="User Login",
    description="Authenticate user credentials and return JWT access token for API access.",
    response_description="JWT access token and user profile information",
)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.

    - **email**: User's email address
    - **password**: User's password

    Returns JWT token for authenticating subsequent API requests.
    Use the token in Authorization header: `Bearer <token>`
    """
    # Get user by email
    user = auth_service.get_user_by_email(db, login_data.email)

    # Verify user and password
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user.to_dict()),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's profile information."""
    return UserResponse.model_validate(current_user.to_dict())


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile information."""
    try:
        # Update user fields
        update_data = user_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(current_user, field, value)

        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)

        return UserResponse.model_validate(current_user.to_dict())

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}",
        )


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change user's password."""
    # Verify current password
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long",
        )

    try:
        # Update password
        current_user.password_hash = get_password_hash(new_password)
        current_user.updated_at = datetime.utcnow()
        db.commit()

        return {"message": "Password updated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}",
        )


@router.delete("/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Deactivate user account."""
    try:
        current_user.is_active = False
        current_user.updated_at = datetime.utcnow()
        db.commit()

        return {"message": "Account deactivated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account deactivation failed: {str(e)}",
        )


@router.post("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Verify token validity, set user as verified, and return user info."""
    try:
        # Set user as verified
        current_user.is_verified = True
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)

        return {
            "valid": True,
            "user": UserResponse.model_validate(current_user.to_dict()),
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to verify user: {str(e)}")
