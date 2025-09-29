from fastapi import APIRouter, HTTPException, status, Body
from ..schema.schemas import UserCreate, UserOut
from ..storage import repo

router = APIRouter()

@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User berhasil dibuat"},
        400: {"description": "Username/email duplikat"},
        422: {"description": "Validasi gagal (misalnya email bukan gmail)"},
    },
)
def create_user(
    payload: UserCreate = Body(
        ...,
        examples={
            "valid": {
                "summary": "Valid (Gmail)",
                "value": {
                    "username": "ayu123",
                    "email": "ayu@gmail.com",
                    "password": "Aa1!aaaa",
                    "role": "staff"
                },
            },
            "invalid_email_domain": {
                "summary": "Invalid (bukan gmail.com)",
                "value": {
                    "username": "ayu124",
                    "email": "ayu@yahoo.com",
                    "password": "Aa1!aaaa",
                    "role": "staff"
                },
            },
            "invalid_email_format": {
                "summary": "Invalid format (tanpa .com)",
                "value": {
                    "username": "ayu125",
                    "email": "ayu@gmail",
                    "password": "Aa1!aaaa",
                    "role": "staff"
                },
            },
        },
    )
):
    try:
        user = repo.create(payload)
        # exclude password_hash biar ga bocor
        return UserOut(**user.model_dump(exclude={"password_hash"}))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))