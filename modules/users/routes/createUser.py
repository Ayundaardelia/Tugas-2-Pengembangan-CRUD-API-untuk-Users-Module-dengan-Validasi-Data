from fastapi import APIRouter, HTTPException, status
from ..schema.schemas import UserCreate, UserOut
from ..storage import repo

router = APIRouter()

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    try:
        user = repo.create(payload)
        return UserOut(**user.model_dump(exclude={"password_hash"}))
    except ValueError as e:
        # duplikasi username/email
        raise HTTPException(status_code=400, detail=str(e))