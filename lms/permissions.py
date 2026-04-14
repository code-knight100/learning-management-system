

def has_role(user, role_name):
    return user.groups.filter(name=role_name).exists()


from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and has_role(request.user, "Admin")
    
    
class IsInstructorRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and has_role(request.user, "Instructor")
    
    
class IsStudentRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and has_role(request.user, "Student")
    
    
class IsSponsorRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and has_role(request.user, "Sponsor")
    
    
class IsAdminOrInstructor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            has_role(request.user, "Admin") or
            has_role(request.user, "Instructor")
        )
        
        
class IsStudentOrInstructor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            has_role(request.user, "Student") or
            has_role(request.user, "Instructor")
        )
        
        
class IsSponsorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            has_role(request.user, "Sponsor") or
            has_role(request.user, "Admin")
        )
        
        
from rest_framework.permissions import BasePermission
from .permissions import has_role


class CanMakePayment(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and (
                has_role(request.user, "Student") or
                has_role(request.user, "Admin") or
                has_role(request.user, "Sponsor")
            )
        )
        
        
