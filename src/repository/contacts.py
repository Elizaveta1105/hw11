from datetime import datetime, timedelta

from sqlalchemy import select, and_, extract, or_
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactSchema, ContactUpdateSchema, ContactSearchSchema


async def get_contacts(limit: int, offset: int, db: Session):
    stmt = select(Contact).limit(limit).offset(offset)
    result = db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def get_contact(contact_id: int, db: Session):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: Session):
    contact = Contact(**body.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactUpdateSchema, contact_id: int, db: Session):
    stmt = select(Contact).filter_by(id=contact_id)
    result = db.execute(stmt)
    contact = result.scalar_one_or_none()
    for key, value in body.dict().items():
        if value is not None:
            setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: Session):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def find_contacts(body: ContactSearchSchema, db: Session):
    conditions = []
    for key, value in body.dict().items():
        if value is not None:
            conditions.append(getattr(Contact, key) == value)
    stmt = select(Contact).where(and_(*conditions))
    result = db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def get_birthday_contacts(limit: int, offset: int, db: Session):
    next_7_days = [datetime.now().date() + timedelta(days=i) for i in range(7)]
    condition = or_(
        *[extract('day', Contact.birthday) == date.day and extract('month', Contact.birthday) == date.month for date in
          next_7_days])

    stmt = select(Contact).limit(limit).offset(offset).where(condition)
    result = db.execute(stmt)
    contacts = result.scalars().all()

    return contacts
