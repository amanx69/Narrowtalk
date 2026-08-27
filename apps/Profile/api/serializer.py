from rest_framework import serializers
from ..models import Profile ,Skill



class Profileserlizsers(serializers.ModelSerializer):
    email=serializers.EmailField(source="user.email")
    
    class Meta:
        model=Profile
        fields=['username','profile_pic',"bio",'email']
         
        
    
class InRoomUserProfile(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields=['profile_pic','username',' english_lable']
        
        
        
        
class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = ("name", "category")

    def validate_name(self, value):
        return value.strip()

    def create(self, validated_data):
        return Skill.objects.create(**validated_data)
    
    
    
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
        