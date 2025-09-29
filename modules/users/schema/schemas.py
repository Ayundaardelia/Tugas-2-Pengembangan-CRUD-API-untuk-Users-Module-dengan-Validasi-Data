from datetime import datetime
from typing import Literal, Optional
import re
from pydantic import BaseModel, EmailStr, Field, field_validator

# Role hanya boleh admin atau staff
Role = Literal["admin", "staff"]

# Aturan username: huruf kecil + angka, 6-15 karakter
USERNAME_REGEX = r"^[a-z0-9]{6,15}$"

# Aturan password: huruf, angka, simbol ! atau @
ALLOWED_CHARS = re.compile(r"^[A-Za-z\d!@]+$")


# --- Validator khusus email ---
def _ensure_gmail(email: str) -> str:
    if not email.lower().endswith("@gmail.com"):
        raise ValueError("email domain must be gmail.com")
    return email


class UserBase(BaseModel):
    username: str = Field(pattern=USERNAME_REGEX)
    email: EmailStr
    role: Role

    @field_validator("email")
    @classmethod
    def email_must_be_gmail(cls, v: EmailStr) -> EmailStr:
        _ensure_gmail(str(v))
        return v


class UserCreate(UserBase):
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "ayu123",
                "email": "ayu@gmail.com",
                "password": "Aa1!aaaa",
                "role": "staff"
            }
        }
    }

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not (8 <= len(v) <= 20):
            raise ValueError("password length must be 8–20")
        if not ALLOWED_CHARS.fullmatch(v):
            raise ValueError("password may contain only letters, digits, and ! or @")
        if not any(c.islower() for c in v):
            raise ValueError("password must contain a lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("password must contain an uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain a digit")
        if not any(c in "!@" for c in v):
            raise ValueError("password must contain ! or @")
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, pattern=USERNAME_REGEX)
    email: Optional[EmailStr] = None
    role: Optional[Role] = None

    @field_validator("email")
    @classmethod
    def email_must_be_gmail_optional(cls, v: EmailStr | None) -> EmailStr | None:
        if v is None:
            return v
        _ensure_gmail(str(v))
        return v


class UserOut(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "8f1a2b1c-7b26-4a2c-83c6-2f6c2e0de9ab",
                "username": "ayu123",
                "email": "ayu@gmail.com",
                "role": "staff",
                "created_at": "2025-09-29T10:00:00Z",
                "updated_at": "2025-09-29T10:00:00Z"
            }
        }
    }


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not (8 <= len(v) <= 20):
            raise ValueError("password length must be 8–20")
        if not ALLOWED_CHARS.fullmatch(v):
            raise ValueError("password may contain only letters, digits, and ! or @")
        if not any(c.islower() for c in v):
            raise ValueError("password must contain a lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("password must contain an uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain a digit")
        if not any(c in "!@" for c in v):
            raise ValueError("password must contain ! or @")
        return v


# Model internal penyimpanan (password disimpan sebagai hash)
class _UserInDB(UserBase):
    id: str
    password_hash: str
    created_at: datetime
    updated_at: datetime