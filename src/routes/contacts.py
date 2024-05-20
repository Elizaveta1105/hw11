from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ContactSchema, ContactResponse, ContactUpdateSchema, ContactSearchSchema

from src.repository import contacts as contact_repository

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: Session = Depends(get_db)):
    contacts = await contact_repository.get_contacts(limit, offset, db)
    return contacts


@router.get("/birthday", response_model=List[ContactResponse])
async def get_birthday_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                db: Session = Depends(get_db)):
    contacts = await contact_repository.get_birthday_contacts(limit, offset, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = await contact_repository.get_contact(contact_id, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/")
async def create_contact(body: ContactSchema, db: Session = Depends(get_db)):
    contact = await contact_repository.create_contact(body, db)
    return contact


@router.put("/{contact_id}")
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = await contact_repository.update_contact(body, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = await contact_repository.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/find")
async def find_contacts(body: ContactSearchSchema, db: Session = Depends(get_db)):
    contacts = await contact_repository.find_contacts(body, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found")
    return contacts
