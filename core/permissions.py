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
        return obj.role.project.owner == request.user
    


class IsRoleOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
                    return True
        return obj.project.owner == request.user
        
    
    
class IsProjectMember(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        
        return Membership.objects.filter(
            project=obj, user=request.user
        ).exists()


class IsProjectownerRemove(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
            if request.method in permissions.SAFE_METHODS:
                        return True
            return obj.project.owner == request.user
            
        

