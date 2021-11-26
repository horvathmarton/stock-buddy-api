"""Test cases for the shared custom permissions."""

from django.contrib.auth.models import Group, User
from django.test import TestCase
from src.stocks.models import StockPortfolio

from .permissions import IsBot, IsOwnerOrAdmin


class _RequestStub:
    """Stub class for Django's request object in test cases."""

    # The stub object is not required to be a valid class.
    # pylint: disable=too-few-public-methods

    def __init__(self, user: User):
        self.user = user


class TestIsBotPermission(TestCase):
    """
    Only a user in the bot group could access the view.
    """

    def setUp(self):
        self.permission = IsBot()

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            "admin",
            "admin@stock-buddy.com",
            "password",
            is_superuser=True,
            is_staff=True,
        )
        cls.bot = User.objects.create_user("bot", "bot@stock-buddy.com", "password")
        cls.other = User.objects.create_user(
            "other", "other@stock-buddy.com", "password"
        )

        admin_group = Group.objects.create(name="Admins")
        bots_group = Group.objects.create(name="Bots")

        cls.admin.groups.add(admin_group)
        cls.bot.groups.add(bots_group)

    def test_bot_could_access(self):
        request = _RequestStub(self.bot)

        self.assertTrue(self.permission.has_permission(request, None))

    def test_other_couldnt_access(self):
        request = _RequestStub(self.other)

        self.assertFalse(self.permission.has_permission(request, None))

    def test_admin_couldnt_access(self):
        request = _RequestStub(self.admin)

        self.assertFalse(self.permission.has_permission(request, None))


class TestIsOwnerOrAdminPermission(TestCase):
    """
    Only an admin and the owner could access the object.
    """

    def setUp(self):
        self.permission = IsOwnerOrAdmin()

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            "admin",
            "admin@stock-buddy.com",
            "password",
            is_superuser=True,
            is_staff=True,
        )
        cls.owner = User.objects.create_user(
            "owner", "owner@stock-buddy.com", "password"
        )
        cls.other = User.objects.create_user(
            "other", "other@stock-buddy.com", "password"
        )

        admin_group = Group.objects.create(name="Admins")

        cls.admin.groups.add(admin_group)

        cls.object = StockPortfolio.objects.create(name="My portfolio", owner=cls.owner)

    def test_owner_could_access(self):
        request = _RequestStub(self.owner)

        self.assertTrue(
            self.permission.has_object_permission(request, None, self.object)
        )

    def test_admin_could_access(self):
        request = _RequestStub(self.admin)

        self.assertTrue(
            self.permission.has_object_permission(request, None, self.object)
        )

    def test_other_couldnt_access(self):
        request = _RequestStub(self.other)

        self.assertFalse(
            self.permission.has_object_permission(request, None, self.object)
        )
