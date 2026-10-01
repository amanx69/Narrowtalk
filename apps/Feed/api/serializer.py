from rest_framework import serializers
from ..models import Projectcomment ,Projectsave
from apps.post.models import Project
from apps.Profile.api.serializer import InFeedProfile ,InCommentProfile
from apps.Profile.models import Skill
from apps.post.models import RoleNeeded
from apps.post.api.serializers import ProjectListSerializer

class CommentSerlizer(serializers.ModelSerializer):
    class Meta:
        model=Projectcomment  
        fields=('text',"created_at")   
    def validate_text(self,value):
        value=value.strip()
        if not value:
            raise serializers.ValidationError("comment must be provided")
        if len(value) > 500:
            raise serializers.ValidationError("Comment cannot exceed 500 characters.")
        
        if len(value) < 2:
            raise serializers.ValidationError("Comment is too short.")
        
        return value
        
        
    def create(self, validated_data):
        user=self.context['request'].user
        comment=Projectcomment.objects.create(
            user=user,
            **validated_data
        )
        return comment
        
        
        
class GetCommentSerializer(serializers.ModelSerializer):
    user= InCommentProfile(source='user.user_profile',read_only=True)
    class Meta:
        model=Projectcomment
        fields=('text',"created_at",'id','user')  
         
        read_only_fields=fields
       
       
       
class SkillMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']

class FeedSerializer(serializers.ModelSerializer):
    owner = InFeedProfile(source="owner.user_profile",read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    def get_is_liked(self, obj):
        if hasattr(obj, 'is_liked_by_user'):
            return obj.is_liked_by_user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ProjectLike.objects.filter(user=request.user, project=obj).exists()
        return False
        
    def get_is_saved(self, obj):
        if hasattr(obj, 'is_saved_by_user'):
            return obj.is_saved_by_user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Projectsave.objects.filter(user=request.user, project=obj).exists()
        return False

 

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description',
            'like_count', 'save_count', 'comment_count',
            'view_count', 'member_count','project_file',
            'owner', 'is_liked', 'is_saved', 'created_at',
        ]
        read_only_fields=fields



from ..models import ProjectLike, Projectsave

class HomeFeedSerializer(serializers.ModelSerializer):
    owner = InFeedProfile(source="owner.user_profile",read_only=True)
    owner_id=serializers.UUIDField(source="owner.id",read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model=Project
        fields = [
                    'id','project_name', 'title', 'description',
                    'like_count', 'save_count', 'comment_count',
                    'view_count', 'member_count','project_file',
                    'owner', 'is_liked', 'is_saved', 'created_at',
                    "owner_id"
                ]
        read_only_fields=fields

    def get_is_liked(self, obj):
        if hasattr(obj, 'is_liked_by_user'):
            return obj.is_liked_by_user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ProjectLike.objects.filter(user=request.user, project=obj).exists()
        return False
        
    def get_is_saved(self, obj):
        if hasattr(obj, 'is_saved_by_user'):
            return obj.is_saved_by_user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Projectsave.objects.filter(user=request.user, project=obj).exists()
        return False
        
class ProjectSaveSerializer(serializers.ModelSerializer):
    project= ProjectListSerializer(read_only=True)
    class Meta:
        model=Projectsave
        fields=("created_at",'project')
        