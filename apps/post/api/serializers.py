from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.Profile.models import Skill
from ..models import Project, RoleNeeded ,Application,Membership
from apps.Profile.api.serializer import SkillSerializer ,MemebrProfileSerializer ,ApplictionProfileSerializer


#! this ser used for create a project and give current user project and {id/}
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id","title", "description", "stage", "created_at",'like_count','comment_count','save_count')

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty or whitespace only.")
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        if len(value) > 150:
            raise serializers.ValidationError("Title must not exceed 150 characters.")
        return value.strip()

    def validate_description(self, value):
       
        if not value or not value.strip():
            raise serializers.ValidationError("Description cannot be empty or whitespace only.")
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        return value.strip()

    def validate_stage(self, value):
        valid_stages = [choice[0] for choice in Project.Stage.choices]
        if value not in valid_stages:
            raise serializers.ValidationError(f"Stage must be one of: {', '.join(valid_stages)}")
        return value
        

#! this ser user for give project owner role list
class GetJobRoleSerializer(serializers.ModelSerializer):
    required_skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = RoleNeeded
        fields = ("id", "title", "description", "slots_available", "required_skills", "is_open", "created_at")

#! this ser used for create a role
class CreateJobRoleSerializer(serializers.ModelSerializer):
    # accept list of skill objects {"name": "...", "category": "..."}
    required_skills = SkillSerializer(
        many=True,
        write_only=True
    )

    class Meta:
        model = RoleNeeded
        fields = ("title", "description", "slots_available", "required_skills")

    def validate_title(self, value):
        """Validate role title is not empty and reasonable length."""
        if not value or not value.strip():
            raise serializers.ValidationError("Role title cannot be empty.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Role title must be at least 2 characters long.")
        if len(value) > 100:
            raise serializers.ValidationError("Role title must not exceed 100 characters.")
        return value.strip()

    def validate_description(self, value):
        """Validate description if provided."""
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError("Description must be at least 5 characters long.")
        return value

    def validate_slots_available(self, value):
        """Validate slots_available is a positive integer."""
        if value is None or value < 1:
            raise serializers.ValidationError("Slots available must be at least 1.")
        if value > 100:
            raise serializers.ValidationError("Slots available cannot exceed 100.")
        return value

    def validate_required_skills(self, value):
        if not value:
            raise serializers.ValidationError("At least one skill is required.")
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 skills allowed per role.")
        
        
        for skill in value:
            name = skill.get("name", "").strip()
            category = skill.get("category", "").strip()
            
            if not name:
                raise serializers.ValidationError("Skill name cannot be empty.")
            if not category:
                raise serializers.ValidationError("Skill category cannot be empty.")
            if len(name) > 100:
                raise serializers.ValidationError("Skill name must not exceed 100 characters.")
            if len(category) > 100:
                raise serializers.ValidationError("Skill category must not exceed 100 characters.")
        
        return value

    def create(self, validated_data):
        skills_data = validated_data.pop("required_skills", [])
        role = RoleNeeded.objects.create(**validated_data)
        skill_objs = []
        for s in skills_data:
            name = s.get("name", "").strip()
            category = s.get("category", "").strip()
            if name and category:
                skill, created = Skill.objects.get_or_create(name=name, category=category)
                skill_objs.append(skill)
        if skill_objs:
            role.required_skills.set(skill_objs)
        return role
    
    
    def update(self, instance, validated_data):
        return super().update(instance, **validated_data)
     
     
     
     
#! this ser used for create a appliction
class ApplictionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Application
        fields=("id",'message','status','apply_role_purpose','github_link','portfolio_link')

    def validate_message(self, value):
        
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        if value and len(value) > 1000:
            raise serializers.ValidationError("Message must not exceed 1000 characters.")
        return value.strip() if value else value

    def validate_apply_role_purpose(self, value):
        if value:
            valid_purposes = [choice[0] for choice in Application.purpose.choices]
            if value not in valid_purposes:
                raise serializers.ValidationError(f"Purpose must be one of: {', '.join(valid_purposes)}")
        return value

    def validate(self, data):

        message = data.get('message', '').strip() if data.get('message') else ''
        purpose = data.get('apply_role_purpose', '')
        
        if not message and not purpose:
            raise serializers.ValidationError("Either a message or role purpose must be provided.")
        
        return data

    def create(self, validated_data):
        user=self.context['request'].user
        appliction=Application.objects.create(user=user,**validated_data)
        return appliction
        
#! this ser used for project owner appliction list
class GetapplictionSerializar(serializers.ModelSerializer):
    user= ApplictionProfileSerializer(source='user.user_profile',read_only=True)
    class Meta:
        model=Application
        fields=('message','apply_role_purpose','status','created_at','github_link','portfolio_link','user')
        read_only_fields=fields    
    
    
#! this ser used for project owner list of his memebrs
class MemebrSerializer(serializers.ModelSerializer):
    user= MemebrProfileSerializer(source='user.user_profile',read_only=True)
    
    class Meta:
        model=Membership
        fields=('role_title','joined_at','is_active','user')
        
     
        
'''
this all ser handle applied user list of appliction
and how many i join project
'''

class AppliedApplictionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Application
        fields=('message','apply_role_purpose','status','created_at','github_link','portfolio_link',)
        
class ProjectJoinSerializer(serializers.ModelSerializer):
    project=ProjectSerializer(read_only=True)
    class Meta:
        model=Membership
        fields = ('is_active','role_title','joined_at','project')
