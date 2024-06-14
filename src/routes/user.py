import pickle

import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.shemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repo_users

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    Fetches the current logged in user.

    Args:
        user (User): The user object.

    Returns:
        UserResponse: The UserResponse object of the current user.
    """
    return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(
        file: UploadFile = File(),
        user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db),
):
    """
    Updates the avatar of the current logged in user.

    Args:
        file (UploadFile): The new avatar file.
        user (User): The user object.
        db (Session): The database session.

    Returns:
        UserResponse: The UserResponse object of the current user with the updated avatar.
    """
    public_id = f"users/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repo_users.update_avatar_url(user.email, res_url, db)
    return user
