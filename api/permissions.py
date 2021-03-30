from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return obj.author == request.user
        return False



class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff and request.user.is_authenticated



class IsModerator(BasePermission):
    roles = ['moderator']
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.role in self.roles:
                return True
        return False        
