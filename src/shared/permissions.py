from rest_framework import permissions

class IsBot(permissions.BasePermission):
    """
    Permission for views that only bot users could access.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Bots").exists()
