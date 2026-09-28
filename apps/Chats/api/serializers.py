from rest_framework import serializers
from ..models import ChatGroup ,Message
from apps.Profile.api.serializer import ChatProfileSerializer

class CompressedProfilePicField(serializers.ImageField):
    def to_representation(self, value):
        url = super().to_representation(value)
        if url and '/upload/' in url:
            return url.replace('/upload/', '/upload/q_auto,f_auto,c_fill,w_500,h_500/')
        return url

class ChatGroupeListSerializer(serializers.ModelSerializer):
    group_dp=CompressedProfilePicField(read_only =True)
    class Meta:
        model= ChatGroup
        fields=('id','group_name','group_dp')
 #! ussed for compress images anf videos       
class CompressedProjectFileField(serializers.FileField):
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
    file=CompressedProfilePicField(required=False)
    class Meta:
        model= Message
        fields=('id','text','file','created_at',"sender_profile")