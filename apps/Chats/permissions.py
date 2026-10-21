from rest_framework.permissions import BasePermission



class IsChatRoomOwner(BasePermission):
    message = "Only the project owner can update group settings."
    def has_object_permission(self,request,view,obj):
        return  obj.project.owner == request.user
    
    
   