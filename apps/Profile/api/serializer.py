from rest_framework import serializers
from ..models import Profile ,Skill
from apps.post.models import Project
from core.helpers import CompressedProfilePicField ,ThumbnailProfilePicField




class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = ("name",)

    def validate_name(self, value):
        return value.strip()

    def create(self, validated_data):
        return Skill.objects.create(**validated_data)
    


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except (TypeError, ValueError):
            self.fail('invalid')

#! this ser used for profile project listing
class ProjectProfileSerializer(serializers.ModelSerializer):
    profile_pic = ThumbnailProfilePicField(read_only=True)
    class Meta:
        model = Profile
        fields = ('id', 'user', 'profile_pic', 'username')

class ProjectDetailSerializer(serializers.ModelSerializer):
    owner = ProjectProfileSerializer(source='owner.user_profile', read_only=True)
    class Meta:
        model = Project 
        fields = ('id', 'project_name', 'title', 'description', 'stage', 'status', 'created_at', 'project_file', 'owner', 'like_count', 'save_count', 'comment_count', 'view_count')
        read_only_fields = fields

class Profileserlizsers(serializers.ModelSerializer):
    profile_pic = CompressedProfilePicField(required=False)
    avter_image = CompressedProfilePicField(required=False)
    email = serializers.EmailField(source="user.email")
    skills = CreatableSlugRelatedField(many=True, slug_field="name", queryset=Skill.objects.all())
    projects = ProjectDetailSerializer(source='user.projects_owner', many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    username = serializers.CharField(min_length=4, error_messages={
        'min_length': 'The username must be at least 4 characters long.'
    })
    bio = serializers.CharField(min_length=5, error_messages={
        'min_length': 'The bio must be at least 5 characters long.'
    })

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.profile_likes.filter(user=request.user).exists()
        return False

    class Meta:
        model = Profile
        fields = [
            'id',
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
            'skills',
            'project_completed',
            'is_liked',
            'project_count',
            'projects',
        ]
        read_only_fields = [
            'id',
            'email',
            'project_joined',
            'project_completed',
            'profile_like',
            'project_count',
            'is_liked',
            'projects',
        ]
        
    def validate_project_file(self, value):
        if not value:
            return value
            
        max_size = 5 * 1024 * 1024  
        if value.size > max_size:
            raise serializers.ValidationError("File size must be under 5 MB.")
        
        allowed_types = ['image/jpeg', 'image/png',]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only JPG, PNG images are allowed.")
            
        return value
    
class OtherUserProfileSerializer(serializers.ModelSerializer):
    profile_pic = CompressedProfilePicField(required=False)
    avter_image = CompressedProfilePicField(required=False)
    projects = ProjectDetailSerializer(source='user.projects_owner', many=True, read_only=True)
    email=serializers.EmailField(source='user.email')
    
    class Meta:
        model=Profile
        fields=[
            'id',
            'username',
            'profile_pic',
            "bio",
            'role',
            'links',
            'email',
            'availability',
            'project_joined',
            'profile_like',
            'looking_for',
            'avter_image',
            'projects',
        ]
        read_only_fields=fields
        
    
class SearchResultProfileSerializer(serializers.ModelSerializer):
    profile_pic = ThumbnailProfilePicField(read_only=True) 
    user_id=serializers.UUIDField(source='user.id',read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'username', 'profile_pic', 'role']
        
        

    
    
#! feed user_profofile serializer
class InFeedProfile(serializers.ModelSerializer):
    profile_pic=ThumbnailProfilePicField(read_only=True)
    class Meta:
        model=Profile
        fields=['profile_pic','username','id']
        
        

class InCommentProfile(serializers.ModelSerializer):
    profile_pic=ThumbnailProfilePicField(read_only=True)
    class Meta:
        model=Profile
        fields=['profile_pic','username','id']
        
        
        
class MemebrProfileSerializer(serializers.ModelSerializer):
    profile_pic=ThumbnailProfilePicField(read_only=True)
    
    class Meta:
        
        model=Profile
        fields=['profile_pic','username','id']
#! used for appliction profile
class ApplictionProfileSerializer(serializers.ModelSerializer):
    profile_pic=ThumbnailProfilePicField(read_only=True)
    
    class Meta:
        
        model=Profile
        fields=['profile_pic','username','id',]
        
        
#! used for projectprofile        
class ProjectProfileSerializer(serializers.ModelSerializer):
    profile_pic=ThumbnailProfilePicField(read_only=True)
    class Meta:
        model=Profile
        fields=('id', 'user', 'profile_pic', 'username')
        
       #! used forchat profile 
class ChatProfileSerializer(serializers.ModelSerializer):
    profile_pic=ThumbnailProfilePicField(read_only=True)
    
    class Meta:
        model=Profile
        fields=('id', 'user', 'profile_pic', 'username')
        
      # used for list and sent request to join  
class RequestProfileSerializer(serializers.ModelSerializer):
    profile_pic=ThumbnailProfilePicField(read_only=True)
    class Meta:
        model=Profile
        fields=('id', 'user', 'profile_pic', 'username')
        