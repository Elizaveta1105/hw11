from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.shemas.contacts import ContactSchema, ContactResponse, ContactUpdateSchema, ContactSearchSchema
from fastapi_limiter.depends import RateLimiter

from src.repository import contacts as contact_repository

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get("/", response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=2, seconds=15))])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Fetches a list of contacts for a specific user with pagination.

    Args:
        limit (int): The number of contacts to return.
        offset (int): The number of contacts to skip before starting to collect the return set.
        db (Session): The database session.
        user (User): The user object.

    Returns:
        List[ContactResponse]: A list of ContactResponse objects.
    """
    contacts = await contact_repository.get_contacts(limit, offset, db, user)
    return contacts


@router.get("/birthday", response_model=List[ContactResponse])
async def get_birthday_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Fetches a list of contacts for a user who have birthdays in the next 7 days.

    Args:
        limit (int): The number of contacts to return.
        offset (int): The number of contacts to skip before starting to collect the return set.
        db (Session): The database session.
        user (User): The user object.

    Returns:
        List[ContactResponse]: A list of ContactResponse objects.
    """
    contacts = await contact_repository.get_birthday_contacts(limit, offset, db, user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Fetches a specific contact for a user.

    Args:
        contact_id (int): The ID of the contact to fetch.
        db (Session): The database session.
        user (User): The user object.

    Returns:
        ContactResponse: The ContactResponse object if found, None otherwise.
    """
    contact = await contact_repository.get_contact(contact_id, db, user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=2, seconds=15))])
async def create_contact(body: ContactSchema, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Creates a new contact for a user.

    Args:
        body (ContactSchema): The contact data.
        db (Session): The database session.
        user (User): The user object.

    Returns:
        ContactResponse: The newly created ContactResponse object.
    """
    contact = await contact_repository.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Updates a specific contact for a user.

    Args:
        body (ContactUpdateSchema): The contact data to update.
        contact_id (int): The ID of the contact to update.
        db (Session): The database session.
        user (User): The user object.

    Returns:
        ContactResponse: The updated ContactResponse object.
    """
    contact = await contact_repository.update_contact(body, contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Deletes a specific contact for a user.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (Session): The database session.
        user (User): The user object.

    Returns:
        None
    """
    contact = await contact_repository.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/find", response_model=List[ContactResponse])
async def find_contacts(body: ContactSearchSchema, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Searches for contacts based on specific criteria.

    Args:
        body (ContactSearchSchema): The search criteria.
        db (Session): The database session.
        user (User): The user object.

    Returns:
        List[ContactResponse]: A list of ContactResponse objects that match the search criteria.
    """
    contacts = await contact_repository.find_contacts(body, db, user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found")
    return contacts
