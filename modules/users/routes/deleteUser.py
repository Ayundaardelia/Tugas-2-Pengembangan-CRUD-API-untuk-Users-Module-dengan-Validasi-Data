from fastapi import APIRouter, Depends, HTTPException, status
from ..storage import repo
from ..deps import get_current_user

router = APIRouter()

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, user = Depends(get_current_user)):
    # admin only
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        repo.delete(user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Not found")
    return