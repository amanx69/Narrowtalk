from rest_framework import serializers
from ..models import Profile ,Skill





class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = ("name",'created_at')

    def validate_name(self, value):
        return value.strip()

    def create(self, validated_data):
        return Skill.objects.create(**validated_data)
    

class Profileserlizsers(serializers.ModelSerializer):
    email=serializers.EmailField(source="user.email")
    
    class Meta:
        model=Profile
        fields=[
            'username',
            'profile_pic',
            "bio",
            'email',
            'role',
            'links',
            'availability',
            'project_joined',
            'profile_like',
            'looking_for',
            'avter_image',
            ]
         
        
    
class InRoomUserProfile(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields=['profile_pic','username',' english_lable']
        
        
        
        

    
    
#! feed user_profofile serializer
class InFeedProfile(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields=['profile_pic','username','id']
        
        

class InCommentProfile(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields=['profile_pic','username','id']
        
        
        
class MemebrProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        
        model=Profile
        fields=['profile_pic','username','id']

class ApplictionProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        
        model=Profile
        fields=['profile_pic','username','id']
        