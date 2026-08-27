from rest_framework import permissions
from apps.post.models import Membership

class Isowner(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        return obj.user==request.user
    
    
    
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class IsProjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
                return True
        return obj.role.proejct.owner == request.user
    

class IsProjectMember(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        
        return Membership.objects.filter(
            project=obj, user=request.user
        ).exists()




"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg3ODkxNDUxLCJpYXQiOjE3ODc0NTk0NTEsImp0aSI6Ijk3ZDM0NWQzNmEwYjQ0ZjFhYTY5NTRlZmVmM2Q4NTc3IiwidXNlcl9pZCI6IjJkNDE3YjlkLTBhNDItNDdmNC04OGM3LTc4YTBlYzE2NmM0NSJ9.aYMLkNXcbSZIvfE4hC5LYH2j-bjmzKdfiybzlzLAkww"