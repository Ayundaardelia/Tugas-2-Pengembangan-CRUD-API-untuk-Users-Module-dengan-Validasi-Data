from fastapi import Header, HTTPException, status

def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
):
    if not x_user_id or not x_user_role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth headers")
    if x_user_role not in ("admin", "staff"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid role")
    return {"id": x_user_id, "role": x_user_role}