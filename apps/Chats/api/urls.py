from django.urls import path
from .views import ChatListViews ,ChatMessageHistoryView ,UpdateChatRoomView ,SendMessageView

urlpatterns = [
    path("chat-list/",ChatListViews.as_view(),name="groupe-list"),
    path('<uuid:group_id>/messages/', ChatMessageHistoryView.as_view(), name='chat_messages'),
    path('update-chatroom/<uuid:id>/', UpdateChatRoomView.as_view(), name='update-chatroom'),
    path('<uuid:group_id>/send-message/', SendMessageView.as_view(), name='send_message'),
]


