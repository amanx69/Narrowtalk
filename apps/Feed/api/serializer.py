from rest_framework import serializers
from ..models import Projectcomment 
from apps.post.models import Project
from apps.Profile.api.serializer import InFeedProfile ,InCommentProfile
from apps.Profile.models import Skill
from apps.post.models import RoleNeeded

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
    required_skills = serializers.SerializerMethodField()
    owner = InFeedProfile(source="owner.user_profile",read_only=True)
    is_liked = serializers.BooleanField(read_only=True, default=False)
    is_saved = serializers.BooleanField(read_only=True, default=False)

    def get_required_skills(self, obj):
        skills = []
        seen = set()
        for role in obj.roles.all():
            for skill in role.required_skills.all():
                if skill.id not in seen:
                    seen.add(skill.id)
                    skills.append(skill)
        return SkillMiniSerializer(skills, many=True).data

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description',
            'like_count', 'save_count', 'comment_count',
            'view_count', 'application_count',
            'owner', 'is_liked', 'is_saved', 'created_at',"required_skills",
        ]
        read_only_fields=fields



class HomeFeedSerializer(serializers.ModelSerializer):
    required_skills = serializers.SerializerMethodField()
    owner = InFeedProfile(source="owner.user_profile",read_only=True)

    def get_required_skills(self, obj): #TODO optmize later  both
        skills = []
        seen = set()
        for role in obj.roles.all():
            for skill in role.required_skills.all():
                if skill.id not in seen:
                    seen.add(skill.id)
                    skills.append(skill)
        return SkillMiniSerializer(skills, many=True).data

    class Meta:
        model=Project
        fields = [
                    'id', 'title', 'description',
                    'like_count', 'save_count', 'comment_count',
                    'view_count', 'application_count',
                    'owner', 'created_at',"required_skills",
                ]
        read_only_fields=fields