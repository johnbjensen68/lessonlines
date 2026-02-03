from fastapi import APIRouter, Depends

from ..models import User
from ..schemas import UserResponse
from ..services.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
