"""Test cases for the shared custom permissions."""

from django.test import TestCase
from src.lib.permissions import IsBot, IsOwnerOrAdmin

from ..seed import generate_test_data
from ..stubs import RequestStub


class TestIsBotPermission(TestCase):
    """
    Only a user in the bot group could access the view.
    """

    def setUp(self):
        self.permission = IsBot()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS

    def test_bot_could_access(self):
        request = RequestStub(user=self.USERS.bot)

        self.assertTrue(self.permission.has_permission(request, None))

    def test_other_couldnt_access(self):
        request = RequestStub(user=self.USERS.other)

        self.assertFalse(self.permission.has_permission(request, None))

    def test_admin_couldnt_access(self):
        request = RequestStub(user=self.USERS.admin)

        self.assertFalse(self.permission.has_permission(request, None))


class TestIsOwnerOrAdminPermission(TestCase):
    """
    Only an admin and the owner could access the object.
    """

    def setUp(self):
        self.permission = IsOwnerOrAdmin()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS

    def test_owner_could_access(self):
        request = RequestStub(user=self.USERS.owner)

        self.assertTrue(
            self.permission.has_object_permission(request, None, self.PORTFOLIOS.main)
        )

    def test_admin_could_access(self):
        request = RequestStub(user=self.USERS.admin)

        self.assertTrue(
            self.permission.has_object_permission(request, None, self.PORTFOLIOS.main)
        )

    def test_other_couldnt_access(self):
        request = RequestStub(user=self.USERS.other)

        self.assertFalse(
            self.permission.has_object_permission(request, None, self.PORTFOLIOS.main)
        )
