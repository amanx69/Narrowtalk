from rest_framework.generics import ListAPIView ,UpdateAPIView
from .serializers import ChatGroupeListSerializer,MessageSerilizer
from ..models import ChatGroup ,Message
from rest_framework.permissions import IsAuthenticated
from ..pagination import ChatPagination
from ..permissions import IsChatRoomOwner
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import PermissionDenied

#! chat list 
class ChatListViews(ListAPIView):
    serializer_class=ChatGroupeListSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        return  ChatGroup.objects.filter(members__user=self.request.user)
    
    
class ChatMessageHistoryView(ListAPIView):
    serializer_class=MessageSerilizer
    permission_classes=[IsAuthenticated]
    pagination_class=ChatPagination
    
    
    def get_queryset(self):
        return  Message.objects.filter(
            group_id=self.kwargs['group_id'],
            
            group__members__user=self.request.user
            
        ).order_by('-created_at')
        
#! class update chatroom

class UpdateChatRoomView(UpdateAPIView):
    serializer_class= ChatGroupeListSerializer
    permission_classes=[IsAuthenticated,IsChatRoomOwner]
    queryset=ChatGroup.objects.all()
    lookup_field = 'id'  
    
  
  

class SendMessageView(CreateAPIView):
    serializer_class = MessageSerilizer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        group_id=self.kwargs['group_id']
        try:
            ChatGroup.objects.get(
                id=group_id, 
                members__user=self.request.user, 
                members__is_active=True
            )
        except ChatGroup.DoesNotExist:
            raise PermissionDenied("You are not an active member of this chat group.")
        serializer.save(
            sender=self.request.user,
            group_id=group_id
        )