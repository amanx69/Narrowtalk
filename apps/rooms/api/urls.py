from .views import (
    RoomViewset,
    RoomJoinWithUinqeId,
    RoomJoinExit,
    RoomParticipantsView,
    VoiceTokenView,
    ShowRoomInHomeScreen,
    mic_on_off,
    remove_member,
    JoinRoomWithLink,
    GiveLinkTORoom,
    ExpireRoomLink,
    
)
from rest_framework.routers import DefaultRouter 
from django.urls import path

router=DefaultRouter()
router.register('room',RoomViewset,basename="room-viewset")
urlpatterns = router.urls

urlpatterns+=[
    
    
    path("rooms/<uuid:room_id>/join/", RoomJoinExit.as_view(), name="join_room"),
    path("rooms/join-by-code/<str:code>/", RoomJoinWithUinqeId.as_view(), name="join_room_by_code"),
    path("rooms/<uuid:room_id>/participants/", RoomParticipantsView.as_view(), name="room_participants"),
    path("rooms/<uuid:room_id>/voice-token/", VoiceTokenView.as_view(), name="voice_token"),
    path("rooms/<uuid:room_id>/remove-member/<uuid:member_id>/", remove_member, name="remove_member"),
    path("rooms/<uuid:room_id>/mic-toggle/", mic_on_off, name="mic_toggle"),
    path("rooms/Fatch_homepage/",ShowRoomInHomeScreen.as_view(),name="home_room"),
    path("rooms/join_with_link/<str:Room_link>/",JoinRoomWithLink.as_view(),name="join_with_token"),
    path("rooms/give_room_link/<uuid:room_id>/",GiveLinkTORoom.as_view(),name="give_room_link"),
    path("rooms/ExpireLink/<uuid:room_id>/",ExpireRoomLink.as_view(),name="expire_the_roomlink")
    
    
]
    

