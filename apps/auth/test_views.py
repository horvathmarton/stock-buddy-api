"""Integration tests for the auth API."""

from os import environ

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from apps.auth.helpers import generate_token
from core.test.seed import generate_test_data


class TestSignIn(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        generate_test_data()

        cls.url = "/auth/sign-in"

    def test_can_sign_in(self):
        response = self.client.post(
            self.url, {"username": "owner", "password": "password"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_cannot_send_malformed(self):
        response = self.client.post(
            self.url, {"email": "owner", "password": "password"}
        )

        self.assertEqual(response.status_code, 400)

    def test_cannot_sign_in_non_existent_user(self):
        response = self.client.post(
            self.url, {"username": "owner100", "password": "password"}
        )

        self.assertEqual(response.status_code, 401)

    def test_cannot_sign_in_with_wrong_password(self):
        response = self.client.post(
            self.url, {"username": "owner", "password": "mypassword"}
        )

        self.assertEqual(response.status_code, 401)


class TestTokenRefresh(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS

        cls.url = "/auth/refresh-token"
        environ["JWT_SECRET"] = "my-secret"  # nosec
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(
            self.url, {"token": generate_token(self.USERS.owner, "refresh")}
        )

        self.assertEqual(response.status_code, 401)

    def test_cannot_send_malformed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 400)

    def test_token_refresh(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(
            self.url, {"token": generate_token(self.USERS.owner, "refresh")}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_invalid_refresh_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        environ["JWT_SECRET"] = "wrong-secret"  # nosec
        refresh_token = generate_token(self.USERS.owner, "refresh")
        environ["JWT_SECRET"] = "my-secret"  # nosec

        response = self.client.post(self.url, {"token": refresh_token})

        self.assertEqual(response.status_code, 401)

    def test_username_mismatch(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(
            self.url, {"token": generate_token(self.USERS.other, "refresh")}
        )

        self.assertEqual(response.status_code, 401)


class TestPasswordChange(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS

        cls.url = "/auth/change-password"
        environ["JWT_SECRET"] = "my-secret"  # nosec
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(
            self.url, {"token": generate_token(self.USERS.owner, "refresh")}
        )

        self.assertEqual(response.status_code, 401)

    def test_cannot_send_malformed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 400)

    def test_change_password(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        previous_password = self.USERS.owner.password
        response = self.client.post(self.url, {"password": "new password"})
        new_password = User.objects.get(username=self.USERS.owner.username).password

        self.assertEqual(response.status_code, 204)
        self.assertNotEqual(new_password, previous_password)
