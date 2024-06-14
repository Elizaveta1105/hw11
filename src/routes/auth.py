import json
import pickle

import redis
from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks, Request
from fastapi.params import Security, Form
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.orm import Session
from src.services.users import reset_password_item

from src.conf.config import config
from src.database.db import get_db
from src.services.auth import auth_service
from src.services.email import send_email, send_reset_email
from src.shemas.user import UserSchema, UserResponse, TokenSchema
from src.repository import users as repo_users

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()
cache = redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Registers a new user.

    Args:
        body (UserSchema): The user data.
        bt (BackgroundTasks): Background tasks instance.
        request (Request): The request instance.
        db (Session): The database session.

    Returns:
        UserResponse: The newly created User object.
    """
    user = await repo_users.get_user_by_email(body.email, db)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repo_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and returns access and refresh tokens.

    Args:
        body (OAuth2PasswordRequestForm): The user's credentials.
        db (Session): The database session.

    Returns:
        TokenSchema: The access and refresh tokens.
    """
    user_hash = str(body.username)
    user_data_bytes = cache.get(user_hash)
    if user_data_bytes is None:
        user = await repo_users.get_user_by_email(body.username, db)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User with such email or password not found")
        if not user.confirmed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not confirmed")
        if not auth_service.verify_password(body.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User with such email or password not found")

        access_token = await auth_service.create_access_token(data={"sub": user.email})
        refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
        await repo_users.update_token(user, refresh_token, db)
        user_data = {"access_token": access_token, "refresh_token": refresh_token}
        user_data_bytes = pickle.dumps(user_data)
        cache.set(user_hash, user_data_bytes, ex=600)  # noqa
        cache.expire(user_hash, 60)  # noqa
        print("from db")

        return user_data

    print("from cache")
    return pickle.loads(user_data_bytes)


@router.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
                        db: Session = Depends(get_db)):
    """
    Refreshes the user's tokens.

    Args:
        credentials (HTTPAuthorizationCredentials): The user's current tokens.
        db (Session): The database session.

    Returns:
        dict: The new access and refresh tokens.
    """
    token = credentials.credentials
    email = await auth_service.get_email_form_refresh_token(token)
    user = await repo_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repo_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repo_users.update_token(user, refresh_token, db)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.get('/confirmed_email/{token}', status_code=status.HTTP_200_OK)
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirms a user's email.

    Args:
        token (str): The confirmation token.
        db (Session): The database session.

    Returns:
        dict: A message indicating the email confirmation status.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repo_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repo_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/reset-password', status_code=status.HTTP_200_OK)
async def reset_password(email: str, bt: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Sends a password reset email to a user.

    Args:
        email (str): The user's email.
        bt (BackgroundTasks): Background tasks instance.
        request (Request): The request instance.
        db (Session): The database session.

    Returns:
        dict: A message indicating the status of the email sending process.
    """
    user = await repo_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    try:
        bt.add_task(send_reset_email, user.email, user.username, str(request.base_url))
        return {"message": "Email sent"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not sent")


@router.get('/reset-password/{token}', status_code=status.HTTP_200_OK)
async def reset_password(token:str, request: Request):
    """
    Validates a password reset token.

    Args:
        token (str): The password reset token.
        request (Request): The request instance.

    Returns:
        dict: A message indicating the status of the token validation process.
    """
    email = await auth_service.get_email_from_token(token)
    return await reset_password_item(request, email)


@router.post('/reset-password/{email}', status_code=status.HTTP_200_OK)
async def reset_password(email: str, new_password: str = Form(...), db: Session = Depends(get_db)):
    """
    Resets a user's password.

    Args:
        email (str): The user's email.
        new_password (str): The new password.
        db (Session): The database session.

    Returns:
        dict: A message indicating the status of the password reset process.
    """
    user = await repo_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    await repo_users.change_password(email, new_password, db)

    return {"message": "Changed password"}
