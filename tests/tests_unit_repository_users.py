import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import UserModel

from src.repository.users import (
    get_user_by_email,
    update_avatar,
    create_user,
    update_token,
    confirmed_email
)


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email_found(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email='test@mail', db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email='test@mail', db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(username='test_name',
                         email='test@mail.com',
                         password='TestPassword',
                         avatar='testAvatar')
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertEqual(result.avatar, body.avatar)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_avatar(self):
        self.session.query().filter().first.return_value = self.user
        result = await update_avatar(email=self.user.email, url='test.url', db=self.session)
        self.assertEqual(result.avatar, self.user.avatar)

    async def test_update_token(self):
        await update_token(user=self.user, refresh_token='test_token', db=self.session)
        self.assertEqual(self.user.refresh_token, 'test_token')

    async def test_confirmed_email(self):
        self.session.query().filter().first.return_value = self.user
        await confirmed_email(email=self.user.email, db=self.session)
        self.assertTrue(self.user.confirmed)

