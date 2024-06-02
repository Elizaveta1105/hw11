from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
import src.services.auth as auth
from src.shemas.user import UserSchema


async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    stmt = select(User).filter_by(email=email)
    user = db.execute(stmt)
    user = user.scalar_one_or_none()

    return user


async def create_user(body: UserSchema, db: Session = Depends(get_db)):
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


async def update_token(user: User, refresh_token: str | None, db: Session = Depends(get_db)):
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def change_password(email: str, password: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.password = auth.auth_service.get_password_hash(password)
    db.commit()


async def update_avatar_url(email: str, avatar_url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = avatar_url
    db.commit()
    db.refresh(user)

    return user
