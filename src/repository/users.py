from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
import src.services.auth as auth
from src.shemas.user import UserSchema


async def get_user_by_email(email: str, db: Session = Depends(get_db)):

    """
    The get_user_by_email function takes in an email address and returns the user associated with that email.
    If no user is found, it will return None.

    :param email: str: Specify the type of data that will be passed into the function
    :param db: Session: Pass the database session to the function
    :return: A user object if the email exists in the database
    """
    stmt = select(User).filter_by(email=email)
    user = db.execute(stmt)
    user = user.scalar_one_or_none()

    return user


async def create_user(body: UserSchema, db: Session = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param db: Session: Pass the database session to the function
    :return: A user object
    """
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


async def update_token(user: User, refresh_token: str | None, db: Session = Depends(get_db)):
    """
    The update_token function updates the refresh_token for a user.

    :param user: User: Get the user object from the database
    :param refresh_token: str | None: Update the refresh_token in the database
    :param db: Session: Pass the database session to the function
    :return: A user object
    """
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:

    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Get the email address of the user
    :param db: Session: Pass in the database session
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def change_password(email: str, password: str, db: Session) -> None:
    """
    The change_password function takes in an email and a password, then changes the user's password to the new one.
    :param email: str: Identify the user who's password is being changed
    :param password: str: Store the password that is passed in
    :param db: Session: Pass the database session into the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.password = auth.auth_service.get_password_hash(password)
    db.commit()


async def update_avatar_url(email: str, avatar_url: str, db: Session) -> User:
    """
    The update_avatar_url function updates the avatar_url of a user in the database.

    :param email: str: Get the user from the database
    :param avatar_url: str: Update the avatar url of a user
    :param db: Session: Create a session with the database
    :return: The user object with the updated avatar url

    """
    user = await get_user_by_email(email, db)
    user.avatar = avatar_url
    db.commit()
    db.refresh(user)

    return user
