from rest_framework import permissions


class IsOwnerOrSuperUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user == obj.user
        )


class TokenHasScopeOrSuperUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        token = request.auth
        user = request.user
        if user.is_authenticated and user.is_superuser:
            return True

        if not token:
            return False

        if hasattr(token, "scope"):
            required_scopes = view.required_scopes
            return token.is_valid(required_scopes)

        return False
