from typing import cast

from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsBot(permissions.BasePermission):
    """
    Permission for views that only bot users could access.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = cast(User, request.user)

        return user.groups.filter(name="Bots").exists()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission for resources that could be only accessed
    by the owner or an admin.
    """

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        user = cast(User, request.user)

        if user.groups.filter(name="Admins").exists():
            return True

        return obj.owner == request.user
