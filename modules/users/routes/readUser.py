from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..schema.schemas import UserOut
from ..storage import repo
from ..deps import get_current_user

router = APIRouter()

@router.get("", response_model=List[UserOut])
def list_users(user = Depends(get_current_user)):
    # admin only
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    rows = [UserOut(**u.model_dump(exclude={"password_hash"})) for u in repo.list_all()]
    return rows

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, user = Depends(get_current_user)):
    rec = repo.get(user_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Not found")
    # admin or owner
    if user["role"] != "admin" and user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return UserOut(**rec.model_dump(exclude={"password_hash"}))