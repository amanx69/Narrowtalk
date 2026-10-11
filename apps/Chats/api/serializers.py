from rest_framework import serializers
from ..models import ChatGroup ,Message ,GroupMember
from apps.Profile.api.serializer import ChatProfileSerializer ,MemebrProfileSerializer
from core.helpers import CompressedProfilePicField


class ChatGroupeListSerializer(serializers.ModelSerializer):
    group_dp=CompressedProfilePicField(read_only =True)
    class Meta:
        model= ChatGroup
        fields=('id','group_name','group_dp')
 #! ussed for compress images anf videos       
class CompressedFileField(serializers.FileField):
    def to_representation(self, value):
        url = super().to_representation(value)
        if url and '/upload/' in url:
            if url.endswith('.pdf'):
                return url
            if url.endswith(('.mp4', '.mov', '.avi', '.webm')):
                return url.replace('/upload/', '/upload/q_auto,f_auto,w_720/')
                
            
            return url.replace('/upload/', '/upload/q_auto,f_auto,w_1080/')
        return url
          
class MessageSerilizer(serializers.ModelSerializer):
    sender_profile = ChatProfileSerializer(source='sender.user_profile',read_only=True)
    file=CompressedFileField(required=False)
    class Meta:
        model= Message
        fields=('id','text','file','created_at',"sender_profile")
        


class GroupMemberListSerilizer(serializers.ModelSerializer):
    user_profile = MemebrProfileSerializer(source='user.user_profile', read_only=True)
    class Meta:
        model = GroupMember
        fields = ('user', 'is_active', 'role', 'joined_at', 'user_profile')


class GroupMediaSerializer(serializers.ModelSerializer):
    file = CompressedFileField(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'file', 'created_at')

    
    