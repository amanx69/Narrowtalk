from django.urls import path
from .views import (
    ChatListViews,
    ChatMessageHistoryView,
    UpdateChatRoomView,
    SendMessageView,
    ListOfGroupMember,
    GroupMediaListView,
    DeleteMessageView,
)

urlpatterns = [
    path("chat-list/", ChatListViews.as_view(), name="groupe-list"),
    path('<uuid:group_id>/messages/', ChatMessageHistoryView.as_view(), name='chat_messages'),
    path('update-chatroom/<uuid:id>/', UpdateChatRoomView.as_view(), name='update-chatroom'),
    path('<uuid:group_id>/send-message/', SendMessageView.as_view(), name='send_message'),
    path('<uuid:group_id>/members/', ListOfGroupMember.as_view(), name='group_members'),
   # path('<uuid:group_id>/media/', GroupMediaListView.as_view(), name='group_media'),
    path('messages/<uuid:id>/delete/', DeleteMessageView.as_view(), name='delete_message'),
    path('<uuid:group_id>/messages/<uuid:id>/delete/', DeleteMessageView.as_view(), name='group_message_delete'),
]





