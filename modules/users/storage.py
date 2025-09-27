from __future__ import annotations
from typing import Dict, List, Optional
from datetime import datetime, timezone
from uuid import uuid4

from .schema.schemas import _UserInDB, UserCreate, UserUpdate, Role
from .utils import hash_password

class UserRepo:
    """In-memory repository (cukup untuk tugas & unit test)."""
    def __init__(self) -> None:
        self._data: Dict[str, _UserInDB] = {}

    # --- helpers
    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _ensure_unique(self, username: str, email: str, exclude_id: Optional[str] = None) -> None:
        for u in self._data.values():
            if exclude_id and u.id == exclude_id:
                continue
            if u.username == username:
                raise ValueError("username already exists")
            if u.email == email:
                raise ValueError("email already exists")

    # --- CRUD
    def create(self, payload: UserCreate) -> _UserInDB:
        self._ensure_unique(payload.username, payload.email)
        uid = str(uuid4())
        now = self._now()
        rec = _UserInDB(
            id=uid,
            username=payload.username,
            email=payload.email,
            role=payload.role,
            password_hash=hash_password(payload.password),
            created_at=now,
            updated_at=now,
        )
        self._data[uid] = rec
        return rec

    def list_all(self) -> List[_UserInDB]:
        return list(self._data.values())

    def get(self, user_id: str) -> Optional[_UserInDB]:
        return self._data.get(user_id)

    def update(self, user_id: str, patch: UserUpdate) -> _UserInDB:
        user = self._data.get(user_id)
        if not user:
            raise KeyError("not found")

        new_username = patch.username if patch.username is not None else user.username
        new_email = patch.email if patch.email is not None else user.email
        self._ensure_unique(new_username, new_email, exclude_id=user_id)

        if patch.username is not None:
            user.username = patch.username
        if patch.email is not None:
            user.email = patch.email
        if patch.role is not None:
            user.role = patch.role
        user.updated_at = self._now()
        self._data[user_id] = user
        return user

    def delete(self, user_id: str) -> None:
        if user_id not in self._data:
            raise KeyError("not found")
        del self._data[user_id]

    def change_password(self, user_id: str, new_raw_password: str) -> None:
        user = self._data.get(user_id)
        if not user:
            raise KeyError("not found")
        user.password_hash = hash_password(new_raw_password)
        user.updated_at = self._now()
        self._data[user_id] = user

# singleton repo
repo = UserRepo()