#!/usr/bin/env python3
"""
Script to create an admin user.
Usage: python create_admin.py
"""
import sys
import os
from getpass import getpass

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserType
from app.services.auth_service import AuthService


def create_admin_user():
    """Create an admin user interactively."""
    print("=== Create Admin User ===\n")

    # Get user input
    email = input("Enter admin email: ").strip()
    if not email:
        print("Error: Email is required")
        return

    first_name = input("Enter first name: ").strip()
    if not first_name:
        print("Error: First name is required")
        return

    last_name = input("Enter last name: ").strip()
    if not last_name:
        print("Error: Last name is required")
        return

    phone = input("Enter phone (optional): ").strip() or None

    password = getpass("Enter password (min 8 characters): ")
    if len(password) < 8:
        print("Error: Password must be at least 8 characters")
        return

    password_confirm = getpass("Confirm password: ")
    if password != password_confirm:
        print("Error: Passwords do not match")
        return

    # Create database session
    db = SessionLocal()

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"\nError: User with email '{email}' already exists")

            # Ask if they want to convert to admin
            convert = input("Would you like to convert this user to admin? (y/n): ").strip().lower()
            if convert == 'y':
                existing_user.user_type = UserType.ADMIN
                existing_user.is_verified = True
                db.commit()
                print(f"\n✓ User '{email}' has been converted to admin!")
                print(f"  Name: {existing_user.full_name}")
                print(f"  User Type: {existing_user.user_type.value}")
            return

        # Hash the password
        password_hash = AuthService.hash_password(password)

        # Create admin user
        admin_user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            user_type=UserType.ADMIN,
            is_active=True,
            is_verified=True  # Auto-verify admin users
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("\n✓ Admin user created successfully!")
        print(f"  ID: {admin_user.id}")
        print(f"  Email: {admin_user.email}")
        print(f"  Name: {admin_user.full_name}")
        print(f"  User Type: {admin_user.user_type.value}")
        print(f"  Status: Active & Verified")

    except Exception as e:
        db.rollback()
        print(f"\nError creating admin user: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        create_admin_user()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)
