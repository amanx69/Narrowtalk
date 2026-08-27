from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.views import APIView
from .serializer import MemberSerlizer, Roomserializer
from rest_framework.permissions import IsAuthenticated
from ..models import Room, RoomParticipant
from rest_framework.decorators import action, permission_classes
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from livekit import api
from django.conf import settings
from rest_framework.decorators import api_view
from ..models import RoomInviteLink
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.decorators import method_decorator

User=get_user_model()

def broadcast_room_event(room_id, payload):
    """Send a websocket event to every connected client of a room."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"room_{room_id}", payload)

def notify_user(user_id, payload):
    """Send a websocket event directly to a single user's connections."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"user_{user_id}", payload)

class RoomViewset(ModelViewSet):
    
    queryset=Room.objects.all()
    serializer_class=Roomserializer
    permission_classes=[IsAuthenticated]
    #! in this class retive show in user profile thire all room
    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user:
            raise PermissionDenied("You can only modify your own data.")

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)
    def get_queryset(self):  # type: ignore[override]
        return Room.objects.filter(owner=self.request.user)
    def partial_update(self, request, *args, **kwargs):
        obj= self.get_object()
        serializer=self.get_serializer(obj,data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
        
    def perform_destroy(self, instance):
        broadcast_room_event(instance.id, {
            "type": "room_deleted",
            "room_id": str(instance.id),
            "room_name": instance.room_name,
            "message": "Room was deleted by the owner",
        })
        instance.delete()
    

#! memebr join whit room id and exit

#TODO remove this class if make if jion with link and code 
class RoomJoinExit(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,room_id):
        room=get_object_or_404(Room,id=room_id)
        try:
            if room.owner == self.request.user:
                return Response({
                    "message":"you are a owner of this room "
                    },status.HTTP_400_BAD_REQUEST)
            if self.request.user in room.participants.all():
                return Response({"you are already in room"},status.HTTP_400_BAD_REQUEST)
            room.participants.add(self.request.user)
            broadcast_room_event(room.id, {"type": "room_participants_update"})
            return Response({
                "message":f"you  {room.room_name} join this room"
            },status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error":"somthing went wrong"},status.HTTP_400_BAD_REQUEST)
        #! exit the room also used for leaving a room 
    def delete(self,request,room_id):  
        try:
            room=get_object_or_404(Room,id=room_id)
            if self.request.user not in room.participants.all():
                return Response({"message":"you are not in this room"},status.HTTP_400_BAD_REQUEST)
            #! if user is remove than deleted the room
            if self.request.user ==room.owner:
                broadcast_room_event(room.id, {
                    "type": "room_deleted",
                    "room_id": str(room.id),
                    "room_name": room.room_name,
                    "message": "Room was deleted by the owner",
                })
                room.delete()
                return Response({"message":"owner remove than room is dissmiss"})
            room.participants.remove(self.request.user)
            broadcast_room_event(room.id, {"type": "room_participants_update"})
            return Response({
                "message":f"you remove {room.room_name} done"
            },status.HTTP_200_OK)
        except Exception as e:
           return Response({"error":str(e)},status.HTTP_400_BAD_REQUEST)
       
       
#! remove a member from the room by owner
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_member(request, room_id, member_id):
    room = get_object_or_404(Room, id=room_id)
    if room.owner != request.user:
        raise PermissionDenied("You can only remove members from your own rooms.")
    
    member = get_object_or_404(User, id=member_id)
    if member not in room.participants.all():
        return Response({"message":f"{member.username} not already in room"})
    room.participants.remove(member)
    broadcast_room_event(room.id, {"type": "room_participants_update"})
    notify_user(member.id, {
        "type": "room_kicked",
        "room_id": str(room.id),
        "room_name": room.room_name,
        "message": "You were kicked by the owner",
    })
    
    return Response({"message": f"{member.email} has been removed from {room.room_name}."}, status=status.HTTP_200_OK)
       
       

#! on and of the mic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mic_on_off(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    user = request.user

    if user not in room.participants.all():
        raise PermissionDenied("You are not a participant of this room.")

  
    participant = get_object_or_404(RoomParticipant, room=room, user=user)
    participant.is_mute = not participant.is_mute  # Toggle mic status
    participant.save(update_fields=['is_mute'])

    return Response({"message": f"Mic status changed to {'on' if not participant.is_mute else 'off'}."}, status=status.HTTP_200_OK)



#! join room with unique id
class RoomJoinWithUinqeId(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,code):
        
        try:
            room=get_object_or_404(Room,uniqe_id=code)
            user= get_object_or_404(User,id=request.user.id)
            if user in room.participants.all():
                return Response({"message":"you are already in room"},status.HTTP_400_BAD_REQUEST)
            room.participants.add(user)
            room.save()
            broadcast_room_event(room.id, {"type": "room_participants_update"})
            return Response(
                Roomserializer(room).data,
                status.HTTP_200_OK,
            )
            
        except Exception as e:
            return Response({"error":str(e)},status.HTTP_400_BAD_REQUEST)
  
#! show all room participants

class RoomParticipantsView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,room_id):
        try:
            room=get_object_or_404(Room,id=room_id)
            participants = RoomParticipant.objects.filter(
                room=room,
            ).select_related('user', 'user__user_profile')
            serializer=MemberSerlizer(participants,many=True)
            return Response(serializer.data,status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":f"Failed to retrieve room participants"},status.HTTP_400_BAD_REQUEST)


class VoiceTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def _generate_token(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        
        # Auto-register participant if entering voice channel
        RoomParticipant.objects.get_or_create(room=room, user=request.user)
        broadcast_room_event(room.id, {"type": "room_participants_update"})

        room_name = str(room.id)
        user_identity = str(request.user.id)
        user_name = getattr(request.user, 'username', '') or request.user.email

        token = (
            api.AccessToken(
                settings.LIVEKIT_API_KEY,
                settings.LIVEKIT_API_SECRET,
            )
            .with_identity(user_identity)
            .with_name(user_name)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                )
            )
            .to_jwt()
        )

        return Response({
            "url": settings.LIVEKIT_URL,
            "token": token,
            "room_name": room_name,
            "identity": user_identity,
            "name": user_name,
        }, status=status.HTTP_200_OK)

    def post(self, request, room_id):
        return self._generate_token(request, room_id)

    def get(self, request, room_id):
        return self._generate_token(request, room_id)
        
        
        

#TODO reove it later 
class ShowRoomInHomeScreen(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        count = int(request.query_params.get('count', 10))
        ids = list(Room.objects.values_list('id', flat=True))
        import random
        sample_ids = random.sample(ids, min(count, len(ids)))
        rooms = Room.objects.filter(id__in=sample_ids)
        serializer = Roomserializer(rooms, many=True)
        return Response(serializer.data)
        
    
        

#! get link in room

class GiveLinkTORoom(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        Target_room = get_object_or_404(Room, id=room_id)

        if Target_room.owner != request.user:
            return Response({"message": "Only the room owner can generate a link."}, status=status.HTTP_403_FORBIDDEN)

        link_key = f"room_link_{room_id}"
        cached_link = cache.get(link_key)
        if cached_link:
            return Response({"link": cached_link})

        RoomLink = RoomInviteLink.objects.filter(
            room=Target_room, is_active=True
        ).order_by('-created_at').first()

        if not RoomLink:
            return Response({"message": "no active invite link for this room"}, status=status.HTTP_404_NOT_FOUND)

        link = f"http://127.0.0.1:8000/api/v1/rooms/join_with_link/{RoomLink.token}"
        cache.set(link_key, link, timeout=300)
        return Response({"link": link})
     
      
#! join with room link 
class JoinRoomWithLink(APIView):
    permission_classes=[IsAuthenticated]
    @method_decorator(ratelimit(key='ip', rate='10/m',method=['POST']))
    def post(self,request,Room_link):

        roomlink = get_object_or_404(RoomInviteLink, token=Room_link)
        if not roomlink.is_valid():
            return Response({"message": "link is expired or disabled; you can't join"}, status.HTTP_400_BAD_REQUEST)
        if self.request.user in roomlink.room.participants.all():
            return Response({"message": "you are already in room"}, status.HTTP_202_ACCEPTED)

        roomlink.room.participants.add(self.request.user)
        roomlink.use_count += 1
        roomlink.save(update_fields=['use_count'])
        broadcast_room_event(roomlink.room.id, {"type": "room_participants_update"})
        return Response({"message": "you are join the room"}, status.HTTP_200_OK)
        



#! expire the room link


class ExpireRoomLink(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        Target_room = get_object_or_404(Room, id=room_id)
        if Target_room.owner != self.request.user:
            return Response({"message": "only Room owner can performe this task"}, status.HTTP_403_FORBIDDEN)

        RoomLink = RoomInviteLink.objects.filter(room=Target_room).order_by('-created_at').first()
        if not RoomLink:
            return Response({"message": "No invite link found for this room"}, status.HTTP_404_NOT_FOUND)
        if RoomLink.is_active is not True:
            return Response({"message": "Link is already disabled"}, status.HTTP_400_BAD_REQUEST)

        RoomLink.is_active = False
        RoomLink.save(update_fields=['is_active'])
        return Response({"message": f"{Target_room.id} link is disable"}, status.HTTP_200_OK)
    