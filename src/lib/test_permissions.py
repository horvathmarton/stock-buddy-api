from django.contrib.auth.models import Group, User
from django.test import TestCase

from .permissions import IsBot, IsOwnerOrAdmin


class _RequestStub:
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
        cls.admin = User.objects.create_user('admin', 'admin@stock-buddy.com', 'password', is_superuser=True, is_staff=True)
        cls.bot = User.objects.create_user('bot', 'bot@stock-buddy.com', 'password')
        cls.other = User.objects.create_user('other', 'owner@stock-buddy.com', 'password')

        admin_group = Group.objects.create(name='Admins')
        bots_group = Group.objects.create(name='Bots')

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

    # TODO: Write me!
    pass
