from fastapi import APIRouter, Depends, HTTPException, status
from ..schema.schemas import UserUpdate, UserOut, PasswordChange
from ..storage import repo
from ..deps import get_current_user
from ..utils import verify_password

router = APIRouter()

@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: str, patch: UserUpdate, user = Depends(get_current_user)):
    rec = repo.get(user_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Not found")
    # admin or owner
    if user["role"] != "admin" and user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        updated = repo.update(user_id, patch)
        return UserOut(**updated.model_dump(exclude={"password_hash"}))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}/password")
def change_password(user_id: str, body: PasswordChange, user = Depends(get_current_user)):
    rec = repo.get(user_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Not found")

    # hanya owner yang boleh ganti sendiri; admin boleh override (opsional)
    if user["role"] != "admin" and user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # jika bukan admin, wajib verifikasi current_password
    if user["role"] != "admin":
        if not verify_password(body.current_password, rec.password_hash):
            raise HTTPException(status_code=403, detail="Current password incorrect")

    repo.change_password(user_id, body.new_password)
    return {"status": "ok"}