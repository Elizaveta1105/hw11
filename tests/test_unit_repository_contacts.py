import unittest
from datetime import date
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.shemas.contacts import ContactSchema, ContactUpdateSchema, ContactSearchSchema
from src.repository.contacts import get_contacts, get_contact, create_contact, update_contact, delete_contact


class TestContacts(unittest.TestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username="test_user", password="qwerty", confirmed=True)
        self.session = Mock(spec=Session)

    async def test_get_contacts(self):
        limit = 10
        offset = 0

        contacts = [Contact(id=1, name="Contact1", surname="Surname", email="contacts1@test.com", phone=12345678, birthday=date(1990, 1, 1), user=self.user),
                    Contact(id=2, name="Contact2", surname="Surname", email="contacts2@test.com", phone=12345678, birthday=date(1990, 2, 1), user=self.user)]

        mocked_contacts = MagicMock()
        mocked_contacts.scalars().all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact_id = 1
        contact = Contact(id=1, name="Contact1", surname="Surname", email="contacts1@test.com", phone=12345678, birthday=date(1990, 1, 1), user=self.user)
        self.session.execute.return_value.scalar_one_or_none.return_value = contact
        result = await get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        body = ContactSchema(name="Contact3", surname="Surname", email="contacts3@test.com", phone=12345678, birthday=date(1990, 3, 1), user=self.user)
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)

    async def test_update_contact(self):
        body = ContactUpdateSchema(name="Contact3", surname="Surname", email="contacts3@test.com", phone=12345678, birthday=date(1990, 3, 1), user=self.user)
        contact_id = 1
        contact = Contact(id=1, name="Contact1", surname="Surname", email="contacts1@test.com", phone=12345678, birthday=date(1990, 1, 1), user=self.user)
        self.session.execute.return_value.scalar_one_or_none.return_value = contact
        result = await update_contact(body, contact_id, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)

    async def test_delete_contact(self):
        contact_id = 1
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, name="Contact1", surname="Surname", email="contacts1@test.com", phone=12345678, birthday=date(1990, 1, 1), user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(contact_id, self.session, self.user)
        self.session.assert_called_once()
        self.assertIsInstance(result, Contact)


