"""Test cases for the custom authenticator."""

from os import environ
from typing import cast

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from apps.auth.authentication import JwtAuthentication
from apps.auth.helpers import generate_token
from core.test.seed import generate_test_data
from core.test.stubs import RequestStub, UserStub


class TestAuthentication(TestCase):
    def setUp(self):
        self.authentication = JwtAuthentication()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS

        environ["JWT_SECRET"] = "my-secret"  # nosec
        cls.token = generate_token(data.USERS.owner)

    def test_missing_header(self):
        result = self.authentication.authenticate(cast(Request, RequestStub()))

        self.assertEqual(result, None)

    def test_invalid_header(self):
        request = cast(Request, RequestStub(authorization=f"{self.token}"))

        self.assertEqual(self.authentication.authenticate(request), None)

        request = cast(Request, RequestStub(authorization=f"Token {self.token}"))

        self.assertEqual(self.authentication.authenticate(request), None)

        request = cast(Request, RequestStub(authorization="Bearer"))

        with self.assertRaises(AuthenticationFailed):
            self.authentication.authenticate(request)

    def test_invalid_token(self):
        environ["JWT_SECRET"] = "wrong-secret"  # nosec
        token = generate_token(self.USERS.owner)
        environ["JWT_SECRET"] = "my-secret"  # nosec

        request = cast(Request, RequestStub(authorization=f"Bearer {token}"))

        with self.assertRaises(AuthenticationFailed):
            self.authentication.authenticate(request)

    def test_non_existent_user(self):
        token = generate_token(cast(User, UserStub("non-existent")))

        request = cast(Request, RequestStub(authorization=f"Bearer {token}"))

        with self.assertRaises(AuthenticationFailed):
            self.authentication.authenticate(request)

    def test_authentication(self):
        request = cast(Request, RequestStub(authorization=f"Bearer {self.token}"))

        result = self.authentication.authenticate(request)

        self.assertEqual(result[0], self.USERS.owner)
