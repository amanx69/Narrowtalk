from rest_framework import serializers
from ..models import Room ,RoomParticipant, RoomInviteLink
from ..service import *
from django.contrib.auth import get_user_model
from ...Profile import models

User=get_user_model()
class Roomserializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.email', read_only=True)
    owner_id = serializers.UUIDField(source='owner.id', read_only=True)

    class Meta:
        model= Room
        fields=['id','room_name',"room_profile","uniqe_id",'owner','owner_id','created_at']
            
    def validate(self, attrs):
        
        room_name=attrs.get('room_name')
        if not room_name:
            raise serializers.ValidationError("room name must be importent")
        
        return attrs
        
        
        


class MemberSerlizer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.user_profile.username')
    profile_pic = serializers.ImageField(
        source='user.user_profile.profile_pic',
        allow_null=True,
        required=False,
    )
    
    class Meta:
        model=RoomParticipant
        fields=['id','username','profile_pic','is_mute','joined_at']
        
#! roomLink serlizers


class RoomInviteLinkSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=RoomInviteLink
        fields=["token",'is_active']