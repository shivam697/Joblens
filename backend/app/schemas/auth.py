"""
Auth Pydantic Schemas — Request/Response validation for authentication endpoints

Pydantic v2 validates all incoming request data automatically.
If a field fails validation, FastAPI returns a 422 error with a clear message.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class RegisterSchema(BaseModel):
    """Schema for user registration — validates name, email, and password strength."""
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        """Name must be between 2 and 100 characters."""
        if len(value.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        if len(value.strip()) > 100:
            raise ValueError("Name must be at most 100 characters")
        return value.strip()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Password must be at least 8 characters for basic security."""
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value

    @field_validator("confirm_password")
    @classmethod
    def validate_passwords_match(cls, value: str, info) -> str:
        """Confirm password must match the password field."""
        password = info.data.get("password")
        if password and value != password:
            raise ValueError("Passwords do not match")
        return value


class LoginSchema(BaseModel):
    """Schema for user login — just email and password."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Schema for returning user data to the frontend.
    Excludes sensitive fields like password_hash.
    from_attributes=True allows converting SQLAlchemy models directly.
    """
    id: str
    full_name: str
    email: str
    avatar_url: Optional[str] = None
    auth_provider: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
