from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView
from .serializers import (
    ChatGroupeListSerializer,
    MessageSerilizer,
    GroupMemberListSerilizer,
    GroupMediaSerializer,
)
from ..models import ChatGroup, Message, GroupMember

from rest_framework.permissions import IsAuthenticated
from ..pagination import ChatPagination
from ..permissions import IsChatRoomOwner
from django.shortcuts import get_object_or_404
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
    
  
  #! send media

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
        
class ListOfGroupMember(ListAPIView):
    serializer_class = GroupMemberListSerilizer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        group_id = self.kwargs['group_id']
        if not GroupMember.objects.filter(chat_group_id=group_id, user=self.request.user, is_active=True).exists():
            raise PermissionDenied("You are not an active member of this chat group.")
            
        return GroupMember.objects.filter(
            chat_group_id=group_id, 
            is_active=True
        ).select_related('user', 'user__user_profile').order_by('joined_at')


class GroupMediaListView(ListAPIView):
    serializer_class = GroupMediaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ChatPagination

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        if not GroupMember.objects.filter(chat_group_id=group_id, user=self.request.user, is_active=True).exists():
            raise PermissionDenied("You are not an active member of this chat group.")

        return Message.objects.filter(
            group_id=group_id,
            file__isnull=False
        ).exclude(file="").order_by('-created_at')

