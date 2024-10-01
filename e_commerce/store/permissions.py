from rest_framework import permissions


class IsSeller(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'seller' role to access the Product API.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return hasattr(request.user, 'role') and request.user.role.role == 'Seller'
        return False
