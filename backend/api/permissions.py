from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrAdmin(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif (request.method == 'POST' and request.user.is_authenticated):
            return True
        elif (request.method in ('PUT', 'PATCH', 'DELETE')
                and request.user.is_authenticated
                and (request.user == obj.author or request.user.is_admin)):
            return True
        return False
