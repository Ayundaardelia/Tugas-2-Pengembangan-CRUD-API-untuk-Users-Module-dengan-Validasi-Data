from datetime import datetime
from typing import Literal, Optional
import re
from pydantic import BaseModel, EmailStr, Field, field_validator

Role = Literal["admin", "staff"]

USERNAME_REGEX = r"^[a-z0-9]{6,15}$"
ALLOWED_CHARS = re.compile(r"^[A-Za-z\d!@]+$")

class UserBase(BaseModel):
    username: str = Field(pattern=USERNAME_REGEX)
    email: EmailStr
    role: Role

class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        # panjang
        if not (8 <= len(v) <= 20):
            raise ValueError("password length must be 8–20")
        # karakter yang diizinkan saja
        if not ALLOWED_CHARS.fullmatch(v):
            raise ValueError("password may contain only letters, digits, and ! or @")
        # komposisi: kecil, besar, digit, spesial
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

class UserOut(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        # pakai aturan yang sama seperti di atas
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

# Model internal penyimpanan (dengan hash password)
class _UserInDB(UserBase):
    id: str
    password_hash: str
    created_at: datetime
    updated_at: datetime