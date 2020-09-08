from rest_framework.permissions import IsAuthenticated


class IsSelfOrSuperUser(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user == obj
        )
