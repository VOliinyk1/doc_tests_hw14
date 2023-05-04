import unittest
import datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, UserModel
from src.repository.contacts import (
    get_contacts,
    get_contact,
    get_nearest_bdays,
    get_contact_by_field,
    create,
    remove,
    update
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter_by().all.return_value = contacts
        result = await get_contacts(current_user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter_by().filter_by().first.return_value = contact
        result = await get_contact(contact_id=1, current_user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter_by().filter_by().first.return_value = None
        result = await get_contact(contact_id=1, current_user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(first_name="Mykola",
                            last_name="Oliinyk",
                            email="mykola@mail.com",
                            phone="+380678965476",
                            birth_date="2004-12-17")
        result = await create(current_user=self.user, body=body, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birth_date, body.birth_date)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter_by().filter_by().first.return_value = contact
        result = await remove(current_user=self.user, contact_id=1, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter_by().filter_by().first.return_value = None
        result = await remove(current_user=self.user, contact_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactModel(first_name="Mykola",
                            last_name="Oliinyk",
                            email="mykola@mail.com",
                            phone="+380678965476",
                            birth_date="2004-12-17")
        contact = Contact()
        self.session.query().filter_by().filter_by().first.return_value = contact
        result = await update(current_user=self.user, contact_id=1, body=body, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactModel(first_name="Mykola",
                            last_name="Oliinyk",
                            email="mykola@mail.com",
                            phone="+380678965476",
                            birth_date="2004-12-17")
        self.session.query().filter_by().filter_by().first.return_value = None
        result = await update(current_user=self.user, contact_id=1, body=body, db=self.session)
        self.assertIsNone(result)

    async def test_nearest_bdays_found(self):
        contacts = [
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date.today() + datetime.timedelta(days=3)),
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date(1995, 4, 28)),
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date.today() + datetime.timedelta(days=1)),
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date(1998, 5, 15)),
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date.today() + datetime.timedelta(days=5)),
        ]
        self.session.query.return_value.filter_by.return_value.all.return_value = contacts
        result = await get_nearest_bdays(current_user=self.user, db=self.session)

        expected_result = [contacts[0], contacts[2], contacts[4]]
        self.assertEqual(result, expected_result)

    async def test_nearest_bdays_not_found(self):
        contacts_not_found = [
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date(2000, 5, 20)),
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date(1995, 4, 25)),
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date(1990, 5, 18)),
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date(1998, 5, 19)),
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date(1980, 5, 30)),
        ]
        self.session.query.return_value.filter_by.return_value.all.return_value = contacts_not_found
        result = await get_nearest_bdays(current_user=self.user, db=self.session)

        return result == []

    async def test_get_contacts_by_field(self):
        contacts = [
            Contact(first_name='John', last_name="Wayne", email="test_1", phone="123456789101112",
                    birth_date=datetime.date(2000, 5, 20)),
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date(1995, 4, 25)),
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date(1990, 5, 18)),
            Contact(first_name='John', last_name="Wayne", email="test_1", phone="123456789101112",
                    birth_date=datetime.date(1990, 5, 19)),
            Contact(first_name='John', last_name="Wayne", email="test", phone="123456789101112",
                    birth_date=datetime.date(1980, 5, 30)),
        ]

        self.session.query.return_value.filter_by.return_value.filter.return_value.all.return_value = [contacts[0],
                                                                                                       contacts[3]]
        result = await get_contact_by_field(current_user=self.user, field_name='email', field_value='test_1',
                                            db=self.session)
        expected_result = [contacts[0], contacts[3]]
        self.assertEqual(result, expected_result)
