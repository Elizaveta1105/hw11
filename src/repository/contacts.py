from datetime import datetime, timedelta

from sqlalchemy import select, and_, extract, or_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.shemas.contacts import ContactSchema, ContactUpdateSchema, ContactSearchSchema


async def get_contacts(limit: int, offset: int, db: Session, user: User):
    """
    The get_contacts function fetches a list of contacts for a specific user with pagination.

    :param limit: int: Specify the number of contacts to return
    :param offset: int: Specify the number of contacts to skip
    :param db: Session: Pass in the database session
    :param user: User: Filter the contacts by user
    :return: A list of contacts
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    result = db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def get_contact(contact_id: int, db: Session, user: User):
    """
    Fetches a specific contact for a user.
    :param contact_id:
    :param db:
    :param user:
    :return:
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: Session, user: User):
    """
    The create_contact function creates a new contact in the database.
    :param body: ContactSchema: Validate the data that is passed in
    :param db: Session: Pass in the database session
    :param user: User: Get the user id from the token
    :return: The contact object that was just created
    """

    contact = Contact(**body.dict(), user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactUpdateSchema, contact_id: int, db: Session, user: User):
    """
    The update_contact function updates a contact in the database.
    :param body: ContactUpdateSchema: Validate the body of the request
    :param contact_id: int: Identify the contact to be updated
    :param db: Session: Pass the database session to the function
    :param user: User: Ensure that the user is authorized to update the contact
    :return: The updated contact object
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = db.execute(stmt)
    contact = result.scalar_one_or_none()
    for key, value in body.dict().items():
        if value is not None:
            setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: Session, user: User):
    """
    :param contact_id: int: Identify the contact to be deleted
    :param db: Session: Access the database
    :param user: User: Check if the user is authorized to delete the contact
    :return: The contact that was deleted
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def find_contacts(body: ContactSearchSchema, db: Session, user: User):
    """
    The find_contacts function is used to search for contacts in the database.
    It takes a ContactSearchSchema as input, which contains all of the fields that can be searched on.
    The function then creates a list of conditions based on what values are present in the schema, and uses those conditions to filter out results from the database.

    :param body: ContactSearchSchema: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :param user: User: Get the user from the database
    :return: A list of contacts that match the search criteria
    """
    conditions = []
    for key, value in body.dict().items():
        if value is not None:
            conditions.append(getattr(Contact, key) == value)
    stmt = select(Contact).filter_by(user=user).where(and_(*conditions))
    result = db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def get_birthday_contacts(limit: int, offset: int, db: Session, user: User):
    """
    :param limit: int: Limit the number of results returned
    :param offset: int: Specify the number of records to skip
    :param db: Session: Pass the database session to the function
    :param user: User: Filter the results by user
    :return: A list of contacts whose birthday is within the next 7 days
    """
    next_7_days = [datetime.now().date() + timedelta(days=i) for i in range(7)]
    condition = or_(
        *[extract('day', Contact.birthday) == date.day and extract('month', Contact.birthday) == date.month for date in
          next_7_days])

    stmt = select(Contact).filter_by(user=user).limit(limit).offset(offset).where(condition)
    result = db.execute(stmt)
    contacts = result.scalars().all()

    return contacts
